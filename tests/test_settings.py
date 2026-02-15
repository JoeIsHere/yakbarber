"""Tests for yakbarber.settings."""

import os
import pytest

from yakbarber.settings import load_settings, SiteSettings


class TestLoadSettings:
    def test_loads_valid_toml(self, fixtures_dir):
        settings = load_settings(os.path.join(fixtures_dir, 'settings.toml'))
        assert settings.site_name == "Test Blog"
        assert settings.author == "Test Author"
        assert settings.posts_per_page == 2

    def test_defaults(self, tmp_path):
        toml_file = tmp_path / "minimal.toml"
        toml_file.write_text('[site]\nsite_name = "Minimal"\n')
        settings = load_settings(str(toml_file))
        assert settings.site_name == "Minimal"
        assert settings.posts_per_page == 10  # default
        assert settings.typekit_id == ""  # default
        assert settings.content_dir == "content/"  # default

    def test_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            load_settings("nonexistent.toml")

    def test_web_root(self, fixtures_dir):
        settings = load_settings(os.path.join(fixtures_dir, 'settings.toml'))
        assert settings.web_root == "https://example.com/"

    def test_integrations_section(self, tmp_path):
        toml_file = tmp_path / "integrations.toml"
        toml_file.write_text(
            '[site]\nsite_name = "Test"\n'
            '[integrations]\ntypekit_id = "abc123"\nanalytics_domain = "test.com"\n'
        )
        settings = load_settings(str(toml_file))
        assert settings.typekit_id == "abc123"
        assert settings.analytics_domain == "test.com"

    def test_social_section(self, tmp_path):
        toml_file = tmp_path / "social.toml"
        toml_file.write_text(
            '[site]\nsite_name = "Test"\n'
            '[social]\ntwitter_handle = "@test"\nfedi_handle = "@test@mastodon.social"\n'
        )
        settings = load_settings(str(toml_file))
        assert settings.twitter_handle == "@test"
        assert settings.fedi_handle == "@test@mastodon.social"


class TestSiteSettings:
    def test_dataclass_defaults(self):
        settings = SiteSettings()
        assert settings.root == "./"
        assert settings.web_root == ""
        assert settings.posts_per_page == 10

    def test_dataclass_custom(self):
        settings = SiteSettings(site_name="Custom", posts_per_page=5)
        assert settings.site_name == "Custom"
        assert settings.posts_per_page == 5
