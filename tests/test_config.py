"""Tests for configurations."""

import os
from unittest.mock import patch

import pytest


class TestConfig:
    """Tests for the configuration module."""

    @patch.dict(
        os.environ,
        {
            "AZURE_API_BASE": "https://test.openai.azure.com",
            "AZURE_API_KEY": "test-key",
            "AZURE_DEPLOYMENT": "gpt-4",
            "TEMPORAL_ADDRESS": "test:7233",
        },
    )
    def test_load_config_from_env(self):
        """Tests loading configuration from environment variables."""
        from config import AzureOpenAIConfig, TemporalConfig

        azure_config = AzureOpenAIConfig.from_env()
        assert azure_config.endpoint == "https://test.openai.azure.com"
        assert azure_config.api_key == "test-key"
        assert azure_config.deployment == "gpt-4"

        temporal_config = TemporalConfig.from_env()
        assert temporal_config.address == "test:7233"

    def test_config_validation(self):
        """Tests configuration validation."""
        from config import AzureOpenAIConfig

        config = AzureOpenAIConfig(
            endpoint="", api_key="key", deployment="gpt-4"
        )

        with pytest.raises(ValueError, match="AZURE_API_BASE"):
            config.validate()
