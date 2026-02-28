from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.modules.ledger.presentation.routers import router as ledger_router
from app.modules.receipts.presentation.routers import router as receipts_router

app = FastAPI(title="AI-Native Accounting Lite")

app.add_middleware(
    CORSMiddleware,
    allow_origins = ['*'],
    allow_credentials = True,
    allow_methods = ['*'],
    allow_headers = ['*'],
)

app.include_router(ledger_router, prefix='/api/v1')
app.include_router(receipts_router, prefix='/api/v1')

@app.get('/')
async def root():
    return {
        'message': 'AI-Native Accounting API',
        'docs': '/docs'
    }

@app.get('/health')
async def health():
    return {'status': 'healthy'}