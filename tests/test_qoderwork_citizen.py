"""
Comprehensive tests for QODERWORK Citizen - Hardware Discovery & Validation
Tests auto-discovery capabilities, constraint validation, and optimization profiling
"""

import pytest
import json
import tempfile
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path for imports
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from gateway_manager.providers.brain_docs.qoderwork_citizen import (
    HardwareDiscoveryCitizen,
    HardwareProfile,
    SoftwareRequirements,
    ValidationResult,
    OptimizationProfile,
    CompatibilityLevel,
    HardwareType,
)


class TestHardwareDiscoveryCitizen:
    """Unit tests for HardwareDiscoveryCitizen"""

    @pytest.fixture
    def citizen(self):
        """Create a fresh citizen instance for each test"""
        return HardwareDiscoveryCitizen()

    def test_initialization(self, citizen):
        """Test citizen initialization"""
        assert citizen.cache is None
        assert citizen.cache_timestamp is None
        assert citizen.cache_timeout == 300

    def test_discover_hardware_specs_returns_profile(self, citizen):
        """Test that hardware discovery returns a valid profile"""
        profile = citizen.discover_hardware_specs()

        assert isinstance(profile, HardwareProfile)
        assert profile.system_id is not None
        assert profile.timestamp is not None
        assert profile.cpu is not None
        assert profile.memory is not None
        assert profile.storage is not None
        assert profile.network is not None
        assert profile.os is not None

    def test_discover_hardware_specs_caching(self, citizen):
        """Test that hardware discovery uses caching"""
        # First call
        start_time = time.time()
        profile1 = citizen.discover_hardware_specs()
        first_call_time = time.time() - start_time

        # Second call (should use cache)
        start_time = time.time()
        profile2 = citizen.discover_hardware_specs()
        second_call_time = time.time() - start_time

        # Profiles should be identical (from cache)
        assert profile1.system_id == profile2.system_id
        assert profile1.timestamp == profile2.timestamp

        # Second call should be much faster (cache hit)
        assert second_call_time < first_call_time * 0.5

    def test_force_refresh_bypasses_cache(self, citizen):
        """Test that force_refresh bypasses cache"""
        # Get cached profile
        profile1 = citizen.discover_hardware_specs()

        # Force refresh
        profile2 = citizen.discover_hardware_specs(force_refresh=True)

        # Timestamps should be different (fresh discovery)
        assert profile1.timestamp != profile2.timestamp

    @pytest.mark.parametrize(
        "min_cpu_cores,min_memory_gb,min_storage_gb,expected_compatible",
        [
            (1, 1.0, 1.0, True),  # Minimal requirements
            (100, 1000.0, 1000.0, False),  # Excessive requirements
        ],
    )
    def test_validate_constraints_basic(
        self, citizen, min_cpu_cores, min_memory_gb, min_storage_gb, expected_compatible
    ):
        """Test basic constraint validation"""
        requirements = SoftwareRequirements(
            min_cpu_cores=min_cpu_cores,
            min_memory_gb=min_memory_gb,
            min_storage_gb=min_storage_gb,
            required_os=["Windows", "Linux", "Darwin"],
            gpu_required=False,
            network_required=True,
            specific_features=[],
        )

        result = citizen.validate_constraints(requirements)

        assert isinstance(result, ValidationResult)
        assert isinstance(result.is_compatible, bool)
        assert isinstance(result.compatibility_level, CompatibilityLevel)
        assert 0.0 <= result.score <= 1.0
        assert isinstance(result.issues, list)
        assert isinstance(result.recommendations, list)
        assert isinstance(result.optimizations, list)

        # For minimal requirements, should be compatible
        if expected_compatible:
            assert result.is_compatible or result.score > 0.5

    def test_validate_constraints_gpu_required(self, citizen):
        """Test GPU requirement validation"""
        requirements = SoftwareRequirements(
            min_cpu_cores=1,
            min_memory_gb=1.0,
            min_storage_gb=1.0,
            required_os=["Windows", "Linux", "Darwin"],
            gpu_required=True,
            network_required=False,
            specific_features=[],
        )

        result = citizen.validate_constraints(requirements)

        # If no GPU detected, should not be fully compatible
        profile = citizen.discover_hardware_specs()
        if not profile.gpu:
            assert "GPU required but no GPU detected" in result.issues
            assert not result.is_compatible

    def test_validate_constraints_os_incompatible(self, citizen):
        """Test OS incompatibility detection"""
        requirements = SoftwareRequirements(
            min_cpu_cores=1,
            min_memory_gb=1.0,
            min_storage_gb=1.0,
            required_os=["NonExistentOS"],
            gpu_required=False,
            network_required=False,
            specific_features=[],
        )

        result = citizen.validate_constraints(requirements)

        assert "Incompatible OS" in " ".join(result.issues)
        assert not result.is_compatible

    def test_generate_optimization_profile(self, citizen):
        """Test optimization profile generation"""
        profile = citizen.generate_optimization_profile()

        assert isinstance(profile, OptimizationProfile)
        assert profile.recommended_thread_count > 0
        assert profile.memory_allocation_strategy in [
            "aggressive",
            "balanced",
            "conservative",
        ]
        assert profile.storage_access_pattern in ["parallel_io", "sequential_io"]
        assert isinstance(profile.gpu_acceleration_enabled, bool)
        assert profile.network_optimization in ["multi_interface", "single_interface"]
        assert isinstance(profile.performance_tuning, dict)

    def test_export_import_profile_json(self, citizen):
        """Test JSON export/import functionality"""
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as f:
            temp_path = f.name

        try:
            # Export profile
            success = citizen.export_profile_json(temp_path)
            assert success

            # Verify file exists and contains valid JSON
            assert Path(temp_path).exists()
            with open(temp_path, "r") as f:
                data = json.load(f)
            assert "system_id" in data
            assert "cpu" in data
            assert "memory" in data

            # Import profile
            imported = citizen.import_profile_json(temp_path)
            assert imported is not None
            assert isinstance(imported, HardwareProfile)

            # Verify cache was updated
            assert citizen.cache is not None
            assert citizen.cache.system_id == imported.system_id

        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_get_system_health_score(self, citizen):
        """Test system health score calculation"""
        score = citizen.get_system_health_score()

        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

        # Score should be reasonable (not zero for a working system)
        assert score > 0.1

    @pytest.mark.parametrize("cache_timeout", [0, 1, 60])
    def test_cache_timeout_behavior(self, cache_timeout):
        """Test cache timeout behavior"""
        citizen = HardwareDiscoveryCitizen()
        citizen.cache_timeout = cache_timeout

        # First call
        profile1 = citizen.discover_hardware_specs()
        citizen.cache_timestamp = time.time() - cache_timeout - 1  # Expire cache

        # Second call should refresh
        profile2 = citizen.discover_hardware_specs()

        if cache_timeout == 0:
            # Immediate expiry - should always refresh
            assert profile1.timestamp != profile2.timestamp
        else:
            # Should refresh after timeout
            assert profile1.timestamp != profile2.timestamp


class TestHardwareProfileDataStructures:
    """Tests for data structure integrity"""

    def test_hardware_profile_serialization(self):
        """Test HardwareProfile JSON serialization/deserialization"""
        # Create a minimal profile for testing
        from gateway_manager.providers.brain_docs.qoderwork_citizen import (
            CPUInfo,
            MemoryInfo,
            StorageInfo,
            NetworkInfo,
            OSInfo,
        )

        profile = HardwareProfile(
            timestamp="2024-01-01T00:00:00",
            system_id="test_system",
            cpu=CPUInfo(
                "x64", 4, 8, 2.5, 3.5, 32, 256, 8, "Intel", "Core i7", ["avx", "sse4"]
            ),
            memory=MemoryInfo(16.0, 12.0, 4.0, 8.0, 2.0, "DDR4", 3200),
            storage=StorageInfo([], 512.0, 256.0, "NTFS", ["/"]),
            gpu=None,
            network=NetworkInfo("testhost", ["192.168.1.1"], [], 1000.0, 10.0),
            os=OSInfo("Windows", "11", "x64", "10.0.22621", 3600),
        )

        # Test serialization
        data = profile.to_dict()
        assert isinstance(data, dict)
        assert data["system_id"] == "test_system"

        # Test deserialization
        restored = HardwareProfile.from_dict(data)
        assert isinstance(restored, HardwareProfile)
        assert restored.system_id == profile.system_id
        assert restored.cpu.cores_physical == profile.cpu.cores_physical

    def test_software_requirements_creation(self):
        """Test SoftwareRequirements data structure"""
        reqs = SoftwareRequirements(
            min_cpu_cores=4,
            min_memory_gb=8.0,
            min_storage_gb=50.0,
            required_os=["Windows", "Linux"],
            gpu_required=True,
            network_required=True,
            specific_features=["avx", "sse4"],
        )

        assert reqs.min_cpu_cores == 4
        assert reqs.gpu_required is True
        assert "avx" in reqs.specific_features


class TestIntegrationScenarios:
    """Integration tests for realistic scenarios"""

    @pytest.fixture
    def citizen(self):
        return HardwareDiscoveryCitizen()

    def test_web_server_requirements_validation(self, citizen):
        """Test validation for typical web server requirements"""
        web_server_reqs = SoftwareRequirements(
            min_cpu_cores=2,
            min_memory_gb=4.0,
            min_storage_gb=20.0,
            required_os=["Linux", "Windows"],
            gpu_required=False,
            network_required=True,
            specific_features=[],
        )

        result = citizen.validate_constraints(web_server_reqs)

        # Web servers should generally be compatible with modern hardware
        assert result.score > 0.6  # Should be reasonably compatible
        assert result.compatibility_level in [
            CompatibilityLevel.FULLY_COMPATIBLE,
            CompatibilityLevel.COMPATIBLE_WITH_LIMITATIONS,
        ]

    def test_ml_training_requirements_validation(self, citizen):
        """Test validation for ML training requirements"""
        ml_reqs = SoftwareRequirements(
            min_cpu_cores=8,
            min_memory_gb=32.0,
            min_storage_gb=500.0,
            required_os=["Linux", "Windows"],
            gpu_required=True,
            network_required=False,
            specific_features=["avx"],
        )

        result = citizen.validate_constraints(ml_reqs)

        # ML training has high requirements
        # Check that appropriate recommendations are made
        profile = citizen.discover_hardware_specs()

        # On ENV2, with GPU required, recommendations focus on ENV2 security
        # Thread count recommendations are still made when CPU cores are sufficient
        if profile.cpu.cores_logical >= 8:
            # Check for ENV2 security messages or alternative recommendations
            assert any(
                "env2 security" in rec.lower() or "thread" in rec.lower()
                for rec in result.recommendations
            )

        if profile.gpu:
            assert any("gpu" in rec.lower() for rec in result.recommendations)

    def test_optimization_profile_adaptation(self, citizen):
        """Test that optimization profile adapts to hardware"""
        profile = citizen.generate_optimization_profile()
        hw_profile = citizen.discover_hardware_specs()

        # Thread count should be reasonable
        assert 1 <= profile.recommended_thread_count <= 8

        # Memory strategy should match available RAM
        if hw_profile.memory.total_gb > 32:
            assert profile.memory_allocation_strategy == "aggressive"
        elif hw_profile.memory.total_gb > 16:
            assert profile.memory_allocation_strategy == "balanced"
        else:
            assert profile.memory_allocation_strategy == "conservative"

        # GPU acceleration should match hardware
        assert profile.gpu_acceleration_enabled == (hw_profile.gpu is not None)

    def test_constraint_validation_edge_cases(self, citizen):
        """Test edge cases in constraint validation"""
        # Test with zero requirements (should always pass)
        zero_reqs = SoftwareRequirements(
            min_cpu_cores=0,
            min_memory_gb=0.0,
            min_storage_gb=0.0,
            required_os=[],
            gpu_required=False,
            network_required=False,
            specific_features=[],
        )

        result = citizen.validate_constraints(zero_reqs)
        assert result.is_compatible
        assert result.score == 1.0

        # Test with extreme requirements (should fail)
        extreme_reqs = SoftwareRequirements(
            min_cpu_cores=1000,
            min_memory_gb=10000.0,
            min_storage_gb=100000.0,
            required_os=["ImpossibleOS"],
            gpu_required=True,
            network_required=True,
            specific_features=["impossible_feature"],
        )

        result = citizen.validate_constraints(extreme_reqs)
        assert not result.is_compatible
        assert result.score < 0.5
        assert len(result.issues) > 0


class TestErrorHandling:
    """Tests for error handling and resilience"""

    def test_discovery_resilient_to_failures(self):
        """Test that discovery continues even if some components fail"""
        citizen = HardwareDiscoveryCitizen()

        # This should not raise exceptions even if hardware detection fails
        profile = citizen.discover_hardware_specs()

        assert profile is not None
        assert profile.cpu is not None  # CPU should always be detectable
        assert profile.os is not None  # OS should always be detectable

        # Other components might be None or have default values
        # but the profile should still be valid

    def test_validation_handles_missing_hardware(self):
        """Test validation when some hardware is not available"""
        citizen = HardwareDiscoveryCitizen()

        # Force a profile with missing GPU
        profile = citizen.discover_hardware_specs()
        # Manually set GPU to None for testing
        citizen.cache.gpu = None

        gpu_reqs = SoftwareRequirements(
            min_cpu_cores=1,
            min_memory_gb=1.0,
            min_storage_gb=1.0,
            required_os=["Windows", "Linux", "Darwin"],
            gpu_required=True,
            network_required=False,
            specific_features=[],
        )

        result = citizen.validate_constraints(gpu_reqs)
        assert "GPU required but no GPU detected" in result.issues

    def test_json_operations_error_handling(self):
        """Test error handling in JSON operations"""
        citizen = HardwareDiscoveryCitizen()

        # Test export to invalid path
        success = citizen.export_profile_json(
            "C:\\invalid\\drive\\letter\\profile.json"
        )
        assert not success

        # Test import from non-existent file
        profile = citizen.import_profile_json("/nonexistent/file.json")
        assert profile is None

        # Test import from invalid JSON
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as f:
            f.write("invalid json content")
            temp_path = f.name

        try:
            profile = citizen.import_profile_json(temp_path)
            assert profile is None
        finally:
            Path(temp_path).unlink(missing_ok=True)


class TestENV2SecurityConstraints:
    """Critical tests for ENV2 security constraints"""

    @pytest.fixture
    def citizen(self):
        return HardwareDiscoveryCitizen()

    def test_env2_gpu_forbidden_constant(self, citizen):
        """Test that ENV2_GPU_FORBIDDEN is True and cannot be changed"""
        assert citizen.ENV2_GPU_FORBIDDEN is True
        assert HardwareDiscoveryCitizen.ENV2_GPU_FORBIDDEN is True

    def test_gpu_discovery_always_returns_none(self, citizen):
        """Test that GPU discovery ALWAYS returns None on ENV2"""
        gpu_info = citizen._discover_gpu()
        assert gpu_info is None, "GPU discovery must return None on ENV2"

    def test_hardware_profile_gpu_always_none(self, citizen):
        """Test that hardware profile always has gpu=None"""
        profile = citizen.discover_hardware_specs()
        assert profile.gpu is None, "Hardware profile GPU must be None on ENV2"

    def test_optimization_profile_gpu_disabled(self, citizen):
        """Test that optimization profiles never recommend GPU"""
        opt_profile = citizen.generate_optimization_profile()
        assert opt_profile.gpu_acceleration_enabled is False, (
            "GPU acceleration must be disabled on ENV2"
        )

        tuning = opt_profile.performance_tuning
        assert tuning.get("gpu_memory_pool") is False, (
            "GPU memory pool must be disabled"
        )
        assert tuning.get("env2_quadro_protection") is True, (
            "Quadro protection flag must be set"
        )

    def test_cpu_thread_limits_env2(self, citizen):
        """Test that CPU thread limits are respected on ENV2"""
        opt_profile = citizen.generate_optimization_profile()
        assert opt_profile.recommended_thread_count <= citizen.ENV2_MAX_CPU_THREADS, (
            f"Thread count {opt_profile.recommended_thread_count} exceeds ENV2 limit {citizen.ENV2_MAX_CPU_THREADS}"
        )

    def test_memory_limits_env2(self, citizen):
        """Test that memory limits are considered on ENV2"""
        assert citizen.ENV2_MAX_MEMORY_USAGE <= 0.8, "ENV2 memory usage limit too high"

    def test_gpu_requirement_validation_env2(self, citizen):
        """Test that GPU requirements are properly rejected on ENV2"""
        gpu_reqs = SoftwareRequirements(
            min_cpu_cores=1,
            min_memory_gb=1.0,
            min_storage_gb=1.0,
            required_os=["Windows", "Linux", "Darwin"],
            gpu_required=True,
            network_required=False,
            specific_features=[],
        )

        result = citizen.validate_constraints(gpu_reqs)

        # Should not be compatible due to GPU requirement
        assert not result.is_compatible
        issues_text = " ".join(result.issues)
        assert (
            "ENV2 SECURITY" in issues_text
            or "GPU required but no GPU detected" in issues_text
        )

    def test_security_validation_on_init(self, citizen):
        """Test that security validation runs on initialization"""
        # If this test passes, security validation ran successfully
        assert citizen is not None
        assert hasattr(citizen, "ENV2_GPU_FORBIDDEN")
        assert citizen.ENV2_GPU_FORBIDDEN is True

    def test_performance_tuning_env2_safe(self, citizen):
        """Test that performance tuning parameters are ENV2-safe"""
        opt_profile = citizen.generate_optimization_profile()
        tuning = opt_profile.performance_tuning

        # Critical ENV2 safety checks
        assert tuning.get("gpu_memory_pool") is False
        assert tuning.get("env2_quadro_protection") is True
        assert tuning.get("max_cpu_threads") <= citizen.ENV2_MAX_CPU_THREADS

        # Ensure no GPU-related optimizations
        gpu_related_keys = [k for k in tuning.keys() if "gpu" in k.lower()]
        for key in gpu_related_keys:
            assert tuning[key] is False, f"GPU-related tuning {key} must be disabled"
