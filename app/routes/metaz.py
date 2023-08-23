from flask import Blueprint, url_for

blueprint = Blueprint(__name__.replace(".", "_"), __name__)


@blueprint.route("")
@blueprint.route("/")
def index():
    meta = {
        "version": "0.1.0",
        "app_name": "Proxy Gate",
        "google_auth": {
            "session_endpoint": url_for("app_routes_auth_google.get_session"),
        },
        "plex_auth": {
            "session_endpoint": url_for("app_routes_auth_plex.get_session"),
        },
    }
    return meta, 200
