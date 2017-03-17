# -*- coding: utf-8 -*-
from flask import Flask

from .schema import Schema
from flask_graphql import GraphQLView


def create_app(path='/graphql', **kwargs):
    app = Flask(__name__)
    app.debug = True
    app.add_url_rule(path, view_func=GraphQLView.as_view('graphql', schema=Schema, **kwargs))
    return app


if __name__ == '__main__':
    app = create_app(graphiql=True)
    app.run()
