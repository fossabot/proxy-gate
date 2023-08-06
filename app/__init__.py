"""Initialize Flask app."""
import os
from pathlib import Path

import yaml
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix

from .config import ProxyGateConfig

db = SQLAlchemy()
proxy_gate_config = ProxyGateConfig()
csrf = CSRFProtect()


def init_app():
    """Create Flask application."""
    app = Flask(__name__, instance_relative_config=False)

    with app.app_context():
        load_user_config(app)
        database_setup(app)

        add_routes(app)
        app.secret_key = get_session_secret_keys(db)
        csrf.init_app(app)
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)
        add_healthz_routes(app)
        return app


def add_routes(app):
    from .routes import login, plexauth

    app.register_blueprint(plexauth.plexauth, url_prefix="/plexauth")
    app.register_blueprint(login.login, url_prefix="/login")


def load_user_config(app):
    """
    Load the config file that the user has provided
    """
    if os.environ.get("PROXY_GATE_CONFIG_DIR") is not None:
        config_file = Path(os.environ["PROXY_GATE_CONFIG_DIR"]) / "flask-config.yml"
        if config_file.exists():
            with open(config_file, "r") as file:
                config_file_data = yaml.safe_load(file)
            app.config.update(config_file_data)
    app.config.from_prefixed_env()


def database_setup(app):
    db.init_app(app)
    from .models import RunTime, SecretKey
    db.create_all()


def get_session_secret_keys(db):
    from .models import SecretKey

    active_secret_key = [
        key.secret_key for key in SecretKey.query.filter(SecretKey.active).all()
    ]
    inactive_secret_keys = [
        key.secret_key for key in SecretKey.query.filter(~SecretKey.active).all()
    ]

    # We can't do this check because of bootup.py needs the app
    # if len(active_secret_key) != 1:
    #     raise Exception(
    #
    #     )

    return inactive_secret_keys + active_secret_key


def add_healthz_routes(app):
    from .routes import healthz

    app.register_blueprint(healthz.healthz, url_prefix="/healthz")
