from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional
from app.modules.receipts.domain.models import Receipt
from app.modules.receipts.infrastructure.models import ReceiptModel

class ReceiptRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, receipt_id: UUID) -> Optional[Receipt]:
        result = await self.session.execute(select(ReceiptModel).where(ReceiptModel.id == receipt_id))
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def save(self, receipt: Receipt) -> Receipt:
        stmt = select(ReceiptModel).where(ReceiptModel.id == receipt.id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            model.filename = receipt.filename
            model.file_path = receipt.file_path
            model.file_hash = receipt.file_hash
            model.status = receipt.status.value
            model.ocr_text = receipt.ocr_text
            model.parsed_data = receipt.parsed_data
            model.journal_entry_id = receipt.journal_entry_id
            model.error_message = receipt.error_message
        else:
            model = ReceiptModel(
                id=receipt.id,
                filename = receipt.filename,
                file_path = receipt.file_path,
                file_hash = receipt.file_hash,
                user_id = receipt.user_id,
                status = receipt.status.value,
                ocr_text = receipt.ocr_text,
                parsed_data = receipt.parsed_data,
                journal_entry_id = receipt.journal_entry_id,
                error_message = receipt.error_message,
                created_at = receipt.created_at
            )
            self.session.add(model)
        await self.session.flush()

        return receipt
