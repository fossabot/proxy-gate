def test_index(app):
    """
    Test the /healthz endpoint returns status code 200
    """
    client = app.test_client()
    response = client.get("/metaz")
    assert response.status_code == 200
    response_json = response.json

    assert "version" in response_json
    assert "name" in response_json
