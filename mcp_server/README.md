# TreeShell MCP Server

A Model Context Protocol (MCP) server for managing conversations using the HEAVEN framework and TreeShell navigation.

## Features

- 🌳 **Conversation Management**: Persistent conversation chains across sessions
- 💬 **Context-Aware Continuation**: Maintains conversation history automatically
- 📚 **Organization**: Conversations organized by date with search and filtering
- 🔄 **Multiple Response Modes**: Text-only, full iteration, or truncated actions
- 🤖 **HEAVEN Integration**: Uses HEAVEN framework for AI agent communication

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install TreeShell library (if not already installed):
```bash
pip install -e /path/to/heaven-tree-repl
```

3. Set environment variables:
```bash
export HEAVEN_DATA_DIR=/path/to/conversation/data
export OPENAI_API_KEY=your_openai_api_key_here
```

## Running the Server

### Standalone Mode
```bash
python -m mcp_server --model gpt-4o-mini --provider openai
```

### As MCP Server
The server implements the MCP protocol and can be used with any MCP-compatible client.

### Claude Desktop Integration
1. Copy `claude_desktop_config_template.json` to your Claude Desktop configuration
2. Update the paths and API keys in the configuration
3. Restart Claude Desktop

## Available Tools

### start_conversation
Start a new conversation with a title and initial message.

**Parameters:**
- `title` (required): Conversation title
- `message` (required): Initial message to send
- `tags` (optional): List of tags for organization

### continue_conversation
Continue an existing conversation with a new message.

**Parameters:**
- `message` (required): Message to send
- `conversation_id` (optional): Conversation ID (uses current if not specified)

### list_conversations
List recent conversations.

**Parameters:**
- `limit` (optional): Maximum number of conversations to return (default: 10)

### load_conversation
Load an existing conversation as the current active one.

**Parameters:**
- `conversation_id` (required): Conversation ID to load

### search_conversations
Search conversations by title or tags.

**Parameters:**
- `query` (required): Search query

### get_conversation_history
Get the history chain for a conversation.

**Parameters:**
- `conversation_id` (optional): Conversation ID (uses current if not specified)

### set_response_mode
Set response extraction mode.

**Parameters:**
- `mode` (required): One of:
  - `text_only`: Just the AI response text (default)
  - `full_iteration`: Complete iteration with all messages
  - `truncated_actions`: Action summaries with final response

### get_current_conversation
Get information about the current active conversation.

**Parameters:** None

## Response Modes

### text_only (default)
Returns only the AI response text. Best for simple conversations.

```json
{
  "success": true,
  "response": "Hello! How can I help you today?"
}
```

### full_iteration
Returns the complete iteration including system messages, user input, AI response, and any tool calls.

```json
{
  "success": true,
  "response": [
    {"type": "HumanMessage", "content": "Hello"},
    {"type": "AIMessage", "content": "Hello! How can I help?"}
  ]
}
```

### truncated_actions
Returns a summary of actions taken plus the final AI response. Useful for tracking tool usage.

```json
{
  "success": true,
  "response": {
    "action_summary": ["ToolUse: WebSearch was used"],
    "final_response": "Based on my search...",
    "has_actions": true
  }
}
```

## Example Usage

### Python Client
```python
import asyncio
from server import TreeShellServer

async def main():
    server = TreeShellServer()
    
    # Start a conversation
    result = await server.start_conversation(
        title="Python Help",
        message="Explain decorators",
        tags=["python", "learning"]
    )
    
    # Continue the conversation
    result = await server.continue_conversation(
        message="Can you show an example?"
    )
    
    print(result["response"])

asyncio.run(main())
```

### MCP Client Configuration
Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "treeshell": {
      "command": "python",
      "args": ["/path/to/server.py"],
      "env": {
        "HEAVEN_DATA_DIR": "/path/to/conversation/data"
      }
    }
  }
}
```

## Data Storage

Conversations are stored in the directory specified by `HEAVEN_DATA_DIR`:

```
$HEAVEN_DATA_DIR/
└── conversations/
    └── 08/           # Month
        └── 04/       # Day
            └── 2025_08_04_21_17_53.json  # Conversation file
```

Each conversation file contains:
- Title and tags
- Conversation metadata
- Chain of history IDs
- Agent configuration

## Development

### Testing
```bash
python test_server.py
```

### Adding New Tools
1. Add tool name to `TreeShellTools` enum
2. Implement method in `TreeShellServer` class
3. Add tool definition in `list_tools()`
4. Handle tool call in `call_tool()`

## License

MIT