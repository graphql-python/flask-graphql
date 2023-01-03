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

First install this library using `pip`
```
pip install Flask-GraphQL
```

Then, just use the `GraphQLView` view from `flask_graphql`

```python
from flask import Flask
from flask_graphql import GraphQLView

from schema import schema

app = Flask(__name__)

app.add_url_rule('/graphql', view_func=GraphQLView.as_view(
    'graphql',
    schema=schema,
    graphiql=True,
))

# Optional, for adding batch query support (used in Apollo-Client)
app.add_url_rule('/graphql/batch', view_func=GraphQLView.as_view(
    'graphql',
    schema=schema,
    batch=True
))

if __name__ == '__main__':
    app.run()
```

This will add `/graphql` endpoint to your app and enable the GraphiQL IDE.

### Special Note for Graphene v3

If you are using the `Schema` type of [Graphene](https://github.com/graphql-python/graphene) library, be sure to use the `graphql_schema` attribute to pass as schema on the `GraphQLView` view. Otherwise, the `GraphQLSchema` from `graphql-core` is the way to go.

More info at [Graphene v3 release notes](https://github.com/graphql-python/graphene/wiki/v3-release-notes#graphene-schema-no-longer-subclasses-graphqlschema-type) and [GraphQL-core 3 usage](https://github.com/graphql-python/graphql-core#usage).


### Supported options for GraphQLView

 * `schema`: The `GraphQLSchema` object that you want the view to execute when it gets a valid request.
 * `context`: A value to pass as the `context_value` to graphql `execute` function. By default is set to `dict` with request object at key `request`.
 * `root_value`: The `root_value` you want to provide to graphql `execute`.
 * `pretty`: Whether or not you want the response to be pretty printed JSON.
 * `graphiql`: If `True`, may present [GraphiQL](https://github.com/graphql/graphiql) when loaded directly from a browser (a useful tool for debugging and exploration).
 * `graphiql_version`: The graphiql version to load. Defaults to **"1.0.3"**.
 * `graphiql_template`: Inject a Jinja template string to customize GraphiQL.
 * `graphiql_html_title`: The graphiql title to display. Defaults to **"GraphiQL"**.
 * `batch`: Set the GraphQL view as batch (for using in [Apollo-Client](http://dev.apollodata.com/core/network.html#query-batching) or [ReactRelayNetworkLayer](https://github.com/nodkz/react-relay-network-layer))
 * `middleware`: A list of graphql [middlewares](http://docs.graphene-python.org/en/latest/execution/middleware/).
 * `encode`: the encoder to use for responses (sensibly defaults to `graphql_server.json_encode`).
 * `format_error`: the error formatter to use for responses (sensibly defaults to `graphql_server.default_format_error`.
 * `subscriptions`: The GraphiQL socket endpoint for using subscriptions in graphql-ws.
 * `headers`: An optional GraphQL string to use as the initial displayed request headers, if not provided, the stored headers will be used.
 * `default_query`: An optional GraphQL string to use when no query is provided and no stored query exists from a previous session. If not provided, GraphiQL will use its own default query.
* `header_editor_enabled`: An optional boolean which enables the header editor when true. Defaults to **false**.
* `should_persist_headers`:  An optional boolean which enables to persist headers to storage when true. Defaults to **false**.

You can also subclass `GraphQLView` and overwrite `get_root_value(self, request)` to have a dynamic root value
per request.

```python
class UserRootValue(GraphQLView):
    def get_root_value(self, request):
        return request.user

```

## Contributing
Since v3, `flask-graphql` code lives at [graphql-server](https://github.com/graphql-python/graphql-server) repository to keep any breaking change on the base package on sync with all other integrations. In order to contribute, please take a look at [CONTRIBUTING.md](https://github.com/graphql-python/graphql-server/blob/master/CONTRIBUTING.md).
