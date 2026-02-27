from pydantic import BaseModel, UUID4
from typing import Optional, Dict, Any
from datetime import datetime

class ReceiptResponse(BaseModel):
    id: UUID4
    filename: str
    file_path: Optional[str]
    status: str
    ocr_text: Optional[str]
    parsed_data: Optional[Dict[str, Any]]
    journal_entry_id: Optional[UUID4]
    error_message: Optional[str]
    created_at: datetime