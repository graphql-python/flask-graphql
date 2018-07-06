from graphql.type.definition import GraphQLArgument, GraphQLField, GraphQLNonNull, GraphQLObjectType, GraphQLList
from graphql.type.scalars import GraphQLString, GraphQLScalarType
from graphql.type.schema import GraphQLSchema


def resolve_test_file(obj, info, what):
    output = what.readline().decode('utf-8')
    what.seek(0)
    return output


def resolve_test_files(obj, info, whats):
    output = ''.join(what.readline().decode('utf-8') for what in whats)
    for what in whats:
        what.seek(0)
    return output


def resolve_raises(*_):
    raise Exception("Throws!")


# This scalar should be added to graphql-core at some point
GraphQLUpload = GraphQLScalarType(
    name="Upload",
    description="The `Upload` scalar type represents an uploaded file",
    serialize=lambda x: None,
    parse_value=lambda x: x,
    parse_literal=lambda x: x,
)

QueryRootType = GraphQLObjectType(
    name='QueryRoot',
    fields={
        'thrower': GraphQLField(GraphQLNonNull(GraphQLString), resolver=resolve_raises),
        'request': GraphQLField(GraphQLNonNull(GraphQLString),
                                resolver=lambda obj, info: info.context.args.get('q')),
        'context': GraphQLField(GraphQLNonNull(GraphQLString),
                                resolver=lambda obj, info: info.context),
        'test': GraphQLField(
            type=GraphQLString,
            args={
                'who': GraphQLArgument(GraphQLString)
            },
            resolver=lambda obj, info, who='World': 'Hello %s' % who
        ),
        'testFile': GraphQLField(
            type=GraphQLString,
            args={
                'what': GraphQLArgument(GraphQLNonNull(GraphQLUpload)),
            },
            resolver=resolve_test_file,
        ),
        'testMultiFile': GraphQLField(
            type=GraphQLString,
            args={
                'whats': GraphQLArgument(GraphQLNonNull(GraphQLList(GraphQLUpload))),
            },
            resolver=resolve_test_files,
        )
    }
)

MutationRootType = GraphQLObjectType(
    name='MutationRoot',
    fields={
        'writeTest': GraphQLField(
            type=QueryRootType,
            resolver=lambda *_: QueryRootType
        )
    }
)

Schema = GraphQLSchema(QueryRootType, MutationRootType)
