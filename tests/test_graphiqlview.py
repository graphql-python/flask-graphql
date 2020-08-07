import pytest
from flask import url_for

from .app import create_app


@pytest.fixture
def app():
    # import app factory pattern
    app = create_app(graphiql=True)

    # pushes an application context manually
    ctx = app.app_context()
    ctx.push()
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_graphiql_is_enabled(app, client):
    with app.test_request_context():
        response = client.get(
            url_for("graphql", externals=False), headers={"Accept": "text/html"}
        )
    assert response.status_code == 200


def test_graphiql_renders_pretty(app, client):
    with app.test_request_context():
        response = client.get(
            url_for("graphql", query="{test}"), headers={"Accept": "text/html"}
        )
    assert response.status_code == 200
    pretty_response = (
        "{\n"
        '  "data": {\n'
        '    "test": "Hello World"\n'
        "  }\n"
        "}".replace('"', '\\"').replace("\n", "\\n")
    )

    assert pretty_response in response.data.decode("utf-8")


def test_graphiql_default_title(app, client):
    with app.test_request_context():
        response = client.get(url_for("graphql"), headers={"Accept": "text/html"})
    assert "<title>GraphiQL</title>" in response.data.decode("utf-8")


@pytest.mark.parametrize(
    "app", [create_app(graphiql=True, graphiql_html_title="Awesome")]
)
def test_graphiql_custom_title(app, client):
    with app.test_request_context():
        response = client.get(url_for("graphql"), headers={"Accept": "text/html"})
    assert "<title>Awesome</title>" in response.data.decode("utf-8")
