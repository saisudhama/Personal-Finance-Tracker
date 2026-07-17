from pydantic import BaseModel, Field
from app.models.transaction import TransactionCategory

class BudgetCreate(BaseModel):
    category: TransactionCategory
    monthly_limit: float = Field(..., gt=0)
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2020, le=2100)

class BudgetResponse(BaseModel):
    id: int
    user_id: int
    category: TransactionCategory
    monthly_limit: float
    month: int
    year: int
    spent: float | None = None
    utilization_pct: float | None = None

    class Config:
        from_attributes = True