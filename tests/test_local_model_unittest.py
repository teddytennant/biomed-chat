"""Tests for local_model.py functionality using unittest."""

import unittest
from unittest.mock import Mock, patch

import local_model


class TestLocalModelStatus(unittest.TestCase):
    """Test status tracking functionality."""

    def test_initial_status(self):
        """Test that initial status is correct."""
        status = local_model.get_status()
        self.assertEqual(status["state"], "not_downloaded")
        self.assertIsNone(status["error"])
        self.assertEqual(status["detail"], "Model not downloaded")
        self.assertIsNone(status["device"])

    def test_set_status_updates_all_fields(self):
        """Test that _set_status updates all provided fields."""
        local_model._set_status(
            "test_state",
            error="test_error",
            detail="test_detail",
            device="test_device"
        )

        status = local_model.get_status()
        self.assertEqual(status["state"], "test_state")
        self.assertEqual(status["error"], "test_error")
        self.assertEqual(status["detail"], "test_detail")
        self.assertEqual(status["device"], "test_device")

    def test_set_status_preserves_existing_fields(self):
        """Test that _set_status preserves fields not explicitly set."""
        # Set initial state
        local_model._set_status("initial", detail="initial_detail")

        # Update only state and error
        local_model._set_status("updated", error="new_error")

        status = local_model.get_status()
        self.assertEqual(status["state"], "updated")
        self.assertEqual(status["error"], "new_error")
        self.assertEqual(status["detail"], "initial_detail")  # Should be preserved


class TestDependencyChecks(unittest.TestCase):
    """Test dependency availability checks."""

    @patch('local_model.torch', None)
    def test_has_cuda_no_torch(self):
        """Test _has_cuda returns False when torch is not available."""
        self.assertFalse(local_model._has_cuda())

    @patch('local_model.torch')
    def test_has_cuda_no_cuda(self, mock_torch):
        """Test _has_cuda returns False when CUDA is not available."""
        mock_torch.cuda.is_available.return_value = False
        self.assertFalse(local_model._has_cuda())

    @patch('local_model.torch')
    def test_has_cuda_with_cuda(self, mock_torch):
        """Test _has_cuda returns True when CUDA is available."""
        mock_torch.cuda.is_available.return_value = True
        self.assertTrue(local_model._has_cuda())

    @patch('local_model.FastLanguageModel', None)
    @patch('local_model.torch')
    def test_gpu_ready_no_unsloth(self, mock_torch):
        """Test _gpu_ready returns False when FastLanguageModel is not available."""
        mock_torch.cuda.is_available.return_value = True
        self.assertFalse(local_model._gpu_ready())

    @patch('local_model.FastLanguageModel')
    @patch('local_model.torch', None)
    def test_gpu_ready_no_torch(self, mock_unsloth):
        """Test _gpu_ready returns False when torch is not available."""
        self.assertFalse(local_model._gpu_ready())

    @patch('local_model.FastLanguageModel')
    @patch('local_model.torch')
    def test_gpu_ready_with_all_deps(self, mock_torch, mock_unsloth):
        """Test _gpu_ready returns True when all GPU dependencies are available."""
        mock_torch.cuda.is_available.return_value = True
        self.assertTrue(local_model._gpu_ready())

    @patch('local_model.torch', None)
    def test_torch_available_no_torch(self):
        """Test _torch_available returns False when torch is not available."""
        self.assertFalse(local_model._torch_available())

    @patch('local_model.torch')
    def test_torch_available_with_torch(self, mock_torch):
        """Test _torch_available returns True when torch is available."""
        self.assertTrue(local_model._torch_available())


class TestPromptBuilding(unittest.TestCase):
    """Test prompt construction functionality."""

    @patch('config.SYSTEM_PROMPT', 'Test system prompt')
    def test_build_prompt_without_context(self):
        """Test building prompt without RAG context."""
        question = "What is CRISPR?"
        prompt = local_model.build_prompt(question)

        expected = (
            "<|im_start|>system\n"
            "Test system prompt<|im_end|>\n"
            "<|im_start|>user\n"
            "What is CRISPR?<|im_end|>\n"
            "<|im_start|>assistant\n"
        )
        self.assertEqual(prompt, expected)

    @patch('config.SYSTEM_PROMPT', 'Test system prompt')
    def test_build_prompt_with_context(self):
        """Test building prompt with RAG context."""
        question = "What is CRISPR?"
        context = "CRISPR is a gene editing tool."
        prompt = local_model.build_prompt(question, context)

        expected = (
            "<|im_start|>system\n"
            "Test system prompt<|im_end|>\n"
            "<|im_start|>user\n"
            "What is CRISPR?\n\nRetrieved Context:\nCRISPR is a gene editing tool.<|im_end|>\n"
            "<|im_start|>assistant\n"
        )
        self.assertEqual(prompt, expected)


class TestResponseExtraction(unittest.TestCase):
    """Test assistant response extraction from generated text."""

    def test_extract_assistant_response_with_marker(self):
        """Test extracting response when <|im_start|>assistant marker is present."""
        generated = (
            "<|im_start|>system\nSystem prompt<|im_end|>\n"
            "<|im_start|>user\nQuestion<|im_end|>\n"
            "<|im_start|>assistant\nThis is the answer<|im_end|>"
        )
        response = local_model._extract_assistant_response(generated)
        self.assertEqual(response, "This is the answer")

    def test_extract_assistant_response_without_marker(self):
        """Test extracting response when marker is not present."""
        generated = "This is just the raw response"
        response = local_model._extract_assistant_response(generated)
        self.assertEqual(response, "This is just the raw response")

    def test_extract_assistant_response_with_end_token(self):
        """Test that <|im_end|> tokens are removed."""
        generated = "<|im_start|>assistant\nAnswer here<|im_end|>"
        response = local_model._extract_assistant_response(generated)
        self.assertEqual(response, "Answer here")


if __name__ == '__main__':
    unittest.main()