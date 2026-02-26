from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid

class ReceiptModel(Base):
    __tablename__ = 'receipts'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255))
    file_path = Column(Text)
    file_hash = Column(String(64))
    user_id = Column(String(100))
    status = Column(String(50), nullable=False)
    ocr_text = Column(Text)
    parsed_data = Column(JSON)
    journal_entry_id = Column(UUID(as_uuid=True), ForeignKey('journal_entries.id'), nullable=True)
    error_message = Column(Text)
    created_at = Column(DateTime)

    def to_domain(self):
        from app.modules.receipts.domain.models import Receipt, ProcessingStatus
        return Receipt(
            id=self.id,
            filename=self.filename,
            file_path=self.file_path,
            file_hash=self.file_hash,
            user_id=self.user_id,
            status=ProcessingStatus(self.status),
            ocr_text=self.ocr_text,
            parsed_data=self.parsed_data,
            journal_entry_id=self.journal_entry_id,
            error_message=self.error_message,
            created_at=self.created_at
        )