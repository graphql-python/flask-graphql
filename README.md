# `graphql-flask`

[![Build Status](https://travis-ci.org/graphql-python/graphql-flask.svg?branch=master)](https://travis-ci.org/graphql-python/graphql-flask) [![Coverage Status](https://coveralls.io/repos/graphql-python/graphql-flask/badge.svg?branch=master&service=github)](https://coveralls.io/github/graphql-python/graphql-flask?branch=master) [![PyPI version](https://badge.fury.io/py/graphql-flask.svg)](https://badge.fury.io/py/graphql-flask)

A `Flask` package that provides two main views for operate with `GraphQL`:
* `GraphQLView`: endpoint for expose the GraphQL schema
* `GraphiQLView`: Graphical Interface for operate with GraphQL easily

## Usage
Use it like you would any other Flask View.

```python
from graphql_flask import GraphQLView, GraphiQLView

app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema))
```

### Supported options
 * `schema`: The `GraphQLSchema` object that you want the view to execute when it gets a valid request.
 * `pretty`: Whether or not you want the response to be pretty printed JSON.
 * `executor`: The `Executor` that you want to use to execute queries.
 * `root_value`: The `root_value` you want to provide to `executor.execute`.

You can also subclass `GraphQLView` and overwrite `get_root_value(self, request)` to have a dynamic root value
per request.

```python
class UserRootValue(GraphQLView):
    def get_root_value(self, request):
        return request.user

```
