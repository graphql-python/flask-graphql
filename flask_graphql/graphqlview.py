import json
from promise import Promise

import six
from flask import Response, request
from flask.views import View
from werkzeug.exceptions import BadRequest, MethodNotAllowed

from graphql import Source, execute, parse, validate
from graphql.error import format_error as format_graphql_error
from graphql.error import GraphQLError
from graphql.execution import ExecutionResult
from graphql.type.schema import GraphQLSchema
from graphql.utils.get_operation_ast import get_operation_ast

from .render_graphiql import render_graphiql


class HttpError(Exception):
    def __init__(self, status_code, message=None, is_graphql_error=False, headers=None):
        self.status_code = status_code
        self.message = message
        self.is_graphql_error = is_graphql_error
        self.headers = headers
        super(HttpError, self).__init__(message)


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

    def render_graphiql(self, **kwargs):
        return render_graphiql(
            graphiql_version=self.graphiql_version,
            graphiql_template=self.graphiql_template,
            **kwargs
        )

    def dispatch_request(self):
        try:
            if request.method.lower() not in ('get', 'post'):
                raise HttpError(
                    405,
                    'GraphQL only supports GET and POST requests.',
                    headers={
                        'Allow': ['GET, POST']
                    }
                )

            data = self.parse_body(request)
            is_batch = isinstance(data, list)

            show_graphiql = not is_batch and self.graphiql and self.can_display_graphiql(data)

            if not is_batch:
                # print data
                data = dict(data, **request.args.to_dict())
                data = [data]
            elif not self.batch:
                raise HttpError(
                    400,
                    'Batch requests are not allowed.'
                )

            responses = [self.get_response(request, entry, show_graphiql) for entry in data]
            response, status_codes = zip(*responses)
            status_code = max(status_codes)

            if not is_batch:
                response = response[0]

            pretty = self.pretty or show_graphiql or request.args.get('pretty')
            result = self.json_encode(response, pretty)

            if show_graphiql:
                query, variables, operation_name, id = self.get_graphql_params(request, data[0])
                return self.render_graphiql(
                    query=query,
                    variables=variables,
                    operation_name=operation_name,
                    result=result
                )

            return Response(
                status=status_code,
                response=result,
                content_type='application/json'
            )

        except HttpError as e:
            return Response(
                self.json_encode({
                    'errors': [self.format_error(e)]
                }),
                status=e.status_code,
                headers=e.headers,
                content_type='application/json'
            )

    def get_response(self, request, data, show_graphiql=False):
        query, variables, operation_name, id = self.get_graphql_params(request, data)
        execution_result = self.execute_graphql_request(
            data,
            query,
            variables,
            operation_name,
            show_graphiql
        )
        return self.format_execution_result(execution_result, id)

    def format_execution_result(self, execution_result, id):
        status_code = 200
        if execution_result:
            response = {}

            if execution_result.errors:
                response['errors'] = [self.format_error(e) for e in execution_result.errors]

            if execution_result.invalid:
                status_code = 400
            else:
                status_code = 200
                response['data'] = execution_result.data

            if self.batch:
                response['id'] = id

        else:
            response = None

        return response, status_code

    @staticmethod
    def json_encode(data, pretty=False):
        if not pretty:
            return json.dumps(data, separators=(',', ':'))

        return json.dumps(
            data,
            indent=2,
            separators=(',', ': ')
        )

    # noinspection PyBroadException
    def parse_body(self, request):
        content_type = self.get_content_type(request)
        if content_type == 'application/graphql':
            return {'query': request.data.decode()}

        elif content_type == 'application/json':
            try:
                return json.loads(request.data.decode('utf8'))
            except:
                raise HttpError(
                    400,
                    'POST body sent invalid JSON.'
                )

        elif content_type == 'application/x-www-form-urlencoded':
            return request.form.to_dict()

        elif content_type == 'multipart/form-data':
            return request.form.to_dict()

        return {}

    def execute(self, *args, **kwargs):
        return execute(self.schema, *args, **kwargs)

    def execute_graphql_request(self, data, query, variables, operation_name, show_graphiql=False):
        if not query:
            if show_graphiql:
                return None
            raise HttpError(400, 'Must provide query string.')

        try:
            source = Source(query, name='GraphQL request')
            ast = parse(source)
            validation_errors = validate(self.schema, ast)
            if validation_errors:
                return ExecutionResult(
                    errors=validation_errors,
                    invalid=True,
                )
        except Exception as e:
            return ExecutionResult(errors=[e], invalid=True)

        if request.method.lower() == 'get':
            operation_ast = get_operation_ast(ast, operation_name)
            if operation_ast and operation_ast.operation != 'query':
                if show_graphiql:
                    return None
                raise HttpError(
                    405,
                    'Can only perform a {} operation from a POST request.'.format(operation_ast.operation),
                    headers={
                        'Allow': ['POST'],
                    }
                )

        try:
            return self.execute(
                ast,
                root_value=self.get_root_value(request),
                variable_values=variables or {},
                operation_name=operation_name,
                context_value=self.get_context(request),
                middleware=self.get_middleware(request),
                executor=self.get_executor(request)
            )
        except Exception as e:
            return ExecutionResult(errors=[e], invalid=True)

    @classmethod
    def can_display_graphiql(cls, data):
        raw = 'raw' in request.args or 'raw' in data
        return not raw and cls.request_wants_html(request)

    @classmethod
    def request_wants_html(cls, request):
        best = request.accept_mimetypes \
            .best_match(['application/json', 'text/html'])
        return best == 'text/html' and \
            request.accept_mimetypes[best] > \
            request.accept_mimetypes['application/json']

    @staticmethod
    def get_graphql_params(request, data):
        query = data.get('query')
        variables = data.get('variables')
        id = data.get('id')

        if variables and isinstance(variables, six.text_type):
            try:
                variables = json.loads(variables)
            except:
                raise HttpError(400, 'Variables are invalid JSON.')

        operation_name = data.get('operationName')

        return query, variables, operation_name, id

    @staticmethod
    def format_error(error):
        if isinstance(error, GraphQLError):
            return format_graphql_error(error)

        return {'message': six.text_type(error)}

    @staticmethod
    def get_content_type(request):
        # We use mimetype here since we don't need the other
        # information provided by content_type
        return request.mimetype
