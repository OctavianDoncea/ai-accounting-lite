from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.modules.ledger.domain.entities import Account, JournalEntry
from app.modules.ledger.infrastructure.models import AccountModel, JournalEntryModel

class AccountRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, account_id: UUID) -> Optional[Account]:
        result = await self.session.execute(select(AccountModel).where(AccountModel.id == account_id))
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def get_by_code(self, code: str) -> Optional[Account]:
        result = await self.session.execute(select(AccountModel).where(AccountModel.code == code))
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def list(self, account_type: Optional[str] = None) -> List[Account]:
        query = select(AccountModel)
        if account_type:
            query = query.where(AccountModel.type == account_type)
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [m.to_domain() for m in models]

    async def save(self, account: Account) -> Account:
        model = AccountModel.from_domain(account)
        self.session.add(model)
        await self.session.flush()
        return account

class JournalEntryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, entry_id: UUID) -> Optional[JournalEntry]:
        result = await self.session.execute(select(JournalEntryModel)
                .where(JournalEntryModel.id==entry_id)
                .options(selectinload(JournalEntryModel.lines))
        )
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def save(self, entry: JournalEntry) -> JournalEntry:
        model = JournalEntryModel.from_domain(entry)
        self.session.add(model)
        await self.session.flush()

        return entry