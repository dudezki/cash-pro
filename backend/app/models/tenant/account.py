from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.tenant.role import Base


class AccountType(str, enum.Enum):
    """Physical account types"""
    CHECKING = "checking"
    SAVINGS = "savings"
    CREDIT = "credit"
    CASH = "cash"
    INVESTMENT = "investment"


class Account(Base):
    """Physical accounts (bank accounts, cash, etc.) - metadata only, NO balance field"""
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(String, nullable=False, unique=True, index=True)
    name = Column(String, nullable=False)
    bank_name = Column(String, nullable=True)
    account_type = Column(Enum(AccountType), nullable=False)
    chart_account_id = Column(Integer, ForeignKey("chart_of_accounts.id"), nullable=False, index=True)
    currency = Column(String, default="USD", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    company_id = Column(Integer, nullable=False, index=True)  # References control DB company
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    chart_account = relationship("ChartOfAccount", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account")

