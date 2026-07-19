"""
Phase 1 API Integration Tests — POC-02 Personal Finance Tracker
8 tests, using FastAPI's TestClient against a real (isolated) test database.
"""


# TC-02-P1-API-01
def test_register_success(client):
    response = client.post("/auth/register", json={
        "name": "Arjun Kapoor",
        "email": "arjun@example.com",
        "phone": "9876543210",
        "monthly_income": 60000,
        "password": "securepass123",
    })
    assert response.status_code == 201
    assert response.json()["email"] == "arjun@example.com"


# TC-02-P1-API-02
def test_register_duplicate_email_fails(client, registered_user):
    response = client.post("/auth/register", json=registered_user)
    assert response.status_code == 400


# TC-02-P1-API-03
def test_login_success(client, registered_user):
    response = client.post("/auth/login", json={
        "email": registered_user["email"],
        "password": registered_user["password"],
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


# TC-02-P1-API-04
def test_login_wrong_password_fails(client, registered_user):
    response = client.post("/auth/login", json={
        "email": registered_user["email"],
        "password": "wrong-password",
    })
    assert response.status_code == 401


# TC-02-P1-API-05
def test_create_account_requires_auth(client):
    response = client.post("/accounts/", json={
        "account_name": "Test Account",
        "account_type": "checking",
        "balance": 1000,
    })
    assert response.status_code == 401


# TC-02-P1-API-06
def test_create_account_success(client, auth_headers):
    response = client.post("/accounts/", json={
        "account_name": "HDFC Salary Account",
        "account_type": "checking",
        "balance": 5000,
    }, headers=auth_headers)
    assert response.status_code == 201
    assert response.json()["account_name"] == "HDFC Salary Account"


# TC-02-P1-API-07
def test_get_nonexistent_account_returns_404(client, auth_headers):
    response = client.get("/accounts/99999", headers=auth_headers)
    assert response.status_code == 404


# TC-02-P1-API-08
def test_create_transaction_updates_account_balance(client, auth_headers):
    account_res = client.post("/accounts/", json={
        "account_name": "Test Checking",
        "account_type": "checking",
        "balance": 1000,
    }, headers=auth_headers)
    account_id = account_res.json()["id"]

    txn_res = client.post("/transactions/", json={
        "account_id": account_id,
        "amount": 200,
        "type": "debit",
        "category": "food",
        "transaction_date": "2026-07-15T10:00:00",
    }, headers=auth_headers)
    assert txn_res.status_code == 201

    account_check = client.get(f"/accounts/{account_id}", headers=auth_headers)
    assert account_check.json()["balance"] == 800  # 1000 - 200
