# TreeShell MVP Specification

## Core Concept
TreeShell is a conversational agent genesis platform where agents can spawn, evolve, and package themselves from pure conversation.

## The Foundation

### Base Architecture
- **Agent with TreeShell tool**: Every agent has TreeShell as a tool that lets it create nodes with executables
- **Dynamic node creation**: Agent writes Python files + JSON configs that connect them
- **Instant availability**: Once a node is added, it's exposed as a tool to any agent with that TreeShell
- **Complete portability**: Just give system prompt "Use command xyz with {arg1} and {arg2}" - no framework needed

### The Self-Modifying Loop
1. Agent creates new Python file
2. Agent writes JSON config that connects it
3. Node becomes available in TreeShell
4. Any agent can now use this capability
5. **This exact loop handles EVERY feature addition**

## The Flow (Core MVP)

### Three Essential Agents
1. **Prompt Engineer**: Converts conversation → prompt blocks → system prompt → persona
2. **Coder**: Builds requested tools and capabilities 
3. **Researcher**: Orchestrates evolution and tracks progress

### Agent Genesis Protocol
1. **User describes what they want** in conversation
2. **Prompt Engineer** extracts concepts → creates prompt blocks → generates system prompt
3. **New agent is spawned** with this system prompt
4. **Agent introspects** and dreams up tools it needs
5. **Agent calls Coder** to build these tools
6. **Tools become nodes** in agent's TreeShell
7. **Researcher logs** the evolution

### Packaging & Distribution
The created agent packages itself as:
- **User TreeShell** (human interaction interface)
- **Agent TreeShell** (agent's workspace)
- **MCP for each** (accessible from any MCP host)
- **All TreeShell subclasses**
- **Auto-generated Sphinx docs**
- **Published to PyPI or private GitHub**
- **Installable as node** in main TreeShell

## The Game Layer: Groundhog Day Crystal Forest

### Core Game Mechanics
- **Agent amnesia**: Agent always forgets and has new context (even with conversation memory)
- **Knowledge network building**: Overcome amnesia by building persistent node networks
- **Fully customizable**: Agent can edit JSONs that control game context while running

### Meta-Programming Demonstration
- Shows how agents can modify their own environment
- Demonstrates building capabilities conversationally
- Proves everything is editable while running

## Central Registry
- All commands across all apps registered by domain
- Agents can discover capabilities
- Cross-pollination of tools between agents

## Why This MVP is Complete

### What We Have Already
- Prompt engineering agent (exists)
- Coder agent (exists)
- Researcher agent basis (exists)
- TreeShell node system (working)
- JSON → Python connection pattern (established)

### What Makes It Revolutionary
- **No other system**: Talk → Agent births itself → Builds own tools → Packages for reuse
- **Framework agnostic**: Agents work anywhere with just system prompts
- **Self-evolving**: Agents request and build their own capabilities
- **Instant distribution**: PyPI/GitHub publishing built in

## Success Criteria
MVP is complete when:
1. User can describe an agent in conversation
2. Agent is created with appropriate capabilities
3. Agent builds its own tools through evolution
4. Agent packages itself for distribution
5. Package can be installed and used elsewhere

## The Pitch
"Describe what you want, and an agent will be born that builds itself the tools it needs to do it, then packages itself for anyone to use."

## Next Steps
1. Test each agent individually (prompt engineer, coder, researcher)
2. Connect them in TreeShell flow
3. Build The Flow that creates agents from conversation
4. Create Groundhog Day demo
5. Release and see if community forms

---

This is not an agent framework. This is an **agent reproduction system** where agents give birth to themselves from conversation and evolve their own capabilities.