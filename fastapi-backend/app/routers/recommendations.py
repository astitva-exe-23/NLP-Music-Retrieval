import logging, hashlib
from fastapi import APIRouter, HTTPException
from app.models.schemas import DiaryRequest, RecommendationResponse
from app.services.normalize import normalize_diary
from app.services import retrieve

router = APIRouter()
log = logging.getLogger("route")

def _hash(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:10]

@router.post("/recommendations", response_model=RecommendationResponse)
async def recommendations(req: DiaryRequest):

    if not retrieve.is_ready():
        raise HTTPException(status_code=503, detail="Service not ready")

    diary_hash = _hash(req.diary_text)
    log.info(f"[recommend] diary={diary_hash}")

    facets = await normalize_diary(req.diary_text)

    diary_clean = req.diary_text.strip()
    q_clean = facets.query_string.strip()

    keywords = ["song", "songs", "music", "playlist", "mood", "vibe"]
    echoed = (
        q_clean == diary_clean or
        len(q_clean) < 5 or
        not any(k in q_clean.lower() for k in keywords)
    )

    log.info(f"[normalize] echoed={echoed} q='{facets.query_string}'")

    # ✅ UI language overrides everything
    language = (
        req.filters.language.strip()
        if (req.filters and req.filters.language)
        else None
    )

    items = retrieve.search(facets.query_string, k=req.k, language=language)

    return RecommendationResponse(
        items=items,
        trace={
            "normalized_query": facets.query_string,
            "facets": facets.model_dump(),
            "user_language": language,
            "echoed": echoed
        },
    )

@router.get("/health")
async def health():
    return {"ready": retrieve.is_ready()}
