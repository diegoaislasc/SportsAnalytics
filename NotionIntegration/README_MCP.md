# Notion MCP Integration Guide - SportsAnalytics

This guide explains how to configure and use Notion MCP (Model Context Protocol) with Cursor to manage your SportsAnalytics project management workspace.

## What is Notion MCP?

Notion MCP allows AI tools like Cursor to interact directly with your Notion workspace. Once configured, you can:

- Create, update, and query tasks directly from Cursor
- Get project status summaries
- Move tasks between sprints
- Search across your PM databases

## Prerequisites

1. **PM Databases deployed**: Run `python NotionIntegration/setup_pm.py` first
2. **Notion account**: With access to your Data-Sports workspace
3. **Cursor IDE**: With MCP support enabled

## Configuration Options

### Option 1: Streamable HTTP (Recommended)

Add this to your Cursor MCP settings (`Cursor Settings > Features > MCP > Add New MCP Server`):

**Name:** Notion
**Type:** URL (Streamable HTTP)
**URL:** `https://mcp.notion.com/mcp`

Or add directly to your Cursor `mcp_servers.json`:

```json
{
  "mcpServers": {
    "Notion": {
      "url": "https://mcp.notion.com/mcp"
    }
  }
}
```

### Option 2: SSE (Server-Sent Events)

```json
{
  "mcpServers": {
    "Notion": {
      "type": "sse",
      "url": "https://mcp.notion.com/sse"
    }
  }
}
```

### Option 3: STDIO (Local Server via npx)

```json
{
  "mcpServers": {
    "notionMCP": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://mcp.notion.com/mcp"]
    }
  }
}
```

## First-Time Setup

1. **Add the MCP server** in Cursor settings
2. **Authenticate**: When you first use a Notion command, you'll be prompted to authenticate via OAuth
3. **Grant permissions**: Allow the MCP server access to your workspace

## Available Capabilities

Once connected, Notion MCP provides these tools:

### Database Operations
- Query databases with filters
- Create new pages/entries
- Update existing pages
- Search across workspaces

### Page Operations
- Read page content
- Append content to pages
- Update page properties

### Comments
- Read comments on pages
- Add new comments

## Example Prompts for SportsAnalytics PM

### Task Management

```
"Create a new task 'Fix data pipeline timeout' in the current sprint with High priority"
```

```
"Show me all tasks in Sprint 1 that are still in progress"
```

```
"Move task 'Implement FBRef ingestion' to Done status"
```

### Sprint Management

```
"What's the status of Sprint 1? How many tasks are completed?"
```

```
"Create a new Sprint 3 starting January 6th for 2 weeks"
```

### Epic Tracking

```
"Show progress on Epic A: Ingesta de Datos"
```

```
"List all tasks under the Transformación epic"
```

### Daily Standups

```
"What did I complete yesterday and what's planned for today?"
```

```
"Are there any blocked tasks in the current sprint?"
```

## Database Reference

After running `setup_pm.py`, your workspace contains:

| Database | Purpose | Key Properties |
|----------|---------|----------------|
| DB Epics | High-level goals | Status, Priority, Progress |
| DB Sprints | Time-boxed iterations | Dates, Status, Goal, Velocity |
| DB Tasks | Work items (Backlog) | Status, Type, Priority, Effort, Epic relation, Sprint relation |

## Troubleshooting

### "Connection failed" or "Authentication error"

1. Ensure you've completed the OAuth flow
2. Check that your Notion integration has access to the workspace
3. Try disconnecting and reconnecting in `Notion Settings > Connections > Notion MCP`

### "Database not found"

- Verify the databases were created by `setup_pm.py`
- Ensure your integration is connected to the parent page
- Check page permissions in Notion

### MCP server not responding

1. Check your internet connection
2. Verify the URL is correct: `https://mcp.notion.com/mcp`
3. Try the alternative STDIO method with `npx`

### Tool not available in Composer

- MCP tools only work in Cursor's **Composer Agent** mode
- Ensure MCP is enabled in Cursor settings
- Click the refresh button in MCP settings to reload tools

## Alternative: Open Source MCP Server

If you need more control or offline access, you can use the open-source Notion MCP server:

**Repository:** https://github.com/makenotion/notion-mcp

This requires:
1. Your own Notion integration token
2. Local Node.js installation
3. Manual configuration

## Workflow Integration

### Recommended Daily Workflow

1. **Morning**: Ask "What tasks are in my current sprint?"
2. **During work**: Update task status as you progress
3. **End of day**: "Mark task X as done" or move incomplete items

### Sprint Ceremonies

- **Planning**: Use Cursor to create tasks and assign to sprints
- **Daily standup**: Query for status updates
- **Review**: Generate sprint summaries
- **Retro**: Add notes and learnings to sprint pages

## Security Notes

- Notion MCP uses OAuth for authentication
- Your credentials are never stored locally
- You can revoke access anytime in Notion settings
- The MCP server only accesses pages you explicitly grant permission to

---

For more information:
- [Notion MCP Documentation](https://developers.notion.com/docs/mcp)
- [Notion API Reference](https://developers.notion.com/reference)
- [Cursor MCP Guide](https://docs.cursor.com/context/model-context-protocol)
