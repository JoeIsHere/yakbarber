"""Core static site generation engine for Yak Barber."""

import os
import re
import shutil
import datetime
import asyncio

import pystache
import markdown
from markdown.extensions.toc import TocExtension

from .utils import (
    safe_mkdir,
    split_every,
    convert_http_to_https,
    remove_punctuation,
    extract_tags,
    strip_tags,
    rfc3339_convert,
)


def process_images(content, post_slug, source_dir, settings):
    """Find relative image paths in content, copy images to output, rewrite paths.

    Args:
        content: HTML/markdown content string with image references.
        post_slug: The post slug (e.g. '2025-01-01-My-Post') for the output subdirectory.
        source_dir: Directory containing the source images (e.g. drafts/).
        settings: SiteSettings instance.

    Returns:
        Content string with relative image paths rewritten to absolute URLs.
    """
    output_images_dir = os.path.join(settings.output_dir, 'images', post_slug)

    def rewrite_match(match):
        attr = match.group(1)  # 'src' or 'srcset'
        path = match.group(2)
        # Skip already-absolute URLs and root-relative paths
        if '://' in path or path.startswith('/'):
            return match.group(0)
        source_file = os.path.join(source_dir, path)
        if os.path.exists(source_file):
            safe_mkdir(output_images_dir)
            shutil.copy2(source_file, os.path.join(output_images_dir, os.path.basename(path)))
        new_url = f"{settings.web_root}images/{post_slug}/{path}"
        return f'{attr}="{new_url}"'

    pattern = r'(src|srcset)="([^"]+)"'
    return re.sub(pattern, rewrite_match, content)


def process_frontmatter_image(image_value, post_slug, source_dir, settings):
    """Rewrite a frontmatter Image field if it's a relative path.

    Args:
        image_value: The Image frontmatter value.
        post_slug: The post slug for the output subdirectory.
        source_dir: Directory containing the source images.
        settings: SiteSettings instance.

    Returns:
        Absolute URL for the image, or the original value if already absolute.
    """
    if '://' in image_value or image_value.startswith('/'):
        return image_value
    output_images_dir = os.path.join(settings.output_dir, 'images', post_slug)
    source_file = os.path.join(source_dir, image_value)
    if os.path.exists(source_file):
        safe_mkdir(output_images_dir)
        shutil.copy2(source_file, os.path.join(output_images_dir, os.path.basename(image_value)))
    return f"{settings.web_root}images/{post_slug}/{image_value}"


def _create_md_processor():
    """Create a configured Markdown processor instance."""
    return markdown.Markdown(
        extensions=['meta', 'smarty', TocExtension(anchorlink=True)]
    )


def open_convert(mdfile, md_processor, web_root):
    """Read a markdown file, extract metadata, and convert to HTML.

    Returns [metadata_dict, html_string] or None if the file has no valid title.
    """
    md_processor.reset()
    with open(mdfile, 'r', encoding='utf-8') as f:
        rawfile = f.read()
    converted = md_processor.convert(rawfile)
    try:
        if re.match(r'[a-zA-Z0-9]+', md_processor.Meta['title'][0]):
            converted = convert_http_to_https(converted, web_root)
            return [md_processor.Meta, converted]
        else:
            return None
    except (KeyError, IndexError):
        return None


def process_posts(settings, md_processor):
    """Process all markdown files in the content directory."""
    posts = []
    content_list = os.listdir(settings.content_dir)
    for c in content_list:
        if c.endswith('.md') or c.endswith('.markdown'):
            mdc = open_convert(settings.content_dir + c, md_processor, settings.web_root)
            if mdc is not None:
                posts.append(mdc)
    return posts


async def render_post(post, settings):
    """Render a single post to HTML using templates."""
    metadata = {}
    for k, v in post[0].items():
        metadata[k] = v[0]
    metadata['content'] = post[1]
    metadata['sitename'] = settings.site_name
    metadata['webRoot'] = settings.web_root
    metadata['author'] = settings.author
    metadata['typekitId'] = settings.typekit_id
    metadata['twitterHandle'] = settings.twitter_handle
    metadata['fediHandle'] = settings.fedi_handle
    metadata['analyticsDomain'] = settings.analytics_domain
    metadata['date'] = str(metadata['date'])
    if 'image' in metadata:
        metadata['image'] = metadata['image']
    else:
        metadata['image'] = settings.ogp_default_image
    post_name = remove_punctuation(metadata['title'])
    post_name = metadata['date'].split(' ')[0] + '-' + post_name.replace(' ', '-').replace('\u2011', '-')
    post_name = '-'.join(post_name.split('-'))
    post_file_name = settings.output_dir + post_name + '.html'
    metadata['postURL'] = settings.web_root + post_name + '.html'
    metadata['title'] = strip_tags(str(markdown.markdown(metadata['title'], extensions=['smarty'])))
    if 'link' in metadata:
        template_type = '/post-content-link.html'
    else:
        template_type = '/post-content.html'
    with open(settings.template_dir + template_type, 'r', encoding='utf-8') as f:
        post_content_template = f.read()
        post_content = pystache.render(post_content_template, metadata, decode_errors='ignore')
        metadata['post-content'] = post_content
    with open(settings.template_dir + '/post-page.html', 'r', encoding='utf-8') as f:
        post_page_template = f.read()
        post_page_result = pystache.render(post_page_template, metadata, decode_errors='ignore')
    with open(post_file_name, 'w', encoding='utf-8') as f:
        f.write(post_page_result)
    return metadata


def about_page(settings, md_processor):
    """Generate the about page from about.markdown."""
    md_processor.reset()
    with open(settings.content_dir + 'about.markdown', 'r', encoding='utf-8') as f:
        rawfile = f.read()
    converted = {
        'about': md_processor.convert(rawfile),
        'sitename': settings.site_name,
        'webRoot': settings.web_root,
        'typekitId': settings.typekit_id,
        'ogpDefaultImage': settings.ogp_default_image,
        'twitterHandle': settings.twitter_handle,
        'fediHandle': settings.fedi_handle,
        'analyticsDomain': settings.analytics_domain,
    }
    with open(settings.template_dir + 'about.html', 'r', encoding='utf-8') as f:
        about_template = f.read()
    with open(settings.output_dir + 'about.html', 'w', encoding='utf-8') as f:
        about_result = pystache.render(about_template, converted)
        f.write(about_result)


def feed(posts, settings):
    """Generate the Atom XML feed."""
    feed_dict = posts[0].copy()
    entry_list = str()
    feed_dict['gen-time'] = datetime.datetime.now(datetime.timezone.utc).isoformat('T') + 'Z'
    with open(settings.template_dir + '/atom.xml', 'r', encoding='utf-8') as f:
        atom_template = f.read()
    with open(settings.template_dir + '/atom-entry.xml', 'r', encoding='utf-8') as f:
        atom_entry_template = f.read()
    for e, p in enumerate(posts):
        p['date'] = rfc3339_convert(p['date'])
        p['content'] = extract_tags(p['content'], 'script')
        p['content'] = extract_tags(p['content'], 'object')
        p['content'] = extract_tags(p['content'], 'iframe')
        p['title'] = strip_tags(p['title'])
        if e < 50:
            atom_entry_result = pystache.render(atom_entry_template, p)
            entry_list += atom_entry_result
    feed_dict['atom-entry'] = entry_list
    feed_result = pystache.render(atom_template, feed_dict, string_encode='utf-8')
    with open(settings.output_dir + 'feed.xml', 'w', encoding='utf-8') as f:
        f.write(feed_result)


def paginated_index(posts, settings):
    """Generate paginated index pages."""
    index_list = posts
    index_of_posts = split_every(settings.posts_per_page, index_list)
    with open(settings.template_dir + '/index.html', 'r', encoding='utf-8') as f:
        index_template = f.read()
    index_dict = {
        'sitename': settings.site_name,
        'typekitId': settings.typekit_id,
        'webRoot': settings.web_root,
        'ogpDefaultImage': settings.ogp_default_image,
        'twitterHandle': settings.twitter_handle,
        'fediHandle': settings.fedi_handle,
        'analyticsDomain': settings.analytics_domain,
    }
    for e, p in enumerate(index_of_posts):
        index_dict['post-content'] = p
        if e == 0:
            file_name = 'index.html'
            if len(index_list) > settings.posts_per_page:
                index_dict['previous'] = settings.web_root + 'index2.html'
        else:
            file_name = 'index' + str(e + 1) + '.html'
            if e == 1:
                index_dict['next'] = settings.web_root + 'index.html'
                index_dict['previous'] = settings.web_root + 'index' + str(e + 2) + '.html'
            else:
                index_dict['previous'] = settings.web_root + 'index' + str(e + 2) + '.html'
                if e < len(index_list):
                    index_dict['next'] = settings.web_root + 'index' + str(e - 1) + '.html'
        index_page_result = pystache.render(index_template, index_dict)
        with open(settings.output_dir + file_name, 'w', encoding='utf-8') as f:
            f.write(index_page_result)


def template_resources(settings):
    """Copy non-HTML/XML template files to output directory."""
    t_list = os.listdir(settings.template_dir)
    t_list = [x for x in t_list if not x.endswith(('.html', '.xml'))]
    for tr in t_list:
        full_path = os.path.join(settings.template_dir, tr)
        if os.path.isfile(full_path):
            shutil.copy(full_path, settings.output_dir)


async def start(settings):
    """Run the full site build."""
    md_processor = _create_md_processor()
    about_page(settings, md_processor)
    posts = process_posts(settings, md_processor)
    rendered_posts = await asyncio.gather(*[render_post(post, settings) for post in posts])
    sorted_rendered_posts = sorted(rendered_posts, key=lambda x: x['date'])[::-1]
    paginated_index(sorted_rendered_posts, settings)
    feed(sorted_rendered_posts, settings)
    template_resources(settings)


def build(settings):
    """Synchronous entry point for building the site."""
    safe_mkdir(settings.content_dir)
    safe_mkdir(settings.template_dir)
    safe_mkdir(settings.output_dir)
    asyncio.run(start(settings))
