from flask import Blueprint

from .graphiqlview import GraphiQLView
from .graphqlview import GraphQLView


class GraphQL(object):
    def __init__(self, app, schema, **options):
        self.app = app
        self.blueprint = Blueprint('graphql', __name__,
                                   template_folder='templates',
                                   static_url_path='/static/graphql',
                                   static_folder='static/graphql/')

        default_query = options.pop('default_query', None)
        app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema, **options))
        app.add_url_rule('/graphiql', view_func=GraphiQLView.as_view('graphiql', default_query=default_query))

        self.app.register_blueprint(self.blueprint)
