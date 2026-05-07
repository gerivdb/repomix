"""Tests for VersesSyncManager - 100% coverage."""

import pytest
import asyncio
from pathlib import Path

# Import through __init__ to cover the __init__.py file
from verses_sync import VersesSyncManager, LocalCache, RemoteRegistry  # noqa: F401


class TestLocalCacheFull:
    """Full test coverage for LocalCache."""
    
    def test_get_returns_none_for_missing(self, tmp_path):
        cache = LocalCache(str(tmp_path / "cache"))
        assert cache.get("MISSING") is None
    
    def test_store_and_get(self, tmp_path):
        cache = LocalCache(str(tmp_path / "cache"))
        cache.store("TEST-ID", {"data": "value"})
        assert cache.has("TEST-ID") is True
        result = cache.get("TEST-ID")
        assert result == {"data": "value"}
    
    def test_invalidate(self, tmp_path):
        cache = LocalCache(str(tmp_path / "cache"))
        cache.store("TEST-ID", {"data": "value"})
        cache.invalidate("TEST-ID")
        assert cache.has("TEST-ID") is False
    
    def test_invalidate_nonexistent(self, tmp_path):
        cache = LocalCache(str(tmp_path / "cache"))
        cache.invalidate("NONEXISTENT")  # Should not raise


class TestRemoteRegistry:
    """Test RemoteRegistry."""
    
    @pytest.mark.asyncio
    async def test_fetch(self):
        registry = RemoteRegistry()
        result = await registry.fetch("BAT-CORE")
        assert result["id"] == "BAT-CORE"
        assert "content" in result
    
    @pytest.mark.asyncio
    async def test_search(self):
        registry = RemoteRegistry()
        results = await registry.search("PHYSICS", limit=3)
        assert len(results) == 3
        assert all(r["domain"] == "PHYSICS" for r in results)


class TestVersesSyncManagerFull:
    """Full test coverage for VersesSyncManager."""
    
    @pytest.mark.asyncio
    async def test_lazy_load_caches_verse(self, tmp_path):
        manager = VersesSyncManager(str(tmp_path / "cache"))
        verse = await manager.lazy_load("BAT-CORE")
        assert verse["id"] == "BAT-CORE"
        assert manager.cache.has("BAT-CORE")
    
    @pytest.mark.asyncio
    async def test_get_cache_stats(self, tmp_path):
        manager = VersesSyncManager(str(tmp_path / "cache"))
        await manager.lazy_load("BAT-CORE")
        stats = manager.get_cache_stats()
        assert stats["total_cached"] >= 1
    
    @pytest.mark.asyncio
    async def test_sync_selective(self, tmp_path):
        manager = VersesSyncManager(str(tmp_path / "cache"))
        results = await manager.sync_selective(["BAT-CORE", "BAT-LOGOS"])
        assert len(results) == 2
        assert results[0]["id"] == "BAT-CORE"
    
    @pytest.mark.asyncio
    async def test_sync_selective_cached(self, tmp_path):
        manager = VersesSyncManager(str(tmp_path / "cache"))
        await manager.sync_selective(["BAT-CORE"])
        results = await manager.sync_selective(["BAT-CORE"])
        assert len(results) == 1


class TestMainFunction:
    """Test main() execution."""
    
    @pytest.mark.asyncio
    async def test_main(self, tmp_path):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "vs", Path(__file__).parent.parent / "verses_sync" / "verses_sync.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Run main in temp dir
        import os
        os.chdir(tmp_path)
        await module.main()