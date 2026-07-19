"""
Phase 1 Unit Tests — POC-02 Personal Finance Tracker
8 tests, no HTTP calls, no live database — pure function/logic testing.
"""
import pytest
from unittest.mock import MagicMock
from datetime import datetime, timezone

from app.auth.jwt_handler import hash_password, verify_password, create_access_token, decode_access_token
from app.services.budget_service import check_and_trigger_alerts
from app.models.budget import Budget
from app.models.budget_alert import AlertType
from app.models.transaction import TransactionCategory


# TC-02-P1-UNIT-01
def test_hash_password_produces_different_hash_each_time():
    h1 = hash_password("supersecure123")
    h2 = hash_password("supersecure123")
    assert h1 != h2  # bcrypt salts each hash uniquely
    assert verify_password("supersecure123", h1)


# TC-02-P1-UNIT-02
def test_verify_password_rejects_wrong_password():
    hashed = hash_password("correct-password")
    assert verify_password("wrong-password", hashed) is False


# TC-02-P1-UNIT-03
def test_create_and_decode_access_token_round_trip():
    token = create_access_token({"sub": "42"})
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "42"


# TC-02-P1-UNIT-04
def test_decode_access_token_rejects_garbage_token():
    assert decode_access_token("not-a-real-token") is None


# TC-02-P1-UNIT-05
def test_budget_alert_fires_warning_at_80_percent():
    budget = Budget(id=1, user_id=1, category=TransactionCategory.food, monthly_limit=1000, month=7, year=2026)
    budget.alerts = []
    db = MagicMock()

    alerts = check_and_trigger_alerts(db, budget, spent=800)  # exactly 80%

    assert len(alerts) == 1
    assert alerts[0].alert_type == AlertType.warning_80


# TC-02-P1-UNIT-06
def test_budget_alert_fires_exceeded_at_100_percent():
    budget = Budget(id=1, user_id=1, category=TransactionCategory.food, monthly_limit=1000, month=7, year=2026)
    budget.alerts = []
    db = MagicMock()

    alerts = check_and_trigger_alerts(db, budget, spent=1000)  # exactly 100%

    assert len(alerts) == 1
    assert alerts[0].alert_type == AlertType.exceeded


# TC-02-P1-UNIT-07
def test_budget_alert_does_not_duplicate_existing_alert():
    budget = Budget(id=1, user_id=1, category=TransactionCategory.food, monthly_limit=1000, month=7, year=2026)
    existing_alert = MagicMock()
    existing_alert.alert_type = AlertType.warning_80
    budget.alerts = [existing_alert]
    db = MagicMock()

    alerts = check_and_trigger_alerts(db, budget, spent=850)  # still in the 80% band

    assert len(alerts) == 0  # already fired, should not fire again


# TC-02-P1-UNIT-08
def test_budget_alert_below_threshold_fires_nothing():
    budget = Budget(id=1, user_id=1, category=TransactionCategory.food, monthly_limit=1000, month=7, year=2026)
    budget.alerts = []
    db = MagicMock()

    alerts = check_and_trigger_alerts(db, budget, spent=400)  # 40%, below both thresholds

    assert len(alerts) == 0
