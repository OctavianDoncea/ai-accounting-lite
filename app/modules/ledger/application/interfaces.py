from abc import ABC, abstractmethod
from ast import Pass

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
    def accounts(self): pass
    @property
    @abstractmethod
    def journal_entries(self): pass
    @property
    @abstractmethod
    def receipts(self): pass