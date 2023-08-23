import base64

import requests
from flask import current_app, request
from itsdangerous import BadSignature, URLSafeTimedSerializer

from app.exceptions import BadCookieSignature, CookieNotFound


def generate_secure_cookie(data: dict, salt=None) -> str:
    serializer = URLSafeTimedSerializer(current_app.secret_key[-1], salt=salt)
    signed_string = serializer.dumps(data)
    return signed_string


def validate_secure_cookie(cookie: bytes, salt=None, max_age=None) -> dict:
    serializer = URLSafeTimedSerializer(current_app.secret_key)
    try:
        return serializer.loads(cookie, max_age=max_age, salt=salt)
    except BadSignature as ex:
        raise BadCookieSignature(
            f"Signature validation failed for cookie: {ex.message}"
        ) from ex


def plex_get_user_info(plex_auth_token, plex_client_id) -> tuple:
    """
    Get user info from plex.tv
    """
    headers = {
        "Accept": "application/json",
        "X-Plex-Token": plex_auth_token,
        "X-Plex-Client-Identifier": plex_client_id,
    }
    resp = requests.get("https://plex.tv/api/v2/user", headers=headers, timeout=10)

    if resp.status_code == 200:
        resp_json = resp.json()
        return resp_json, resp.status_code

    print("**** get_user_info failed ****")
    print(resp.status_code)
    print(resp.text)
    return None, resp.status_code


def plex_get_plex_resources(plex_auth_token, plex_client_id) -> tuple:
    """
    Get the resources the user has access to
    """
    headers = {
        "Accept": "application/json",
        "X-Plex-Token": plex_auth_token,
        "X-Plex-Client-Identifier": plex_client_id,
    }
    resp = requests.get("https://plex.tv/api/v2/resources", headers=headers, timeout=10)
    if resp.status_code == 200:
        resp_json = resp.json()
        return resp_json, resp.status_code

    print("**** plex_get_plex_resources failed ****")
    print(resp.status_code)
    print(resp.text)
    return None, resp.status_code


def get_user_session(cookie_names: list, salt: str, max_age: int) -> dict:
    cookie = None

    for cookie_name in cookie_names:
        cookie = request.cookies.get(cookie_name)
        if cookie is not None:
            break

    if cookie is None:
        print("** Case 1 no cookie")
        raise CookieNotFound(f"No cookie found: {cookie_names}")

    cookie_data = validate_secure_cookie(cookie, salt=salt, max_age=max_age)

    return cookie_data


def google_get_user_info(google_access_token) -> tuple:
    """
    Get user info from google
    """
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {google_access_token}",
    }
    resp = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo", headers=headers, timeout=10
    )

    if resp.status_code == 200:
        resp_json = resp.json()
        return resp_json, resp.status_code

    print("**** get_user_info failed ****")
    print(resp.status_code)
    print(resp.text)
    return None, resp.status_code


def base64_url_decode(url: str) -> str:
    # Add padding characters if needed (length % 4 !== 0)
    while len(url) % 4 != 0:
        url += "="

    base64_encoded = url.replace("-", "+").replace("_", "/")
    base64_decoded = base64.b64decode(base64_encoded)
    return base64_decoded.decode("utf-8")
