import structlog
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.budget import Budget
from app.models.budget_alert import BudgetAlert, AlertType
from app.models.transaction import Transaction, TransactionType
from app.models.account import Account

log = structlog.get_logger()

def get_spent_amount(db: Session, user_id: int, category: str, month: int, year: int) -> float:
    """Sum of debit transactions for a category within a given month/year, across all user accounts."""
    total = (
        db.query(func.sum(Transaction.amount))
        .join(Account, Transaction.account_id == Account.id)
        .filter(
            Account.user_id == user_id,
            Transaction.category == category,
            Transaction.type == TransactionType.debit,
            func.strftime("%m", Transaction.transaction_date) == f"{month:02d}",
            func.strftime("%Y", Transaction.transaction_date) == str(year),
        )
        .scalar()
    )
    return total or 0.0

def check_and_trigger_alerts(db: Session, budget: Budget, spent: float) -> list[BudgetAlert]:
    """Fires warning_80 at 80% utilization and exceeded at 100%. Avoids duplicate alerts."""
    utilization = spent / budget.monthly_limit if budget.monthly_limit > 0 else 0
    new_alerts = []

    existing_types = {a.alert_type for a in budget.alerts}

    if utilization >= 1.0 and AlertType.exceeded not in existing_types:
        alert = BudgetAlert(budget_id=budget.id, alert_type=AlertType.exceeded)
        db.add(alert)
        new_alerts.append(alert)
    elif utilization >= 0.8 and AlertType.warning_80 not in existing_types:
        alert = BudgetAlert(budget_id=budget.id, alert_type=AlertType.warning_80)
        db.add(alert)
        new_alerts.append(alert)

    if new_alerts:
        db.commit()
        log.info(
            "budget_alert_triggered",
            operation="check_and_trigger_alerts",
            budget_id=budget.id,
            category=budget.category.value,
            utilization=round(utilization, 2),
            alerts_fired=[a.alert_type.value for a in new_alerts],
            status="success",
        )
    return new_alerts