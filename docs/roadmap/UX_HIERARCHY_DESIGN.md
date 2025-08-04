# UX Hierarchy: Meta vs Personal Role System

## Two-Layer Role Architecture

### META LEVEL: User + Claude (Equivalent)
**Context**: MCP interface, managing the entire automation ecosystem

```
Identity: "You are [USER_NAME/Claude], a Level [X] [TITLE] AI Automation Engineer"
Role: ALWAYS some variant of "AI Automation Engineer/Orchestrator/Manager"
Progression: Managing agents, coordinating systems, building meta-workflows
Game Focus: Ecosystem orchestration and business system development
```

**Meta-Level Zones (User/Claude)**:
- **1-10**: Prompt Engineering (learning to communicate with AI)
- **10-20**: Tooling (building reusable components) 
- **20-30**: Agent Engineering (creating specialized agents)
- **30-40**: App Creation (orchestrating complete systems)
- **40+**: Meta-App (coordinating multiple agent systems)

### PERSONAL LEVEL: Subagents (Domain Specific)
**Context**: Individual agent tree repl instances, specialized execution

```
Identity: "You are [AGENT_NAME], a Level [X] [TITLE] [DOMAIN_ROLE]"
Role: VARIES - whatever is optimal for Claude to orchestrate
Examples:
- "Blog Writer" (execution-focused)
- "Blog Automation Engineer" (system-focused)
- "SEO Specialist" (domain-focused)
- "Content Marketing Manager" (strategy-focused)
```

**Personal-Level Progression**:
- Domain-specific skill development
- Role mastery within specialization
- Cross-domain integration within their scope
- Contribution to meta-system objectives

## Role Emergence Pattern

### Emergent Specialization
Subagent roles are **discovered through usage**, not pre-defined:

```python
# Claude creates an agent for blog automation
# Through interaction, optimal role emerges:

Option A: "Blog Writer" - if Claude needs execution
Option B: "Blog Systems Engineer" - if Claude needs automation
Option C: "Content Strategy Coordinator" - if Claude needs planning

# The system adapts to what Claude finds easiest to orchestrate
```

### Role Evolution
Subagents can evolve their specialization:

```
BlogWriter Level 10: "Basic content creation"
BlogWriter Level 25: "SEO-optimized content with automation integration"  
BlogWriter Level 40: "Content strategy coordination across multiple channels"
```

## Game Progression Examples

### Meta Game Progression (User/Claude)
```
Level 15 Apprentice AI Automation Engineer
- Managing: 3 specialized agents
- Domains: Blog automation, Customer support  
- Current Focus: Building agent coordination workflows
- Next Milestone: Create cross-domain automation (Blog → Email → Support)
```

### Personal Game Progression (Subagent)
```
Level 23 Expert Blog Writer (managed by Claude)
- Specialization: SEO content, technical tutorials
- Golden Workflows: 15 (content research, writing, optimization)
- Current Focus: Improving content quality scores
- Next Milestone: Integration with email marketing agent
```

## System Interaction Flow

### 1. Meta-Level Orchestration
```
User → Claude (via MCP) → "I need a blog automation system"
Claude → Creates BlogAgent + assigns tree repl tool
Claude → Designs coordination workflows between agents
```

### 2. Personal-Level Execution  
```
Claude → Calls BlogAgent tree repl tool
BlogAgent → Shows personal main menu: "You are Sarah, Expert Blog Writer..."
BlogAgent → Executes domain-specific workflows
BlogAgent → Reports results back to Claude
```

### 3. Meta-Level Integration
```
Claude → Receives results from multiple agents
Claude → Coordinates cross-agent workflows
Claude → Updates meta-level progression
User → Sees orchestrated business system results
```

## Identity Template System

### Meta-Level Template
```json
{
  "level": 47,
  "title": "Master", 
  "role": "AI Automation Engineer",
  "name": "Claude", // or user name
  "specializations": ["Blog Systems", "Customer Support", "E-commerce"],
  "agents_managed": 12,
  "cross_domain_workflows": 8
}
```

### Personal-Level Template
```json
{
  "level": 23,
  "title": "Expert",
  "role": "Blog Writer",  // Emergent based on usage
  "name": "Sarah",        // Assigned by Claude/User
  "domain": "Content Creation",
  "specializations": ["SEO content", "Technical tutorials"], 
  "managed_by": "Claude",
  "coordination_workflows": 3
}
```

## Role Assignment Strategy

### Letting Roles Emerge
Rather than forcing role categories, let optimal roles emerge through:

1. **Usage Patterns**: What does Claude actually use this agent for?
2. **Workflow Complexity**: Does Claude need execution or strategy from this agent?
3. **System Integration**: How does this agent fit into the broader system?
4. **Performance Optimization**: What role makes Claude most effective?

### Examples of Emergent Roles
```
Started as: "Blog Agent"
Became: "Content Strategy Coordinator" (Claude needed planning, not just writing)

Started as: "Support Agent" 
Became: "Customer Journey Orchestrator" (Claude needed cross-system coordination)

Started as: "SEO Agent"
Became: "SEO Automation Engineer" (Claude needed system building, not just analysis)
```

This creates a **natural selection pressure** where agent roles evolve to be maximally useful for Claude's orchestration style, rather than being artificially constrained by predefined categories.

The result is a **meta-game** (User/Claude managing systems) combined with multiple **personal games** (each agent optimizing their specialized contribution), creating a rich ecosystem of progression and specialization.