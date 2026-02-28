from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Enum, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
from datetime import datetime, timezone

class AccountModel(Base):
    __tablename__ = 'accounts'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    type = Column(Enum('asset', 'liability', 'equity', 'revenue', 'expense', name='account_type', native_enum=False), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_domain(self):
        from app.modules.ledger.domain.entities import Account, AccountType
        return Account(
            id=self.id,
            code=self.code,
            name=self.name,
            type=AccountType(self.type),
            description=self.description,
            is_active=self.is_active,
            created_at=self.created_at,
            updated_at=self.updated_at
        )

    @classmethod
    def from_domain(cls, account):
        return cls(
            id=account.id,
            code=account.code,
            name=account.name,
            type=account.type.value,
            description=account.description,
            is_active=account.is_active,
            created_at=account.created_at,
            updated_at=account.updated_at
        )

class JournalEntryModel(Base):
    __tablename__ = 'journal_entries'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entry_number = Column(String(50), unique=True, nullable=False)
    entry_date = Column(DateTime, nullable=False)
    description = Column(Text)
    status = Column(Enum('draft', 'posted', 'void', name='entry_status', native_enum=False), default='draft')
    created_by = Column(String(100))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    posted_at = Column(DateTime, nullable=False)

    lines = relationship('JournalLineModel', back_populates='entry', cascade='all, delete-orphan')

    def to_domain(self):
        from app.modules.ledger.domain.entities import JournalEntry, JournalEntryStatus
        return JournalEntry(
            id=self.id,
            entry_number=self.entry_number,
            entry_date=self.entry_date,
            description=self.description,
            lines=[line.to_domain() for line in self.lines],
            status=JournalEntryStatus(self.status),
            created_by=self.created_by,
            created_at=self.created_at,
            posted_at=self.posted_at
        )

    @classmethod
    def from_domain(cls, entry):
        return cls(
            id=entry.id,
            entry_number=entry.entry_number,
            entry_date=entry.entry_date,
            description=entry.description,
            status=entry.status.value,
            created_by=entry.created_by,
            created_at=entry.created_at,
            posted_at=entry.posted_by
        )

class JournalLineModel(Base):
    __tablename__ = 'journal_lines'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entry_id = Column(UUID(as_uuid=True), ForeignKey('journal_entries.id'), nullable=False)
    account_id = Column(UUID(as_uuid=True), ForeignKey('accounts.id'), nullable=False)
    direction = Column(Enum('debit', 'credit', name='line_direction', native_enum=False), nullable=False)
    amount=Column(Numeric(12, 2), nullable=False)
    description = Column(Text)

    entry = relationship('JournalEntryModel', back_populates='lines')
    account = relationship('AccountModel')

    def to_domain(self):
        from app.modules.ledger.domain.entities import JournalLine
        return JournalLine(
            id=self.id,
            account_id=self.account_id,
            direction=self.direction,
            amount=self.amount,
            description=self.description
        )