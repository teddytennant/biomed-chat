"""Tests for api_client.py error handling and provider routing."""

from unittest.mock import MagicMock, patch
import pytest


def test_process_query_invalid_provider():
    """An unrecognized API_PROVIDER should return an error string."""
    with patch("api_client.USE_MOCK_MODE", False), \
         patch("api_client.API_PROVIDER", "nonexistent"):
        from api_client import process_query
        result = process_query("test query")
        assert "Invalid API provider" in result


def test_process_query_mock_mode():
    """In mock mode, process_query should return a mock response without crashing."""
    mock_gen = MagicMock()
    mock_gen.get_response.return_value = "Mock response"
    with patch("api_client.USE_MOCK_MODE", True), \
         patch("api_client.mock_generator", mock_gen):
        from api_client import process_query
        result = process_query("test query")
        assert result == "Mock response"


def test_grok_exception_handling_uses_generic_exception():
    """process_grok_query should catch generic exceptions, not just anthropic-specific ones."""
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = Exception("connection refused")
    mock_gen = MagicMock()
    mock_gen.get_response.return_value = "fallback"
    with patch("api_client.grok_client", mock_client), \
         patch("api_client.mock_generator", mock_gen):
        from api_client import process_grok_query
        result = process_grok_query("test", "")
        assert "fallback" in result or "Error" in result


def test_gemini_exception_handling_uses_generic_exception():
    """process_gemini_query should catch generic exceptions, not just anthropic-specific ones."""
    mock_model = MagicMock()
    mock_model.generate_content.side_effect = Exception("API error")
    mock_gen = MagicMock()
    mock_gen.get_response.return_value = "fallback"
    with patch("api_client.gemini_model", mock_model), \
         patch("api_client.mock_generator", mock_gen):
        from api_client import process_gemini_query
        result = process_gemini_query("test", "")
        assert "fallback" in result or "Error" in result


def test_openai_exception_handling_uses_generic_exception():
    """process_openai_query should catch generic exceptions, not just anthropic-specific ones."""
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = Exception("rate limited")
    mock_gen = MagicMock()
    mock_gen.get_response.return_value = "fallback"
    with patch("api_client.openai_client", mock_client), \
         patch("api_client.mock_generator", mock_gen):
        from api_client import process_openai_query
        result = process_openai_query("test", "")
        assert "fallback" in result or "Error" in result
