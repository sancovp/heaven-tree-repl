# HEAVEN LEGOs Integration with Tree Repl

This document explains how HEAVEN LangGraph LEGOs are integrated with the Tree Repl system, combining the power of AI agent workflows with the structured navigation and quarantine/golden approval system.

## Overview

The integration creates a bridge between:

- **HEAVEN LangGraph LEGOs**: Composable AI agent workflow components
- **Tree Repl System**: Coordinate-based navigation with quarantine/golden lifecycle
- **Agent Approval Workflow**: Fresh → Quarantined → Golden progression

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                Tree Repl Navigation                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐             │
│  │ Node    │───▶│ Node    │───▶│ Node    │             │
│  │ 0.1.1   │    │ 0.1.2   │    │ 0.1.3   │             │
│  └─────────┘    └─────────┘    └─────────┘             │
│       │              │              │                   │
│       ▼              ▼              ▼                   │
│  ┌─────────────────────────────────────────────────────┐ │
│  │            HEAVEN LEGOs Integration              │ │
│  │  • Simple Completion (completion_runner)          │ │
│  │  • Iterative Workflows (hermes_legos)             │ │
│  │  • Agent Chains (build_agent_chain_graph)         │ │
│  │  • Analysis Workflows (specialized agents)        │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                         │
│  ┌─────────────────────────────────────────────────────┐ │
│  │           Quarantine/Golden System                  │ │
│  │  Fresh → Quarantined → Golden                       │ │
│  │  User Approval Required for Reuse                   │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Key Components

### 1. HeavenTreeIntegration Class

Central integration layer that provides:

- **Agent Management**: Create and manage HEAVEN agents
- **Workflow Execution**: Execute LangGraph LEGOs workflows
- **State Management**: Maintain session state across tree navigation
- **Error Handling**: Graceful failure and recovery

```python
from heaven_legos_integration import HeavenTreeIntegration

integration = HeavenTreeIntegration()

# Create specialized agents
agent = integration.create_agent(
    "math_expert", 
    "You are a mathematics expert. Solve problems step by step."
)

# Execute workflows
result = await integration.iterative_workflow(
    "Solve this complex math problem", 
    max_iterations=3,
    agent_name="math_expert"
)
```

### 2. Tree Repl Compatible Functions

Functions that can be called directly from tree repl configurations:

```python
# Simple completion
def _heaven_simple_completion(prompt: str, agent: str = "default") -> str

# Iterative workflow  
def _heaven_iterative_workflow(goal: str, iterations: int = 3, agent: str = "default") -> str

# Data analysis
def _heaven_analyze_data(data: str, analysis_type: str = "general") -> str

# Agent chains
def _heaven_chain_workflow(input_data: str, workflow_config: str) -> str

# Agent creation
def _heaven_create_agent(name: str, system_prompt: str, model: str = "gpt-4.1-mini") -> str
```

### 3. Tree Configuration Integration

Tree repl nodes can directly use HEAVEN functions:

```json
{
  "heaven_completion": {
    "type": "Callable",
    "prompt": "HEAVEN Simple Completion",
    "description": "Execute prompt using HEAVEN agent",
    "signature": "completion(prompt: str, agent: str) -> str",
    "function_name": "_heaven_simple_completion",
    "args_schema": {
      "prompt": "str",
      "agent": "str"
    }
  }
}
```

## Workflow Patterns

### Pattern 1: Simple Agent Execution

Use HEAVEN agents for single-step processing:

```python
# Tree repl coordinate: 0.1.2
# Function: _heaven_simple_completion
# Args: {"prompt": "Analyze this data", "agent": "analyst"}

result = await heaven_integration.simple_completion(
    "What is the pattern in: 2, 4, 8, 16, ?",
    "pattern_detector"
)
```

### Pattern 2: Iterative Problem Solving

Use LangGraph LEGOs for multi-step workflows:

```python
# Tree repl coordinate: 0.2.1  
# Function: _heaven_iterative_workflow
# Args: {"goal": "Plan a project", "iterations": 3, "agent": "planner"}

result = await heaven_integration.iterative_workflow(
    "Create a comprehensive marketing strategy",
    max_iterations=5,
    agent_name="marketing_expert"
)
```

### Pattern 3: Agent Chains

Chain multiple specialized agents:

```python
# Tree repl coordinate: 0.2.2
# Function: _heaven_chain_workflow
# Args: {"input_data": "raw data", "workflow_config": "[chain_steps]"}

workflow_steps = [
    {"agent": "analyzer", "prompt": "Analyze: {data}"},
    {"agent": "synthesizer", "prompt": "Synthesize: {data}"},
    {"agent": "recommender", "prompt": "Recommend actions: {data}"}
]

result = await heaven_integration.chain_workflow(
    "Customer complaint about slow service",
    json.dumps(workflow_steps)
)
```

### Pattern 4: Specialized Analysis

Use domain-specific agents for analysis:

```python
# Tree repl coordinate: 0.3.1
# Function: _heaven_analyze_data  
# Args: {"data": "dataset", "analysis_type": "math"}

analysis_types = {
    "general": "General purpose analysis",
    "math": "Mathematical/statistical analysis", 
    "text": "Natural language analysis",
    "pattern": "Pattern detection and trends"
}

result = await heaven_integration.agent_analysis(
    "Sales figures: Q1: 100K, Q2: 120K, Q3: 115K, Q4: 140K",
    "math"
)
```

## Quarantine/Golden Integration

The integration works seamlessly with the Tree Repl quarantine system:

### Fresh Execution

```python
# Agent executes HEAVEN workflow for first time
agent_id, tree_agent = user_repl.launch_agent(heaven_config, mode="auto")

# Navigate to HEAVEN-powered node
result = tree_agent.handle_command("jump 0.1.2 {'prompt': 'Hello', 'agent': 'assistant'}")

# Workflow executes immediately (FRESH status)
# Results stored and workflow quarantined for reuse approval
```

### Quarantined State

```python
# Subsequent attempts to reuse workflow are blocked
result = tree_agent.handle_command("jump 0.1.2 {}")

# Returns: {"error": "BLOCKED - workflow quarantined, needs approval"}
# User must approve before reuse
```

### Golden Approval

```python
# User approves workflow for autonomous reuse
pending = user_repl.list_pending_approvals()
approval_id = pending[0]['approval_id']

user_repl.approve_workflow(approval_id, mark_golden=True)

# Now workflow can be reused autonomously
result = tree_agent.handle_command("jump 0.1.2 {}")
# Executes successfully without user intervention
```

## Configuration Examples

### Complete Tree Config with HEAVEN LEGOs

See `heaven_tree_config.json` for a full example that includes:

- **Agent Management**: Create and list HEAVEN agents
- **Workflow Patterns**: Iterative, chain, and analysis workflows
- **Examples**: Pre-configured demonstrations
- **Custom Builders**: Interactive workflow construction

### Usage Patterns

```bash
# Run the demo
python heaven_tree_demo.py

# Interactive mode
python heaven_tree_demo.py --interactive

# Test integration
python heaven_legos_integration.py
```

## Benefits of Integration

### 1. Structured AI Workflows

- **Geometric Navigation**: Use tree coordinates to organize AI workflows
- **Reusable Patterns**: Save and reuse successful workflow patterns
- **Approval Gates**: Human oversight for autonomous AI operations

### 2. HEAVEN LEGOs Power

- **Composable Components**: Mix and match workflow building blocks
- **Agent Specialization**: Create domain-specific AI experts
- **State Management**: Persistent state across workflow steps

### 3. Safe AI Automation

- **Quarantine System**: Test AI workflows before autonomous use
- **Golden Workflows**: Approved patterns for reliable automation
- **User Control**: Explicit approval required for AI pattern reuse

## Development Workflow

### 1. Create HEAVEN Functions

```python
# Add new HEAVEN-powered function
def _heaven_new_workflow(input_data: str, config: str) -> str:
    """New workflow pattern using HEAVEN LEGOs."""
    # Implementation using heaven_integration
    pass
```

### 2. Add to Tree Config

```json
{
  "new_workflow_node": {
    "type": "Callable",
    "function_name": "_heaven_new_workflow",
    "args_schema": {"input_data": "str", "config": "str"}
  }
}
```

### 3. Test and Approve

```python
# Test in tree repl
result = tree_agent.handle_command("jump 0.new.coordinate {args}")

# Approve for reuse if successful
user_repl.approve_workflow(approval_id, mark_golden=True)
```

## Advanced Patterns

### Dynamic Workflow Generation

Use HEAVEN agents to generate new tree repl configurations:

```python
def _heaven_generate_workflow(description: str) -> str:
    """Generate tree repl config using HEAVEN agent."""
    prompt = f"Create a tree repl workflow configuration for: {description}"
    return _heaven_simple_completion(prompt, "workflow_architect")
```

### Self-Modifying Trees

Combine HEAVEN LEGOs with tree repl's meta-operations:

```python
def _heaven_evolve_tree(current_config: str, performance_data: str) -> str:
    """Evolve tree structure using HEAVEN analysis."""
    analysis = _heaven_analyze_data(performance_data, "pattern")
    return _heaven_simple_completion(f"Improve this config based on: {analysis}", "tree_optimizer")
```

### Multi-Modal Integration

Extend HEAVEN LEGOs to handle different data types:

```python
def _heaven_multimodal_analysis(data: str, data_type: str) -> str:
    """Analyze different data types using appropriate HEAVEN agents."""
    type_agents = {
        "text": "text_specialist",
        "code": "code_analyst", 
        "data": "data_scientist",
        "image": "vision_expert"
    }
    agent = type_agents.get(data_type, "general_analyst")
    return _heaven_analyze_data(data, agent)
```

## Conclusion

The HEAVEN LEGOs integration with Tree Repl creates a powerful platform for:

- **Structured AI Development**: Organize AI workflows with geometric precision
- **Safe AI Automation**: Test and approve AI patterns before autonomous use
- **Composable Intelligence**: Build complex AI systems from reusable components
- **Human-AI Collaboration**: Maintain human oversight while enabling AI automation

This integration demonstrates how to combine the flexibility of LangGraph LEGOs with the safety and structure of the Tree Repl system, creating a robust foundation for AI-powered applications.