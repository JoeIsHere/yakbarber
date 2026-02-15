"""Tests for image processing in yakbarber.engine."""

import os
import pytest

from yakbarber.engine import process_images, process_frontmatter_image
from yakbarber.settings import SiteSettings


@pytest.fixture
def image_settings(tmp_path):
    settings = SiteSettings(
        web_root="https://example.com/",
        output_dir=str(tmp_path / "output") + "/",
    )
    os.makedirs(settings.output_dir, exist_ok=True)
    return settings


@pytest.fixture
def source_with_image(tmp_path):
    """Create a source directory with a test image file."""
    source_dir = tmp_path / "drafts"
    source_dir.mkdir()
    image_file = source_dir / "photo.jpg"
    image_file.write_bytes(b"\xff\xd8\xff\xe0fake-jpeg-data")
    return str(source_dir)


class TestProcessImages:
    def test_rewrites_relative_src(self, image_settings, source_with_image):
        content = '<img src="photo.jpg" alt="test">'
        result = process_images(content, "2024-01-01-Test-Post", source_with_image, image_settings)
        assert 'src="https://example.com/images/2024-01-01-Test-Post/photo.jpg"' in result

    def test_leaves_absolute_url_unchanged(self, image_settings, source_with_image):
        content = '<img src="https://example.com/existing.jpg">'
        result = process_images(content, "slug", source_with_image, image_settings)
        assert content == result

    def test_leaves_root_relative_unchanged(self, image_settings, source_with_image):
        content = '<img src="/images/existing.jpg">'
        result = process_images(content, "slug", source_with_image, image_settings)
        assert content == result

    def test_copies_image_to_output(self, image_settings, source_with_image):
        content = '<img src="photo.jpg">'
        process_images(content, "2024-01-01-Test", source_with_image, image_settings)
        expected_path = os.path.join(
            image_settings.output_dir, "images", "2024-01-01-Test", "photo.jpg"
        )
        assert os.path.exists(expected_path)

    def test_handles_srcset(self, image_settings, source_with_image):
        content = '<source srcset="photo.jpg" type="image/jpeg">'
        result = process_images(content, "2024-01-01-Test", source_with_image, image_settings)
        assert 'srcset="https://example.com/images/2024-01-01-Test/photo.jpg"' in result

    def test_handles_multiple_images(self, image_settings, tmp_path):
        source_dir = tmp_path / "multi"
        source_dir.mkdir()
        (source_dir / "a.jpg").write_bytes(b"fake-a")
        (source_dir / "b.jpg").write_bytes(b"fake-b")
        content = '<img src="a.jpg"><img src="b.jpg">'
        result = process_images(content, "slug", str(source_dir), image_settings)
        assert "a.jpg" in result
        assert "b.jpg" in result
        assert result.count("https://example.com/images/slug/") == 2

    def test_missing_source_file_still_rewrites(self, image_settings, tmp_path):
        """Even if the source file doesn't exist, the URL should be rewritten."""
        source_dir = tmp_path / "empty"
        source_dir.mkdir()
        content = '<img src="missing.jpg">'
        result = process_images(content, "slug", str(source_dir), image_settings)
        assert "https://example.com/images/slug/missing.jpg" in result


class TestProcessFrontmatterImage:
    def test_rewrites_relative_path(self, image_settings, source_with_image):
        result = process_frontmatter_image("photo.jpg", "2024-01-01-Test", source_with_image, image_settings)
        assert result == "https://example.com/images/2024-01-01-Test/photo.jpg"

    def test_leaves_absolute_url(self, image_settings, source_with_image):
        result = process_frontmatter_image(
            "https://example.com/existing.jpg", "slug", source_with_image, image_settings
        )
        assert result == "https://example.com/existing.jpg"

    def test_copies_file(self, image_settings, source_with_image):
        process_frontmatter_image("photo.jpg", "2024-01-01-Test", source_with_image, image_settings)
        expected = os.path.join(image_settings.output_dir, "images", "2024-01-01-Test", "photo.jpg")
        assert os.path.exists(expected)
