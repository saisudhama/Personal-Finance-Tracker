from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import structlog, time
from app.database import get_db
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.models.transaction import Transaction, TransactionType
from app.models.account import Account
from app.models.budget import Budget
from app.services.balance_service import apply_transaction_to_balance
from app.services.budget_service import get_spent_amount, check_and_trigger_alerts
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/transactions", tags=["transactions"])
log = structlog.get_logger()

@router.post("/", response_model=TransactionResponse, status_code=201)
def create_transaction(payload: TransactionCreate, db: Session = Depends(get_db),
                        current_user=Depends(get_current_user)):
    start = time.time()
    account = db.query(Account).filter(
        Account.id == payload.account_id, Account.user_id == current_user.id
    ).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    transaction = Transaction(**payload.model_dump())
    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    apply_transaction_to_balance(db, account, transaction)

    # Budget alert check — only relevant for debits
    if transaction.type == TransactionType.debit:
        budget = db.query(Budget).filter(
            Budget.user_id == current_user.id,
            Budget.category == transaction.category,
            Budget.month == transaction.transaction_date.month,
            Budget.year == transaction.transaction_date.year,
        ).first()
        if budget:
            spent = get_spent_amount(db, current_user.id, transaction.category.value,
                                      budget.month, budget.year)
            check_and_trigger_alerts(db, budget, spent)

    log.info("operation_complete", operation="create_transaction", status="success",
              duration_ms=int((time.time() - start) * 1000), transaction_id=transaction.id)
    return transaction

@router.get("/account/{account_id}", response_model=list[TransactionResponse])
def list_transactions(account_id: int, db: Session = Depends(get_db),
                       current_user=Depends(get_current_user)):
    account = db.query(Account).filter(
        Account.id == account_id, Account.user_id == current_user.id
    ).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return db.query(Transaction).filter(Transaction.account_id == account_id).all()