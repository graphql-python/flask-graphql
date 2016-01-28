Flask-GraphQL
=============

|Build Status| |Coverage Status| |PyPI version|

Adds GraphQL support to your Flask application.

Usage
-----

Just create a ``GraphQL`` instance from ``flask_graphql``

.. code:: python

    from flask_graphql import GraphQL

    graphql_blueprint = GraphQL(app, schema=schema)

This will add ``/graphql`` and ``/graphiql`` endpoints to your app.

Customization
-------------

This package provides the following Views: \* ``GraphQLView``: endpoint
for expose the GraphQL schema \* ``GraphiQLView``: Graphical Interface
for operate with GraphQL easily

You can also add only the views you want to use:

.. code:: python

    from flask_graphql import GraphQLView, GraphiQLView

    app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema))

Supported options
~~~~~~~~~~~~~~~~~

-  ``schema``: The ``GraphQLSchema`` object that you want the view to
   execute when it gets a valid request.
-  ``pretty``: Whether or not you want the response to be pretty printed
   JSON.
-  ``executor``: The ``Executor`` that you want to use to execute
   queries.
-  ``root_value``: The ``root_value`` you want to provide to
   ``executor.execute``.
-  ``default_query``: The ``default_query`` you want to provide to
   GraphiQL interface.

You can also subclass ``GraphQLView`` and overwrite
``get_root_value(self, request)`` to have a dynamic root value per
request.

.. code:: python

    class UserRootValue(GraphQLView):
        def get_root_value(self, request):
            return request.user

.. |Build Status| image:: https://travis-ci.org/graphql-python/graphql-flask.svg?branch=master
   :target: https://travis-ci.org/graphql-python/graphql-flask
.. |Coverage Status| image:: https://coveralls.io/repos/graphql-python/graphql-flask/badge.svg?branch=master&service=github
   :target: https://coveralls.io/github/graphql-python/graphql-flask?branch=master
.. |PyPI version| image:: https://badge.fury.io/py/graphql-flask.svg
   :target: https://badge.fury.io/py/graphql-flask
