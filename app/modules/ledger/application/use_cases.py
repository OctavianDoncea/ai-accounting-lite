from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Dict, Any
from uuid import UUID, uuid4
from app.modules.ledger.domain.entities import JournalEntry, JournalLine, JournalEntryStatus
from app.modules.ledger.application.interfaces import UnitOfWork

class CreateJournalEntryUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def execute(self, entry_date: datetime, description: str, lines: List[Dict[str, Any]], created_by: str) -> JournalEntry:
        async with self.uow:
            journal_lines = [JournalLine(
                    account_id=UUID(line["account_id"]),
                    direction=line["direction"],
                    amount=Decimal(str(line["amount"])),
                    description=line.get("description")
                ) for line in lines]
            entry_number = f"JE-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid4().hex[:4].upper()}"
            entry = JournalEntry(entry_number=entry_number, entry_date=entry_date, description=description, lines=journal_lines, created_by=created_by)
            saved = await self.uow.journal_entries.save(entry)
            await self.uow.commit()

            return saved

class PostJournalEntryUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def execute(self, entry_id: UUID) -> JournalEntry:
        async with self.uow():
            entry = await self.uow.journal_entries.get(entry_id)
            if not entry:
                raise ValueError('Entry not found')
            if entry.status != JournalEntryStatus.DRAFT:
                raise ValueError('Only draft entries can be posted')
            entry.status = JournalEntryStatus.POSTED
            entry.posted_at = datetime.now(timezone.utc)

            await self.uow.journal_entries.save(entry)
            await self.uow.commit()

            return entry