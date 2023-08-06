import pytest
from app import init_app
import tempfile
import os
from pathlib import Path


# Fixture to create and return the Flask app instance
@pytest.fixture
def app():
    set_test_environment()
    app = init_app()
    app.secret_key = ["test"]
    yield app


# Fixture to create and return a test client for the app
@pytest.fixture
def client(app):
    return app.test_client()


def set_test_environment():
    # Create a temporary directory for data files
    os.environ["PROXY_GATE_DATA_DIR"] = tempfile.mkdtemp()
    os.environ["PROXY_GATE_CONFIG_DIR"] = os.path.join(tempfile.mkdtemp(), "configs")
    os.environ["PROXY_GATE_CONFIG_DIR"] = os.path.join(tempfile.mkdtemp(), "migrations")
    os.environ["PROXY_GATE_SECRET_KEY_VALIDITY"] = "72"
    os.environ["PROXY_GATE_SECRET_KEY_INTERIM_VALIDITY"] = "168"
    os.environ[
        "FLASK_SQLALCHEMY_DATABASE_URI"
    ] = f'sqlite:///{os.environ["PROXY_GATE_DATA_DIR"]}/app.db'
    os.environ["FLASK_SQLALCHEMY_TRACK_MODIFICATIONS"] = "False"
