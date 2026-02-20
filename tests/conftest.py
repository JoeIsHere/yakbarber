"""Shared test fixtures for yakbarber tests."""

import os
import pytest

from yakbarber.settings import load_settings

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')


@pytest.fixture
def fixtures_dir():
    return FIXTURES_DIR


@pytest.fixture
def test_settings(tmp_path):
    """Load test settings with all paths resolved to absolute locations.

    This ensures tests are fully isolated from the live site regardless
    of the working directory when pytest is run.
    """
    settings = load_settings(os.path.join(FIXTURES_DIR, 'settings.toml'))
    settings.output_dir = str(tmp_path) + '/'
    settings.content_dir = os.path.join(FIXTURES_DIR, 'content') + '/'
    settings.template_dir = os.path.join(FIXTURES_DIR, 'templates', 'default') + '/'
    return settings
