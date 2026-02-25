from pydantic_settings import BaseSettings  # type: ignore[import]

class Settings(BaseSettings):
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_KEY: str

    DATABASE_URL: str

    REDIS_URL: str

    ENVIRONMENT: str = 'development'

    class Config:
        env_file = '.env'

settings = Settings()