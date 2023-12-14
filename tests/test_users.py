

def test_create_user(client):
    res = client.post(
        "/users/", json={"email": "aziz@gmail.com", "password": "password"})
    assert res.status_code == 201


def test_login_user(client, test_user):
    user = test_user
    res = client.post(
        "/login", data={"username": user['email'], "password": user['password']})
    assert res.status_code == 200
