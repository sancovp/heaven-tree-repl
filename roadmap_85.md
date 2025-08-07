# TreeShell Development Roadmap 8.5
*The Path to Universal Computational Substrate*

## Executive Summary

TreeShell will evolve into a universal application builder where anything that can be described can be built. Through a hierarchical agent system, we'll create a meta-computational environment where TreeShell builds TreeShells, agents orchestrate agents, and workflows compose workflows.

## The Complete Architecture

### Tier 1: Base Agents
- **Default Researcher** - Autonomous research with TreeShell orchestration
- **Default Coder** - Human-supervised coding with approval gates

### Tier 2: Workflow Compositions
- **MCP Generator Workflow** - Uses Default Coder for MCP development
- **update_some_github_repo** - Hardcoded chain workflow pattern

### Tier 3: Super Agents  
- **SGHC Agent** - Ultimate orchestrator that:
  - Uses Default Researcher for investigation
  - Calls MCP Generator Workflow for development
  - Handles GitHub through its own subagents
  - Knows the entire HEAVEN ecosystem

### Tier 4: Meta-System
- **User TreeShell** - Controls all tiers, builds fullstack TreeShells, executes HEAVEN LangGraph nodes arbitrarily

## Implementation Phases

### Phase 1: Foundation (Current)
- ✅ TreeShell MCP integration working
- ✅ Conversation management system
- ✅ OmniTool access to 96+ HEAVEN tools
- ✅ Callable node system with 3 implementation approaches

### Phase 2: Base Agents
**Default Coder Agent**
- Container spawn functionality in existing agents
- Conversation-based workflow using history_id continuation
- Block report format for status communication
- GitHub workflow automation (setup.py, pyproject.toml, tag, push → PyPI)
- Semi-autonomous with human approval gates

**Default Researcher Agent**  
- Fully autonomous with its own TreeShell instance
- Web research workflows
- Code analysis capabilities
- Subagent orchestration through its TreeShell
- Knowledge synthesis and reporting

### Phase 3: Workflow Patterns
**MCP Generator Workflow**
```
User: chain update_some_github_repo {"repo": "heaven-tree-repl", "task": "Add MCP CI/CD"}

→ 0.3.1: ContainerSetupNode 
→ 0.3.2: RepoCloneNode  
→ 0.3.3: FeatureImplementationNode
→ 0.3.4: TestValidationNode
→ 0.3.5: GitHubMergeNode
```

**Hardcoded Chain Commands**
- `chain update_some_github_repo` → Predefined 5-node workflow
- Parameterizable through node arguments
- Always-present nodes in every TreeShell app

### Phase 4: Super Agent (SGHC)
**SGHC Agent Capabilities**
- Research existing patterns (via Default Researcher)
- Generate code (via MCP Generator Workflow)  
- Handle GitHub deployment (via subagents)
- Complete autonomous HEAVEN development
- No human intervention except final approval

**Example SGHC Workflow**
```
SGHC: "I need to add feature X to HEAVEN"
├── Spawns Default Researcher → Research existing patterns
├── Calls MCP Generator Workflow → Generate the code
├── Spawns GitHub Subagent → Handle PR/merge workflow
└── Returns: "Feature X implemented and published"
```

### Phase 5: Meta-System
**User TreeShell as Universal Builder**
```
Us: "Build me a customer support TreeShell"
User TreeShell:
├── Spawns SGHC Agent → Research customer support patterns
├── Calls MCP Generator → Build support-specific MCPs
├── Spawns Default Coder → Generate TreeShell app structure
├── Executes HEAVEN LangGraph nodes → Deploy the system
└── Result: Complete customer support TreeShell ready to use
```

## Technical Architecture Patterns

### Conversation-Based Workflows
Instead of complex orchestration, workflows emerge through TreeShell's pathway system:
- Each node = one conversation phase
- history_id = workflow state continuation
- Pathways = reusable workflow templates
- Chain commands = automation when desired

### Node Type System (Lego Architecture)
**Safe Node Types** (User App layer):
- AgentNode, ToolNode, ConditionalNode, StateNode, WorkflowNode
- ContainerTestNode, MCPInstallNode, GitWorkflowNode
- All validated through Pydantic schemas
- Impossible to create broken nodes

**Agent Development** (Liquid layer):
- Containerized coder agents with full repo access
- Novel code development in isolated environments
- Proper git workflow and PyPI publishing
- Results consumed by User App as safe node types

### Recursive TreeShell Architecture
**TreeShell All The Way Down**:
```
User TreeShell 
→ Launches Researcher Agent (with its own TreeShell)
  → Researcher's TreeShell launches Web Research Subagent
  → Researcher's TreeShell launches Code Analysis Subagent  
  → Researcher synthesizes findings
→ Returns comprehensive research report to User
```

### State Continuity
- All results retained in TreeShell state
- Infinite composition through history_id chains
- Perfect context preservation across workflow phases
- Arbitrary HEAVEN LangGraph node execution

## Key Design Principles

### Two-Tier Safety Model
- **User App** (Safe Zone) - Node types only, Pydantic validation, configuration-based
- **Agent App** (Liquid Zone) - Containerized development, full code generation, git workflows

### Emergent vs. Explicit Orchestration
- Workflows emerge naturally through pathway traversal
- Chain commands available for automation
- No complex state machines required
- Self-documenting through tree structure

### Universal Substrate Vision
- TreeShell builds TreeShells
- Agents orchestrate agents  
- Workflows compose workflows
- Anything describable becomes buildable

## Expected Outcomes

### Immediate (Phase 2-3)
- Autonomous GitHub repo development workflows
- MCP CI/CD system implementation
- Containerized development environment

### Medium-term (Phase 4)
- SGHC agent capable of autonomous HEAVEN development
- Complete research → code → deploy pipelines
- Multi-agent orchestration systems

### Long-term (Phase 5)
- Universal application builder
- TreeShell as computational substrate
- Infinite scalability through composition
- God-mode development capabilities

## Success Metrics

1. **Time to build new TreeShell applications** - From days to minutes
2. **Autonomous development success rate** - SGHC agent deployment success
3. **Workflow composition complexity** - Number of agents/workflows combinable
4. **State retention accuracy** - Perfect context preservation across phases
5. **User cognitive load** - Simple commands producing complex results

## Conclusion

This roadmap transforms TreeShell from a navigation interface into a **universal computational substrate**. The end state: a system where complex applications, agent ecosystems, and development workflows can be generated through simple natural language descriptions to our User TreeShell.

**We become the architects of autonomous systems**, with TreeShell as our universal building tool.

---
*Roadmap 8.5 - Generated 2025-08-05*
*"TreeShell as Universal Computational Substrate"*