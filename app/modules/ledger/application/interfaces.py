from abc import ABC, abstractmethod
from app.core.database import AsyncSessionLocal
from app.modules.ledger.infrastructure.repositories import AccountRepository, JournalEntryRepository
from app.modules.receipts.infrastructure.repositories import ReceiptRepository

class UnitOfWork(ABC):
    @abstractmethod
    async def __aenter__(self): pass
    @abstractmethod
    async def __aexit__(self): pass
    @abstractmethod
    async def commit(self): pass
    @abstractmethod
    async def rollback(self): pass

    @property
    @abstractmethod
    def accounts(self) -> AccountRepository: pass
    @property
    @abstractmethod
    def journal_entries(self) -> JournalEntryRepository: pass
    @property
    @abstractmethod
    def receipts(self) -> ReceiptRepository: pass

class SQLALchemyUnitOfWork(UnitOfWork):
    def __init__(self):
        self.session_factory = AsyncSessionLocal
        self.session = None

    async def __aenter__(self):
        self.session = self.session_factory()
        self.accounts = AccountRepository(self.session)
        self._journal_entries = JournalEntryRepository(self.session)
        self._receipts = ReceiptRepository(self.session)

        return self

    async def _aexit_(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()

    @property
    def accounts(self) -> AccountRepository:
        return self._accounts

    @property
    def journal_entries(self) -> JournalEntryRepository:
        return self._journal_entries

    @property
    def receipts(self) -> ReceiptRepository:
        return self._receipts