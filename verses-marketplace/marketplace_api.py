#!/usr/bin/env python3
"""Verses Marketplace API Server."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid
import time

app = FastAPI(title="Verses Marketplace API", version="1.0.0")

# Storage (would be database in production)
verses_db = {}


class VersePublish(BaseModel):
    name: str
    domain: str
    content: str
    author: str


class VerseResponse(BaseModel):
    id: str
    name: str
    domain: str
    qualityScore: float
    downloads: int
    rating: float
    author: str
    created_at: float


@app.post("/api/v1/verses/publish", response_model=VerseResponse)
async def publish_verse(verse: VersePublish):
    """Publish a new verse to the marketplace."""
    verse_id = f"VERSE-{uuid.uuid4().hex[:8].upper()}"
    
    # Mock quality score calculation
    quality_score = min(100, len(verse.content) / 10 + 50)
    
    verse_data = VerseResponse(
        id=verse_id,
        name=verse.name,
        domain=verse.domain,
        qualityScore=quality_score,
        downloads=0,
        rating=0.0,
        author=verse.author,
        created_at=time.time()
    )
    
    verses_db[verse_id] = verse_data.model_dump()
    return verse_data


@app.get("/api/v1/verses/search", response_model=List[VerseResponse])
async def search_verses(domain: Optional[str] = None, limit: int = 20):
    """Search verses by domain."""
    results = list(verses_db.values())
    if domain:
        results = [v for v in results if v["domain"] == domain]
    return results[:limit]


@app.get("/api/v1/verses/{verse_id}", response_model=VerseResponse)
async def get_verse(verse_id: str):
    """Get verse details."""
    if verse_id not in verses_db:
        raise HTTPException(status_code=404, detail="Verse not found")
    return verses_db[verse_id]


class VerseRate(BaseModel):
    score: int


@app.post("/api/v1/verses/{verse_id}/rate")
async def rate_verse(verse_id: str, payload: VerseRate):
    """Rate a verse (1-5)."""
    score = payload.score
    if verse_id not in verses_db:
        raise HTTPException(status_code=404, detail="Verse not found")
    if not 1 <= score <= 5:
        raise HTTPException(status_code=400, detail="Score must be 1-5")
    
    verse = verses_db[verse_id]
    # Simple average calculation
    new_rating = (verse["rating"] * verse["downloads"] + score) / (verse["downloads"] + 1)
    verse["rating"] = round(new_rating, 1)
    verse["downloads"] += 1
    
    return {"status": "ok", "new_rating": verse["rating"]}


@app.get("/api/v1/verses/{verse_id}/versions")
async def get_versions(verse_id: str):
    """Get verse versions."""
    if verse_id not in verses_db:
        raise HTTPException(status_code=404, detail="Verse not found")
    return [{"version": "1.0.0", "created_at": verses_db[verse_id]["created_at"]}]


if __name__ == "__main__":  # pragma: no cover
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)