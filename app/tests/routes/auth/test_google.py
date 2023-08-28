from app.utils import generate_secure_cookie


def test_check_401(app):
    """
    Test the /check endpoint returns status code 401 when no cookie is present
    """
    client = app.test_client()
    response = client.get("/auth/google/check")
    assert response.status_code == 401


def test_check_200(app):
    client = app.test_client()
    google_auth_cookie = {
        "userauth": True,
        "verified_email": True,
    }
    with app.app_context():
        plexauth_cookie = generate_secure_cookie(google_auth_cookie, salt="googleauth")

    client.set_cookie("_googleauth", plexauth_cookie)
    response = client.get("/auth/google/check")
    assert response.status_code == 200


def test_check_with_email_id(app):
    client = app.test_client()
    google_auth_cookie = {
        "userauth": True,
        "email": "foo@example.com",
    }
    with app.app_context():
        google_auth_cookie = generate_secure_cookie(
            google_auth_cookie, salt="googleauth"
        )

    client.set_cookie("_googleauth", google_auth_cookie)
    response = client.get("/auth/google/check?emailIn=foo@example.com,fee@nono.com")
    assert response.status_code == 200

    response = client.get("/auth/google/check?emailIn=goo@example.com,fee@nono.com")
    assert response.status_code == 403
