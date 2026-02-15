"""Shared test fixtures for yakbarber tests."""

import os
import pytest

from yakbarber.settings import load_settings, SiteSettings

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')


@pytest.fixture
def fixtures_dir():
    return FIXTURES_DIR


@pytest.fixture
def test_settings(tmp_path):
    """Load test settings with output directed to a temporary directory."""
    settings = load_settings(os.path.join(FIXTURES_DIR, 'settings.toml'))
    settings.output_dir = str(tmp_path) + '/'
    return settings
