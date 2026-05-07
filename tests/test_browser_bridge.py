#!/usr/bin/env python3
"""Test Browser Bridge - Validation CDP/Playwright"""

import asyncio
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from managers.browser_bridge import BrowserBridge, BridgeMode, BridgeResult
from managers.cdp_capabilities import CDPMode

class TestBrowserBridge:
    """Tests pour BrowserBridge"""
    
    @pytest.fixture
    async def bridge(self):
        """Fixturebridge"""
        b = BrowserBridge()
        yield b
        await b.close()
    
    @pytest.mark.asyncio
    async def test_init_normal_mode(self, bridge):
        """Test init en mode NORMAL"""
        result = await bridge.init()
        assert result is True
        assert bridge._ready is True
        assert bridge._mode in [BridgeMode.NORMAL, BridgeMode.DEGRADED]
    
    @pytest.mark.asyncio
    async def test_open_url(self, bridge):
        """Test ouverture URL"""
        await bridge.init()
        
        # Ouvrir arXiv
        result = await bridge.open_url("https://arxiv.org/abs/1706.03762")
        
        # Vérifications
        assert result is not None
        assert result.url == "https://arxiv.org/abs/1706.03762"
        assert result.status > 0
    
    @pytest.mark.asyncio
    async def test_list_pages(self, bridge):
        """Test liste pages"""
        await bridge.init()
        
        # Ouvrir une page
        await bridge.open_url("https://arxiv.org/abs/1706.03762")
        
        # Lister
        pages = await bridge.list_pages()
        
        assert len(pages) > 0
        assert all(isinstance(p, BridgeResult) for p in pages)
    
    @pytest.mark.asyncio
    async def test_close(self, bridge):
        """Test fermeture"""
        await bridge.init()
        await bridge.close()
        
        assert bridge._ready is False

if __name__ == "__main__":
    asyncio.run(pytest.main([__file__, "-v"]))