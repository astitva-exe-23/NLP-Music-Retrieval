from app.adapters.gemini import normalize_with_gemini
from app.models.schemas import Facets

async def normalize_diary(diary_text: str) -> Facets:
    try:
        rewritten = await normalize_with_gemini(diary_text)
        if not rewritten:
            rewritten = diary_text[:200]
        return Facets(
            mood=None,
            topics=[],
            energy="med",
            language_pref=None,
            era=None,
            query_string=rewritten.strip()
        )
    except Exception:
        return Facets(
            mood=None,
            topics=[],
            energy="med",
            language_pref=None,
            era=None,
            query_string=diary_text.strip()[:280]
        )
