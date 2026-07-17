from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.schemas.budget import BudgetCreate, BudgetResponse
from app.models.budget import Budget
from app.services.budget_service import get_spent_amount
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/budgets", tags=["budgets"])

@router.post("/", response_model=BudgetResponse, status_code=201)
def create_budget(payload: BudgetCreate, db: Session = Depends(get_db),
                   current_user=Depends(get_current_user)):
    budget = Budget(user_id=current_user.id, **payload.model_dump())
    db.add(budget)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400,
                             detail="Budget already exists for this category/month/year")
    db.refresh(budget)
    return budget

@router.get("/", response_model=list[BudgetResponse])
def list_budgets(month: int, year: int, db: Session = Depends(get_db),
                  current_user=Depends(get_current_user)):
    budgets = db.query(Budget).filter(
        Budget.user_id == current_user.id, Budget.month == month, Budget.year == year
    ).all()
    result = []
    for b in budgets:
        spent = get_spent_amount(db, current_user.id, b.category.value, b.month, b.year)
        result.append({
            **b.__dict__,
            "spent": spent,
            "utilization_pct": round((spent / b.monthly_limit) * 100, 1) if b.monthly_limit else 0,
        })
    return result