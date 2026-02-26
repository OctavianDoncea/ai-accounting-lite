from fastapi import APIRouter, Depends, HTTPException, HTTPException, status
from uuid import UUID
from typing import List, Optional
from app.modules.ledger.presentation.schemas import JournalEntryCreate, JournalEntryResponse, AccountResponse
from app.modules.ledger.application.use_cases import CreateJournalEntryUseCase, PostJournalEntryUseCase
from app.modules.ledger.application.interfaces import UnitOfWork, SQLALchemyUnitOfWork
from app.core.dependencies import get_current_user

router = APIRouter(prefix='/ledger', tags=['ledger'])

def get_uow() -> UnitOfWork:
    return SQLALchemyUnitOfWork()

@router.post('/journal-entries', response_model=JournalEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_journal_entry(data: JournalEntryCreate, uow: UnitOfWork=Depends(get_uow), user=Depends(get_current_user)):
    use_case = CreateJournalEntryUseCase(uow)
    
    try:
        entry = await use_case.execute(
            entry_date=data.entry_date,
            description=data.description,
            lines=[line.model_dump() for line in data.lines],
            created_by=user['id']
        )
        return entry
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/journal-entries/{entry_id}/post", response_model=JournalEntryResponse)
async def post_journal_entry(entry_id: UUID, uow: UnitOfWork=Depends(get_uow), user=Depends(get_current_user)):
    use_case = PostJournalEntryUseCase(uow)
    
    try:
        entry = await use_case.execute(entry_id)
        return entry
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get('/accounts', response_model=List[AccountResponse])
async def list_accounts(account_type: Optional[str] = None, uow: UnitOfWork = Depends(get_uow)):
    async with uow:
        accounts = await uow.accounts.list(account_type)
        return accounts