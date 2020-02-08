# Flask-GraphQL

Adds GraphQL support to your Flask application.

[![travis][travis-image]][travis-url]
[![pypi][pypi-image]][pypi-url]
[![Anaconda-Server Badge][conda-image]][conda-url]
[![coveralls][coveralls-image]][coveralls-url]

[travis-image]: https://travis-ci.org/graphql-python/flask-graphql.svg?branch=master
[travis-url]: https://travis-ci.org/graphql-python/flask-graphql
[pypi-image]: https://img.shields.io/pypi/v/flask-graphql.svg?style=flat
[pypi-url]: https://pypi.org/project/flask-graphql/
[coveralls-image]: https://coveralls.io/repos/graphql-python/flask-graphql/badge.svg?branch=master&service=github
[coveralls-url]: https://coveralls.io/github/graphql-python/flask-graphql?branch=master
[conda-image]: https://img.shields.io/conda/vn/conda-forge/flask-graphql.svg
[conda-url]: https://anaconda.org/conda-forge/flask-graphql

## Usage

Just use the `GraphQLView` view from `flask_graphql`

```python
from flask_graphql import GraphQLView

app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True))

# Optional, for adding batch query support (used in Apollo-Client)
app.add_url_rule('/graphql/batch', view_func=GraphQLView.as_view('graphql', schema=schema, batch=True))
```

This will add `/graphql` and `/graphiql` endpoints to your app.

### Supported options
 * `schema`: The `GraphQLSchema` object that you want the view to execute when it gets a valid request.
 * `context`: A value to pass as the `context` to the `graphql()` function.
 * `root_value`: The `root_value` you want to provide to `executor.execute`.
 * `pretty`: Whether or not you want the response to be pretty printed JSON.
 * `executor`: The `Executor` that you want to use to execute queries.
 * `graphiql`: If `True`, may present [GraphiQL](https://github.com/graphql/graphiql) when loaded directly from a browser (a useful tool for debugging and exploration).
 * `graphiql_template`: Inject a Jinja template string to customize GraphiQL.
 * `batch`: Set the GraphQL view as batch (for using in [Apollo-Client](http://dev.apollodata.com/core/network.html#query-batching) or [ReactRelayNetworkLayer](https://github.com/nodkz/react-relay-network-layer))
 * `middleware`: A list of graphql [middlewares](http://docs.graphene-python.org/en/latest/execution/middleware/).

You can also subclass `GraphQLView` and overwrite `get_root_value(self, request)` to have a dynamic root value
per request.

```python
class UserRootValue(GraphQLView):
    def get_root_value(self, request):
        return request.user

```

## Contributing
See [CONTRIBUTING.md](contributing.md)
