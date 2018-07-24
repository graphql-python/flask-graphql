# Flask-GraphQL

[![Build Status](https://travis-ci.org/graphql-python/flask-graphql.svg?branch=master)](https://travis-ci.org/graphql-python/flask-graphql) [![Coverage Status](https://coveralls.io/repos/graphql-python/flask-graphql/badge.svg?branch=master&service=github)](https://coveralls.io/github/graphql-python/flask-graphql?branch=master) [![PyPI version](https://badge.fury.io/py/flask-graphql.svg)](https://badge.fury.io/py/flask-graphql)

Adds GraphQL support to your Flask application.

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

### File upload support

File uploads are supported via [multipart requests](https://github.com/jaydenseric/graphql-multipart-request-spec).

You can simply define a ``FileUpload`` field in your schema, and use
it to receive data from uploaded files.


Example using ``graphql-core``:

```python
from collections import NamedTuple
from graphql.type.definition import GraphQLScalarType


GraphQLFileUpload = GraphQLScalarType(
    name='FileUpload',
    description='File upload',
    serialize=lambda x: None,
    parse_value=lambda value: value,
    parse_literal=lambda node: None,
)


FileEchoResult = namedtuple('FileEchoResult', 'data,name,type')


FileEchoResultSchema = GraphQLObjectType(
    name='FileEchoResult,
    fields={
        'data': GraphQLField(GraphQLString),
        'name': GraphQLField(GraphQLString),
        'type': GraphQLField(GraphQLString),
    }
)


def resolve_file_echo(obj, info, file):
    data = file.stream.read().decode()
    return FileEchoResult(
        data=data,
        name=file.filename,
        type=file.content_type)


MutationRootType = GraphQLObjectType(
    name='MutationRoot',
    fields={
        # ...
        'fileEcho': GraphQLField(
            type=FileUploadTestResultSchema,
            args={'file': GraphQLArgument(GraphQLFileUpload)},
            resolver=resolve_file_echo,
        ),
        # ...
    }
)
```


Example using ``graphene``:

```python
import graphene

class FileUpload(graphene.Scalar):

    @staticmethod
    def serialize(value):
        return None

    @staticmethod
    def parse_literal(node):
        return None

    @staticmethod
    def parse_value(value):
        return value  # IMPORTANT


class FileEcho(graphene.Mutation):

    class Arguments:
        myfile = FileUpload(required=True)

    ok = graphene.Boolean()
    name = graphene.String()
    data = graphene.String()
    type = graphene.String()

    def mutate(self, info, myfile):
        return FileEcho(
            ok=True
            name=myfile.filename
            data=myfile.stream.read(),
            type=myfile.content_type)
```
