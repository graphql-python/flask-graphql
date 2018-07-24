from graphql.type.definition import (
    GraphQLArgument, GraphQLField, GraphQLNonNull, GraphQLObjectType,
    GraphQLScalarType)
from graphql.type.scalars import GraphQLString
from graphql.type.schema import GraphQLSchema


def resolve_raises(*_):
    raise Exception("Throws!")


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
        )
    }
)


FileUploadTestResult = GraphQLObjectType(
    name='FileUploadTestResult',
    fields={
        'data': GraphQLField(GraphQLString),
        'name': GraphQLField(GraphQLString),
        'type': GraphQLField(GraphQLString),
    }
)

GraphQLFileUpload = GraphQLScalarType(
    name='FileUpload',
    description='File upload',
    serialize=lambda x: None,
    parse_value=lambda value: value,
    parse_literal=lambda node: None,
)


def to_object(dct):
    class MyObject(object):
        pass

    obj = MyObject()
    for key, val in dct.items():
        setattr(obj, key, val)
    return obj


def resolve_file_upload_test(obj, info, file):
    data = file.stream.read().decode()

    # Need to return an object, not a dict
    return to_object({
        'data': data,
        'name': file.filename,
        'type': file.content_type,
    })


MutationRootType = GraphQLObjectType(
    name='MutationRoot',
    fields={
        'writeTest': GraphQLField(
            type=QueryRootType,
            resolver=lambda *_: QueryRootType
        ),
        'fileUploadTest': GraphQLField(
            type=FileUploadTestResult,
            args={'file': GraphQLArgument(GraphQLFileUpload)},
            resolver=resolve_file_upload_test,
        ),
    }
)

Schema = GraphQLSchema(QueryRootType, MutationRootType)
