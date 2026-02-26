import json
import ollama
import asyncio
from typing import Optional
from pydantic import BaseModel

class ReceiptData(BaseModel):
    merchant_name: Optional[str] = None
    transaction_date: Optional[str] = None
    total_amount: Optional[float] = None
    line_items: list = []
    category: Optional[str] = None

class OllamaParser:
    def __init__(self, model: str = 'llama3.2:3b'):
        self.model = model

    async def parse(self, ocr_text: str) -> ReceiptData:
        return await asyncio.to_thread(self._parse_sync, ocr_text)

    def parse_sync(self, ocr_text: str) -> ReceiptData:
        prompt = f"""You are a receipt parser. Extract structured data from the text below.
Receipt text:
{ocr_text}

Return JSON with these fields: merchant_name, transaction_date (YYYY-MM-DD), total_amount (number), line_items (list of objects with name, quantity, price), category (string). Only output JSON, nothing else"""

        try:
            response = ollama.chat(model=self.model, messages=[{'role': 'user', 'content': prompt}], options={'temperature': 0.1})
            content = response['message']['content']
            start = content.find('{')
            end = content.rfind('}') + 1

            if start != -1 and end > start:
                json_str = content[start:end]
                data = json.loads(json_str)
                return ReceiptData(**data)
            else:
                return ReceiptData(merchant_name='Unknown', total_amount=0.0)
        except Exception as e:
            print(f'Ollama parsing error: {e}')
            return ReceiptData(merchant_name='Error', total_amount=0.0)