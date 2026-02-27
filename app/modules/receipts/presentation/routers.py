from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from uuid import UUID, uuid4
from datetime import datetime
from app.modules.receipts.presentation.schemas import ReceiptResponse
from app.modules.receipts.application.receipt_service import ReceiptProcessingService
from app.modules.receipts.infrastructure.ocr_service import OCRService
from app.modules.receipts.infrastructure.ai_parser import OllamaParser
from app.modules.receipts.infrastructure.file_storage import SupabaseStorage
from app.modules.receipts.infrastructure.repositories import ReceiptRepository
from app.modules.ledger.application.interfaces import SQLALchemyUnitOfWork, SQLAlchemyUnitOfWork
from app.core.dependencies import get_current_user

router = APIRouter(prefix='/receipts', tags=['receipts'])

def get_receipt_service():
    uow_factory = SQLAlchemyUnitOfWork
    receipt_repo = ReceiptRepository
    ocr = OCRService()
    parser = OllamaParser()
    storage = SupabaseStorage()

    return ReceiptProcessingService(uow_factory=SQLALchemyUnitOfWork, receipt_repo=ReceiptRepository, ocr_service=ocr, ai_parser=parser, storage=storage)

@router.post('/upload', response_model=ReceiptResponse)
async def upload_receipt(background_tasks: BackgroundTasks, file: UploadFile=File(...), service: ReceiptProcessingService=Depends(get_receipt_service), user=Depends(get_current_user)):
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail='File must be an image')
    
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail='File too large (max 10MB)')

    background_tasks.add_task(service.process_receipt, content, file.filename, user['id'])
    return {'message': 'Receipt upload accepted, processing in background', 'filename': file.filename}

@router.post('/upload-and-process', response_model=ReceiptResponse)
async def upload_and_process(file: UploadFile = File(...), service: ReceiptProcessingService=Depends(get_receipt_service), user=Depends(get_current_user)):
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail='File must be an image')
    
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail='File too large (10MB)')

    receipt = await service.process_receipt(content, file.filename, user['id'])
    return ReceiptResponse(id=receipt.id, filename=receipt.filename, file_path=receipt.file_path, status=receipt.status.value, ocr_text=receipt.ocr_text,
parsed_data=receipt.parsed_data, journal_entry_id=receipt.journal_entry_id, error_message=receipt.error_message, created_at=receipt.created_at)

@router.get('/{receipt_id}', response_model=ReceiptResponse)
async def get_receipt(receipt_id: UUID, service: ReceiptProcessingService = Depends(get_receipt_service), user = Depends(get_current_user)):
    async with SQLALchemyUnitOfWork() as uow:
        repo = ReceiptRepository(uow.session)
        receipt = await repo.get(receipt_id)

    if not receipt:
        raise HTTPException(status_code=404, detail='Receipt not found')
    if receipt.user_id != user['id']:
        raise HTTPException(status_code=403, detail='Not authorized')
    
    return ReceiptResponse(id=receipt.id, filename=receipt.filename, file_path=receipt.file_path, status=receipt.status.value,
ocr_text=receipt.ocr_text, parsed_data=receipt.parsed_data, journal_entry_id=receipt.journal_entry_id, error_message=receipt.error_message,
created_at=receipt.created_at)