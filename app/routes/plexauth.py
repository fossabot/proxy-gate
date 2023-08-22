# https://forums.plex.tv/t/authenticating-with-plex/609370
# https://plexapi.dev/docs/plex-tv/

from datetime import timedelta
from urllib.parse import urlparse

from flask import Blueprint, Response, make_response, request, session

from ..exceptions import BadCookieSignature, CookieNotFound
from ..utils import (
    generate_secure_cookie,
    get_user_session,
    plex_get_plex_resources,
    plex_get_user_info,
)

plexauth = Blueprint("plexauth", __name__)


@plexauth.route("/check")
def check():
    """
    Perform authentication and authorization checks given the conditions.

    if plexServer is provided, then we check if the user has access to that server
    if user2fa is provided, then we check if the user has 2fa enabled on their plex
        account
    if emailIn is provided, then we check if the user has an email address that is in
        the emailIn. Multiple values can be provided in csv format.
    """
    plex_resource_client_id = request.args.get(
        "plexResourceClientId", default=None, type=str
    )
    user_2fa = request.args.get("user2fa", default=False, type=bool)
    email_in = request.args.get("emailIn", type=str)

    try:
        plex_auth_user_session = get_user_session(
            ["_plexauth"], salt="plexauth", max_age=15552000
        )
    except (CookieNotFound, BadCookieSignature):
        return "authentication required", 401

    if (
        plex_resource_client_id is not None
        and plex_resource_client_id
        not in plex_auth_user_session.get("plex_resource_client_ids", [])
    ):
        return "access denied", 403
    elif user_2fa is True and plex_auth_user_session.get("2fa-enabled", False) is False:
        return "access denied", 403
    elif email_in is not None and plex_auth_user_session.get(
        "email", None
    ) not in email_in.split(","):
        return "access denied", 403
    else:
        # at this point we know the user is authenticated and if needed has access to
        # the resource
        return "access ok", 200


@plexauth.route("/session")
def get_session():
    plex_auth_token = request.args.get("plexAuthToken")
    plex_client_id = request.args.get("plexClientId")
    redirect_arg = request.args.get("redirect")
    url_parse_redirect = urlparse(redirect_arg) if redirect_arg is not None else None

    if plex_auth_token is None or plex_client_id is None:
        return "invalid request", 400

    plex_user_info, http_status_code = plex_get_user_info(
        plex_auth_token, plex_client_id
    )

    if http_status_code == 401:
        return "invalid token", 400
    elif http_status_code != 200:
        return "unknown error", 500

    plex_resources, http_status_code = plex_get_plex_resources(
        plex_auth_token, plex_client_id
    )

    if http_status_code == 401:
        return "invalid token", 400
    elif http_status_code != 200:
        return "unknown error", 500

    cookie_domains = [request.host]
    if url_parse_redirect is not None:
        cookie_domains.append(url_parse_redirect.hostname)
    response = make_response()
    create_user_auth_session(
        response,
        plex_auth_token,
        plex_client_id,
        plex_user_info,
        plex_resources,
        domains=cookie_domains,
    )
    return response


@plexauth.route("/logout")
def logout():
    # Clear the session and log out the user
    response = make_response("Logged out")
    response.delete_cookie("_plexauth")
    session.clear()
    return response


def create_user_auth_session(
    response: Response,
    plex_auth_token: str,
    plex_client_id: str,
    plex_user_info: dict,
    plex_resources: dict,
    domains: list = [None],
) -> None:
    # Setup the cookie data
    cookie_data = {}
    cookie_data["userauth"] = True
    cookie_data["plex_auth_token"] = plex_auth_token
    cookie_data["plex_resource_client_ids"] = [
        resource["clientIdentifier"] for resource in plex_resources
    ]
    cookie_data["2fa-enabled"] = plex_user_info["twoFactorEnabled"]
    cookie_data["email"] = plex_user_info["email"]

    plexauth_cookie = generate_secure_cookie(cookie_data, salt="plexauth")

    for domain in domains:
        response.set_cookie(
            "_plexauth",
            plexauth_cookie,
            max_age=timedelta(days=180),
            domain=domain,
            secure=True,
            httponly=True,
            samesite="Lax",
        )
