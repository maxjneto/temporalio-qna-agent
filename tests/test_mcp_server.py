"""Tests for the MCP Server."""

import json
from unittest.mock import MagicMock, patch

import pytest


class TestMCPServer:
    """Tests for the MCP server."""

    @pytest.fixture
    def mock_openai_client(self):
        """Mock for OpenAI client."""
        with patch("mcp_server.openai_client_async_max") as mock:
            mock.embeddings.create.return_value = MagicMock(
                data=[MagicMock(embedding=[0.1, 0.2, 0.3])]
            )
            yield mock

    @pytest.fixture
    def sample_index(self, tmp_path):
        """Creates a test index."""
        index_data = [
            {
                "id": "doc1",
                "chunk": "Python is a programming language",
                "embedding": [0.1, 0.2, 0.3],
            },
            {
                "id": "doc2",
                "chunk": "FastAPI is a web framework",
                "embedding": [0.15, 0.25, 0.35],
            },
        ]
        index_file = tmp_path / "test_index.json"
        index_file.write_text(json.dumps(index_data))
        return str(index_file)

    def test_get_embedding(self, mock_openai_client):
        """Tests embedding generation."""
        from mcp_server import get_embedding

        result = get_embedding("test query")
        assert result == [0.1, 0.2, 0.3]
        mock_openai_client.embeddings.create.assert_called_once()

    def test_cosine_similarity(self):
        """Tests cosine similarity calculation."""
        from mcp_server import numpy_cosine_similarity

        emb1 = [1.0, 0.0, 0.0]
        emb2 = [1.0, 0.0, 0.0]
        similarity = numpy_cosine_similarity(emb1, emb2)
        assert abs(similarity - 1.0) < 0.001

        emb3 = [0.0, 1.0, 0.0]
        similarity2 = numpy_cosine_similarity(emb1, emb3)
        assert abs(similarity2 - 0.0) < 0.001
