from pydantic import BaseModel
import os, json

class _Settings(BaseModel):
    mongo_uri: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    mongo_db: str = os.getenv("MONGO_DB", "coolcybergames")
    cors_allow_origins: list[str] = json.loads(os.getenv("CORS_ALLOW_ORIGINS", '["*"]'))
    # optional: simple shared secret for dev
    api_secret: str = os.getenv("API_SECRET", "devsecret")

settings = _Settings()
