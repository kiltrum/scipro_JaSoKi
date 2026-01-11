"""Tests for CDS API configuration and connectivity."""

import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


class TestCdsApiConfiguration:
    """Tests for CDS API configuration."""

    def test_cdsapirc_file_exists(self):
        """Test that the .cdsapirc file exists in the home directory."""
        cdsapirc_path = Path.home() / ".cdsapirc"
        assert cdsapirc_path.exists(), (
            f".cdsapirc file not found at {cdsapirc_path}. "
            "Please create it with your CDS API credentials. "
            "See: https://cds.climate.copernicus.eu/how-to-api"
        )

    def test_cdsapirc_file_has_content(self):
        """Test that the .cdsapirc file is not empty."""
        cdsapirc_path = Path.home() / ".cdsapirc"
        if not cdsapirc_path.exists():
            pytest.skip(".cdsapirc file not found")
        
        content = cdsapirc_path.read_text().strip()
        assert len(content) > 0, ".cdsapirc file is empty"

    def test_cdsapirc_has_required_fields(self):
        """Test that the .cdsapirc file contains url and key fields."""
        cdsapirc_path = Path.home() / ".cdsapirc"
        if not cdsapirc_path.exists():
            pytest.skip(".cdsapirc file not found")
        
        content = cdsapirc_path.read_text()
        assert "url" in content.lower(), ".cdsapirc is missing 'url' field"
        assert "key" in content.lower(), ".cdsapirc is missing 'key' field"

    def test_cdsapi_client_can_be_created(self):
        """Test that the cdsapi.Client can be instantiated."""
        try:
            import cdsapi
            client = cdsapi.Client()
            assert client is not None
        except Exception as e:
            pytest.fail(f"Failed to create cdsapi.Client: {e}")

    def test_cdsapi_module_installed(self):
        """Test that the cdsapi module is installed."""
        try:
            import cdsapi
        except ImportError:
            pytest.fail(
                "cdsapi module is not installed. "
                "Install it with: pip install cdsapi"
            )