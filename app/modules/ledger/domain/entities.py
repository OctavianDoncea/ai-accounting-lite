from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, field_validator

class AccountType(str, Enum):
    ASSET = 'asset'
    LIABILITY = 'liability'
    EQUITY = 'equity'
    REVENUE = 'revenue'
    EXPENSE = 'expense'

class Account(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    code: str
    name: str
    type: AccountType
    description: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class JournalEntryStatus(str, Enum):
    DRAFT = 'draft'
    POSTED = 'posted'
    VOID = 'void'

class JournalLine(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    account_id: UUID
    direction: str
    amount: Decimal = Field(decimal_place=2, max_digits=12)
    description: Optional[str] = None

class JournalEntry(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    entry_number: str
    entry_date: datetime
    description: str
    lines: List[JournalLine]
    status: JournalEntryStatus = JournalEntryStatus.DRAFT
    created_by: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    posted_at: Optional[datetime] = None

    @field_validator('lines')
    def validate_double_entry(cls, lines):
        total_debits = sum(line.amount for line in lines if line.direction == 'debit')
        total_credits = sum(line.amount for line in lines if line.direction == 'credit')

        if total_debits != total_credits:
            raise ValueError(f'Debits ({total_debits}) must equal Credits ({total_credits})')
        if len(lines) < 2:
            raise ValueError('At least two lines required')

        return lines