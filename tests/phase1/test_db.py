"""
Phase 1 Database Tests — POC-02 Personal Finance Tracker
4 tests verifying data actually persists correctly in SQLite,
including constraint enforcement and cascade deletes.
"""
from tests.phase1.conftest import TestingSessionLocal
from app.models.user import User
from app.models.account import Account
from app.models.budget import Budget
from app.models.transaction import TransactionCategory
from app.auth.jwt_handler import hash_password


# TC-02-P1-DB-01
def test_transaction_persists_with_correct_foreign_key(client, auth_headers):
    account_res = client.post("/accounts/", json={
        "account_name": "Persistence Test",
        "account_type": "savings",
        "balance": 500,
    }, headers=auth_headers)
    account_id = account_res.json()["id"]

    client.post("/transactions/", json={
        "account_id": account_id,
        "amount": 100,
        "type": "credit",
        "category": "salary",
        "transaction_date": "2026-07-15T09:00:00",
    }, headers=auth_headers)

    db = TestingSessionLocal()
    account = db.query(Account).filter(Account.id == account_id).first()
    assert len(account.transactions) == 1
    assert account.transactions[0].account_id == account_id
    db.close()


# TC-02-P1-DB-02
def test_budget_unique_constraint_per_category_month_year():
    db = TestingSessionLocal()
    user = User(name="DB Test", email="dbtest@example.com", hashed_password=hash_password("pass12345"))
    db.add(user)
    db.commit()
    db.refresh(user)

    budget1 = Budget(user_id=user.id, category=TransactionCategory.food, monthly_limit=5000, month=7, year=2026)
    db.add(budget1)
    db.commit()

    budget2 = Budget(user_id=user.id, category=TransactionCategory.food, monthly_limit=6000, month=7, year=2026)
    db.add(budget2)

    with __import__("pytest").raises(Exception):
        db.commit()

    db.rollback()
    db.close()


# TC-02-P1-DB-03
def test_deleting_account_cascades_to_transactions(client, auth_headers):
    account_res = client.post("/accounts/", json={
        "account_name": "Cascade Test",
        "account_type": "checking",
        "balance": 1000,
    }, headers=auth_headers)
    account_id = account_res.json()["id"]

    client.post("/transactions/", json={
        "account_id": account_id,
        "amount": 50,
        "type": "debit",
        "category": "transport",
        "transaction_date": "2026-07-15T08:00:00",
    }, headers=auth_headers)

    client.delete(f"/accounts/{account_id}", headers=auth_headers)

    db = TestingSessionLocal()
    from app.models.transaction import Transaction
    remaining = db.query(Transaction).filter(Transaction.account_id == account_id).all()
    assert len(remaining) == 0  # cascade delete should remove orphaned transactions
    db.close()


# TC-02-P1-DB-04
def test_account_balance_correct_after_multiple_transactions(client, auth_headers):
    account_res = client.post("/accounts/", json={
        "account_name": "Multi Txn Test",
        "account_type": "checking",
        "balance": 1000,
    }, headers=auth_headers)
    account_id = account_res.json()["id"]

    transactions = [
        {"amount": 200, "type": "debit", "category": "food"},
        {"amount": 5000, "type": "credit", "category": "salary"},
        {"amount": 150, "type": "debit", "category": "transport"},
    ]
    for t in transactions:
        client.post("/transactions/", json={
            "account_id": account_id,
            "amount": t["amount"],
            "type": t["type"],
            "category": t["category"],
            "transaction_date": "2026-07-15T12:00:00",
        }, headers=auth_headers)

    final = client.get(f"/accounts/{account_id}", headers=auth_headers)
    # 1000 - 200 + 5000 - 150 = 5650
    assert final.json()["balance"] == 5650
