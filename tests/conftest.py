"""Shared fixtures for tests."""

import pytest


@pytest.fixture
def temp_env_vars(monkeypatch):
    """Fixture to set temporary environment variables."""

    def _set_env(**kwargs):
        for key, value in kwargs.items():
            monkeypatch.setenv(key, value)

    return _set_env


@pytest.fixture
def sample_documents():
    """Sample documents for testing."""
    return [
        {
            "id": "1",
            "chunk": "Python is a high-level programming language.",
            "embedding": [0.1, 0.2, 0.3, 0.4],
        },
        {
            "id": "2",
            "chunk": "FastAPI is a modern web framework for Python.",
            "embedding": [0.2, 0.3, 0.4, 0.5],
        },
        {
            "id": "3",
            "chunk": "Temporal is a workflow orchestration platform.",
            "embedding": [0.3, 0.4, 0.5, 0.6],
        },
    ]
