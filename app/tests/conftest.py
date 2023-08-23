import os
import tempfile

import pytest

from app import init_app


@pytest.fixture(name="app")
def app_fixture():
    set_test_environment()
    flask_app = init_app()
    flask_app.secret_key = ["test"]
    yield flask_app


@pytest.fixture
def metaz(app):
    client = app.test_client()
    response = client.get("/metaz")

    assert response.status_code == 200
    assert isinstance(response.json, dict)
    return response.json


def set_test_environment():
    # Create a temporary directory for data files
    os.environ["PROXY_GATE_DATA_DIR"] = tempfile.mkdtemp()
    os.environ["PROXY_GATE_CONFIG_DIR"] = os.path.join(tempfile.mkdtemp(), "configs")
    os.environ["PROXY_GATE_CONFIG_DIR"] = os.path.join(tempfile.mkdtemp(), "migrations")
    os.environ[
        "FLASK_SQLALCHEMY_DATABASE_URI"
    ] = f'sqlite:///{os.environ["PROXY_GATE_DATA_DIR"]}/app.db'
    os.environ["FLASK_SQLALCHEMY_TRACK_MODIFICATIONS"] = "False"
