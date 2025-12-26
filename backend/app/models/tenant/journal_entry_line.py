from sqlalchemy import Column, Integer, ForeignKey, Numeric, String, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.tenant.role import Base


class JournalEntryLine(Base):
    """Individual debit/credit lines for journal entries"""
    __tablename__ = "journal_entry_lines"
    
    id = Column(Integer, primary_key=True, index=True)
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id", ondelete="CASCADE"), nullable=False, index=True)
    chart_account_id = Column(Integer, ForeignKey("chart_of_accounts.id"), nullable=False, index=True)
    debit_amount = Column(Numeric(15, 2), nullable=True, default=0.00)
    credit_amount = Column(Numeric(15, 2), nullable=True, default=0.00)
    description = Column(String, nullable=True)
    reference = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    journal_entry = relationship("JournalEntry", back_populates="lines")
    chart_account = relationship("ChartOfAccount", back_populates="journal_entry_lines")
    
    # Constraint: Either debit or credit, but not both or neither
    __table_args__ = (
        CheckConstraint(
            "(debit_amount IS NOT NULL AND debit_amount >= 0 AND credit_amount IS NULL) OR "
            "(credit_amount IS NOT NULL AND credit_amount >= 0 AND debit_amount IS NULL)",
            name="check_debit_credit_exclusive"
        ),
    )

