import pytest

from .app import create_app
from flask import url_for


@pytest.fixture
def app():
    return create_app(graphiql=True)


def test_graphiql_is_enabled(client):
    response = client.get(url_for('graphql'), headers={'Accept': 'text/html'})
    assert response.status_code == 200


def test_graphiql_renders_pretty(client):
    response = client.get(url_for('graphql', query='{test}'), headers={'Accept': 'text/html'})
    assert response.status_code == 200
    pretty_response = (
        '{\n'
        '  "data": {\n'
        '    "test": "Hello World"\n'
        '  }\n'
        '}'
    ).replace("\"", "\\\"").replace("\n", "\\n")

    assert pretty_response in response.data.decode('utf-8')


def test_graphiql_default_title(client):
    response = client.get(url_for('graphql'), headers={'Accept': 'text/html'})
    assert '<title>GraphiQL</title>' in response.data.decode('utf-8')


@pytest.mark.parametrize('app', [create_app(graphiql=True, graphiql_html_title="Awesome")])
def test_graphiql_custom_title(app, client):
    response = client.get(url_for('graphql'), headers={'Accept': 'text/html'})
    assert '<title>Awesome</title>' in response.data.decode('utf-8')
