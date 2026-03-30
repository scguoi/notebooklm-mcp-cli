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

### Step 1: Find Your Enterprise IDs

Open Chrome and go to your Gemini Enterprise NotebookLM page. Extract these from the URL:

| Variable | Where to find | Example |
|----------|--------------|---------|
| `NOTEBOOKLM_BASE_URL` | Always the same | `https://vertexaisearch.cloud.google.com` |
| `NOTEBOOKLM_PROJECT_ID` | `project=` in the iframe URL | `77341597043` |
| `NOTEBOOKLM_CID` | `cid/` in the URL | `79e69e06-91db-410c-8426-98f01f2098ab` |

### Step 2: Set Environment Variables

```bash
export NOTEBOOKLM_BASE_URL="https://vertexaisearch.cloud.google.com"
export NOTEBOOKLM_PROJECT_ID="<your-project-id>"
export NOTEBOOKLM_CID="<your-customer-id>"
```

Add these to your `~/.zshrc` or `~/.bashrc` to persist across sessions.

### Step 3: Login

```bash
nlm login
```

Chrome opens the Gemini Enterprise page automatically. Log in with your Google Workspace account — cookies are extracted and saved to a local profile.

> After login, subsequent commands work without re-authentication until cookies expire.

### Verify

```bash
nlm list notebooks
```

## CLI Command Reference

### Notebooks

```bash
nlm list notebooks                         # List all notebooks
nlm create notebook "My Research"          # Create a notebook
nlm get notebook <id>                       # Get notebook details
nlm describe notebook <id>                  # AI-generated summary
nlm rename notebook <id> "New Title"       # Rename
nlm delete notebook <id> --confirm          # Delete (irreversible)
```

### Sources

```bash
nlm list sources <notebook-id>                              # List sources
nlm add url <notebook-id> "https://example.com/article"     # Add URL
nlm add text <notebook-id> "Content" --title "Title"        # Add text
nlm rename source -n <notebook-id> <source-id> "New Name"  # Rename
nlm delete source <source-id> --confirm                     # Delete
```

### Chat / Query

```bash
nlm chat send <notebook-id> "What are the key findings?"
```

### Studio Content

```bash
nlm studio create <notebook-id> audio --confirm    # Create podcast
nlm studio status <notebook-id>                    # Check status
```

### Sharing

```bash
nlm share status <notebook-id>                           # View status
nlm share invite <notebook-id> user@example.com          # Invite collaborator
```

> Enterprise does not support public link sharing — invite-only.

### Notes

```bash
nlm note create <notebook-id> --title "My Note" --content "Content"
nlm note delete <notebook-id> <note-id> --confirm
```

## MCP Server Configuration

Configure in your AI tool's MCP settings:

```json
{
  "mcpServers": {
    "notebooklm": {
      "command": "notebooklm-mcp",
      "env": {
        "NOTEBOOKLM_BASE_URL": "https://vertexaisearch.cloud.google.com",
        "NOTEBOOKLM_PROJECT_ID": "<your-project-id>",
        "NOTEBOOKLM_CID": "<your-customer-id>"
      }
    }
  }
}
```

> The MCP server reads saved cookies from the local profile (created by `nlm login`). No need to include cookies in the config.

### Manual Cookies (Optional)

If you prefer not to use `nlm login`, you can provide cookies via environment variable:

```bash
export NOTEBOOKLM_COOKIES="SID=...; HSID=...; SSID=...; ..."
```

Cookies must include HttpOnly cookies (`HSID`, `SSID`, `__Secure-1PSID`, etc.) — extract via Chrome DevTools Protocol, not `document.cookie`.

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

Run `nlm login` again. Enterprise cookies rotate periodically — CSRF tokens and session IDs refresh automatically, but base cookies require re-login when expired.

### "API error (code 3)"

Invalid parameters. Ensure `NOTEBOOKLM_PROJECT_ID` is correct. Find it in the URL when viewing any notebook: `?project=XXXXX`.

### Empty notebook list

- Verify you logged in with the correct Google Workspace account via `nlm login`
- Check that `NOTEBOOKLM_CID` matches the organization ID in the URL

### Studio content types not available

Enterprise does not support flashcards, infographics, slide decks, or data tables. Supported types: audio overview, video overview, briefing doc, study guide, FAQ, timeline, mind map.
