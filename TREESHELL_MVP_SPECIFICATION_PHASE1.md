# TreeShell MVP Specification - Phase 1: Maker Paradigm Architecture

## Core Concept
TreeShell is a conversational agent genesis platform where agents can spawn, evolve, and package themselves from pure conversation using a hierarchical "Maker" system.

## The Maker Paradigm Architecture

### **Layer 1: Prompt Engineering System**
- **Make Hermes Config** → Hermes Config Specialist Agent
- **Make Prompt** → Prompt Engineering Agent ✅ (implemented)
- **Make Prompt Block** → Prompt Block Specialist Agent
- **Dependencies**: Hermes system docs, prompt block docs, progenitor integration

### **Layer 2: Tool Engineering**
- **Make Tool** → Tool Engineering Agent
- **Make Stateful Tool** → Advanced Tool Agent  
- **Make Registry Entry** → Registry Specialist Agent
- **Dependencies**: HEAVEN tool docs, registry docs, tool creation patterns

### **Layer 3: Agent Engineering**
- **Make Agent Config** → Agent Engineering Agent
- **Make Agent Persona** → Persona Specialist Agent
- **Make Agent TreeShell** → TreeShell Specialist Agent
- **Dependencies**: HEAVEN agent config docs, integration docs, MCP patterns

### **Layer 4: Flow Engineering**
- **Flow** (LangGraph workflow coordinator)
- **FlowTool** (tool that executes the Flow)
- **FlowAgent** (agent with Flow as run override)
- **spawn_orchestrator(Agent)** → creates orchestrator tools for any agent

### **The Orchestration Layer**
- **Master Orchestrator Agent**: Coordinates all Maker specialists
- **Specialist Agents**: Each is an expert in their specific domain
- **LangGraph Integration**: Workflows tie specialists together
- **Flow Override System**: Agents can use LangGraph as their execution engine

## Phase 1 Implementation Plan

### **Current Status** ✅
- TreeShell library integration working
- Prompt Engineering Agent accessible via TreeShell
- Coder Agent accessible via TreeShell
- Basic agent discovery from heaven-framework library

### **Phase 1.1: Prompt Engineering System Enhancement**
1. **Audit existing systems**:
   - Core progenitor system (system prompts)
   - Hermes config system (now in heaven-framework)
   - Prompt block system
   - Reconcile overlapping functionality

2. **Enhance Prompt Engineering Agent**:
   - Add awareness of existing prompt engineering tools
   - Integrate with ConstructHermesConfigTool
   - Handle prompt block creation and management
   - Connect to progenitor system patterns

3. **Resolve Dependencies**:
   - Move ConstructHermesConfigTool to heaven-framework
   - Remove agentmaker/toolmaker dependencies OR
   - Make toolmaker/agentmaker available in heaven-framework
   - Document all prompt engineering patterns

### **Phase 1.2: Maker Tool Infrastructure**
1. **Create Maker Tool Base Class**:
   - Standard interface for all Maker tools
   - Automatic specialist agent routing
   - Result packaging and validation
   - Error handling and retry logic

2. **Implement Core Maker Tools**:
   - **MakeHermesConfigTool** → routes to Hermes Config Agent
   - **MakePromptTool** → routes to Prompt Engineering Agent  
   - **MakePromptBlockTool** → routes to Prompt Block Agent

3. **Specialist Agent Coordination**:
   - Each Maker tool calls its specialist agent
   - Results are validated and integrated
   - Dependencies between makers are handled

### **Phase 1.3: LangGraph Integration Foundation**
1. **HEAVEN LangGraph Legos**:
   - Document existing lego system for LLM consumption
   - Create modular, understandable components
   - Add to heaven-framework documentation

2. **Flow System Architecture**:
   - **Flow**: LangGraph workflow that chains Maker tools
   - **FlowTool**: Tool wrapper that executes Flows
   - **FlowAgent**: Agent that uses Flow as run override

3. **Orchestrator Pattern**:
   - `spawn_orchestrator(Agent)` creates orchestrator tools
   - Master orchestrator coordinates specialist agents
   - Self-prompting and result checking loops

## The Enhanced Flow (Phase 1)

### **Maker-Based Agent Genesis**
1. **User describes what they want** in conversation
2. **Master Orchestrator** analyzes requirements
3. **Orchestrator calls appropriate Maker tools**:
   - MakePromptTool → Prompt Engineering Agent creates system prompt
   - MakeHermesConfigTool → Hermes Agent creates workflow config
   - MakeToolTool → Tool Agent creates required capabilities
4. **Flow coordinates** all maker outputs
5. **New agent is assembled** from maker results
6. **Agent packages itself** for distribution

### **Maker Tool Pattern**
```
MakeTool Interface:
- input: requirements/specifications
- specialist_agent: domain expert agent
- output: validated component
- integration: automatic TreeShell node creation
```

### **Orchestration Flow**
```
User Request → Master Orchestrator → Maker Tools → Specialist Agents → Component Assembly → Agent Package
```

## Success Criteria for Phase 1

1. **Prompt Engineering System**:
   - ✅ Prompt Engineering Agent working via TreeShell
   - [ ] Hermes Config creation integrated
   - [ ] Prompt block system working
   - [ ] All prompt systems reconciled

2. **Maker Infrastructure**:
   - [ ] Maker tool base class implemented
   - [ ] Core maker tools working (Prompt, Hermes Config)
   - [ ] Specialist agent routing functional

3. **Basic Flow**:
   - [ ] Simple conversation → agent workflow working
   - [ ] LangGraph integration foundation laid
   - [ ] Master orchestrator prototype functional

## Phase 1 Deliverables

1. **Enhanced TreeShell** with Maker tool infrastructure
2. **Integrated Prompt Engineering System** with all components working together
3. **Basic Flow MVP** that can create simple agents from conversation
4. **Foundation for Phase 2** (Tool Engineering and Agent Engineering layers)

## Next Steps After Phase 1

- **Phase 2**: Tool Engineering layer (Make Tool, Make Stateful Tool)
- **Phase 3**: Agent Engineering layer (Make Agent Config, Make Agent)
- **Phase 4**: Full Flow Engineering with complex orchestration
- **Phase 5**: Community release and content creation

---

This phase 1 focuses on getting the foundational Maker paradigm working with the prompt engineering system, setting up the architecture for the full hierarchical agent creation system.