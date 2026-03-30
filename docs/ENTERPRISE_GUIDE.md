# NotebookLM Enterprise Guide

Use the NotebookLM CLI & MCP Server with **Gemini Enterprise (NotebookLM Pro)** at `vertexaisearch.cloud.google.com`.

## Installation

```bash
uv tool install notebooklm-mcp-cli
```

After installation you get two executables:
- `nlm` — Command-line interface
- `notebooklm-mcp` — MCP server for AI assistants

## Authentication

One command — paste your enterprise URL:

```bash
nlm login --url "https://vertexaisearch.cloud.google.com/u/0/home/cid/79e69e06-xxxx-xxxx?hl=en_US"
```

Chrome opens the enterprise page automatically. Log in with your Google Workspace account — cookies, org ID, and project ID are all extracted and saved.

> Where to find the URL? It's in your browser address bar after logging into Gemini Enterprise.

### Verify

```bash
nlm list notebooks
```

Subsequent commands work without re-authentication until cookies expire. When they do, run `nlm login --url ...` again.

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

### Manual Configuration (Optional)

If you prefer not to use `nlm login --url`, you can set environment variables manually:

```bash
export NOTEBOOKLM_BASE_URL="https://vertexaisearch.cloud.google.com"
export NOTEBOOKLM_CID="79e69e06-..."        # Org ID
export NOTEBOOKLM_PROJECT_ID="77341597043"  # Project ID
nlm login                                    # Still needed to extract cookies
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

Run `nlm login` again. Enterprise cookies rotate periodically — CSRF tokens and session IDs refresh automatically, but base cookies require re-login when expired.

### "API error (code 3)"

Invalid parameters. Ensure `NOTEBOOKLM_PROJECT_ID` is correct. Find it in the URL when viewing any notebook: `?project=XXXXX`.

### Empty notebook list

- Verify you logged in with the correct Google Workspace account via `nlm login`
- Check that `NOTEBOOKLM_CID` matches the organization ID in the URL

### Studio content types not available

Enterprise does not support flashcards, infographics, slide decks, or data tables. Supported types: audio overview, video overview, briefing doc, study guide, FAQ, timeline, mind map.
