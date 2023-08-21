import os
import tempfile

import pytest

from app import init_app


# Fixture to create and return the Flask app instance
@pytest.fixture
def app():
    set_test_environment()
    app = init_app()
    app.secret_key = ["test"]
    yield app


def set_test_environment():
    # Create a temporary directory for data files
    os.environ["PROXY_GATE_DATA_DIR"] = tempfile.mkdtemp()
    os.environ["PROXY_GATE_CONFIG_DIR"] = os.path.join(tempfile.mkdtemp(), "configs")
    os.environ["PROXY_GATE_CONFIG_DIR"] = os.path.join(tempfile.mkdtemp(), "migrations")
    os.environ[
        "FLASK_SQLALCHEMY_DATABASE_URI"
    ] = f'sqlite:///{os.environ["PROXY_GATE_DATA_DIR"]}/app.db'
    os.environ["FLASK_SQLALCHEMY_TRACK_MODIFICATIONS"] = "False"
