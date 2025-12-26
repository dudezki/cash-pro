from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal
from typing import List, Dict, Optional
from datetime import date, datetime
from app.models.tenant.journal_entry import JournalEntry
from app.models.tenant.journal_entry_line import JournalEntryLine
from app.models.tenant.chart_of_accounts import ChartOfAccount, AccountType


def validate_journal_entry_balance(db: Session, journal_entry_id: int) -> bool:
    """Validate that a journal entry has balanced debits and credits"""
    lines = db.query(JournalEntryLine).filter(
        JournalEntryLine.journal_entry_id == journal_entry_id
    ).all()
    
    total_debits = sum(
        Decimal(str(line.debit_amount or 0)) for line in lines
    )
    total_credits = sum(
        Decimal(str(line.credit_amount or 0)) for line in lines
    )
    
    return total_debits == total_credits


def create_journal_entry(
    db: Session,
    entry_number: str,
    entry_date: date,
    description: str,
    lines: List[Dict],
    created_by: int,
    company_id: int,
    reference: Optional[str] = None
) -> JournalEntry:
    """
    Create a journal entry with lines.
    Lines should be a list of dicts with: chart_account_id, debit_amount (or credit_amount), description, reference (optional)
    """
    # Create journal entry
    journal_entry = JournalEntry(
        entry_number=entry_number,
        entry_date=entry_date,
        description=description,
        reference=reference,
        created_by=created_by,
        company_id=company_id,
        is_posted=False
    )
    db.add(journal_entry)
    db.flush()
    
    # Create journal entry lines
    total_debits = Decimal("0.00")
    total_credits = Decimal("0.00")
    
    for line_data in lines:
        debit_amount = Decimal(str(line_data.get("debit_amount", 0) or 0))
        credit_amount = Decimal(str(line_data.get("credit_amount", 0) or 0))
        
        if debit_amount > 0 and credit_amount > 0:
            raise ValueError("Line cannot have both debit and credit amounts")
        if debit_amount == 0 and credit_amount == 0:
            raise ValueError("Line must have either debit or credit amount")
        
        total_debits += debit_amount
        total_credits += credit_amount
        
        line = JournalEntryLine(
            journal_entry_id=journal_entry.id,
            chart_account_id=line_data["chart_account_id"],
            debit_amount=debit_amount if debit_amount > 0 else None,
            credit_amount=credit_amount if credit_amount > 0 else None,
            description=line_data.get("description"),
            reference=line_data.get("reference")
        )
        db.add(line)
    
    # Validate balance
    if total_debits != total_credits:
        db.rollback()
        raise ValueError(
            f"Journal entry is not balanced: Debits={total_debits}, Credits={total_credits}"
        )
    
    db.commit()
    db.refresh(journal_entry)
    return journal_entry


def get_account_balance(db: Session, chart_account_id: int) -> Decimal:
    """
    Calculate account balance from journal entries.
    For Asset/Expense: Balance = SUM(debits) - SUM(credits)
    For Liability/Equity/Revenue: Balance = SUM(credits) - SUM(debits)
    """
    chart_account = db.query(ChartOfAccount).filter(
        ChartOfAccount.id == chart_account_id
    ).first()
    
    if not chart_account:
        raise ValueError(f"Chart account {chart_account_id} not found")
    
    # Get all journal entry lines for this account (only from posted entries)
    lines = db.query(JournalEntryLine).join(JournalEntry).filter(
        JournalEntryLine.chart_account_id == chart_account_id,
        JournalEntry.is_posted == True
    ).all()
    
    total_debits = sum(Decimal(str(line.debit_amount or 0)) for line in lines)
    total_credits = sum(Decimal(str(line.credit_amount or 0)) for line in lines)
    
    # Calculate balance based on account type
    if chart_account.account_type in [AccountType.ASSET, AccountType.EXPENSE]:
        balance = total_debits - total_credits
    else:  # LIABILITY, EQUITY, REVENUE
        balance = total_credits - total_debits
    
    return balance


def get_account_balance_as_of(
    db: Session,
    chart_account_id: int,
    as_of_date: date
) -> Decimal:
    """Calculate account balance up to a specific date"""
    chart_account = db.query(ChartOfAccount).filter(
        ChartOfAccount.id == chart_account_id
    ).first()
    
    if not chart_account:
        raise ValueError(f"Chart account {chart_account_id} not found")
    
    # Get all posted journal entry lines up to the date
    lines = db.query(JournalEntryLine).join(JournalEntry).filter(
        JournalEntryLine.chart_account_id == chart_account_id,
        JournalEntry.entry_date <= as_of_date,
        JournalEntry.is_posted == True
    ).all()
    
    total_debits = sum(Decimal(str(line.debit_amount or 0)) for line in lines)
    total_credits = sum(Decimal(str(line.credit_amount or 0)) for line in lines)
    
    # Calculate balance based on account type
    if chart_account.account_type in [AccountType.ASSET, AccountType.EXPENSE]:
        balance = total_debits - total_credits
    else:  # LIABILITY, EQUITY, REVENUE
        balance = total_credits - total_debits
    
    return balance


def create_transaction_with_journal(
    db: Session,
    account_id: int,
    transaction_type: str,
    amount: Decimal,
    description: str,
    transaction_date: date,
    created_by: int,
    company_id: int,
    category_id: Optional[int] = None
) -> tuple:
    """
    Create a transaction and auto-create corresponding journal entry.
    Returns (transaction, journal_entry)
    
    Transaction types:
    - deposit: Debit Account (asset), Credit Revenue/Equity
    - withdrawal: Debit Expense, Credit Account (asset)
    - transfer: Debit Account A, Credit Account B (requires to_account_id)
    """
    from app.models.tenant.account import Account
    from app.models.tenant.transaction import Transaction, TransactionType
    from app.models.tenant.chart_of_accounts import AccountType as ChartAccountType
    
    # Get the account
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise ValueError(f"Account {account_id} not found")
    
    # Get chart account
    chart_account = db.query(ChartOfAccount).filter(
        ChartOfAccount.id == account.chart_account_id
    ).first()
    if not chart_account:
        raise ValueError(f"Chart account {account.chart_account_id} not found")
    
    # Generate entry number
    entry_count = db.query(JournalEntry).filter(
        JournalEntry.company_id == company_id
    ).count()
    entry_number = f"JE-{company_id}-{entry_count + 1:06d}"
    
    # Create journal entry based on transaction type
    if transaction_type == TransactionType.DEPOSIT:
        # Debit: Account (asset), Credit: Revenue or Equity
        # For simplicity, credit to a default Revenue account (would need to be configured)
        revenue_account = db.query(ChartOfAccount).filter(
            ChartOfAccount.account_type == ChartAccountType.REVENUE,
            ChartOfAccount.company_id == company_id
        ).first()
        
        if not revenue_account:
            raise ValueError("No revenue account found in chart of accounts")
        
        lines = [
            {
                "chart_account_id": chart_account.id,
                "debit_amount": amount,
                "description": description
            },
            {
                "chart_account_id": revenue_account.id,
                "credit_amount": amount,
                "description": description
            }
        ]
    elif transaction_type == TransactionType.WITHDRAWAL:
        # Debit: Expense, Credit: Account (asset)
        expense_account = db.query(ChartOfAccount).filter(
            ChartOfAccount.account_type == ChartAccountType.EXPENSE,
            ChartOfAccount.company_id == company_id
        ).first()
        
        if not expense_account:
            raise ValueError("No expense account found in chart of accounts")
        
        lines = [
            {
                "chart_account_id": expense_account.id,
                "debit_amount": amount,
                "description": description
            },
            {
                "chart_account_id": chart_account.id,
                "credit_amount": amount,
                "description": description
            }
        ]
    else:
        raise ValueError(f"Unsupported transaction type: {transaction_type}")
    
    # Create journal entry
    journal_entry = create_journal_entry(
        db=db,
        entry_number=entry_number,
        entry_date=transaction_date,
        description=description,
        lines=lines,
        created_by=created_by,
        company_id=company_id,
        reference=None
    )
    
    # Post the journal entry
    journal_entry.is_posted = True
    
    # Create transaction record
    transaction = Transaction(
        account_id=account_id,
        transaction_type=TransactionType(transaction_type),
        amount=amount,
        description=description,
        category_id=category_id,
        transaction_date=transaction_date,
        journal_entry_id=journal_entry.id,
        created_by=created_by
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    
    return transaction, journal_entry

