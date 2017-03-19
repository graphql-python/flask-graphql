import json
from promise import Promise
from collections import namedtuple

import six
from flask import Response, request
from flask.views import View

from graphql import Source, execute, parse, validate
from graphql.error import format_error as format_graphql_error
from graphql.error import GraphQLError
from graphql.execution import ExecutionResult
from graphql.type.schema import GraphQLSchema
from graphql.utils.get_operation_ast import get_operation_ast

from .render_graphiql import render_graphiql


GraphQLParams = namedtuple('GraphQLParams', 'query,variables,operation_name,id')
GraphQLResponse = namedtuple('GraphQLResponse', 'result,params,status_code')


class HttpQueryError(Exception):
    def __init__(self, status_code, message=None, is_graphql_error=False, headers=None):
        self.status_code = status_code
        self.message = message
        self.is_graphql_error = is_graphql_error
        self.headers = headers
        super(HttpQueryError, self).__init__(message)


class GraphQLView(View):
    schema = None
    executor = None
    root_value = None
    context = None
    pretty = False
    graphiql = False
    graphiql_version = None
    graphiql_template = None
    middleware = None
    batch = False

    methods = ['GET', 'POST', 'PUT', 'DELETE']

    def __init__(self, **kwargs):
        super(GraphQLView, self).__init__()
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

        assert isinstance(self.schema, GraphQLSchema), 'A Schema is required to be provided to GraphQLView.'

    # noinspection PyUnusedLocal
    def get_root_value(self, request):
        return self.root_value

    def get_context(self, request):
        if self.context is not None:
            return self.context
        return request

    def get_middleware(self, request):
        return self.middleware

    def get_executor(self, request):
        return self.executor

    def render_graphiql(self, params, result):
        return render_graphiql(
            params=params,
            result=result,
            graphiql_version=self.graphiql_version,
            graphiql_template=self.graphiql_template,
        )

    def dispatch_request(self):
        
        try:
            request_method = request.method.lower()
            if request_method not in ('get', 'post'):
                raise HttpQueryError(
                    405,
                    'GraphQL only supports GET and POST requests.',
                    headers={
                        'Allow': ['GET, POST']
                    }
                )

            data = self.parse_body()
            is_batch = isinstance(data, list)

            show_graphiql = not is_batch and self.should_display_graphiql(data)
            catch = HttpQueryError if show_graphiql else None
            only_allow_query = request_method == 'get'

            if not is_batch:
                assert isinstance(data, dict), "GraphQL params should be a dict. Received {}.".format(data)
                data = dict(data, **request.args.to_dict())
                data = [data]
            elif not self.batch:
                raise HttpQueryError(
                    400,
                    'Batch requests are not allowed.'
                )


            responses = [self.get_response(
                self.schema,
                entry,
                catch,
                only_allow_query,
                root_value=self.get_root_value(request),
                context_value=self.get_context(request),
                middleware=self.get_middleware(request),
                executor=self.get_executor(request),
            ) for entry in data]

            response, params, status_codes = zip(*responses)
            status_code = max(status_codes)

            if not is_batch:
                response = response[0]

            pretty = self.pretty or show_graphiql or request.args.get('pretty')
            result = self.json_encode(response, pretty)

            if show_graphiql:
                return self.render_graphiql(
                    params=params[0],
                    result=result
                )

            return Response(
                status=status_code,
                response=result,
                content_type='application/json'
            )

        except HttpQueryError as e:
            return Response(
                self.json_encode({
                    'errors': [self.format_error(e)]
                }),
                status=e.status_code,
                headers=e.headers,
                content_type='application/json'
            )

    def get_response(self, schema, data, catch=None, only_allow_query=False, **kwargs):
        params = self.get_graphql_params(data)
        try:
            execution_result = self.execute_graphql_request(
                schema,
                data,
                params,
                only_allow_query,
                **kwargs
            )
        except catch:
            execution_result = None
        
        response, status_code = self.format_execution_result(execution_result, params.id, self.format_error)
        return GraphQLResponse(
            response,
            params,
            status_code
        )

    @staticmethod
    def format_execution_result(execution_result, id, format_error):
        status_code = 200
        if execution_result:
            response = {}

            if execution_result.errors:
                response['errors'] = [format_error(e) for e in execution_result.errors]

            if execution_result.invalid:
                status_code = 400
            else:
                status_code = 200
                response['data'] = execution_result.data

            if id:
                response['id'] = id

        else:
            response = None

        return response, status_code

    # noinspection PyBroadException
    def parse_body(self):
        # We use mimetype here since we don't need the other
        # information provided by content_type
        content_type = request.mimetype
        if content_type == 'application/graphql':
            return {'query': request.data.decode()}

        elif content_type == 'application/json':
            try:
                return json.loads(request.data.decode('utf8'))
            except:
                raise HttpQueryError(
                    400,
                    'POST body sent invalid JSON.'
                )

        elif content_type == 'application/x-www-form-urlencoded':
            return request.form.to_dict()

        elif content_type == 'multipart/form-data':
            return request.form.to_dict()

        return {}

    @staticmethod
    def execute_graphql_request(schema, data, params, only_allow_query=False, **kwargs):
        if not params.query:
            raise HttpQueryError(400, 'Must provide query string.')

        try:
            source = Source(params.query, name='GraphQL request')
            ast = parse(source)
            validation_errors = validate(schema, ast)
            if validation_errors:
                return ExecutionResult(
                    errors=validation_errors,
                    invalid=True,
                )
        except Exception as e:
            return ExecutionResult(errors=[e], invalid=True)

        if only_allow_query:
            operation_ast = get_operation_ast(ast, params.operation_name)
            if operation_ast and operation_ast.operation != 'query':
                raise HttpQueryError(
                    405,
                    'Can only perform a {} operation from a POST request.'.format(operation_ast.operation),
                    headers={
                        'Allow': ['POST'],
                    }
                )

        try:
            return execute(
                schema,
                ast,
                operation_name=params.operation_name,
                variable_values=params.variables,
                **kwargs
            )
        except Exception as e:
            return ExecutionResult(errors=[e], invalid=True)

    @staticmethod
    def json_encode(data, pretty=False):
        if not pretty:
            return json.dumps(data, separators=(',', ':'))

        return json.dumps(
            data,
            indent=2,
            separators=(',', ': ')
        )

    def should_display_graphiql(self, data):
        if not self.graphiql or 'raw' in data:
            return False

        return self.request_wants_html()

    def request_wants_html(self):
        best = request.accept_mimetypes \
            .best_match(['application/json', 'text/html'])
        return best == 'text/html' and \
            request.accept_mimetypes[best] > \
            request.accept_mimetypes['application/json']

    @staticmethod
    def get_variables(variables):
        if variables and isinstance(variables, six.text_type):
            try:
                return json.loads(variables)
            except:
                raise HttpQueryError(400, 'Variables are invalid JSON.')
        return variables

    @classmethod
    def get_graphql_params(cls, data):
        query = data.get('query')
        variables = cls.get_variables(data.get('variables'))
        id = data.get('id')
        operation_name = data.get('operationName')

        return GraphQLParams(query, variables, operation_name, id)

    @staticmethod
    def format_error(error):
        if isinstance(error, GraphQLError):
            return format_graphql_error(error)

        return {'message': six.text_type(error)}
