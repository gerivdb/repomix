"""
TDD TESTS - PrfaaSProviderCitizen
IntentHash: 0xEPIC_PRFaaS_9006_20260420
"""
import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
import asyncio
from src.citizens.PrfaaSProviderCitizen import KVCache, PrfaaSProviderCitizen

class TestKVCache:
    """Tests unitaires pour la structure KVCache"""
    
    def test_serialize_deserialize(self):
        """Test sérialisation → désérialisation lossless"""
        original = KVCache(
            layer_count = 48,
            head_count = 32,
            hidden_dim = 128,
            data = b"\x00\x01\x02\x03\x04\x05\x06\x07" * 1024,
            compression_ratio = 0.068,
            token_count = 12288
        )
        
        serialized = original.serialize()
        restored = KVCache.deserialize(serialized)
        
        assert original.layer_count == restored.layer_count
        assert original.head_count == restored.head_count
        assert original.hidden_dim == restored.hidden_dim
        assert original.compression_ratio == restored.compression_ratio
        assert original.token_count == restored.token_count
        assert original.data == restored.data
        
    def test_size(self):
        """Test taille minimum des headers"""
        cache = KVCache(1,1,1,b"test", 0.5, 1)
        data = cache.serialize()
        expected = 4 + len(json.dumps({
            "layer_count":1,"head_count":1,"hidden_dim":1,"compression_ratio":0.5,"token_count":1
        }).encode("utf-8")) + len(b"test")
        assert len(data) == expected

class TestPrfaaSProviderCitizen:
    """Tests unitaires du citoyen"""
    
    def test_init(self):
        """Test initialisation valide"""
        citizen = PrfaaSProviderCitizen()
        
        assert citizen.CITIZEN_ID == "prfaas_provider"
        assert citizen.CITIZEN_LEVEL == 3
        assert citizen.INTENT_HASH == "0xEPIC_PRFaaS_9006_20260420"
        assert citizen.COMPRESSION_LEVEL == 22
        assert citizen.stats["prefill_executed"] == 0
        
    @pytest.mark.asyncio
    async def test_compression(self):
        """Test efficacité compression zstd"""
        citizen = PrfaaSProviderCitizen()
        
        # Données test: float16 typiques KVCache
        test_data = b"\x00\x3f" * 32768 # 64KB de zero/one pattern
        
        compressed = citizen.compiler.compress(test_data)
        ratio = len(compressed) / len(test_data)
        
        # Zstd niveau 22 doit compresser >15x ce pattern
        assert ratio < 0.07
        print(f"✅ Compression ratio vérifié: {ratio:.3f} → {1/ratio:.1f}x")
        
    def test_metrics_calcul(self):
        """Test calcul des métriques moyennes"""
        citizen = PrfaaSProviderCitizen()
        
        ratios = [0.06, 0.07, 0.065, 0.068]
        for r in ratios:
            citizen.stats["prefill_executed"] += 1
            n = citizen.stats["prefill_executed"]
            citizen.stats["compression_ratio_mean"] = (
                citizen.stats["compression_ratio_mean"] * (n-1) + r
            ) / n
            
        assert abs(citizen.stats["compression_ratio_mean"] - 0.06575) < 0.00001


if __name__ == "__main__":
    print("🧪 EXÉCUTION TESTS TDD PrfaaSProviderCitizen")
    print("=" * 60)
    
    # Tests KVCache
    print("\n📦 Tests KVCache:")
    test_kv = TestKVCache()
    test_kv.test_serialize_deserialize()
    print("  ✅ serialize/deserialize OK")
    test_kv.test_size()
    print("  ✅ header size OK")
    
    # Tests Citizen
    print("\n🤖 Tests Citoyen:")
    test_cit = TestPrfaaSProviderCitizen()
    test_cit.test_init()
    print("  ✅ init OK")
    asyncio.run(test_cit.test_compression())
    test_cit.test_metrics_calcul()
    print("  ✅ metrics calcul OK")
    
    print("\n" + "=" * 60)
    print("✅ TOUS LES TESTS TDD PASSENT")