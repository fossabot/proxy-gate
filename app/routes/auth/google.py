# https://developers.google.com/identity/gsi/web/guides/overview

from datetime import timedelta
from urllib.parse import urlparse

from flask import Blueprint, Response, make_response, request

from ...exceptions import BadCookieSignature, CookieNotFound
from ...utils import (
    base64_url_decode,
    generate_secure_cookie,
    get_user_session,
    google_get_user_info,
)

blueprint = Blueprint(__name__.replace('.', '_'), __name__)


@blueprint.route("/check")
def check():
    """
    Perform authentication and authorization checks given the conditions.

    if emailIn is provided, then we check if the user has an email address that is in
        the emailIn. Multiple values can be provided in csv format.
    """
    email_in = request.args.get("emailIn", type=str)

    try:
        google_auth_user_session = get_user_session(
            ["_googleauth"], salt="googleauth", max_age=15552000
        )
    except (CookieNotFound, BadCookieSignature):
        return "authentication required", 401

    if email_in is not None and google_auth_user_session.get(
        "email", None
    ) not in email_in.split(","):
        return "access denied", 403
    else:
        # at this point we know the user is authenticated and if needed has access to
        # the resource
        return "access ok", 200


@blueprint.route("/session")
def get_session():
    google_access_token = request.args.get("googleAccessToken")
    redirect_arg = request.args.get("redirect")
    redirect_arg_decoded = (
        base64_url_decode(redirect_arg) if redirect_arg is not None else None
    )
    url_parse_redirect = (
        urlparse(redirect_arg_decoded) if redirect_arg is not None else None
    )

    if google_access_token is None:
        return "invalid request", 400

    google_user_info, http_status_code = google_get_user_info(google_access_token)

    if http_status_code == 401:
        return "invalid token", 400
    elif http_status_code != 200:
        return "unknown error", 500
    elif google_user_info.get("verified_email", False) is False:
        return "unverified email", 403

    cookie_domains = [request.host]
    print(f"**** {request.host}")
    print(request.headers)
    if url_parse_redirect is not None:
        cookie_domains.append(url_parse_redirect.hostname)
    response = make_response()
    create_user_auth_session(
        response,
        google_user_info,
        domains=cookie_domains,
    )
    return response


def create_user_auth_session(
    response: Response,
    google_user_info: dict,
    domains: list = [None],
) -> None:
    # Setup the cookie data
    cookie_data = {}
    cookie_data["userauth"] = True
    cookie_data["verified_email"] = google_user_info["verified_email"]
    cookie_data["email"] = google_user_info["email"]

    google_auth_cookie = generate_secure_cookie(cookie_data, salt="googleauth")

    for domain in domains:
        response.set_cookie(
            "_googleauth",
            google_auth_cookie,
            max_age=timedelta(days=180),
            domain=domain,
            secure=True,
            httponly=True,
            samesite="Lax",
        )
