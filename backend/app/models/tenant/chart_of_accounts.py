from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.tenant.role import Base


class AccountType(str, enum.Enum):
    """Chart of Accounts account types following accounting principles"""
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"


class ChartOfAccount(Base):
    """Chart of Accounts - defines the accounting structure"""
    __tablename__ = "chart_of_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    account_code = Column(String, nullable=False, index=True)  # e.g., "1000", "2000", "3000"
    account_name = Column(String, nullable=False)
    account_type = Column(Enum(AccountType), nullable=False, index=True)
    parent_account_id = Column(Integer, ForeignKey("chart_of_accounts.id"), nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    company_id = Column(Integer, nullable=False, index=True)  # References control DB company
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Self-referential relationship for hierarchical accounts
    parent_account = relationship("ChartOfAccount", remote_side=[id], backref="sub_accounts")
    
    # Relationships
    journal_entry_lines = relationship("JournalEntryLine", back_populates="chart_account")
    accounts = relationship("Account", back_populates="chart_account")

