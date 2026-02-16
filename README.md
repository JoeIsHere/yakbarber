# Yak Barber

A fiddly little time sink, and blog system.

Yak Barber is a static site generator that converts Markdown posts into a complete blog with Atom feeds, pagination, and responsive templates. It uses Mustache templating and includes a file watcher for automatic rebuilds during development.

## Features

- **Markdown to HTML**: Write posts in Markdown with YAML frontmatter
- **Mustache Templates**: Customize your site's look with simple templating
- **Atom Feeds**: Automatic RSS/Atom feed generation
- **Pagination**: Configurable posts-per-page with automatic index pages
- **File Watching**: Auto-rebuild when content changes
- **Image Processing**: Automatic image path handling and copying
- **Link Posts**: Support for link-style blog posts with external URLs

## Installation

### Requirements

- Python 3.10 or higher
- pip package manager

### Install Dependencies

```bash
pip install -r requirements.txt
```

For Python versions before 3.11, the `tomli` package is required (included in requirements.txt). Python 3.11+ uses the built-in `tomllib`.

## Configuration

1. Copy the example settings file:
   ```bash
   cp settings.example.toml settings.toml
   ```

2. Edit `settings.toml` with your site details:
   ```toml
   [site]
   root = "./"
   web_root = "https://yourdomain.com/"
   content_dir = "content/"
   template_dir = "templates/default/"
   output_dir = "output/"
   site_name = "Your Blog Name"
   author = "Your Name"
   ogp_default_image = "https://yourdomain.com/images/default-card.jpg"
   posts_per_page = 10

   [integrations]
   typekit_id = ""  # Optional Adobe Typekit ID
   analytics_domain = ""  # Optional Plausible Analytics domain

   [social]
   twitter_handle = "@yourhandle"  # Optional
   fedi_handle = "@you@mastodon.social"  # Optional
   ```

## Usage

### Build Your Site

```bash
# One-time build
python3 -m yakbarber.cli -s settings.toml

# Or using the wrapper script
python3 yakbarber3.py -s settings.toml
```

### Watch Mode

Automatically rebuild when content changes:

```bash
python3 -m yakbarber.cli -s settings.toml -w
```

### Command-Line Options

- `-s, --settings PATH` - Path to settings.toml (default: settings.toml)
- `-w, --watch` - Watch for file changes and auto-rebuild
- `-c, --cprofile` - Enable profiling output

## Content Structure

### Blog Posts

Create Markdown files in your `content/` directory with YAML frontmatter:

```markdown
Title: Your Post Title
Date: 2024-03-15 14:30
Author: Your Name
Category: Technology

Your post content here in Markdown format.

## Headings work

- So do lists
- And all standard Markdown features

![Images too](images/photo.jpg)
```

### Required Frontmatter Fields

- **Title**: Post title
- **Date**: Publication date (YYYY-MM-DD HH:MM format)
- **Author**: Author name
- **Category**: Post category

### Optional Frontmatter Fields

- **Link**: External URL (for link posts)
- **Image**: Custom OpenGraph image URL
- **Permalink**: Custom post slug (auto-generated from title if omitted)

### About Page

Create `content/about.markdown` for your about page. It uses the same frontmatter format but renders with the about template.

## Templates

Templates use [Mustache](http://mustache.github.io/) syntax. Available templates:

- `post-page.html` - Individual post pages
- `index.html` - Homepage and pagination pages
- `about.html` - About page
- `atom.xml` - Atom feed
- `atom-entry.xml` - Individual feed entries
- `post-content.html` - Post content partial (standard posts)
- `post-content-link.html` - Post content partial (link posts)

### Template Variables

Common variables available in templates:

- `{{siteName}}` - Site name from settings
- `{{webRoot}}` - Base URL for the site
- `{{author}}` - Default author name
- `{{twitterHandle}}` - Twitter/X handle (if configured)
- `{{fediHandle}}` - Fediverse handle (if configured)
- `{{typekitId}}` - Typekit ID (if configured)
- `{{#analyticsDomain}}...{{/analyticsDomain}}` - Conditional analytics block

See the included templates in `templates/default/` for examples.

## Output

Generated files are written to your `output_dir`:

```
output/
├── index.html
├── page2.html
├── about.html
├── feed.xml
├── main.css
├── YYYY/
│   └── MM/
│       └── DD/
│           └── post-slug.html
└── images/
    └── post-slug/
        └── image.jpg
```

## Testing

Run the test suite:

```bash
pytest tests/
```

Tests cover:
- Settings loading and validation
- Markdown processing and frontmatter parsing
- Post rendering and template variables
- Image path rewriting and copying
- Full build integration

## Development

### Project Structure

```
yakbarber/
├── __init__.py       # Package metadata
├── settings.py       # TOML settings loader
├── utils.py          # Utility functions
├── engine.py         # Core rendering logic
└── cli.py            # Command-line interface
```

### Running from Source

```bash
python3 -m yakbarber.cli -s settings.toml
```

## License

See the repository for license information.

## Version

Current version: 3.0.0
