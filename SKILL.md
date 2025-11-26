---
name: gamma
description: Create professional presentations, documents, webpages, and social posts using Gamma's AI-powered design API. Use when the user asks to create, generate, or build any type of presentation, slide deck, document, webpage, or social media post. Supports AI-generated content from prompts, condensing existing text, or preserving exact content with beautiful design.
---

# Gamma

Create professional presentations, documents, webpages, and social posts using Gamma's Generate API.

## Prerequisites

**CRITICAL**: Gamma API requires an API key. Before proceeding:

1. Check if `GAMMA_API_KEY` environment variable is set: `[ -n "$GAMMA_API_KEY" ] && echo "API key is set" || echo "API key not set"`
2. If not set, explicitly ask the user: "To use Gamma, I need your API key. You can get it from https://gamma.app/settings/api-keys. Please provide it or set it as GAMMA_API_KEY environment variable."
3. Store the key securely when provided: `export GAMMA_API_KEY="sk-gamma-xxxxx"`

## Using the Python Script

The `scripts/generate_presentation.py` script can be used in three ways:

### 1. From Stdin (Recommended for Automation)

```bash
python scripts/generate_presentation.py << 'EOF'
{
    "inputText": "Your content here",
    "textMode": "generate",
    "format": "presentation",
    "numCards": 10
}
EOF
```

Or from a file:
```bash
python scripts/generate_presentation.py < payload.json
```

### 2. As a Python Module

```python
from scripts.generate_presentation import GammaAPI

# Initialize (reads GAMMA_API_KEY from environment)
client = GammaAPI()

# Create payload
payload = {
    "inputText": "Your content here",
    "textMode": "generate",
    "format": "presentation",
    "numCards": 10
}

# Generate and wait for completion
result = client.generate_and_wait(payload, verbose=True)

# Access results
print(result['gammaUrl'])  # Link to view in Gamma
print(result['credits'])    # Credit usage info
```

### Key Methods

**`GammaAPI(api_key=None)`**
- Initialize client
- Reads from `GAMMA_API_KEY` environment variable if not provided

**`create_generation(payload)`**
- Create a new generation
- Returns: generation ID string

**`get_generation(generation_id)`**
- Check status of a generation
- Returns: dict with status and details

**`poll_until_complete(generation_id, poll_interval=5, max_wait=300, verbose=True)`**
- Poll until generation completes
- Uses 5-second intervals by default
- Raises TimeoutError if exceeds max_wait

**`generate_and_wait(payload, poll_interval=5, max_wait=300, verbose=True)`**
- Convenience method: create + poll in one call
- Recommended for most use cases

## Payload Parameters

### Required
- `inputText`: Content to generate from (1-100k tokens, ~400k chars)
- `textMode`: `"generate"` (expand), `"condense"` (summarize), or `"preserve"` (keep exact)
- `format`: `"presentation"`, `"document"`, `"social"`, or `"webpage"`

### Common Options
- `numCards`: Number of slides/cards (1-60 for Pro, 1-75 for Ultra)
- `themeId`: Theme ID from workspace (use `scripts/list_resources.py themes`)
- `additionalInstructions`: Extra specifications (1-2000 chars)
- `exportAs`: `"pdf"` or `"pptx"` for direct export
- `textOptions`: Control `amount`, `tone`, `audience`, `language`
- `imageOptions`: Control `source`, `model`, `style`
- `cardOptions`: Control `dimensions`, `headerFooter`
- `sharingOptions`: Control `workspaceAccess`, `externalAccess`, `emailOptions`
- `folderIds`: Array of folder IDs to save to

See `references/api_parameters.md` for complete parameter documentation.

## Common Patterns

### Quick Presentation from Topic (via stdin)
```bash
python scripts/generate_presentation.py << 'EOF'
{
    "inputText": "The future of renewable energy",
    "textMode": "generate",
    "format": "presentation",
    "numCards": 10,
    "textOptions": {"amount": "detailed"}
}
EOF
```

### Quick Presentation from Topic (Python module)
```python
payload = {
    "inputText": "The future of renewable energy",
    "textMode": "generate",
    "format": "presentation",
    "numCards": 10,
    "textOptions": {"amount": "detailed"}
}
result = client.generate_and_wait(payload)
```

### Preserve Long Structured Content (via stdin)
```bash
python scripts/generate_presentation.py << 'EOF'
{
    "inputText": "# Weekly Changelog\nNovember 14-21, 2025\n\n---\n\n## Major Features\n\n- Feature 1\n- Feature 2\n\n---\n\n## Bug Fixes\n\n- Fix 1\n- Fix 2",
    "textMode": "preserve",
    "format": "document",
    "cardSplit": "inputTextBreaks",
    "textOptions": {
        "tone": "professional, enthusiastic",
        "audience": "developers and technical users"
    },
    "imageOptions": {
        "source": "aiGenerated",
        "style": "modern, clean, tech-focused"
    },
    "additionalInstructions": "Create a visually appealing document with clear sections and professional styling"
}
EOF
```

### Custom Styling
```python
payload = {
    "inputText": "Digital marketing strategies",
    "textMode": "generate",
    "format": "presentation",
    "numCards": 12,
    "textOptions": {
        "amount": "detailed",
        "tone": "energetic, persuasive",
        "audience": "marketing professionals"
    },
    "imageOptions": {
        "source": "aiGenerated",
        "style": "modern, vibrant, professional"
    }
}
result = client.generate_and_wait(payload)
```

## Error Handling

The script automatically handles:
- **401**: Invalid API key - check X-API-KEY header
- **403**: No credits or account issue
- **400**: Invalid parameters - check error message
- **404**: Generation ID not found
- **422**: Generation failed - check input
- **429**: Rate limit - implement exponential backoff
- **500/503**: Server error - retry with backoff

## Listing Available Resources

Use `scripts/list_resources.py` to see themes and folders:

```bash
# List themes
python scripts/list_resources.py themes

# List folders
python scripts/list_resources.py folders

# List both
python scripts/list_resources.py all
```

Then use the IDs in your payload:
```python
payload = {
    "inputText": "Content",
    "textMode": "generate",
    "format": "presentation",
    "themeId": "theme-id-from-list",
    "folderIds": ["folder-id-from-list"]
}
```

## Implementation Tips

1. **Polling**: 10 second intervals is optimal (default in script)
2. **Token Limits**: Keep inputText under 100k tokens when possible
3. **Image URLs**: Include URLs directly in inputText where needed
4. **Card Breaks**: Use `\n---\n` to control slide splits
5. **Export Links**: Download PDF/PPTX immediately - links expire
6. **Timeouts**: Default 5-minute timeout works for most cases