from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from app.models.transaction import TransactionType, TransactionCategory

class TransactionCreate(BaseModel):
    account_id: int
    amount: float = Field(..., gt=0, description="Must be positive")
    type: TransactionType
    category: TransactionCategory
    description: str | None = None
    merchant: str | None = None
    transaction_date: datetime

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("amount must be greater than 0")
        return v

class TransactionResponse(BaseModel):
    id: int
    account_id: int
    amount: float
    type: TransactionType
    category: TransactionCategory
    description: str | None
    merchant: str | None
    transaction_date: datetime

    class Config:
        from_attributes = True