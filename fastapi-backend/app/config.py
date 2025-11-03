from pydantic import BaseModel
import os

class Settings(BaseModel):
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    encoder_name: str = os.getenv("ENCODER_NAME", "sentence-transformers/all-MiniLM-L6-v2")
    artifacts_dir: str = os.getenv("ARTIFACTS_DIR", "data/artifacts")
    topk_default: int = int(os.getenv("TOPK_DEFAULT", "10"))
    request_timeout_s: float = float(os.getenv("REQUEST_TIMEOUT_S", "8"))
    enable_normalize: bool = os.getenv("ENABLE_NORMALIZE", "true").lower() == "true"

settings = Settings()
