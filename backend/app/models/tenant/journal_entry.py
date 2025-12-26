from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.tenant.role import Base


class JournalEntry(Base):
    """Journal entries following double-entry accounting principles"""
    __tablename__ = "journal_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    entry_number = Column(String, nullable=False, unique=True, index=True)
    entry_date = Column(DateTime, nullable=False, index=True)
    description = Column(String, nullable=False)
    reference = Column(String, nullable=True)
    created_by = Column(Integer, nullable=False, index=True)  # References control DB people.id
    company_id = Column(Integer, nullable=False, index=True)  # References control DB company
    is_posted = Column(Boolean, default=False, nullable=False)  # Prevents editing after posting
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    lines = relationship("JournalEntryLine", back_populates="journal_entry", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="journal_entry")

