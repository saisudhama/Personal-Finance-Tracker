from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.analytics_service import get_income_vs_expense, get_spending_by_category
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/summary")
def dashboard_summary(month: int, year: int, db: Session = Depends(get_db),
                       current_user=Depends(get_current_user)):
    return {
        "income_vs_expense": get_income_vs_expense(db, current_user.id, month, year),
        "spending_by_category": get_spending_by_category(db, current_user.id, month, year),
    }