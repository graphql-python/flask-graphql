import pytest
import json
from tempfile import NamedTemporaryFile

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

from .app import create_app
from flask import url_for


@pytest.fixture
def app():
    return create_app()

def url_string(**url_params):
    string = url_for('graphql')

    if url_params:
        string += '?' + urlencode(url_params)

    return string


def response_json(response):
    return json.loads(response.data.decode())


j = lambda **kwargs: json.dumps(kwargs)
jl = lambda **kwargs: json.dumps([kwargs])


def test_allows_get_with_query_param(client):
    response = client.get(url_string(query='{test}'))

    assert response.status_code == 200
    assert response_json(response) == {
        'data': {'test': "Hello World"}
    }


def test_allows_get_with_variable_values(client):
    response = client.get(url_string(
        query='query helloWho($who: String){ test(who: $who) }',
        variables=json.dumps({'who': "Dolly"})
    ))

    assert response.status_code == 200
    assert response_json(response) == {
        'data': {'test': "Hello Dolly"}
    }


def test_allows_get_with_operation_name(client):
    response = client.get(url_string(
        query='''
        query helloYou { test(who: "You"), ...shared }
        query helloWorld { test(who: "World"), ...shared }
        query helloDolly { test(who: "Dolly"), ...shared }
        fragment shared on QueryRoot {
          shared: test(who: "Everyone")
        }
        ''',
        operationName='helloWorld'
    ))

    assert response.status_code == 200
    assert response_json(response) == {
        'data': {
            'test': 'Hello World',
            'shared': 'Hello Everyone'
        }
    }


def test_reports_validation_errors(client):
    response = client.get(url_string(
        query='{ test, unknownOne, unknownTwo }'
    ))

    assert response.status_code == 400
    assert response_json(response) == {
        'errors': [
            {
                'message': 'Cannot query field "unknownOne" on type "QueryRoot".',
                'locations': [{'line': 1, 'column': 9}]
            },
            {
                'message': 'Cannot query field "unknownTwo" on type "QueryRoot".',
                'locations': [{'line': 1, 'column': 21}]
            }
        ]
    }


def test_errors_when_missing_operation_name(client):
    response = client.get(url_string(
        query='''
        query TestQuery { test }
        mutation TestMutation { writeTest { test } }
        '''
    ))

    assert response.status_code == 400
    assert response_json(response) == {
        'errors': [
            {
                'message': 'Must provide operation name if query contains multiple operations.'
            }
        ]
    }


def test_errors_when_sending_a_mutation_via_get(client):
    response = client.get(url_string(
        query='''
        mutation TestMutation { writeTest { test } }
        '''
    ))
    assert response.status_code == 405
    assert response_json(response) == {
        'errors': [
            {
                'message': 'Can only perform a mutation operation from a POST request.'
            }
        ]
    }


def test_errors_when_selecting_a_mutation_within_a_get(client):
    response = client.get(url_string(
        query='''
        query TestQuery { test }
        mutation TestMutation { writeTest { test } }
        ''',
        operationName='TestMutation'
    ))

    assert response.status_code == 405
    assert response_json(response) == {
        'errors': [
            {
                'message': 'Can only perform a mutation operation from a POST request.'
            }
        ]
    }


def test_allows_mutation_to_exist_within_a_get(client):
    response = client.get(url_string(
        query='''
        query TestQuery { test }
        mutation TestMutation { writeTest { test } }
        ''',
        operationName='TestQuery'
    ))

    assert response.status_code == 200
    assert response_json(response) == {
        'data': {'test': "Hello World"}
    }


def test_allows_post_with_json_encoding(client):
    response = client.post(url_string(), data=j(query='{test}'), content_type='application/json')

    assert response.status_code == 200
    assert response_json(response) == {
        'data': {'test': "Hello World"}
    }


def test_allows_sending_a_mutation_via_post(client):
    response = client.post(url_string(), data=j(query='mutation TestMutation { writeTest { test } }'), content_type='application/json')

    assert response.status_code == 200
    assert response_json(response) == {
        'data': {'writeTest': {'test': 'Hello World'}}
    }


def test_allows_post_with_url_encoding(client):
    response = client.post(url_string(), data=urlencode(dict(query='{test}')), content_type='application/x-www-form-urlencoded')

    assert response.status_code == 200
    assert response_json(response) == {
        'data': {'test': "Hello World"}
    }


# def test_benchmark(client, benchmark):
#     url = url_string()
#     data = urlencode(dict(query='{test}'))
#     def fun():
#         return client.post(url_string(), data=data, content_type='application/x-www-form-urlencoded')

#     response = benchmark(fun)
#     assert response.status_code == 200
#     assert response_json(response) == {
#         'data': {'test': "Hello World"}
#     }


def test_supports_post_json_query_with_string_variables(client):
    response = client.post(url_string(), data=j(
        query='query helloWho($who: String){ test(who: $who) }',
        variables=json.dumps({'who': "Dolly"})
    ), content_type='application/json')

    assert response.status_code == 200
    assert response_json(response) == {
        'data': {'test': "Hello Dolly"}
    }


def test_supports_post_json_query_with_json_variables(client):
    response = client.post(url_string(), data=j(
        query='query helloWho($who: String){ test(who: $who) }',
        variables={'who': "Dolly"}
    ), content_type='application/json')

    assert response.status_code == 200
    assert response_json(response) == {
        'data': {'test': "Hello Dolly"}
    }


def test_supports_post_url_encoded_query_with_string_variables(client):
    response = client.post(url_string(), data=urlencode(dict(
        query='query helloWho($who: String){ test(who: $who) }',
        variables=json.dumps({'who': "Dolly"})
    )), content_type='application/x-www-form-urlencoded')

    assert response.status_code == 200
    assert response_json(response) == {
        'data': {'test': "Hello Dolly"}
    }


def test_supports_post_json_quey_with_get_variable_values(client):
    response = client.post(url_string(
        variables=json.dumps({'who': "Dolly"})
    ), data=j(
        query='query helloWho($who: String){ test(who: $who) }',
    ), content_type='application/json')

    assert response.status_code == 200
    assert response_json(response) == {
        'data': {'test': "Hello Dolly"}
    }


def test_post_url_encoded_query_with_get_variable_values(client):
    response = client.post(url_string(
        variables=json.dumps({'who': "Dolly"})
    ), data=urlencode(dict(
        query='query helloWho($who: String){ test(who: $who) }',
    )), content_type='application/x-www-form-urlencoded')

    assert response.status_code == 200
    assert response_json(response) == {
        'data': {'test': "Hello Dolly"}
    }


def test_supports_post_raw_text_query_with_get_variable_values(client):
    response = client.post(url_string(
        variables=json.dumps({'who': "Dolly"})
    ),
        data='query helloWho($who: String){ test(who: $who) }',
        content_type='application/graphql'
    )

    assert response.status_code == 200
    assert response_json(response) == {
        'data': {'test': "Hello Dolly"}
    }


def test_allows_post_with_operation_name(client):
    response = client.post(url_string(), data=j(
        query='''
        query helloYou { test(who: "You"), ...shared }
        query helloWorld { test(who: "World"), ...shared }
        query helloDolly { test(who: "Dolly"), ...shared }
        fragment shared on QueryRoot {
          shared: test(who: "Everyone")
        }
        ''',
        operationName='helloWorld'
    ), content_type='application/json')

    assert response.status_code == 200
    assert response_json(response) == {
        'data': {
            'test': 'Hello World',
            'shared': 'Hello Everyone'
        }
    }


def test_allows_post_with_get_operation_name(client):
    response = client.post(url_string(
        operationName='helloWorld'
    ), data='''
    query helloYou { test(who: "You"), ...shared }
    query helloWorld { test(who: "World"), ...shared }
    query helloDolly { test(who: "Dolly"), ...shared }
    fragment shared on QueryRoot {
      shared: test(who: "Everyone")
    }
    ''',
        content_type='application/graphql')

    assert response.status_code == 200
    assert response_json(response) == {
        'data': {
            'test': 'Hello World',
            'shared': 'Hello Everyone'
        }
    }


@pytest.mark.parametrize('app', [create_app(pretty=True)])
def test_supports_pretty_printing(client):
    response = client.get(url_string(query='{test}'))

    assert response.data.decode() == (
        '{\n'
        '  "data": {\n'
        '    "test": "Hello World"\n'
        '  }\n'
        '}'
    )


@pytest.mark.parametrize('app', [create_app(pretty=False)])
def test_not_pretty_by_default(client):
    response = client.get(url_string(query='{test}'))

    assert response.data.decode() == (
        '{"data":{"test":"Hello World"}}'
    )


def test_supports_pretty_printing_by_request(client):
    response = client.get(url_string(query='{test}', pretty='1'))

    assert response.data.decode() == (
        '{\n'
        '  "data": {\n'
        '    "test": "Hello World"\n'
        '  }\n'
        '}'
    )


def test_handles_field_errors_caught_by_graphql(client):
    response = client.get(url_string(query='{thrower}'))
    assert response.status_code == 200
    assert response_json(response) == {
        'data': None,
        'errors': [{'locations': [{'column': 2, 'line': 1}], 'path': ['thrower'], 'message': 'Throws!'}]
    }


def test_handles_syntax_errors_caught_by_graphql(client):
    response = client.get(url_string(query='syntaxerror'))
    assert response.status_code == 400
    assert response_json(response) == {
        'errors': [{'locations': [{'column': 1, 'line': 1}],
                    'message': 'Syntax Error GraphQL (1:1) '
                               'Unexpected Name "syntaxerror"\n\n1: syntaxerror\n   ^\n'}]
    }


def test_handles_errors_caused_by_a_lack_of_query(client):
    response = client.get(url_string())

    assert response.status_code == 400
    assert response_json(response) == {
        'errors': [{'message': 'Must provide query string.'}]
    }


def test_handles_batch_correctly_if_is_disabled(client):
    response = client.post(url_string(), data='[]', content_type='application/json')

    assert response.status_code == 400
    assert response_json(response) == {
        'errors': [{'message': 'Batch GraphQL requests are not enabled.'}]
    }


def test_handles_incomplete_json_bodies(client):
    response = client.post(url_string(), data='{"query":', content_type='application/json')

    assert response.status_code == 400
    assert response_json(response) == {
        'errors': [{'message': 'POST body sent invalid JSON.'}]
    }


def test_handles_plain_post_text(client):
    response = client.post(url_string(
        variables=json.dumps({'who': "Dolly"})
    ),
        data='query helloWho($who: String){ test(who: $who) }',
        content_type='text/plain'
    )
    assert response.status_code == 400
    assert response_json(response) == {
        'errors': [{'message': 'Must provide query string.'}]
    }


def test_handles_poorly_formed_variables(client):
    response = client.get(url_string(
        query='query helloWho($who: String){ test(who: $who) }',
        variables='who:You'
    ))
    assert response.status_code == 400
    assert response_json(response) == {
        'errors': [{'message': 'Variables are invalid JSON.'}]
    }


def test_handles_unsupported_http_methods(client):
    response = client.put(url_string(query='{test}'))
    assert response.status_code == 405
    assert response.headers['Allow'] in ['GET, POST', 'HEAD, GET, POST, OPTIONS']
    assert response_json(response) == {
        'errors': [{'message': 'GraphQL only supports GET and POST requests.'}]
    }


def test_passes_request_into_request_context(client):
    response = client.get(url_string(query='{request}', q='testing'))

    assert response.status_code == 200
    assert response_json(response) == {
        'data': {
            'request': 'testing'
        }
    }


@pytest.mark.parametrize('app', [create_app(get_context=lambda:"CUSTOM CONTEXT")])
def test_supports_pretty_printing(client):
    response = client.get(url_string(query='{context}'))


    assert response.status_code == 200
    assert response_json(response) == {
        'data': {
            'context': 'CUSTOM CONTEXT'
        }
    }


def test_post_multipart_data(client):
    query = 'mutation TestMutation($file: Upload!) { writeTest { testFile( what: $file ) } }'
    with NamedTemporaryFile() as t_file:
        t_file.write(b'Fake Data\nLine2\n')
        t_file.seek(0)
        response = client.post(
            url_string(),
            data={
                'operations': j(query=query, variables={'file': None}),
                't_file': t_file,
                'map': j(t_file=["variables.file"]),
            },
            content_type='multipart/form-data'
        )
    assert response.status_code == 200
    assert response_json(response) == {'data': {u'writeTest': {u'testFile': u'Fake Data\n'}}}


@pytest.mark.parametrize('app', [create_app(batch=True)])
def test_post_multipart_data_multi(client):
    query1 = '''
    mutation TestMutation($file: Upload!) {
      writeTest { testFile( what: $file ) }
    }'''
    query2 = '''
    mutation TestMutation($files: [Upload]!) {
      writeTest { testMultiFile( whats: $files ) }
    }'''
    with NamedTemporaryFile() as tf1, NamedTemporaryFile() as tf2:
        tf1.write(b'tf1\nNot This line!!\n')
        tf1.seek(0)
        tf2.write(b'tf2\nNot This line!!\n')
        tf2.seek(0)
        response = client.post(
            url_string(),
            data={
                'operations': json.dumps([
                    {'query': query1, 'variables': {'file': None}},
                    {'query': query2, 'variables': {'files': [None, None]}},
                ]),
                'tf1': tf1,
                'tf2': tf2,
                'map': j(
                    tf1=['0.variables.file', '1.variables.files.0'],
                    tf2=['1.variables.files.1'],
                ),
            },
            content_type='multipart/form-data'
        )
        assert response.status_code == 200
        assert response_json(response) == [
            {'data': {
                u'writeTest': {u'testFile': u'tf1\n'}
            }},
            {'data': {
                u'writeTest': {u'testMultiFile': u'tf1\ntf2\n'}
            }},
        ]


@pytest.mark.parametrize('app', [create_app(batch=True)])
def test_batch_allows_post_with_json_encoding(client):
    response = client.post(
        url_string(),
        data=jl(
            # id=1,
            query='{test}'
        ),
        content_type='application/json'
    )

    assert response.status_code == 200
    assert response_json(response) == [{
        # 'id': 1,
        'data': {'test': "Hello World"}
    }]


@pytest.mark.parametrize('app', [create_app(batch=True)])
def test_batch_supports_post_json_query_with_json_variables(client):
    response = client.post(
        url_string(),
        data=jl(
            # id=1,
            query='query helloWho($who: String){ test(who: $who) }',
            variables={'who': "Dolly"}
        ),
        content_type='application/json'
    )

    assert response.status_code == 200
    assert response_json(response) == [{
        # 'id': 1,
        'data': {'test': "Hello Dolly"}
    }]


@pytest.mark.parametrize('app', [create_app(batch=True)])
def test_batch_allows_post_with_operation_name(client):
    response = client.post(
        url_string(),
        data=jl(
            # id=1,
            query='''
            query helloYou { test(who: "You"), ...shared }
            query helloWorld { test(who: "World"), ...shared }
            query helloDolly { test(who: "Dolly"), ...shared }
            fragment shared on QueryRoot {
              shared: test(who: "Everyone")
            }
            ''',
            operationName='helloWorld'
        ),
        content_type='application/json'
    )

    assert response.status_code == 200
    assert response_json(response) == [{
        # 'id': 1,
        'data': {
            'test': 'Hello World',
            'shared': 'Hello Everyone'
        }
    }]
