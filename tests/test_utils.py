"""Tests for yakbarber.utils."""

from yakbarber.utils import (
    remove_punctuation,
    split_every,
    rfc3339_convert,
    convert_http_to_https,
    extract_tags,
    strip_tags,
)


class TestRemovePunctuation:
    def test_removes_commas(self):
        assert remove_punctuation("Hello, World") == "Hello World"

    def test_removes_special_chars(self):
        result = remove_punctuation("It's a test!")
        assert "'" not in result
        assert "!" not in result

    def test_preserves_alphanumeric(self):
        assert remove_punctuation("abc123") == "abc123"

    def test_handles_unicode(self):
        result = remove_punctuation("Caf\u00e9 Latt\u00e9")
        assert isinstance(result, str)


class TestSplitEvery:
    def test_even_split(self):
        result = list(split_every(2, [1, 2, 3, 4]))
        assert result == [[1, 2], [3, 4]]

    def test_uneven_split(self):
        result = list(split_every(2, [1, 2, 3, 4, 5]))
        assert result == [[1, 2], [3, 4], [5]]

    def test_single_chunk(self):
        result = list(split_every(10, [1, 2, 3]))
        assert result == [[1, 2, 3]]

    def test_empty(self):
        result = list(split_every(2, []))
        assert result == []


class TestRFC3339Convert:
    def test_basic_conversion(self):
        result = rfc3339_convert("2024-01-15 10:00:00")
        assert result.endswith("Z")
        assert "2024-01-15" in result

    def test_returns_string(self):
        result = rfc3339_convert("2023-06-11 10:45:00")
        assert isinstance(result, str)


class TestConvertHttpToHttps:
    def test_converts_http(self):
        result = convert_http_to_https(
            'http://example.com/test',
            'https://example.com/'
        )
        assert result == 'https://example.com/test'

    def test_leaves_https_alone(self):
        result = convert_http_to_https(
            'https://example.com/test',
            'https://example.com/'
        )
        assert result == 'https://example.com/test'

    def test_no_conversion_for_http_site(self):
        result = convert_http_to_https(
            'http://example.com/test',
            'http://example.com/'
        )
        assert result == 'http://example.com/test'


class TestExtractTags:
    def test_removes_script_tags(self):
        html = '<p>Hello</p><script>alert("x")</script><p>World</p>'
        result = extract_tags(html, 'script')
        assert '<script>' not in result
        assert 'Hello' in result
        assert 'World' in result

    def test_removes_iframe_tags(self):
        html = '<p>Before</p><iframe src="x"></iframe><p>After</p>'
        result = extract_tags(html, 'iframe')
        assert '<iframe' not in result


class TestStripTags:
    def test_strips_html(self):
        assert strip_tags('<p>Hello <b>World</b></p>') == 'Hello World'

    def test_plain_text_unchanged(self):
        assert strip_tags('No tags here') == 'No tags here'
