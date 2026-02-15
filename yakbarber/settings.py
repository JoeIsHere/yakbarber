"""Settings loading for Yak Barber using TOML configuration."""

import sys
from dataclasses import dataclass, field

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        raise ImportError(
            "Python < 3.11 requires the 'tomli' package. Install it with: pip install tomli"
        )


@dataclass
class SiteSettings:
    root: str = "./"
    web_root: str = ""
    content_dir: str = "content/"
    template_dir: str = "templates/default/"
    output_dir: str = "output/"
    drafts_dir: str = "drafts/"
    site_name: str = ""
    author: str = ""
    ogp_default_image: str = ""
    posts_per_page: int = 10
    typekit_id: str = ""
    twitter_handle: str = ""
    fedi_handle: str = ""
    analytics_domain: str = ""


def load_settings(path: str) -> SiteSettings:
    """Load settings from a TOML file and return a SiteSettings instance."""
    with open(path, "rb") as f:
        data = tomllib.load(f)

    site = data.get("site", {})
    integrations = data.get("integrations", {})
    social = data.get("social", {})

    return SiteSettings(
        root=site.get("root", "./"),
        web_root=site.get("web_root", ""),
        content_dir=site.get("content_dir", "content/"),
        template_dir=site.get("template_dir", "templates/default/"),
        output_dir=site.get("output_dir", "output/"),
        drafts_dir=site.get("drafts_dir", "drafts/"),
        site_name=site.get("site_name", ""),
        author=site.get("author", ""),
        ogp_default_image=site.get("ogp_default_image", ""),
        posts_per_page=site.get("posts_per_page", 10),
        typekit_id=integrations.get("typekit_id", ""),
        twitter_handle=social.get("twitter_handle", ""),
        fedi_handle=social.get("fedi_handle", ""),
        analytics_domain=integrations.get("analytics_domain", ""),
    )
