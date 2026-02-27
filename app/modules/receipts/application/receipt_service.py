from datetime import datetime, timezone
from uuid import uuid4
import hashlib
from app.modules.receipts.domain.models import Receipt, ProcessingStatus
from app.modules.receipts.infrastructure.repositories import ReceiptRepository
from app.modules.receipts.infrastructure.ocr_service import OCRService
from app.modules.receipts.infrastructure.ai_parser import OllamaParser, ReceiptData
from app.modules.receipts.infrastructure.file_storage import SupabaseStorage
from app.modules.ledger.application.use_cases import CreateJournalEntryUseCase
from app.modules.ledger.application.interfaces import UnitOfWork, SQLAlchemyUnitOfWork

class ReceiptProcessingService:
    def __init__(self, uow_factory, receipt_repo, ocr_sevice: OCRService, ai_parser: OllamaParser, storage: SupabaseStorage):
        self.uow_factory = uow_factory
        self.receipt_repo = receipt_repo
        self.ocr = ocr_sevice
        self.parser = ai_parser
        self.storage = storage

    async def process_receipt(self, image_bytes: bytes, filename: str, user_id: str):
        receipt = Receipt(id=uuid4(), filename=filename, user_id=user_id, status=ProcessingStatus.PENDING)

        # Save initial receipt
        async with self.uow_factory() as uow:
            await self.receipt_repo.save(receipt)
            await uow.commit()

        # Upload file to Supabase
        try:
            file_hash = hashlib.sha256(image_bytes).hexdigest()
            file_path = f'receipts/{receipt.id}.jpg'
            public_url = await self.storage.save(image_bytes, file_path)
            receipt.file_path = public_url
            receipt.file_hash = file_hash
            receipt.status = ProcessingStatus.OCR_PROCESSING

            async with self.uow_factory() as uow:
                await self.receipt_repo.save(receipt)
                await uow.commit()
        except Exception as e:
            receipt.status = ProcessingStatus.OCR_FAILED
            receipt.error_message = str(e)
            
            async with self.uow_factory() as uow:
                await self.receipt_repo.save(receipt)
                await uow.commit()

            return receipt

        # OCR
        try:
            ocr_text = await self.ocr.extract_text(image_bytes)
            receipt.ocr_text = ocr_text
            receipt.status = ProcessingStatus.OCR_COMPLETED

            async with self.uow_factory() as uow:
                await self.receipt_repo.save(receipt)
                await uow.commit()
        except Exception as e:
            receipt.status = ProcessingStatus.OCR_FAILED
            receipt.error_message = str(e)

            async with self.uow_factory() as uow:
                await self.receipt_repo.save(receipt)
                await uow.commit()

            return receipt

        # AI Parsing
        try:
            receipt.status = ProcessingStatus.AI_PARSING

            async with self.uow_factory() as uow:
                await self.receipt_repo.save(receipt)
                await uow.commit()
            
            parsed: ReceiptData = await self.parser.parse(ocr_text)
            receipt.parsed_data = parsed.model_dump()
            receipt.status = ProcessingStatus.PARSING_COMPLETED

            async with self.uow_factory() as uow:
                await self.receipt_repo.save(receipt)
                await uow.commit()
        except Exception as e:
            receipt.status = ProcessingStatus.PARSING_FAILED
            receipt.error_message = str(e)

            async with self.uow_factory() as uow:
                await self.receipt_repo.save(receipt)
                await uow.commit()

            return receipt

        # Create journal entry
        try:
            async with self.uow_factory() as uow:
                expense_acc = await uow.accounts.get_by_code('5000') # expense account code
                cash_acc = await uow.accounts.get_by_code('1000') # cash account code

                if not expense_acc or not cash_acc:
                    raise ValueError('Required accounts not found. Run seed script.')
                lines = [
                    {
                        'acccount_id': str(expense_acc.id),
                        'direction': 'debit',
                        'amount': parsed.total_amount
                    },
                    {
                        'account_id': str(cash_acc.id),
                        'direction': 'credit',
                        'amount': parsed.total_amount
                    }
                ]
                create_uc = CreateJournalEntryUseCase(uow)
                entry = await create_uc.execute(
                    entry_date = datetime.strptime(parsed.transaction_date, '%Y-%m-%d') if parsed.transaction_date else datetime.now(timezone.utc),
                    description = f'Receipt: {parsed.merchant_name}',
                    lines = lines,
                    created_by = user_id
                )
                receipt.journal_entry_id = entry.id
                receipt.status = ProcessingStatus.COMPLETED if self._should_auto_post(parsed) else ProcessingStatus.PENDING_REVIEW
                await self.receipt_repo.save(receipt)
                await uow.commit()
        except Exception as e:
            receipt.status = ProcessingStatus.JOURNAL_FAILED
            receipt.error_message = str(e)

            async with self.uow_factory() as uow:
                await self.receipt_repo.save(receipt)
                await uow.commit()
        
        return receipt

    def _should_auto_post(self, parsed: ReceiptData) -> bool:
        return parsed.total_amount is not None and parsed.total_amount < 1000