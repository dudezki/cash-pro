from sqlalchemy import Column, Integer, ForeignKey, Enum, Numeric, String, DateTime, Date
from sqlalchemy.orm import relationship
from datetime import datetime, date
import enum
from app.models.tenant.role import Base


class TransactionType(str, enum.Enum):
    """Transaction types that auto-create journal entries"""
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"


class Transaction(Base):
    """Simplified transactions that auto-create journal entries"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    description = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True, index=True)
    transaction_date = Column(Date, nullable=False, index=True)
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"), nullable=True, index=True)
    created_by = Column(Integer, nullable=False, index=True)  # References control DB people.id
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    account = relationship("Account", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
    journal_entry = relationship("JournalEntry", back_populates="transactions")

