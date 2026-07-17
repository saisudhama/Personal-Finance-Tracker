import structlog
from sqlalchemy.orm import Session
from app.models.account import Account
from app.models.transaction import Transaction, TransactionType

log = structlog.get_logger()

def apply_transaction_to_balance(db: Session, account: Account, transaction: Transaction) -> Account:
    """Every debit decreases balance, every credit increases it."""
    if transaction.type == TransactionType.debit:
        account.balance -= transaction.amount
    else:
        account.balance += transaction.amount

    db.add(account)
    db.commit()
    db.refresh(account)

    log.info(
        "balance_updated",
        operation="apply_transaction_to_balance",
        account_id=account.id,
        transaction_type=transaction.type.value,
        amount=transaction.amount,
        new_balance=account.balance,
        status="success",
    )
    return account