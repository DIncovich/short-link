import os

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/shortener.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "P-54-HH-Y3PJSM5-3523DF")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

settings = Settings()
