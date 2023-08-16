import os

import pytest

from app.utils import generate_secure_cookie, validate_secure_cookie


def test_check_401(app):
    """
    Test the /check endpoint returns status code 401 when no cookie is present
    """
    client = app.test_client()
    response = client.get("/plexauth/check")
    assert response.status_code == 401


def test_check_200(app):
    """ """
    client = app.test_client()
    plex_auth_cookie = {
        "userauth": True,
    }
    with app.app_context():
        plexauth_cookie = generate_secure_cookie(plex_auth_cookie, salt="plexauth")

    client.set_cookie("_plexauth", plexauth_cookie)
    response = client.get("/plexauth/check")
    assert response.status_code == 200


def test_check_with_plex_resource_id(app):
    """ """
    client = app.test_client()
    plex_auth_cookie = {"userauth": True, "plex_resource_client_ids": ["a", "b", "c"]}
    with app.app_context():
        plexauth_cookie = generate_secure_cookie(plex_auth_cookie, salt="plexauth")

    client.set_cookie("_plexauth", plexauth_cookie)
    response = client.get("/plexauth/check?plexResourceClientId=a")
    assert response.status_code == 200

    response = client.get("/plexauth/check?plexResourceClientId=y")
    assert response.status_code == 403


def test_check_with_user_2fa(app):
    """ """
    client = app.test_client()
    plex_auth_cookie = {
        "userauth": True,
        "2fa-enabled": True,
    }
    with app.app_context():
        plexauth_cookie = generate_secure_cookie(plex_auth_cookie, salt="plexauth")

    client.set_cookie("_plexauth", plexauth_cookie)
    response = client.get("/plexauth/check?user2fa=True")
    assert response.status_code == 200

    plex_auth_cookie = {
        "userauth": True,
        "2fa-enabled": False,
    }
    with app.app_context():
        plexauth_cookie = generate_secure_cookie(plex_auth_cookie, salt="plexauth")

    client.set_cookie("_plexauth", plexauth_cookie)
    response = client.get("/plexauth/check?user2fa=True")
    assert response.status_code == 403


def test_check_with_email_id(app):
    """ """
    client = app.test_client()
    plex_auth_cookie = {
        "userauth": True,
        "email": "foo@example.com",
    }
    with app.app_context():
        plexauth_cookie = generate_secure_cookie(plex_auth_cookie, salt="plexauth")

    client.set_cookie("_plexauth", plexauth_cookie)
    response = client.get("/plexauth/check?emailIn=foo@example.com,fee@nono.com")
    assert response.status_code == 200

    response = client.get("/plexauth/check?emailIn=goo@example.com,fee@nono.com")
    assert response.status_code == 403


@pytest.mark.skipif(
    os.environ.get("PLEX_AUTH_TOKEN") is None,
    reason="PLEX_AUTH_TOKEN is not set, can't run this test",
)
def test_session_success(app):
    """ """

    plex_auth_token = os.environ.get("PLEX_AUTH_TOKEN")

    client = app.test_client()
    response = client.get(
        f"/plexauth/session?plexAuthToken={plex_auth_token}&plexClientId=1&redirect=http://foo.localhost:5000/"
    )
    assert response.status_code == 200

    cookie_domains = [x.domain for x in client.cookie_jar if x.key == "_plexauth"]
    cookie_values = [x.value for x in client.cookie_jar if x.key == "_plexauth"]

    for cookie_value in cookie_values:
        with app.app_context():
            decoded_cookie = validate_secure_cookie(cookie_value, salt="plexauth")

        assert decoded_cookie["plex_auth_token"] == plex_auth_token
        assert decoded_cookie["userauth"] is True
        assert isinstance(decoded_cookie["plex_resource_client_ids"], list)
        assert "2fa-enabled" in decoded_cookie
        assert "email" in decoded_cookie

    assert "localhost" in cookie_domains
    assert "foo.localhost" in cookie_domains


def test_session_fail(app):
    """ """

    plex_auth_token = "wrongvalue"

    client = app.test_client()
    response = client.get(
        f"/plexauth/session?plexAuthToken={plex_auth_token}&plexClientId=33"
    )
    assert response.status_code == 400
    assert response.text == "invalid token"

    assert len(client.cookie_jar) == 0

    response = client.get("/plexauth/session")
    assert response.status_code == 400
    assert response.text == "invalid request"


def test_logout(app):
    """ """
    client = app.test_client()
    plex_auth_cookie = {
        "userauth": True,
        "2fa-enabled": True,
    }
    with app.app_context():
        plexauth_cookie = generate_secure_cookie(plex_auth_cookie, salt="plexauth")

    client.set_cookie("_plexauth", plexauth_cookie)

    assert len(client.cookie_jar) != 0

    response = client.get("/plexauth/logout")
    assert response.status_code == 200

    assert len(client.cookie_jar) == 0
