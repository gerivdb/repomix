#!/usr/bin/env python3
"""VersesSyncManager - Intelligent synchronization of verses."""

import asyncio
import json
import hashlib
import time
from pathlib import Path
from typing import List, Dict, Optional, Set, Tuple
import heapq

# BLO Primitives Integration (Mock for demonstration)
class TritVerseSync:
    """Mock BLO primitive for verse synchronization."""
    async def sync_verse(self, verse_id: str, fetch_func) -> Dict:
        return await fetch_func(verse_id)

class TritReadWithVectorClock:
    """Mock BLO primitive for vector clock consistency."""
    async def verify_consistency(self, verse_id: str, data: Dict) -> bool:
        # Simple mock - always consistent for demo
        return True

class TritCompressDelta:
    """Mock BLO primitive for delta compression."""
    def compress_verse(self, verse: Dict) -> Dict:
        # Simple mock - return as-is for demo
        return verse


class LocalCache:
    """Local caching for verses with intelligent prediction."""

    def __init__(self, cache_dir: str = ".verses_cache", max_size_mb: int = 500):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.max_size_bytes = max_size_mb * 1024 * 1024

        # Cache metadata for LRU and prediction
        self.metadata_file = self.cache_dir / ".cache_metadata.json"
        self._load_metadata()

        # Prediction engine
        self.access_patterns = {}  # verse_id -> access frequency
        self.dependencies = {}     # verse_id -> set of dependent verses

    def _load_metadata(self):
        """Load cache metadata."""
        if self.metadata_file.exists():
            try:
                data = json.loads(self.metadata_file.read_text())
                self.access_patterns = data.get('access_patterns', {})
                self.dependencies = data.get('dependencies', {})
            except:
                self.access_patterns = {}
                self.dependencies = {}

    def _save_metadata(self):
        """Save cache metadata."""
        data = {
            'access_patterns': self.access_patterns,
            'dependencies': {k: list(v) for k, v in self.dependencies.items()}
        }
        self.metadata_file.write_text(json.dumps(data))

    def has(self, verse_id: str) -> bool:
        cache_file = self.cache_dir / f"{verse_id}.json"
        exists = cache_file.exists()
        if exists:
            # Update access patterns for prediction
            self.access_patterns[verse_id] = self.access_patterns.get(verse_id, 0) + 1
        return exists

    def get(self, verse_id: str) -> Optional[Dict]:
        cache_file = self.cache_dir / f"{verse_id}.json"
        if cache_file.exists():
            try:
                data = json.loads(cache_file.read_text())
                # Update access patterns
                self.access_patterns[verse_id] = self.access_patterns.get(verse_id, 0) + 1
                self._save_metadata()
                return data
            except:
                return None
        return None

    def store(self, verse_id: str, verse_data: Dict) -> None:
        # Check cache size before storing
        if self._get_cache_size() > self.max_size_bytes:
            self._evict_lru()

        cache_file = self.cache_dir / f"{verse_id}.json"
        cache_file.write_text(json.dumps(verse_data))

        # Initialize access pattern
        if verse_id not in self.access_patterns:
            self.access_patterns[verse_id] = 1

        self._save_metadata()

    def invalidate(self, verse_id: str) -> None:
        cache_file = self.cache_dir / f"{verse_id}.json"
        if cache_file.exists():
            cache_file.unlink()

        # Clean up metadata
        self.access_patterns.pop(verse_id, None)
        self.dependencies.pop(verse_id, None)
        self._save_metadata()

    def predict_access(self, current_verse: str, limit: int = 5) -> List[str]:
        """Predict which verses might be accessed next based on patterns."""
        if current_verse not in self.dependencies:
            return []

        candidates = list(self.dependencies[current_verse])
        # Sort by access frequency
        candidates.sort(key=lambda x: self.access_patterns.get(x, 0), reverse=True)
        return candidates[:limit]

    def prefetch(self, verse_ids: List[str]) -> None:
        """Prefetch verses into cache."""
        for verse_id in verse_ids:
            if not self.has(verse_id):
                # In real implementation, this would trigger async fetch
                pass

    def _get_cache_size(self) -> int:
        """Get total cache size in bytes."""
        total = 0
        for f in self.cache_dir.glob("*.json"):
            if f.name != ".cache_metadata.json":
                total += f.stat().st_size
        return total

    def _evict_lru(self) -> None:
        """Evict least recently used items."""
        # Simple LRU: remove items with lowest access count
        if not self.access_patterns:
            return

        # Find least accessed
        lru_verse = min(self.access_patterns, key=self.access_patterns.get)
        self.invalidate(lru_verse)


class DependencyResolver:
    """Resolve verse dependencies intelligently."""

    def __init__(self, versus_root: str):
        self.versus_root = Path(versus_root)
        self.dependency_graph = {}  # verse_id -> set of dependencies
        self.reverse_graph = {}    # verse_id -> set of dependents

    def load_dependencies_from_spokes(self):
        """Load dependency information from spoke manifests."""
        for spoke_dir in (self.versus_root / "spokes").iterdir():
            if spoke_dir.is_dir():
                manifest_file = spoke_dir / "manifest.json"
                if manifest_file.exists():
                    try:
                        manifest = json.loads(manifest_file.read_text())
                        spoke = manifest.get("spoke", "")
                        verses = manifest.get("verses", [])

                        # Create dependencies based on spoke relationships
                        for verse in verses:
                            verse_id = verse.get("id", "")
                            if verse_id:
                                # AI depends on MATH, PHYSICS depends on MATH, etc.
                                deps = self._infer_dependencies(verse_id, spoke)
                                self.dependency_graph[verse_id] = set(deps)
                                for dep in deps:
                                    if dep not in self.reverse_graph:
                                        self.reverse_graph[dep] = set()
                                    self.reverse_graph[dep].add(verse_id)
                    except:
                        continue

    def _infer_dependencies(self, verse_id: str, spoke: str) -> List[str]:
        """Infer dependencies based on verse ID and spoke."""
        deps = []

        # Cross-spoke dependencies
        if spoke == "AI":
            # AI depends on MATH for algorithms
            if "math" in verse_id.lower():
                deps.extend([f"MATH_{i}" for i in range(1, 4)])
        elif spoke == "PHYSICS":
            # PHYSICS depends on MATH for calculations
            if "quantum" in verse_id.lower() or "energy" in verse_id.lower():
                deps.extend([f"MATH_{i}" for i in range(1, 3)])
        elif spoke == "BIO":
            # BIO depends on CHEMISTRY and MATH
            if "protein" in verse_id.lower():
                deps.extend([f"CHEMISTRY_{i}" for i in range(1, 3)])
                deps.append("MATH_1")

        return deps

    def resolve_dependencies(self, verse_ids: List[str]) -> List[str]:
        """Resolve all dependencies for given verses."""
        resolved = set()
        to_resolve = set(verse_ids)

        while to_resolve:
            current = to_resolve.pop()
            if current not in resolved:
                resolved.add(current)
                # Add dependencies
                deps = self.dependency_graph.get(current, set())
                to_resolve.update(deps - resolved)

        return list(resolved)

    def get_dependents(self, verse_id: str) -> Set[str]:
        """Get all verses that depend on the given verse."""
        return self.reverse_graph.get(verse_id, set())


class RemoteRegistry:
    """Remote registry client with performance optimization."""

    def __init__(self, registry_url: str = "https://versus.local", timeout: float = 5.0):
        self.registry_url = registry_url
        self.timeout = timeout
        self.connection_pool = {}  # Simple connection caching

    async def fetch(self, verse_id: str) -> Dict:
        """Fetch verse from remote registry with <5s guarantee."""
        start_time = time.time()

        # Simulate optimized fetch (real implementation would use HTTP client)
        # Mock data for demonstration
        verse_data = {
            "id": verse_id,
            "content": f"verse_{verse_id}_data_optimized",
            "timestamp": time.time(),
            "size": len(verse_id) * 10,
            "dependencies": []  # Would be populated from real registry
        }

        # Ensure <5s response time
        fetch_time = time.time() - start_time
        if fetch_time > 5.0:
            raise TimeoutError(f"Fetch timeout: {fetch_time:.2f}s > 5.0s")

        return verse_data

    async def search(self, domain: str = None, limit: int = 20) -> List[Dict]:
        """Search verses by domain with optimized query."""
        # Mock optimized search
        results = []
        for i in range(min(limit, 20)):
            results.append({
                "id": f"VERSE-{domain or 'GENERAL'}-{i}",
                "domain": domain,
                "score": 1.0 - (i * 0.05)  # Decreasing relevance
            })
        return results

    async def get_dependencies(self, verse_id: str) -> List[str]:
        """Get dependency list for a verse."""
        # In real implementation, this would query the registry API
        return [f"DEP_{verse_id}_{i}" for i in range(3)]


class VersesSyncManager:
    """Main sync manager for intelligent verse synchronization with BLO TripleWrite."""

    def __init__(self, cache_dir: str = ".verses_cache", versus_root: str = None):
        self.cache = LocalCache(cache_dir)
        self.registry = RemoteRegistry()
        self.dependency_resolver = DependencyResolver(versus_root or ".")
        self.dependency_resolver.load_dependencies_from_spokes()

        # BLO Primitives initialization
        self.trit_sync = TritVerseSync()
        self.trit_read_vc = TritReadWithVectorClock()
        self.trit_compress = TritCompressDelta()

        # Performance tracking with BLO metrics
        self.performance_stats = {
            "lazy_load_times": [],
            "cache_hits": 0,
            "cache_misses": 0,
            "prefetch_hits": 0,
            "blo_operations": 0,
            "sync_conflicts": 0
        }

    async def sync_selective(self, verse_refs: List[str]) -> List[Dict]:
        """Sync only specified verses with BLO TripleWrite synchronization."""
        # Resolve dependencies using BLO-aware resolution
        all_verses = self.dependency_resolver.resolve_dependencies(verse_refs)

        results = []
        prefetch_tasks = []

        for verse_id in all_verses:
            # Use TritReadWithVectorClock for consistency checks
            cached_data = self.cache.get(verse_id)
            if cached_data:
                # Verify vector clock consistency
                is_consistent = await self.trit_read_vc.verify_consistency(verse_id, cached_data)
                if is_consistent:
                    self.performance_stats["cache_hits"] += 1
                    results.append(cached_data)

                    # Prefetch predicted dependencies using BLO compression
                    predicted = self.cache.predict_access(verse_id)
                    if predicted:
                        prefetch_tasks.append(self._prefetch_async(predicted))
                else:
                    # Inconsistency detected, force refresh
                    self.performance_stats["sync_conflicts"] += 1
                    await self._force_refresh_verse(verse_id)
                    results.append(self.cache.get(verse_id))
            else:
                self.performance_stats["cache_misses"] += 1
                # Lazy load with BLO TripleWrite guarantee
                verse = await self._lazy_load_with_triple_write(verse_id)
                results.append(verse)

        # Execute prefetch in background with BLO optimization
        if prefetch_tasks:
            asyncio.gather(*prefetch_tasks, return_exceptions=True)

        return results

    async def lazy_load(self, verse_id: str) -> Dict:
        """Load verse on demand with BLO TripleWrite guarantee."""
        return await self._lazy_load_with_triple_write(verse_id)

    async def _lazy_load_with_triple_write(self, verse_id: str) -> Dict:
        """Lazy load with BLO TripleWrite guarantee for consistency."""
        start_time = time.time()

        try:
            cached_data = self.cache.get(verse_id)
            if not cached_data:
                # Use TritVerseSync for optimized fetch
                verse = await asyncio.wait_for(
                    self.trit_sync.sync_verse(verse_id, self.registry.fetch),
                    timeout=5.0
                )

                # Apply TritCompressDelta for efficient storage
                compressed_verse = self.trit_compress.compress_verse(verse)
                self.cache.store(verse_id, compressed_verse)

                # Update dependencies with BLO-aware resolution
                deps = await self.registry.get_dependencies(verse_id)
                self.cache.dependencies[verse_id] = set(deps)

                # BLO operation tracking
                self.performance_stats["blo_operations"] += 1

                # Prefetch likely next accesses with BLO prediction
                predicted = self.cache.predict_access(verse_id)
                if predicted:
                    asyncio.create_task(self._prefetch_async(predicted))

            result = self.cache.get(verse_id)

            # Track performance with BLO metrics
            load_time = time.time() - start_time
            self.performance_stats["lazy_load_times"].append(load_time)

            if load_time > 5.0:
                raise TimeoutError(f"BLO lazy load timeout: {load_time:.2f}s > 5.0s")

            return result

        except asyncio.TimeoutError:
            raise TimeoutError(f"BLO lazy load timeout for verse {verse_id}")

    async def _force_refresh_verse(self, verse_id: str) -> None:
        """Force refresh verse using BLO TripleWrite conflict resolution."""
        # Invalidate cache
        self.cache.invalidate(verse_id)

        # Fetch fresh data with BLO sync
        verse = await self.trit_sync.sync_verse(verse_id, self.registry.fetch)

        # Store with compression
        compressed_verse = self.trit_compress.compress_verse(verse)
        self.cache.store(verse_id, compressed_verse)

        self.performance_stats["blo_operations"] += 1

    async def _prefetch_async(self, verse_ids: List[str]) -> None:
        """Prefetch verses asynchronously."""
        for verse_id in verse_ids:
            if not self.cache.has(verse_id):
                try:
                    verse = await asyncio.wait_for(
                        self.registry.fetch(verse_id),
                        timeout=2.0  # Shorter timeout for prefetch
                    )
                    self.cache.store(verse_id, verse)
                    self.performance_stats["prefetch_hits"] += 1
                except:
                    pass  # Prefetch failures don't block main operation
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics with BLO performance metrics."""
        files = list(self.cache.cache_dir.glob("*.json"))
        cache_size = sum(f.stat().st_size for f in files)

        # Calculate cache hit rate
        total_requests = self.performance_stats["cache_hits"] + self.performance_stats["cache_misses"]
        hit_rate = (self.performance_stats["cache_hits"] / total_requests * 100) if total_requests > 0 else 0

        return {
            "total_cached": len(files),
            "cache_size_bytes": cache_size,
            "cache_size_mb": cache_size / (1024 * 1024),
            "cache_hit_rate_percent": hit_rate,
            "blo_operations": self.performance_stats["blo_operations"],
            "sync_conflicts_resolved": self.performance_stats["sync_conflicts"],
            "average_lazy_load_time": sum(self.performance_stats["lazy_load_times"]) / len(self.performance_stats["lazy_load_times"]) if self.performance_stats["lazy_load_times"] else 0,
            "prefetch_effectiveness": self.performance_stats["prefetch_hits"] / max(1, self.performance_stats["cache_hits"])
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
            "lazy_load_under_5s": all(r["load_time"] < 5.0 for r in results),
            "blo_operations_count": self.performance_stats["blo_operations"],
            "cache_hit_rate": self.get_cache_stats()["cache_hit_rate_percent"]
        }


class DependencyResolutionAPI:
    """API for automatic dependency resolution across verses."""

    def __init__(self, dependency_resolver: DependencyResolver, sync_manager: VersesSyncManager):
        self.resolver = dependency_resolver
        self.sync_manager = sync_manager

    async def resolve_and_sync(self, verse_ids: List[str]) -> Dict:
        """Resolve dependencies and sync all required verses."""
        start_time = time.time()

        # Resolve full dependency tree
        all_deps = self.resolver.resolve_dependencies(verse_ids)

        # Sync with BLO optimization
        synced_verses = await self.sync_manager.sync_selective(all_deps)

        resolution_time = time.time() - start_time

        return {
            "requested_verses": verse_ids,
            "resolved_dependencies": all_deps,
            "synced_verses_count": len(synced_verses),
            "resolution_time": resolution_time,
            "cache_performance": self.sync_manager.get_cache_stats()
        }

    async def get_dependency_graph(self, verse_id: str) -> Dict:
        """Get complete dependency graph for a verse."""
        dependencies = self.resolver.resolve_dependencies([verse_id])
        dependents = self.resolver.get_dependents(verse_id)

        # Get sync status for all related verses
        graph_data = {
            "verse_id": verse_id,
            "direct_dependencies": list(self.resolver.dependency_graph.get(verse_id, set())),
            "all_dependencies": dependencies,
            "dependents": list(dependents),
            "sync_status": {}
        }

        # Check cache status for all verses in graph
        for vid in dependencies + list(dependents):
            graph_data["sync_status"][vid] = {
                "in_cache": self.sync_manager.cache.has(vid),
                "last_access": self.sync_manager.cache.access_patterns.get(vid, 0)
            }

        return graph_data

    async def optimize_dependency_loading(self, access_pattern: List[str]) -> Dict:
        """Optimize loading based on predicted access patterns."""
        # Analyze access pattern
        predictions = {}
        for verse_id in access_pattern:
            predictions[verse_id] = self.sync_manager.cache.predict_access(verse_id)

        # Prefetch high-probability dependencies
        prefetch_candidates = []
        for preds in predictions.values():
            prefetch_candidates.extend(preds[:3])  # Top 3 predictions

        # Remove duplicates and prefetch
        unique_candidates = list(set(prefetch_candidates))
        if unique_candidates:
            self.sync_manager.cache.prefetch(unique_candidates)

        return {
            "access_pattern_analyzed": access_pattern,
            "predictions_made": predictions,
            "prefetch_candidates": unique_candidates,
            "optimization_applied": len(unique_candidates) > 0
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
