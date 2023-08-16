from flask import Blueprint, abort, request, send_from_directory, make_response

login = Blueprint("login", __name__)


@login.route("", defaults={"path": "index.html"})
@login.route("/", defaults={"path": "index.html"})
@login.route("/<path:path>")
def login_page(path):
    if path == "index.html":
        workflow = _check_workflow_step(request.args.get("workflowStep", "start"))
        if workflow in ["start", "forbidden"]:
            return login_workflow("Proxy Gate", request, workflow, ["redirect"])
        elif workflow == "callback":
            return login_workflow("Proxy Gate", request, workflow, ["method"])

    return send_from_directory("static/login", path)


def login_workflow(app_name, request, workflow_step, required_args=[]):
    for required_arg in required_args:
        _arg = request.args.get(required_arg)
        if _arg is None:
            return "invalid request", 400
    response = make_response(send_from_directory("static/login", "index.html"))
    response.headers["X-Proxy-Gate-Google-Client-Id"] = "1234"
    response.headers["X-App-Version"] = "09125"
    return response


def _check_workflow_step(workflow_step_arg):
    valid_workflow_steps = ["start", "callback", "forbidden"]
    if workflow_step_arg not in valid_workflow_steps:
        abort(400)
    else:
        return workflow_step_arg
