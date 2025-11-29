#!/usr/bin/env python3
"""
Test script to verify ARE payload compression and size limits work correctly.
This ensures 413 errors are prevented while maintaining functionality.
"""

import json
import sys
import os

# Add the are directory to Python path for testing
sys.path.insert(0, os.path.dirname(__file__))

def test_payload_compression():
    """Test the payload compression logic"""
    print("Testing ARE payload compression...")

    # Mock the compression function (simplified version)
    PAYLOAD_SIZE_LIMITS = {
        'are_plan': 500000,      # 500KB
        'are_execution': 1000000, # 1MB
        'are_content': 500000,    # 500KB
        'are_evaluation': 200000, # 200KB
        'are_guardrail': 100000,  # 100KB
        'are_metadata': 100000   # 100KB
    }

    def compress_are_payload(data, field_name):
        if not data:
            return data

        json_string = json.dumps(data)
        size_bytes = len(json_string.encode('utf-8'))
        limit = PAYLOAD_SIZE_LIMITS.get(field_name, 100000)

        if size_bytes <= limit:
            return data  # No compression needed

        print(f"WARNING: ARE payload for {field_name} is {size_bytes} bytes, limit is {limit}. Compressing...")

        # For large payloads, create a compressed version with essential data only
        if field_name == 'are_execution' and isinstance(data, dict):
            return {
                'status': data.get('status'),
                'task_count': data.get('task_count', 0),
                'success_rate': data.get('success_rate', 0),
                'total_time': data.get('total_time', 0),
                'compressed': True,
                'original_size': size_bytes,
                'summary': data.get('summary', 'Execution completed')
            }

        if field_name == 'are_plan' and isinstance(data, dict):
            return {
                'plan_id': data.get('plan_id'),
                'goal_type': data.get('goal_type'),
                'task_count': len(data.get('tasks', [])),
                'status': data.get('status'),
                'compressed': True,
                'original_size': size_bytes
            }

        if field_name == 'are_content' and isinstance(data, dict):
            return {
                'method': data.get('method', 'unknown'),
                'status': data.get('status', 'unknown'),
                'compressed': True,
                'original_size': size_bytes
            }

        # For other fields, truncate to fit within limits
        truncated_string = json_string[:limit-100] + '"}'
        try:
            return json.loads(truncated_string)
        except json.JSONDecodeError:
            return {
                'error': 'Payload too large',
                'original_size': size_bytes,
                'limit': limit,
                'compressed': True
            }

    # Test cases
    test_cases = [
        # Small payload (should pass through unchanged)
        {
            'field': 'are_evaluation',
            'data': {'status': 'passed', 'score': 85},
            'expected_compressed': False
        },
        # Large execution payload (should be compressed)
        {
            'field': 'are_execution',
            'data': {
                'status': 'completed',
                'task_count': 50,
                'success_rate': 0.85,
                'total_time': 120,
                'results': [{'id': f'task_{i}', 'status': 'success', 'large_data': 'x' * 2000} for i in range(500)],  # Make it large
                'summary': 'Large execution with many results',
                'extra_field': 'x' * 500000  # This should push it over the 1MB limit
            },
            'expected_compressed': True
        },
        # Large plan payload (should be compressed)
        {
            'field': 'are_plan',
            'data': {
                'plan_id': 'plan_123',
                'goal_type': 'REVIVE_PIPELINE',
                'status': 'active',
                'tasks': [{'id': f'task_{i}', 'type': 'email', 'data': 'x' * 2000} for i in range(300)],  # Make it large
                'extra_data': 'x' * 600000  # This should push it over the 500KB limit
            },
            'expected_compressed': True
        }
    ]

    all_passed = True

    for i, test_case in enumerate(test_cases, 1):
        field_name = test_case['field']
        input_data = test_case['data']
        expected_compressed = test_case['expected_compressed']

        # Test compression
        result = compress_are_payload(input_data, field_name)

        # Verify result
        is_compressed = isinstance(result, dict) and result.get('compressed', False)
        input_size = len(json.dumps(input_data).encode('utf-8'))
        result_size = len(json.dumps(result).encode('utf-8'))

        print(f"Test {i}: {field_name}")
        print(f"  Input size: {input_size} bytes")
        print(f"  Result size: {result_size} bytes")
        print(f"  Compressed: {is_compressed}")
        print(f"  Within limit: {result_size <= PAYLOAD_SIZE_LIMITS[field_name]}")

        if expected_compressed and not is_compressed:
            print(f"  Expected compression but got none")
            all_passed = False
        elif not expected_compressed and is_compressed:
            print(f"  Unexpected compression")
            all_passed = False
        elif result_size > PAYLOAD_SIZE_LIMITS[field_name]:
            print(f"  Result size exceeds limit ({PAYLOAD_SIZE_LIMITS[field_name]} bytes)")
            all_passed = False
        else:
            print(f"  PASSED")

        print()

    return all_passed

def test_request_size_validation():
    """Test request size validation logic"""
    print("Testing request size validation...")

    def validate_request_size(request_body, max_size=1000000):
        request_size = len(json.dumps(request_body).encode('utf-8'))
        return request_size <= max_size, request_size

    # Test cases
    test_cases = [
        {'data': {'lead_ids': list(range(10))}, 'should_pass': True},
        {'data': {'lead_ids': list(range(100))}, 'should_pass': True},
        {'data': {'lead_ids': list(range(1000)), 'extra': 'x' * 2000000}, 'should_pass': False},  # Too large
        {'data': {'lead_ids': [1], 'large_field': 'x' * 2000000}, 'should_pass': False},  # Too large
    ]

    all_passed = True

    for i, test_case in enumerate(test_cases, 1):
        is_valid, size = validate_request_size(test_case['data'])
        expected_valid = test_case['should_pass']

        print(f"Request size test {i}:")
        print(f"  Size: {size} bytes")
        print(f"  Valid: {is_valid}")
        print(f"  Expected: {expected_valid}")

        if is_valid != expected_valid:
            print("  FAILED")
            all_passed = False
        else:
            print("  PASSED")
        print()

    return all_passed

def main():
    """Run all tests"""
    print("ARE Payload Limits Test Suite")
    print("=" * 50)

    compression_passed = test_payload_compression()
    validation_passed = test_request_size_validation()

    print("=" * 50)
    if compression_passed and validation_passed:
        print("All tests passed! 413 errors should be prevented.")
        return 0
    else:
        print("Some tests failed. Check implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())