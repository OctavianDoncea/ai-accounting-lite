import json
import ollama
import asyncio
import time
from typing import Optional
from pydantic import BaseModel

class ReceiptData(BaseModel):
    merchant_name: Optional[str] = None
    transaction_date = Optional[str] = None
    total_amount: Optional[float] = None
    line_items: list = []
    category: Optional[str] = None

class OllamaParser:
    def __init__(self, model: str = 'llama3.2:3b'):
        self.model = model
        self._ensure_model_ready()

    def _ensure_model_ready(self):
        max_retries = 5

        for i in range(max_retries):
            try:
                models = ollama.list()
                model_names = [m.get('name', '') for m in models.get('models', [])]

                if any(self.model in name for name in model_names):
                    print(f'Model {self.model} is ready!')
                    return
                print(f'Pulling model {self.model}...')
                ollama.pull(self.model)
                return
            except Exception as e:
                if i < max_retries - 1:
                    wait = 2 ** i
                    print(f'Waiting for model {self.model} (attempt {i+1}/{max_retries})...')
                    time.sleep(wait)
                else:
                    print(f'Could not verify model {self.model}: {e}')

    async def parse(self, ocr_text: str) -> ReceiptData:
        try:
            return await asyncio.wait_for(asyncio.to_thread(self._parse_sync, ocr_text), timeout = 30.0)
        except asyncio.TimeoutError:
            print('Ollama parsing timed out')
            return ReceiptData(merchant_name='Timeout', total_amount=0.0)

    def _parse_sync(self, ocr_text: str) -> ReceiptData:
        prompt = f"""You are a receipt parser. Extract structured data from the text below.
Receipt text:
{ocr_text}

Return JSON with these field: merchant_name, transaction_date (YYYY-MM-DD), total_amount (number), line_items (list of objects with name, quantity, price), category (string). Only output JSON, nothing else."""

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