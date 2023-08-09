from flask import Blueprint

metaz = Blueprint("metaz", __name__)


@metaz.route("")
@metaz.route("/")
def index():
    meta = {
        "version": "0.1.0",
        "name": "Proxy Gate",
        "googleAuth": {
            "clientId": "1234",
        }
    }
    return meta, 200
