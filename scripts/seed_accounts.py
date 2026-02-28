import asyncio 
import uuid
from sqlalchemy.ext.asyncio import create_async_engine
from app.modules.ledger.infrastructure.models import AccountModel
from app.core.config import settings

async def seed():
    engine = create_async_engine(settings.DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://'))

    async with engine.begin() as conn:
        accounts = [
            AccountModel(id=uuid.uuid4(), code='1000', name='Cash', type='asset'),
            AccountModel(id=uuid.uuid4(), code='2000', name='Accounts Payable', type='liability'),
            AccountModel(id=uuid.uuid4(), code='3000', name="Owner's Equity", type='equity'),
            AccountModel(id=uuid.uuid4(), code='4000', name='Revenue', type='revenue'),
            AccountModel(id=uuid.uuid4(), code='5000', name='Expenses', type='expense'),
        ]

        for acc in accounts:
            await conn.execute(AccountModel.__table__.insert().values(id=acc.id, code=acc.code, name=acc.name, type=acc.type))

    print('Seeded accounts!')

if __name__ == '__main__':
    asyncio.run(seed())