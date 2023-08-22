from flask import Blueprint

blueprint = Blueprint(__name__.replace(".", "_"), __name__)


@blueprint.route("")
@blueprint.route("/")
def index():
    return "OK", 200
