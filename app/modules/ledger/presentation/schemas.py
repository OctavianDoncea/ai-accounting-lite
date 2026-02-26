from pydantic import BaseModel, UUID4, Field
from datetime import datetime
from typing import List, Optional

class AccountResponse(BaseModel):
    id: UUID4
    code: str
    name: str
    type: str
    description: Optional[str] = None
    is_active: bool

class JournalLineCreate(BaseModel):
    account_id: UUID4
    direction: str
    amount: float
    description: Optional[str] = None

class JournalEntryCreate(BaseModel):
    entry_date: datetime
    description: str
    lines: List[JournalLineCreate]

class JournalLineResponse(BaseModel):
    id: UUID4
    account_id: UUID4
    direction: str
    amount: float
    description: Optional[str] = None

class JournalEntryResponse(BaseModel):
    id: UUID4
    entry_number: str
    entry_date: datetime
    description: str
    status: str
    lines: List[JournalLineResponse]
    created_by: Optional[str]
    created_at: datetime
    posted_at: Optional[datetime] = None