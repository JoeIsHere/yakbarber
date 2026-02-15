"""Tests for draft detection logic."""

import os
import sys
import pytest

# Add automation directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from automation.draft_watcher import has_complete_frontmatter, compute_post_slug


FIXTURES_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')


class TestHasCompleteFrontmatter:
    def test_incomplete_draft(self):
        path = os.path.join(FIXTURES_DIR, 'drafts', 'incomplete.md')
        assert has_complete_frontmatter(path) is None

    def test_complete_draft(self):
        path = os.path.join(FIXTURES_DIR, 'drafts', 'complete.md')
        result = has_complete_frontmatter(path)
        assert result is not None
        assert result['title'][0] == 'Ready to Publish'
        assert result['date'][0] == '2024-04-01 12:00:00'
        assert result['author'][0] == 'test'
        assert result['category'][0] == 'text'

    def test_draft_with_image(self):
        path = os.path.join(FIXTURES_DIR, 'drafts', 'with-image.md')
        result = has_complete_frontmatter(path)
        assert result is not None
        assert result['image'][0] == 'test-photo.jpg'

    def test_nonexistent_file(self):
        assert has_complete_frontmatter('/nonexistent/file.md') is None

    def test_missing_one_field(self, tmp_path):
        draft = tmp_path / "partial.md"
        draft.write_text("Title: Test\nDate: 2024-01-01 10:00:00\nAuthor: me\n\nNo category.\n")
        assert has_complete_frontmatter(str(draft)) is None


class TestComputePostSlug:
    def test_basic_slug(self):
        meta = {
            'title': ['My Test Post'],
            'date': ['2024-01-15 10:00:00'],
        }
        slug = compute_post_slug(meta)
        assert slug == '2024-01-15-My-Test-Post'

    def test_slug_with_punctuation(self):
        meta = {
            'title': ["It's a Test!"],
            'date': ['2024-06-01 12:00:00'],
        }
        slug = compute_post_slug(meta)
        assert '2024-06-01' in slug
        assert "'" not in slug
        assert "!" not in slug
