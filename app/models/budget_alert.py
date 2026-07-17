from sqlalchemy import Column, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from app.database import Base

class AlertType(str, enum.Enum):
    warning_80 = "warning_80"
    exceeded = "exceeded"

class BudgetAlert(Base):
    __tablename__ = "budget_alerts"

    id = Column(Integer, primary_key=True, index=True)
    budget_id = Column(Integer, ForeignKey("budgets.id"), nullable=False)
    alert_type = Column(Enum(AlertType), nullable=False)
    triggered_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    budget = relationship("Budget", back_populates="alerts")