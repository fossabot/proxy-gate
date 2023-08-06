def test_index(app):
    """
    Test the /healthz endpoint returns status code 200
    """
    client = app.test_client()
    response = client.get("/healthz")
    assert response.status_code == 200