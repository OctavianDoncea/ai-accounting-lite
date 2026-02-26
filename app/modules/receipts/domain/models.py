from enum import Enum
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field

class ProcessingStatus(str, Enum):
    PENDING = 'pending'
    OCR_PROCESSING = 'ocr_processing'
    OCR_COMPLETED = 'ocr_completed'
    OCR_FAILED = 'ocr_failed'
    AI_PARSING = 'ai_parsing'
    PARSING_COMPLETED = 'parsing_completed'
    PARSING_FAILED = 'parsing_failed'
    JOURNAL_CREATION = 'journal_creation'
    JOURNAL_FAILED = 'journal_failed'
    COMPLETED = 'completed'
    PENDING_REVIEW = 'pending_review'

class Receipt(BaseModel):
    id: UUID
    filename: str
    file_path: Optional[str] = None
    file_hash: Optional[str] = None
    user_id: str
    status: ProcessingStatus
    ocr_text: Optional[str] = None
    parsed_data: Optional[Dict[str, Any]] = None
    journal_entry_id: Optional[UUID] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
