def test_login_success(app):
    """
    Test the /login endpoint returns status code 200
    """
    client = app.test_client()
    response = client.get("/login/?redirect=http://foo.localhost:5000/")
    assert response.status_code == 200

    response = client.get(
        "/login/?workflowStep=callback&redirect=http://foo.localhost:5000/&method=plex"
    )
    assert response.status_code == 200


def test_login_invalid_workflow(app):
    """
    Test the /login endpoint returns status code 400 when workflowStep is invalid
    """
    client = app.test_client()
    response = client.get("/login/?workflowStep=wrongValue")
    assert response.status_code == 400
