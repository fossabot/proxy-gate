"""Initialize Flask app."""
import importlib
import os
import pkgutil
from pathlib import Path

import yaml
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix

from .config import ProxyGateConfig

db = SQLAlchemy()
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
    routes = get_routes()

    for route in routes:
        route_url_prefix = "/" + "/".join(route.split("."))
        route_module = importlib.import_module("." + route, package="app.routes")
        if hasattr(route_module, "blueprint"):
            print(f"Registering {route_url_prefix} at {route}")
            app.register_blueprint(
                getattr(route_module, "blueprint"), url_prefix="/" + route_url_prefix
            )
        else:
            print(f"Skipping {route_url_prefix} at app.routes.{route} as it does not have a blueprint")

    # app.register_blueprint(google.googleauth, url_prefix="/googleauth")
    # app.register_blueprint(login.login, url_prefix="/login")
    # app.register_blueprint(metaz.metaz, url_prefix="/metaz")


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
    # from .routes import healthz

    # app.register_blueprint(healthz.healthz, url_prefix="/healthz")
    pass


def get_routes():
    return walk_packages(Path(__file__).parent / "routes")


def walk_packages(path: Path, prefix: str = ""):
    # Recursively find all modules under the specified package
    modules = []
    for loader, name, is_pkg in pkgutil.walk_packages([path], prefix=prefix):
        if is_pkg:
            print(f"Found package {name} at {loader.path} (will recurse)")
            modules += walk_packages(loader.path + "/" + name, name + ".")
        else:
            modules.append(name)
            
    return modules
