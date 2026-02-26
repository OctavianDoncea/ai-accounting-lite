import io
import numpy as np
from PIL import Image
from paddleocr import PaddleOCR
import asyncio

class OCRService:
    def __init__(self):
        self.ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)

    async def extract_text(self, image_bytes: bytes) -> str:
        return await asyncio.to_thread(self._extract_sync, image_bytes)

    def _extract_sync(self, image_bytes: bytes) -> str:
        image = Image.open(io.BytesIO(image_bytes))
        image_np = np.array(image)
        result = self.ocr.predict(image_np, cls=True)

        if not result or not result[0]:
            return ''

        lines = [line[1][0] for line in result[0]]
        return '/n'.join(lines)