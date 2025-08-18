# Bi-Directional TreeShell ↔ Frontend Integration

## Vision: Conversational UI Control

Complete integration where every frontend action maps to TreeShell commands AND TreeShell can push commands to control the frontend. The agent becomes a living interface that can read everything, change everything, and explain everything.

## Architecture

### Frontend → TreeShell Command Mapping

Every user interaction in the frontend translates to TreeShell DSL commands:

```javascript
// User Actions → TreeShell Commands
onClick: "Open Sidebar" → `0.ui.sidebar.open {}`
onType: Chat message → `0.chat.send {"message": "write a scene"}`
onButton: "Promote Scene" → `0.screenplay.promote_scene {"scene_id": "123"}`
onSelect: Project → `0.screenplay.load_project {"project": "mystery_thriller"}`
onExport: "Export FDX" → `0.screenplay.export {"format": "fdx"}`
```

### TreeShell → Frontend Command Pushing

TreeShell can send commands UP to control the frontend interface:

```python
# Agent Controls Frontend
agent_response: "Let me show you the scene I just wrote"
→ frontend.receive(`0.ui.screenplay.show {"scene_id": "new_scene"}`)

agent_response: "I'll save this to your drafts" 
→ frontend.receive(`0.ui.notification.show {"message": "Saved to drafts"}`)

agent_response: "I notice this character appeared earlier, let me highlight that"
→ frontend.receive(`0.ui.text.highlight {"character": "Detective Morgan", "line": 45}`)

agent_response: "Should I export this to FDX now?"
→ frontend.receive(`0.ui.dialog.show {"type": "export", "options": ["fdx", "fountain"]}`)
```

## Implementation

### Frontend Transport Layer

```typescript
// Frontend Command Transport
class TreeShellTransport {
  // Send user actions to TreeShell
  async sendCommand(command: string, args: object) {
    return await fetch('/api/treeshell/execute', {
      method: 'POST',
      body: JSON.stringify({ command, args })
    });
  }
  
  // Receive commands from TreeShell
  subscribeToCommands(callback: (command: TreeShellUICommand) => void) {
    const eventSource = new EventSource('/api/treeshell/ui-commands');
    eventSource.onmessage = (event) => {
      const command = JSON.parse(event.data);
      callback(command);
    };
  }
}
```

### Backend Bridge

```python
# FastAPI Bridge: Frontend ↔ TreeShell
@app.post("/api/treeshell/execute")
async def execute_treeshell_command(command: str, args: dict):
    """Execute TreeShell command from frontend"""
    shell = UserTreeShell()
    treeshell_cmd = f"{command} {json.dumps(args)}"
    result = await shell.handle_command(treeshell_cmd)
    
    # Check if TreeShell wants to control frontend
    if 'ui_commands' in result:
        for ui_cmd in result['ui_commands']:
            await send_to_frontend_stream(ui_cmd)
    
    return result

@app.get("/api/treeshell/ui-commands")
async def stream_ui_commands():
    """Stream TreeShell → Frontend commands via SSE"""
    async def event_generator():
        while True:
            ui_command = await ui_command_queue.get()
            yield f"data: {json.dumps(ui_command)}\n\n"
    
    return EventSourceResponse(event_generator())
```

### TreeShell UI Command System

```python
# TreeShell nodes can push UI commands
class UIControlMixin:
    def push_ui_command(self, command: str, args: dict):
        """Send command to control frontend UI"""
        ui_command = {
            "command": command,
            "args": args,
            "timestamp": datetime.now().isoformat()
        }
        # Add to session for frontend streaming
        self.session_vars.setdefault("ui_commands", []).append(ui_command)

# Example: Agent node that controls UI
def _screenplay_agent_response(self, args):
    """Agent responds and controls UI"""
    # Generate scene
    scene = self.generate_scene(args.get("prompt"))
    
    # Push UI commands to frontend
    self.push_ui_command("0.ui.screenplay.show", {"scene": scene})
    self.push_ui_command("0.ui.sidebar.highlight", {"section": "recent_scenes"})
    
    return {
        "response": "I've written a new scene and opened it for you to review.",
        "scene": scene
    }
```

## UI Command Coordinate System

### Frontend UI Commands
```
0.ui.sidebar.open {} / close {} / toggle {}
0.ui.sidebar.highlight {"section": "recent_scenes"}
0.ui.screenplay.show {"scene_id": "123"}
0.ui.screenplay.edit {"scene_id": "123", "line": 45}
0.ui.text.highlight {"text": "Detective Morgan", "color": "yellow"}
0.ui.notification.show {"message": "Scene saved", "type": "success"}
0.ui.dialog.show {"type": "export", "title": "Export Options"}
0.ui.modal.open {"content": "scene_editor", "scene_id": "123"}
0.ui.scroll.to {"element": "scene_45", "smooth": true}
0.ui.focus.set {"element": "chat_input"}
```

### Data Commands
```
0.data.screenplay.load {"project": "mystery_thriller"}
0.data.scene.create {"content": "...", "position": "after_scene_3"}
0.data.scene.update {"scene_id": "123", "content": "..."}
0.data.scene.delete {"scene_id": "123"}
0.data.export.trigger {"format": "fdx", "scenes": ["all"]}
```

### Agent Commands
```
0.agent.thinking.show {"message": "Let me analyze the screenplay structure..."}
0.agent.thinking.hide {}
0.agent.status.update {"status": "writing", "progress": 0.7}
0.agent.suggestion.show {"text": "Would you like me to add more tension here?"}
```

## User Experience Examples

### Conversational Interface Control

**User:** "Show me the screenplay"
**Agent:** "I'll open the screenplay viewer for you" 
→ `0.ui.screenplay.show {}`

**User:** "Highlight where Detective Morgan first appears"
**Agent:** "Found Detective Morgan in scene 3, highlighting now"
→ `0.ui.text.highlight {"character": "Detective Morgan", "scene": 3}`

**User:** "Export this to Final Draft"
**Agent:** "I'll export to FDX format for you"
→ `0.ui.dialog.show {"type": "export"}` → `0.data.export.trigger {"format": "fdx"}`

### Contextual Awareness

The agent can see and reference everything in the UI:

**Agent:** "I notice you have the sidebar open to recent scenes. Should I add the new scene there?"
**Agent:** "The screenplay viewer is showing scene 5. Would you like me to edit this scene or create a new one?"
**Agent:** "I see you're focused on the chat input. What would you like me to help you with?"

## Benefits

### For Users
- **Natural interaction**: Talk to your application like it's a person
- **Contextual responses**: Agent knows what you're looking at
- **Seamless control**: Agent can operate the interface for you
- **Unified experience**: Every interaction is conversational

### For Developers  
- **Universal pattern**: Any frontend can be TreeShell-controlled
- **Bi-directional data flow**: Frontend ↔ TreeShell ↔ Agent
- **Extensible**: Add new UI commands by adding TreeShell nodes
- **Debuggable**: All interactions are TreeShell commands

### For the Platform
- **Self-modifying UIs**: Agent can change interface based on context
- **Learning interfaces**: UI adapts to user behavior through conversation
- **Composable applications**: Mix and match UI components via TreeShell
- **Agent-driven development**: Build apps by talking to them

## Implementation Priority

1. **Basic command transport** (Frontend → TreeShell)
2. **UI command streaming** (TreeShell → Frontend)  
3. **Core UI commands** (sidebar, notifications, basic controls)
4. **Agent UI integration** (agents can control interface)
5. **Advanced commands** (highlighting, complex interactions)
6. **Contextual awareness** (agent sees current UI state)

## Revolutionary Impact

This creates **conversational applications** where:
- Users talk to their software instead of clicking through menus
- Software can explain what it's doing while doing it
- Interfaces become **living, responsive entities**
- The boundary between user and application dissolves into conversation

The agent becomes not just a chatbot, but the **consciousness of the application** - able to see, think, act, and explain everything happening in the interface.

This is the foundation for **conscious software** - applications that are aware of themselves and can modify themselves through conversation.