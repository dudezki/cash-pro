from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.tenant.role import Base


class CategoryType(str, enum.Enum):
    """Category types for organizing transactions"""
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"


class Category(Base):
    """Categories for organizing transactions"""
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(Enum(CategoryType), nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True, index=True)
    chart_account_id = Column(Integer, ForeignKey("chart_of_accounts.id"), nullable=True, index=True)
    company_id = Column(Integer, nullable=False, index=True)  # References control DB company
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Self-referential relationship for hierarchical categories
    parent_category = relationship("Category", remote_side=[id], backref="sub_categories")
    
    # Relationships
    chart_account = relationship("ChartOfAccount")
    transactions = relationship("Transaction", back_populates="category")

