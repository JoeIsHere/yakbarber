Title: Welcome to Yak Barber
Date: 2024-01-01 12:00
Author: Your Name
Category: Meta

Welcome to your new blog powered by Yak Barber! This is an example post to help you get started.

## Getting Started

To create your own posts, simply create Markdown files in your `content/` directory with YAML frontmatter at the top. Each post needs four required fields:

- **Title**: The post title
- **Date**: Publication date in `YYYY-MM-DD HH:MM` format
- **Author**: Your name
- **Category**: A category for organizing posts

## Markdown Features

You can use all standard Markdown syntax:

### Headings

Use `##` for subheadings, `###` for sub-subheadings, and so on.

### Lists

Unordered lists:
- Item one
- Item two
- Item three

Ordered lists:
1. First item
2. Second item
3. Third item

### Links and Emphasis

Create [links](https://example.com) with `[text](url)`.

Make text **bold** with `**double asterisks**` or *italic* with `*single asterisks*`.

### Code

Inline `code` uses backticks.

Code blocks use triple backticks:

```python
def hello_world():
    print("Hello from Yak Barber!")
```

### Images

Add images with standard Markdown syntax:

```markdown
![Alt text](images/photo.jpg)
```

## Link Posts

Want to share a link with commentary? Add a `Link:` field to your frontmatter:

```markdown
Title: Interesting Article
Date: 2024-01-02 10:00
Author: Your Name
Category: Links
Link: https://example.com/article

Your commentary about the linked article goes here.
```

## Custom Styling

Customize the look of your blog by editing the templates in `templates/default/`. The templates use Mustache syntax for simple, logic-less templating.

## Questions?

Check the README.md for complete documentation, or explore the test files in `tests/fixtures/content/` for more examples.

Happy blogging!
