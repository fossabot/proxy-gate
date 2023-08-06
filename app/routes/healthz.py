from flask import Blueprint

healthz = Blueprint("healthz", __name__)


@healthz.route("")
@healthz.route("/")
def index():
    return "OK", 200
