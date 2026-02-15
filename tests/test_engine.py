"""Tests for yakbarber.engine."""

import os
import pytest

import markdown
from markdown.extensions.toc import TocExtension

from yakbarber.engine import (
    open_convert,
    process_posts,
    render_post,
    about_page,
    paginated_index,
    feed,
    build,
    _create_md_processor,
)


@pytest.fixture
def md_processor():
    return _create_md_processor()


class TestOpenConvert:
    def test_parses_valid_post(self, fixtures_dir, md_processor):
        filepath = os.path.join(fixtures_dir, 'content', '2024-01-15-Example-Post.md')
        result = open_convert(filepath, md_processor, 'https://example.com/')
        assert result is not None
        meta, html = result
        assert meta['title'][0] == 'Example Post'
        assert meta['date'][0] == '2024-01-15 10:00:00'
        assert '<strong>bold</strong>' in html

    def test_returns_none_for_no_title(self, tmp_path, md_processor):
        post = tmp_path / "notitle.md"
        post.write_text("No frontmatter here, just text.\n")
        result = open_convert(str(post), md_processor, 'https://example.com/')
        assert result is None

    def test_parses_link_post(self, fixtures_dir, md_processor):
        filepath = os.path.join(fixtures_dir, 'content', '2024-02-20-Link-Post.md')
        result = open_convert(filepath, md_processor, 'https://example.com/')
        assert result is not None
        meta, html = result
        assert 'link' in meta

    def test_resets_between_calls(self, fixtures_dir, md_processor):
        """Verify metadata doesn't leak between successive conversions."""
        path1 = os.path.join(fixtures_dir, 'content', '2024-02-20-Link-Post.md')
        path2 = os.path.join(fixtures_dir, 'content', '2024-01-15-Example-Post.md')
        result1 = open_convert(path1, md_processor, 'https://example.com/')
        result2 = open_convert(path2, md_processor, 'https://example.com/')
        assert 'link' in result1[0]
        assert 'link' not in result2[0]


class TestProcessPosts:
    def test_processes_all_content(self, test_settings, md_processor):
        posts = process_posts(test_settings, md_processor)
        # Should find the 3 .md files (not about.markdown which has no title field)
        assert len(posts) == 3


class TestRenderPost:
    @pytest.mark.asyncio
    async def test_renders_html_file(self, test_settings, md_processor):
        filepath = os.path.join(test_settings.content_dir, '2024-01-15-Example-Post.md')
        result = open_convert(filepath, md_processor, test_settings.web_root)
        metadata = await render_post(result, test_settings)
        assert metadata['title'] == 'Example Post'
        assert metadata['postURL'].startswith('https://example.com/')
        # Check that the HTML file was created
        expected_file = os.path.join(test_settings.output_dir, '2024-01-15-Example-Post.html')
        assert os.path.exists(expected_file)

    @pytest.mark.asyncio
    async def test_uses_default_image(self, test_settings, md_processor):
        filepath = os.path.join(test_settings.content_dir, '2024-01-15-Example-Post.md')
        result = open_convert(filepath, md_processor, test_settings.web_root)
        metadata = await render_post(result, test_settings)
        assert metadata['image'] == 'https://example.com/images/default.jpg'

    @pytest.mark.asyncio
    async def test_uses_custom_image(self, test_settings, md_processor):
        filepath = os.path.join(test_settings.content_dir, '2024-03-10-Post-With-Image.md')
        result = open_convert(filepath, md_processor, test_settings.web_root)
        metadata = await render_post(result, test_settings)
        assert metadata['image'] == 'https://example.com/images/custom.jpg'


class TestFullBuild:
    def test_build_creates_output(self, test_settings):
        build(test_settings)
        output_dir = test_settings.output_dir
        assert os.path.exists(os.path.join(output_dir, 'index.html'))
        assert os.path.exists(os.path.join(output_dir, 'about.html'))
        assert os.path.exists(os.path.join(output_dir, 'feed.xml'))

    def test_build_creates_post_pages(self, test_settings):
        build(test_settings)
        output_dir = test_settings.output_dir
        assert os.path.exists(os.path.join(output_dir, '2024-01-15-Example-Post.html'))
        assert os.path.exists(os.path.join(output_dir, '2024-02-20-A-Link-Post.html'))

    def test_build_creates_pagination(self, test_settings):
        """With posts_per_page=2 and 3 posts, should create index.html and index2.html."""
        build(test_settings)
        output_dir = test_settings.output_dir
        assert os.path.exists(os.path.join(output_dir, 'index.html'))
        assert os.path.exists(os.path.join(output_dir, 'index2.html'))

    def test_feed_contains_entries(self, test_settings):
        build(test_settings)
        feed_path = os.path.join(test_settings.output_dir, 'feed.xml')
        with open(feed_path, 'r') as f:
            content = f.read()
        assert '<entry>' in content
        assert 'Example Post' in content
