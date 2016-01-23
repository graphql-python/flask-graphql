from flask import Flask
from graphql_flask import GraphQL
from .schema import Schema

def create_app(**kwargs):
    app = Flask(__name__, static_url_path='/static/')
    app.debug = True
    graphql = GraphQL(app, schema=Schema, **kwargs)
    return app
