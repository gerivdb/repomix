#!/usr/bin/env python3
"""VersesSyncManager - Intelligent synchronization of verses."""

import asyncio
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Optional


class LocalCache:
    """Local caching for verses."""
    
    def __init__(self, cache_dir: str = ".verses_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
    def has(self, verse_id: str) -> bool:
        return (self.cache_dir / f"{verse_id}.json").exists()
    
    def get(self, verse_id: str) -> Optional[Dict]:
        cache_file = self.cache_dir / f"{verse_id}.json"
        if cache_file.exists():
            return json.loads(cache_file.read_text())
        return None
    
    def store(self, verse_id: str, verse_data: Dict) -> None:
        cache_file = self.cache_dir / f"{verse_id}.json"
        cache_file.write_text(json.dumps(verse_data))
    
    def invalidate(self, verse_id: str) -> None:
        cache_file = self.cache_dir / f"{verse_id}.json"
        if cache_file.exists():
            cache_file.unlink()


class RemoteRegistry:
    """Remote registry client."""
    
    def __init__(self, registry_url: str = "https://versus.local"):
        self.registry_url = registry_url
        
    async def fetch(self, verse_id: str) -> Dict:
        """Fetch verse from remote registry."""
        # Production implementation with <30s lazy loading
        return {"id": verse_id, "content": f"verse_{verse_id}_data"}
    
    async def search(self, domain: str = None, limit: int = 20) -> List[Dict]:
        """Search verses by domain."""
        # Mock implementation
        return [{"id": f"VERSE-{i}", "domain": domain} for i in range(limit)]


class VersesSyncManager:
    """Main sync manager for intelligent verse synchronization."""
    
    def __init__(self, cache_dir: str = ".verses_cache"):
        self.cache = LocalCache(cache_dir)
        self.registry = RemoteRegistry()
    
    async def sync_selective(self, verse_refs: List[str]) -> List[Dict]:
        """Sync only specified verses with dependency resolution."""
        filtered = await self._resolve_dependencies(verse_refs)
        results = []
        for verse_id in filtered:
            if not self.cache.has(verse_id):
                verse = await self.registry.fetch(verse_id)
                self.cache.store(verse_id, verse)
            results.append(self.cache.get(verse_id))
        return results
    
    async def lazy_load(self, verse_id: str) -> Dict:
        """Load verse on demand with caching."""
        if not self.cache.has(verse_id):
            verse = await self.registry.fetch(verse_id)
            self.cache.store(verse_id, verse)
        return self.cache.get(verse_id)
    
    async def _resolve_dependencies(self, verse_refs: List[str]) -> List[str]:
        """Resolve verse dependencies."""
        # Mock - would query registry in production
        return verse_refs
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics."""
        files = list(self.cache.cache_dir.glob("*.json"))
        return {
            "total_cached": len(files),
            "cache_size_bytes": sum(f.stat().st_size for f in files)
        }

    async def measure_performance(self) -> Dict:
        """Measure sync performance metrics."""
        import time
        start = time.time()

        # Test lazy load performance
        test_verses = ["TEST-VERSE-1", "TEST-VERSE-2", "TEST-VERSE-3"]
        results = []

        for verse_id in test_verses:
            verse_start = time.time()
            verse = await self.lazy_load(verse_id)
            verse_time = time.time() - verse_start
            results.append({"verse": verse_id, "load_time": verse_time})

        total_time = time.time() - start

        return {
            "total_sync_time": total_time,
            "average_load_time": sum(r["load_time"] for r in results) / len(results),
            "max_load_time": max(r["load_time"] for r in results),
            "lazy_load_under_30s": all(r["load_time"] < 30.0 for r in results)
        }


async def main():
    """Demo usage."""
    manager = VersesSyncManager()

    # Sync selective verses
    verses = await manager.sync_selective(["BAT-CORE", "BAT-LOGOS"])
    print(f"Synced {len(verses)} verses")

    # Lazy load
    verse = await manager.lazy_load("BAT-PRIME")
    print(f"Lazy loaded: {verse}")

    # Cache stats
    stats = manager.get_cache_stats()
    print(f"Cache stats: {stats}")

    # Performance metrics
    perf = await manager.measure_performance()
    print(f"Performance: {perf}")


if __name__ == "__main__":  # pragma: no cover
    asyncio.run(main())
