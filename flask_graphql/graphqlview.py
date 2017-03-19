import json

from flask import Response, request
from flask.views import View

from graphql.type.schema import GraphQLSchema
from graphql_server import run_http_query, HttpQueryError, default_format_error, load_json_body

from .render_graphiql import render_graphiql


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
    def get_root_value(self):
        return self.root_value

    def get_context(self):
        if self.context is not None:
            return self.context
        return request

    def get_middleware(self):
        return self.middleware

    def get_executor(self):
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
            data = self.parse_body()
            if isinstance(data, dict):
                data = dict(data, **request.args.to_dict())

            show_graphiql = request_method == 'get' and self.should_display_graphiql()
            catch = HttpQueryError if show_graphiql else None

            pretty = self.pretty or show_graphiql or request.args.get('pretty')

            result, status_code, all_params = run_http_query(
                self.schema,
                request_method,
                data,
                batch_enabled=self.batch,
                catch=catch,

                # Execute options
                root_value=self.get_root_value(),
                context_value=self.get_context(),
                middleware=self.get_middleware(),
                executor=self.get_executor(),
            )

            result = self.json_encode(result, pretty)

            if show_graphiql:
                return self.render_graphiql(
                    params=all_params[0],
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
                    'errors': [default_format_error(e)]
                }),
                status=e.status_code,
                headers=e.headers,
                content_type='application/json'
            )

    # Flask
    # noinspection PyBroadException
    def parse_body(self):
        # We use mimetype here since we don't need the other
        # information provided by content_type
        content_type = request.mimetype
        if content_type == 'application/graphql':
            return {'query': request.data.decode()}

        elif content_type == 'application/json':
            return load_json_body(request.data.decode('utf8'))

        elif content_type == 'application/x-www-form-urlencoded' \
          or content_type == 'multipart/form-data':
            return request.form.to_dict()

        return {}

    @staticmethod
    def json_encode(data, pretty=False):
        if not pretty:
            return json.dumps(data, separators=(',', ':'))

        return json.dumps(
            data,
            indent=2,
            separators=(',', ': ')
        )

    def should_display_graphiql(self):
        if not self.graphiql or 'raw' in request.args:
            return False

        return self.request_wants_html()

    def request_wants_html(self):
        best = request.accept_mimetypes \
            .best_match(['application/json', 'text/html'])
        return best == 'text/html' and \
            request.accept_mimetypes[best] > \
            request.accept_mimetypes['application/json']
