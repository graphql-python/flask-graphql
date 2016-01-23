import pytest

from .app import create_app
from flask import url_for


@pytest.fixture
def app():
    return create_app()

def test_graphiql_endpoint_exists(client):
    response = client.get(url_for('graphiql'))
    assert response.status_code == 200

# def test_graphiql_static_files_exposed(client):
#     print url_for("static", filename="graphiql/graphiql.min.js")
#     response = client.get(url_for("static", filename="graphiql/graphiql.min.js"))
#     assert response.status_code == 200
