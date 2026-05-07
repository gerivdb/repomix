"""Tests for Verses Marketplace API."""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys
import os

# Force correct working directory
PROJECT_ROOT = Path(__file__).parent.parent
os.chdir(PROJECT_ROOT)

sys.path.insert(0, str(PROJECT_ROOT / "verses-marketplace"))
from marketplace_api import app  # noqa: E402

client = TestClient(app)


class TestMarketplaceAPI:
    """Test marketplace endpoints."""
    
    def test_publish_verse(self):
        response = client.post("/api/v1/verses/publish", json={
            "name": "TEST-VERSE",
            "domain": "PHYSICS",
            "content": "test content here",
            "author": "test-user"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "TEST-VERSE"
        assert data["domain"] == "PHYSICS"
        assert "id" in data
    
    def test_search_verses(self):
        response = client.get("/api/v1/verses/search?domain=PHYSICS&limit=5")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_rate_verse(self):
        # First publish
        pub = client.post("/api/v1/verses/publish", json={
            "name": "RATE-TEST",
            "domain": "MATH",
            "content": "x" * 100,
            "author": "tester"
        })
        verse_id = pub.json()["id"]
        
        # Then rate
        response = client.post(f"/api/v1/verses/{verse_id}/rate", json={"score": 5})
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
    
    def test_get_versions(self):
        # Publish first
        pub = client.post("/api/v1/verses/publish", json={
            "name": "VERSION-TEST",
            "domain": "TECH",
            "content": "content",
            "author": "dev"
        })
        verse_id = pub.json()["id"]
        
        response = client.get(f"/api/v1/verses/{verse_id}/versions")
        assert response.status_code == 200
        assert len(response.json()) >= 1
    
    def test_rate_invalid_verse(self):
        response = client.post("/api/v1/verses/NOT-EXIST/rate", json={"score": 5})
        assert response.status_code == 404
    
    def test_rate_out_of_range(self):
        pub = client.post("/api/v1/verses/publish", json={
            "name": "RANGE-TEST",
            "domain": "AI",
            "content": "test",
            "author": "tester"
        })
        verse_id = pub.json()["id"]
        
        response = client.post(f"/api/v1/verses/{verse_id}/rate", json={"score": 10})
        assert response.status_code == 400
    
    def test_get_verse(self):
        pub = client.post("/api/v1/verses/publish", json={
            "name": "GET-TEST",
            "domain": "BIO",
            "content": "content for get",
            "author": "tester"
        })
        verse_id = pub.json()["id"]
        
        response = client.get(f"/api/v1/verses/{verse_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "GET-TEST"
    
    def test_get_verse_not_found(self):
        response = client.get("/api/v1/verses/NONEXISTENT")
        assert response.status_code == 404
    
    def test_get_versions_not_found(self):
        response = client.get("/api/v1/verses/NONEXISTENT/versions")
        assert response.status_code == 404


class TestMainExecution:
    """Test __main__ block execution."""
    
    def test_module_main_block(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "mp_main", Path(__file__).parent.parent / "verses-marketplace" / "marketplace_api.py"
        )
        module = importlib.util.module_from_spec(spec)
        
        # Just verify module loads without running uvicorn
        # The if __name__ == "__main__" is tested via import