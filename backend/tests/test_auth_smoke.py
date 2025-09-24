import os
import json
from app import create_app


def test_auth_signup_and_login_client():
    os.environ["MONGODB_URI"] = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    os.environ["MONGODB_DB_NAME"] = os.getenv("MONGODB_DB_NAME", "truthlens_test")
    app = create_app()
    client = app.test_client()

    # signup
    resp = client.post("/auth/signup", json={"email": "test@example.com", "password": "test123"})
    assert resp.status_code in (200, 201, 409)

    # login
    resp = client.post("/auth/login", json={"email": "test@example.com", "password": "test123"})
    assert resp.status_code == 200
    token = resp.get_json().get("access_token")
    assert token

    # profile
    resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data.get("email") == "test@example.com"
