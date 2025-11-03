import json
import os
import numpy as np
from typing import List, Tuple, Optional
from sentence_transformers import SentenceTransformer
from app.config import settings
from app.models.schemas import Track

_embeddings: Optional[np.ndarray] = None
_norm_embeddings: Optional[np.ndarray] = None
_songs: Optional[list] = None
_encoder: Optional[SentenceTransformer] = None
_ready: bool = False

def _l2_normalize(mat: np.ndarray, axis: int = 1, eps: float = 1e-12) -> np.ndarray:
    denom = np.linalg.norm(mat, axis=axis, keepdims=True)
    denom = np.maximum(denom, eps)
    return mat / denom

def load_artifacts() -> Tuple[int, int]:
    global _embeddings, _norm_embeddings, _songs, _encoder, _ready
    art = settings.artifacts_dir
    emb_path = os.path.join(art, "embeddings.npy")
    songs_path = os.path.join(art, "songs.json")
    if not os.path.exists(emb_path) or not os.path.exists(songs_path):
        raise FileNotFoundError("embeddings.npy or songs.json missing")

    _embeddings = np.load(emb_path).astype(np.float32)
    _norm_embeddings = _l2_normalize(_embeddings, axis=1)

    with open(songs_path, "r", encoding="utf-8") as f:
        _songs = json.load(f)

    _encoder = SentenceTransformer(settings.encoder_name)
    _ready = True
    return _embeddings.shape[0], _embeddings.shape[1]

def is_ready() -> bool:
    return _ready and _embeddings is not None and _songs is not None and _encoder is not None

def _apply_filters(idx_list: List[int], language: Optional[str]) -> List[int]:
    if language is None:
        return idx_list
    lang = language.lower()
    out = []
    for i in idx_list:
        rec = _songs[i]
        song_lang = (rec.get("Language") or rec.get("language") or "").lower()
        if song_lang.startswith(lang):
            out.append(i)
    return out

def search(normalized_query: str, k: int = 10, language: Optional[str] = None) -> List[Track]:
    assert is_ready(), "Artifacts not loaded"

    qv = _encoder.encode([normalized_query], normalize_embeddings=True).astype(np.float32)[0]
    sims = _norm_embeddings @ qv

    all_idx = list(range(len(_songs)))

    # ✅ language filter FIRST
    lang_idx = _apply_filters(all_idx, language)

    # if no songs in selected language → fallback gracefully
    if not lang_idx:
        lang_idx = all_idx

    # score only allowed songs
    scored = [(i, sims[i]) for i in lang_idx]
    scored.sort(key=lambda x: x[1], reverse=True)

    top_idx = [i for i, _ in scored[:k]]

    items: List[Track] = []
    for i in top_idx:
        rec = _songs[i]
        items.append(Track(
            id=str(rec.get("Id") or rec.get("id") or i),
            title=str(rec.get("Song") or rec.get("title") or "Unknown"),
            artist=str(rec.get("Artist") or rec.get("artist") or "Unknown"),
            language=(rec.get("Language") or rec.get("language")),
            score=float(sims[i]),
        ))
    return items
