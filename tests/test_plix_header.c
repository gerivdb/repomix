// PLIX Header Tests - EPIC-PLIX-002
// Unit tests for header validation and utilities

#include "plix_header.h"
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

// Test magic bytes validation
int test_header_magic() {
    plix_header_t header;

    // Valid magic
    header.magic = PLIX_MAGIC;
    assert(plix_header_validate_magic(&header) == PLIX_SUCCESS);

    // Invalid magic
    header.magic = 0x12345678;
    assert(plix_header_validate_magic(&header) == PLIX_ERROR_INVALID_MAGIC);

    printf("✅ test_header_magic passed\n");
    return 0;
}

// Test version validation
int test_header_version() {
    plix_header_t header;

    // Valid version
    header.version = PLIX_VERSION_1_0_0;
    assert(plix_header_validate_version(&header) == PLIX_SUCCESS);

    // Invalid version
    header.version = 0x020000;  // v2.0.0
    assert(plix_header_validate_version(&header) == PLIX_ERROR_INVALID_VERSION);

    printf("✅ test_header_version passed\n");
    return 0;
}

// Test reserved field validation
int test_header_reserved() {
    plix_header_t header;

    // Valid reserved (0)
    header.reserved = 0;
    assert(plix_header_validate_reserved(&header) == PLIX_SUCCESS);

    // Invalid reserved (non-zero)
    header.reserved = 1;
    assert(plix_header_validate_reserved(&header) == PLIX_ERROR_INVALID_SIZE);

    printf("✅ test_header_reserved passed\n");
    return 0;
}

// Test complete header validation
int test_header_validation() {
    plix_header_t header;

    // Valid header
    plix_header_init(&header, 123, 1000);
    assert(plix_header_validate(&header) == PLIX_SUCCESS);

    // Invalid magic
    header.magic = 0x12345678;
    assert(plix_header_validate(&header) != PLIX_SUCCESS);
    header.magic = PLIX_MAGIC;  // Reset

    // Invalid version
    header.version = 0x020000;
    assert(plix_header_validate(&header) != PLIX_SUCCESS);
    header.version = PLIX_VERSION_1_0_0;  // Reset

    // Invalid reserved
    header.reserved = 1;
    assert(plix_header_validate(&header) != PLIX_SUCCESS);
    header.reserved = 0;  // Reset

    printf("✅ test_header_validation passed\n");
    return 0;
}

// Test version encoding/decoding
int test_version_encoding() {
    uint8_t major = 1, minor = 2;
    uint16_t patch = 345;

    // Encode
    uint32_t encoded = plix_encode_version(major, minor, patch);
    assert(encoded == 0x01020345);  // 1.2.845 in hex

    // Decode
    uint8_t decoded_major, decoded_minor;
    uint16_t decoded_patch;
    plix_decode_version(encoded, &decoded_major, &decoded_minor, &decoded_patch);

    assert(decoded_major == major);
    assert(decoded_minor == minor);
    assert(decoded_patch == patch);

    printf("✅ test_version_encoding passed\n");
    return 0;
}

// Test version compatibility
int test_version_compatibility() {
    // Same version
    assert(plix_version_is_compatible(PLIX_VERSION_1_0_0, PLIX_VERSION_1_0_0) == true);

    // Compatible minor versions (reader can handle older)
    uint32_t v1_2_0 = plix_encode_version(1, 2, 0);
    uint32_t v1_1_0 = plix_encode_version(1, 1, 0);
    assert(plix_version_is_compatible(v1_2_0, v1_1_0) == true);  // v1.2.0 can read v1.1.0
    assert(plix_version_is_compatible(v1_1_0, v1_2_0) == false); // v1.1.0 cannot read v1.2.0

    // Incompatible major versions
    uint32_t v2_0_0 = plix_encode_version(2, 0, 0);
    assert(plix_version_is_compatible(PLIX_VERSION_1_0_0, v2_0_0) == false);

    printf("✅ test_version_compatibility passed\n");
    return 0;
}

// Test checksum calculation and verification
int test_checksum() {
    const char* test_data = "Hello, PLIX World!";
    size_t data_len = strlen(test_data);
    uint8_t checksum[PLIX_CHECKSUM_SIZE];

    // Calculate checksum
    assert(plix_calculate_checksum((const uint8_t*)test_data, data_len, checksum) == PLIX_SUCCESS);

    // Verify correct checksum
    assert(plix_verify_checksum((const uint8_t*)test_data, data_len, checksum) == PLIX_SUCCESS);

    // Verify incorrect checksum
    uint8_t wrong_checksum[PLIX_CHECKSUM_SIZE];
    memset(wrong_checksum, 0xFF, PLIX_CHECKSUM_SIZE);
    assert(plix_verify_checksum((const uint8_t*)test_data, data_len, wrong_checksum) == PLIX_ERROR_CHECKSUM_MISMATCH);

    printf("✅ test_checksum passed\n");
    return 0;
}

// Test frame creation and validation
int test_frame_operations() {
    const uint64_t token_count = 100;
    const size_t payload_size = token_count * sizeof(int8_t);

    // Create frame
    plix_frame_t* frame = plix_frame_create(token_count);
    assert(frame != NULL);
    assert(frame->payload != NULL);

    // Initialize header
    plix_header_init(&frame->header, 42, token_count);

    // Fill payload with test data
    for (uint64_t i = 0; i < token_count; i++) {
        frame->payload[i] = (int8_t)(i % 3 - 1);  // Ternary values: -1, 0, 1
    }

    // Calculate checksum
    assert(plix_calculate_checksum(frame->payload, payload_size, frame->checksum) == PLIX_SUCCESS);

    // Validate frame
    assert(plix_frame_validate(frame, payload_size) == PLIX_SUCCESS);

    // Test invalid frame
    frame->header.magic = 0x12345678;  // Corrupt magic
    assert(plix_frame_validate(frame, payload_size) == PLIX_ERROR_INVALID_MAGIC);

    // Cleanup
    plix_frame_destroy(frame);

    printf("✅ test_frame_operations passed\n");
    return 0;
}

// Test error string conversion
int test_error_strings() {
    assert(strcmp(plix_error_string(PLIX_SUCCESS), "Success") == 0);
    assert(strcmp(plix_error_string(PLIX_ERROR_INVALID_MAGIC), "Invalid magic bytes") == 0);
    assert(strcmp(plix_error_string(PLIX_ERROR_INVALID_VERSION), "Invalid version") == 0);
    assert(strcmp(plix_error_string(PLIX_ERROR_CHECKSUM_MISMATCH), "Checksum mismatch") == 0);
    assert(strcmp(plix_error_string(PLIX_ERROR_INVALID_SIZE), "Invalid size") == 0);
    assert(strcmp(plix_error_string(999), "Unknown error") == 0);

    printf("✅ test_error_strings passed\n");
    return 0;
}

// Benchmark header parsing (performance test)
int benchmark_header_parsing() {
    plix_header_t header;
    plix_header_init(&header, 12345, 1000000);

    const int iterations = 100000;
    clock_t start = clock();

    for (int i = 0; i < iterations; i++) {
        plix_header_validate(&header);
    }

    clock_t end = clock();
    double time_ms = ((double)(end - start) / CLOCKS_PER_SEC) * 1000;
    double avg_time_us = (time_ms / iterations) * 1000;

    printf("✅ benchmark_header_parsing: %.2f μs per validation (%.2f ms total)\n",
           avg_time_us, time_ms);

    // Should be well under 100μs as per requirements
    assert(avg_time_us < 100.0);

    return 0;
}

// Main test runner
int main() {
    printf("🧪 Running PLIX Header Tests (EPIC-PLIX-002)\n");
    printf("===========================================\n\n");

    // Run all tests
    test_header_magic();
    test_header_version();
    test_header_reserved();
    test_header_validation();
    test_version_encoding();
    test_version_compatibility();
    test_checksum();
    test_frame_operations();
    test_error_strings();
    benchmark_header_parsing();

    printf("\n🎉 All PLIX Header tests passed! ✅\n");
    printf("EPIC-PLIX-002: Header/Magic/Versioning implementation validated\n");

    return 0;
}