from pydantic import BaseModel, Field
from app.models.account import AccountType

class AccountCreate(BaseModel):
    account_name: str = Field(..., min_length=1, max_length=100)
    account_type: AccountType
    balance: float = 0.0
    currency: str = "INR"

class AccountResponse(BaseModel):
    id: int
    user_id: int
    account_name: str
    account_type: AccountType
    balance: float
    currency: str

    class Config:
        from_attributes = True