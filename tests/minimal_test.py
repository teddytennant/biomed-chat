"""Minimal test for local_model.py."""

import sys
sys.path.insert(0, '..')

import local_model

def test_basic_status():
    """Test basic status functionality."""
    status = local_model.get_status()
    assert status["state"] == "not_downloaded"
    assert status["error"] is None
    print("✓ Basic status test passed")

def test_prompt_building():
    """Test prompt building."""
    # Mock config
    import config
    original_prompt = config.SYSTEM_PROMPT
    config.SYSTEM_PROMPT = "Test system prompt"

    try:
        prompt = local_model.build_prompt("Test question")
        assert "Test system prompt" in prompt
        assert "Test question" in prompt
        print("✓ Prompt building test passed")
    finally:
        config.SYSTEM_PROMPT = original_prompt

if __name__ == "__main__":
    test_basic_status()
    test_prompt_building()
    print("All tests passed!")