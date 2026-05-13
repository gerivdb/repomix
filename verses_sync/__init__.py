"""VERSUS - Architecture Diamant pour l'organisation des verses."""
from .verses_sync import VersesSyncManager, LocalCache, RemoteRegistry, DependencyResolutionAPI

__version__ = "1.0.0"
__all__ = ["VersesSyncManager", "LocalCache", "RemoteRegistry", "DependencyResolutionAPI"]