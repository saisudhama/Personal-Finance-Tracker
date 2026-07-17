from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.transaction import Transaction, TransactionType
from app.models.account import Account

def get_income_vs_expense(db: Session, user_id: int, month: int, year: int) -> dict:
    base_filter = [
        Account.user_id == user_id,
        func.strftime("%m", Transaction.transaction_date) == f"{month:02d}",
        func.strftime("%Y", Transaction.transaction_date) == str(year),
    ]

    income = (
        db.query(func.sum(Transaction.amount))
        .join(Account, Transaction.account_id == Account.id)
        .filter(*base_filter, Transaction.type == TransactionType.credit)
        .scalar()
    ) or 0.0

    expense = (
        db.query(func.sum(Transaction.amount))
        .join(Account, Transaction.account_id == Account.id)
        .filter(*base_filter, Transaction.type == TransactionType.debit)
        .scalar()
    ) or 0.0

    savings_rate = round(((income - expense) / income) * 100, 1) if income > 0 else 0.0

    return {
        "income": income,
        "expense": expense,
        "net_cash_flow": income - expense,
        "savings_rate_pct": savings_rate,
    }

def get_spending_by_category(db: Session, user_id: int, month: int, year: int) -> list[dict]:
    rows = (
        db.query(Transaction.category, func.sum(Transaction.amount))
        .join(Account, Transaction.account_id == Account.id)
        .filter(
            Account.user_id == user_id,
            Transaction.type == TransactionType.debit,
            func.strftime("%m", Transaction.transaction_date) == f"{month:02d}",
            func.strftime("%Y", Transaction.transaction_date) == str(year),
        )
        .group_by(Transaction.category)
        .all()
    )
    return [{"category": category.value, "total": total} for category, total in rows]