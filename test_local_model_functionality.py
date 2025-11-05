#!/usr/bin/env python3
"""Test script for local model functionality without requiring actual model download."""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import local_model
import config

def test_status_tracking():
    """Test status tracking functionality."""
    print("Testing status tracking...")

    # Test initial status
    status = local_model.get_status()
    print(f"Initial status: {status}")
    assert status["state"] == "not_downloaded"

    # Test setting status
    local_model._set_status("testing", detail="Test status")
    status = local_model.get_status()
    print(f"Updated status: {status}")
    assert status["state"] == "testing"
    assert status["detail"] == "Test status"

    print("✓ Status tracking works")

def test_prompt_building():
    """Test prompt building functionality."""
    print("\nTesting prompt building...")

    # Test basic prompt
    prompt = local_model.build_prompt("What is CRISPR?")
    print("Basic prompt built successfully")
    assert "What is CRISPR?" in prompt
    assert config.SYSTEM_PROMPT in prompt
    assert "<|im_start|>assistant" in prompt

    # Test prompt with context
    prompt_with_context = local_model.build_prompt("What is CRISPR?", "CRISPR is gene editing")
    print("Prompt with context built successfully")
    assert "Retrieved Context:" in prompt_with_context
    assert "CRISPR is gene editing" in prompt_with_context

    print("✓ Prompt building works")

def test_response_extraction():
    """Test response extraction functionality."""
    print("\nTesting response extraction...")

    # Test with assistant marker
    test_text = "<|im_start|>assistant\nThis is my answer<|im_end|>"
    response = local_model._extract_assistant_response(test_text)
    print(f"Extracted response: '{response}'")
    assert response == "This is my answer"

    # Test without marker
    test_text2 = "Direct response"
    response2 = local_model._extract_assistant_response(test_text2)
    print(f"Direct response: '{response2}'")
    assert response2 == "Direct response"

    print("✓ Response extraction works")

def test_dependency_checks():
    """Test dependency checking functions."""
    print("\nTesting dependency checks...")

    # These should return False since dependencies aren't installed
    has_cuda = local_model._has_cuda()
    gpu_ready = local_model._gpu_ready()
    torch_available = local_model._torch_available()

    print(f"CUDA available: {has_cuda}")
    print(f"GPU ready: {gpu_ready}")
    print(f"Torch available: {torch_available}")

    # Should all be False in this environment
    assert not has_cuda
    assert not gpu_ready
    assert not torch_available

    print("✓ Dependency checks work")

def test_download_start_error_handling():
    """Test download start with missing dependencies."""
    print("\nTesting download start error handling...")

    status = local_model.start_download()
    print(f"Download start status: {status}")

    # Should be in error state due to missing dependencies
    assert status["state"] == "error"
    assert "PyTorch is required" in status["error"]

    print("✓ Error handling works")

def test_generate_response_error_handling():
    """Test generate_response error handling."""
    print("\nTesting generate_response error handling...")

    try:
        local_model.generate_response("Test question")
        assert False, "Should have raised RuntimeError"
    except RuntimeError as e:
        print(f"Expected error: {e}")
        assert "not ready" in str(e)

    print("✓ Error handling for generation works")

def main():
    """Run all tests."""
    print("=" * 60)
    print("TESTING LOCAL MODEL FUNCTIONALITY")
    print("=" * 60)

    try:
        test_status_tracking()
        test_prompt_building()
        test_response_extraction()
        test_dependency_checks()
        test_download_start_error_handling()
        test_generate_response_error_handling()

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED! ✓")
        print("Local model functionality is working correctly.")
        print("Note: Actual model loading requires PyTorch and unsloth dependencies.")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())