# NotebookLM Enterprise Guide

Use the NotebookLM CLI & MCP Server with **Gemini Enterprise (NotebookLM Pro)** at `vertexaisearch.cloud.google.com`.

## Installation

```bash
# Install from source (enterprise support is on feat/enterprise-support branch)
git clone https://github.com/jacob-bd/notebooklm-mcp-cli.git
cd notebooklm-mcp-cli
git checkout feat/enterprise-support
uv tool install .
```

After installation you get two executables:
- `nlm` — Command-line interface
- `notebooklm-mcp` — MCP server for AI assistants

## Authentication

Enterprise authentication requires three environment variables and cookies from your browser.

### Step 1: Find Your Enterprise IDs

1. Open Chrome and go to your Gemini Enterprise NotebookLM page
2. The URL looks like: `https://vertexaisearch.cloud.google.com/u/0/home/cid/<CID>/r/notebook`
3. Click any notebook — the URL parameters contain your **project ID** (`project=XXXXX`)

| Variable | Where to find | Example |
|----------|--------------|---------|
| `NOTEBOOKLM_BASE_URL` | Always the same | `https://vertexaisearch.cloud.google.com` |
| `NOTEBOOKLM_PROJECT_ID` | `project=` in the URL | `77341597043` |
| `NOTEBOOKLM_CID` | `cid/` in the URL | `79e69e06-91db-410c-8426-98f01f2098ab` |

### Step 2: Extract Cookies

Cookies must include HttpOnly cookies (`HSID`, `SSID`, `__Secure-1PSID`, etc.), so you need Chrome DevTools Protocol (CDP) extraction — not just `document.cookie`.

**Option A: Via Chrome with remote debugging**

```bash
# Launch Chrome with debugging enabled
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/.notebooklm-mcp-cli/chrome-profile" &

# Log in to Gemini Enterprise in the opened Chrome window
# Then extract cookies:
python3 -c "
from notebooklm_tools.utils.cdp import extract_cookies_from_page
result = extract_cookies_from_page(cdp_http_url='http://localhost:9222')
cookies = result.get('cookies', [])
gc = [c for c in cookies if c.get('domain','') == '.google.com']
print('; '.join(f'{c[\"name\"]}={c[\"value\"]}' for c in gc))
"
```

**Option B: Via MCP (if using Playwright MCP or Chrome DevTools MCP)**

Use the `save_auth_tokens` MCP tool to save cookies directly from the browser.

### Step 3: Set Environment Variables

```bash
export NOTEBOOKLM_BASE_URL="https://vertexaisearch.cloud.google.com"
export NOTEBOOKLM_PROJECT_ID="<your-project-id>"
export NOTEBOOKLM_CID="<your-customer-id>"
export NOTEBOOKLM_COOKIES="<full-cookie-string>"
```

### Verify

```bash
nlm list notebooks
```

## CLI Command Reference

### Notebooks

```bash
# List all notebooks
nlm list notebooks

# Create a notebook
nlm create notebook "My Research"

# Get notebook details
nlm get notebook <notebook-id>

# Get AI-generated summary
nlm describe notebook <notebook-id>

# Rename a notebook
nlm rename notebook <notebook-id> "New Title"

# Delete a notebook (irreversible)
nlm delete notebook <notebook-id> --confirm
```

### Sources

```bash
# List sources in a notebook
nlm list sources <notebook-id>

# Add a URL source
nlm add url <notebook-id> "https://example.com/article"

# Add text source
nlm add text <notebook-id> "Your text content" --title "Source Title"

# Rename a source
nlm rename source -n <notebook-id> <source-id> "New Name"

# Delete a source (irreversible)
nlm delete source <source-id> --confirm
```

### Chat / Query

```bash
# Ask a question about notebook contents
nlm chat send <notebook-id> "What are the key findings?"
```

### Studio Content

```bash
# Create audio overview (podcast)
nlm studio create <notebook-id> audio --confirm

# Check generation status
nlm studio status <notebook-id>
```

### Sharing

```bash
# View sharing status
nlm share status <notebook-id>

# Invite a collaborator (enterprise uses invite-only, no public links)
nlm share invite <notebook-id> user@example.com
```

### Notes

```bash
# Create a note
nlm note create <notebook-id> --title "My Note" --content "Note content"

# Delete a note
nlm note delete <notebook-id> <note-id> --confirm
```

## MCP Server Usage

Start the MCP server with enterprise environment variables:

```bash
export NOTEBOOKLM_BASE_URL="https://vertexaisearch.cloud.google.com"
export NOTEBOOKLM_PROJECT_ID="<your-project-id>"
export NOTEBOOKLM_CID="<your-customer-id>"
export NOTEBOOKLM_COOKIES="<cookies>"

notebooklm-mcp
```

Or configure in your AI tool's MCP settings (e.g. `.claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "notebooklm": {
      "command": "notebooklm-mcp",
      "env": {
        "NOTEBOOKLM_BASE_URL": "https://vertexaisearch.cloud.google.com",
        "NOTEBOOKLM_PROJECT_ID": "<your-project-id>",
        "NOTEBOOKLM_CID": "<your-customer-id>",
        "NOTEBOOKLM_COOKIES": "<cookies>"
      }
    }
  }
}
```

## Enterprise vs Standard Differences

| Feature | Standard (Free/Plus) | Enterprise |
|---------|---------------------|------------|
| Base URL | `notebooklm.google.com` | `vertexaisearch.cloud.google.com` |
| Max sources per notebook | 50 | 300 |
| Public link sharing | Yes | No (invite-only) |
| File upload | 3-step protocol | 2-step (Discovery Engine) |
| Audio/Video overview | Yes | Yes |
| Flashcards | Yes | Not available |
| Infographics | Yes | Not available |
| Slide decks | Yes | Not available |
| Data tables | Yes | Not available |

## Troubleshooting

### "Authentication expired"

Re-extract cookies from your browser. Enterprise cookies rotate frequently — the CSRF token and session ID are refreshed automatically, but the base cookies must be current.

### "API error (code 3)"

Invalid request parameters. Ensure `NOTEBOOKLM_PROJECT_ID` is set correctly. Find it in the URL when viewing any notebook: `?project=XXXXX`.

### Empty notebook list

- Verify you're using the correct Google account's cookies
- Check that `NOTEBOOKLM_CID` matches the organization ID in the URL

### Studio content types not available

Enterprise does not support flashcards, infographics, slide decks, or data tables. Supported types: audio overview, video overview, briefing doc, study guide, FAQ, timeline, mind map.
