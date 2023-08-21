from flask import Blueprint

blueprint = Blueprint(__name__.replace(".", "_"), __name__)

@blueprint.route("")
@blueprint.route("/")
def index():
    meta = {
        "version": "0.1.0",
        "name": "Proxy Gate",
        "googleAuth": {
            "clientId": "1234",
        },
    }
    return meta, 200
