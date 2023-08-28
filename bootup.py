"""
Executable script to run on bootup of application before starting the server.
"""
import os
import secrets
import shutil
from datetime import datetime, timedelta
from pathlib import Path

from flask_migrate import Migrate, init, migrate, upgrade
from sqlalchemy import and_

from app.config import ProxyGateConfig

# from app.exceptions import GoogleClientSecretFileNotFound
from app.models import db, RunTime, SecretKey

# from app.utils import google_oauth_flow
from wsgi import app


def secret_key_setup():
    """
    Handle secret key setup and rotation logic.
    The secret key is loaded during server startup and is used to sign the
    secure cookies used for authentication.
    """

    print("** Setup secret key")
    key_validity = ProxyGateConfig()("secret_key_validity")
    key_interim_validity = ProxyGateConfig()("secret_key_interim_validity")
    active_keys = SecretKey.query.filter(SecretKey.active).all()

    if len(active_keys) == 0:
        print("No secret key found, creating one")
        _secret_key = SecretKey(
            secret_key=secrets.token_urlsafe(),
            created_on=datetime.now(),
            active=True,
        )
        db.session.add(_secret_key)
    elif len(active_keys) > 1:
        print("More than one active keys found, marking all but first one as inactive")
        for key in active_keys[1:]:
            key.active = False
            key.inactive_since = datetime.now()
    elif len(active_keys) == 1:
        print("One active key found checking if we need to rotate it")
        active_key = active_keys[0]
        if datetime.now() > active_key.created_on + timedelta(hours=key_validity):
            print(
                (
                    "Active key is expired, creating a new one and marking the old one as"
                    " rotated."
                )
            )
            active_key.active = False
            active_key.inactive_since = datetime.now()
            _secret_key = SecretKey(
                secret_key=secrets.token_urlsafe(),
                created_on=datetime.now(),
                active=True,
            )
            db.session.add(_secret_key)
        else:
            print("Active key is still valid, doing nothing to it")

    inactive_keys = SecretKey.query.filter(and_(~SecretKey.active)).all()
    for key in inactive_keys:
        if datetime.now() > key.inactive_since + timedelta(hours=key_interim_validity):
            print(
                (
                    f"Inactive key id: {key.id} has surpassed {key_interim_validity}h"
                    " since inactivity, deleting it"
                )
            )
            db.session.delete(key)
        else:
            print(
                (
                    f"Inactive key id: {key.id} has not surpassed"
                    f" {key_interim_validity}h since inactivity, doing nothing to it"
                )
            )

    db.session.commit()


def runtime_data_setup():
    """
    Handle data used during runtime of the server.
    Data is newly created on each bootup.
    """
    db.session.query(RunTime).delete()
    db.session.add(RunTime(key="boot_time", value=datetime.now().isoformat()))
    # try:
    #     google_credentials = google_oauth_flow.init_flow_credentials()
    #     db.session.add(RunTime(key="google_credentials", value=google_credentials))
    # except GoogleClientSecretFileNotFound:
    #     print("** Google client secret file not found")
    db.session.commit()


def dir_setup():
    print("** Seting up directories")
    os.makedirs(os.environ["PROXY_GATE_DATA_DIR"], exist_ok=True)
    os.makedirs(os.environ["PROXY_GATE_CONFIG_DIR"], exist_ok=True)


def config_file_setup():
    print("** Copying config files if needed")
    config_files = ["flask-config.yml", "proxy-gate-config.yml", "gunicorn.conf.py"]

    for config_file in config_files:
        destination_path = os.path.join(
            os.environ["PROXY_GATE_CONFIG_DIR"], config_file
        )
        if not os.path.isfile(destination_path):
            print(f"Copying default {config_file}")
            source_path = os.path.join("examples", config_file)
            shutil.copy(source_path, destination_path)
        else:
            print(
                f"Config file {config_file} already exists in {destination_path}, skipping copy"
            )


def main():
    """
    Main function
    """
    print("** Booting up")
    dir_setup()
    config_file_setup()
    print("** Running migrations")
    migrate_engine = Migrate()

    migrations_dir = Path(os.environ["PROXY_GATE_DB_MIGRATION_DIR"])
    if migrations_dir.exists():
        shutil.rmtree(migrations_dir)

    migrations_dir.mkdir(parents=True)
    migrate_engine.init_app(app, db, directory=migrations_dir)
    with app.app_context():
        print("  Running init")
        init()
        print("  Running migrate")
        migrate()
        print("  Running upgrade")
        upgrade()
        print("** Running secret key setup")
        secret_key_setup()
        print("** Running runtime data setup")
        runtime_data_setup()


main()
