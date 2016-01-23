from flask import Blueprint
from .graphqlview import GraphQLView
from .graphiqlview import GraphiQLView


class GraphQL(object):
    def __init__(self, app, schema, **options):
        self.app = app
        self.blueprint = Blueprint('graphql', __name__,
                                   template_folder='templates',
                                   static_folder='./static/')

        app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema, **options))
        app.add_url_rule('/graphiql', view_func=GraphiQLView.as_view('graphiql'))

        self.app.register_blueprint(self.blueprint)
