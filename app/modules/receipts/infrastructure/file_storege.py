import asyncio
from supabase import create_client, Client
from app.core.config import settings

class SupabaseStorage:
    def __init__(self):
        self.client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
        self.bucket = 'receipts'

    async def save(self, file_bytes: bytes, file_path: str) -> str:
        return await asyncio.to_thread(self._save_sync, file_bytes, file_path)

    def _save_sync(self, file_bytes: bytes, file_path: str) -> str:
        self.client.storage.from_(self.bucket).upload(path=file_path, file=file_bytes, file_options={'content-type': 'image/jpeg'})
        public_url = self.client.storage.from_(self.bucket).get_public_url(file_path)

        return public_url