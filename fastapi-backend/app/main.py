# app/main.py
import logging, sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # ✅ add this
from app.routers.recommendations import router as rec_router
from app.services.retrieve import load_artifacts
from dotenv import load_dotenv

def setup_logging():
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    root = logging.getLogger()
    root.handlers = [h]
    root.setLevel(logging.INFO)
    logging.getLogger("httpx").setLevel(logging.DEBUG)

def create_app() -> FastAPI:
    load_dotenv()
    setup_logging()
    app = FastAPI(title="Diary-to-Music API", version="0.1.0")

    # ✅ CORS so Vite frontend can talk to FastAPI backend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # or ["http://localhost:5173"]
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(rec_router)

    @app.on_event("startup")
    async def _startup():
        try:
            n, d = load_artifacts()
            logging.getLogger("startup").info(f"embeddings ready: {n} x {d}")
        except Exception as e:
            logging.getLogger("startup").error(f"artifacts load failed: {e}")

    return app

app = create_app()
