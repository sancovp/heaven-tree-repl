# Workflow Status System and Execution Modes

## Workflow Status System

### Three States
1. **Unran** - Workflow never executed
2. **Quarantine** - Workflow executed but awaiting human approval
3. **Golden** - Human-approved workflow, trusted for automation

### State Transitions
- **Unran → Quarantine**: Occurs on first execution of any workflow
- **Quarantine → Golden**: Requires explicit human approval through ApprovalQueue
- **No automatic promotion** - Human judgment is the only path to Golden status

## Execution Modes

### Liquid Mode (Development/Exploration)
**Capabilities:**
- Execute ANY workflow (Unran, Quarantine, Golden)
- Generate NEW workflows dynamically
- Modify tree structure
- Create new pathways
- Send workflows to quarantine for approval

**Purpose:** Discovery, experimentation, pattern finding, development

**Use Cases:**
- Developing new automation patterns
- Exploring solution spaces
- Testing hypotheses
- Building initial workflows

### Crystal Mode (Production/Operations)
**Capabilities:**
- Execute ONLY Golden workflows
- Cannot create new workflows
- Cannot modify tree structure
- Cannot generate quarantine requests
- Guaranteed safe execution

**Purpose:** Safe production execution, business operations

**Use Cases:**
- Running business operations
- Production automation
- Customer-facing workflows
- Any context requiring guaranteed safety

## Standard Operating Procedures (SOPs)

### Definition
SOPs are Golden workflows that are **involved in any profit-generating workflow chain**.

### Identification Logic
```python
def is_sop(workflow):
    if workflow.status != "Golden":
        return False
    
    # Direct profit generation
    if workflow.profit_generated > 0:
        return True
    
    # Part of profit-generating chain
    for other_workflow in golden_workflows:
        if other_workflow.profit_generated > 0:
            if workflow in other_workflow.dependency_chain:
                return True
    
    return False
```

### SOP Characteristics
- Always Golden status (human-approved)
- Part of value generation chain
- Critical for business operations
- Form the "equipment slots" in Business phase

## View Filters

### Full Tree View
- Shows all workflows regardless of status
- Available in Liquid mode only
- Used for development and debugging

### Crystal View
- Shows only Golden workflows
- Available in both modes
- Used for viewing trusted automation

### Business View
- Shows only SOPs (profit-generating Golden workflows)
- Available in Crystal mode
- Used for business operations

## Integration with ApprovalQueue

The existing `ApprovalQueue` class in `tree_shell.py` handles the quarantine → golden transition:

1. **Workflow Execution in Liquid Mode**:
   - New workflow runs → enters Quarantine status
   - ApprovalQueue receives approval request
   - Human reviews execution results

2. **Human Approval Process**:
   - View pending approvals
   - Review workflow steps and results
   - Approve → workflow becomes Golden
   - Reject → workflow remains in Quarantine (or deleted)

3. **Crystal Mode Execution**:
   - Only Golden workflows visible
   - No approval requests generated
   - Safe for autonomous operation

## Mode Switching

### Command Interface
```
mode liquid  # Switch to development mode
mode crystal # Switch to production mode
```

### Mode Persistence
- Mode setting persists across sessions
- Default mode configurable in settings
- Business entities default to Crystal mode

## Safety Implications

### Liquid Mode Risks
- Can execute untested code
- Can modify system structure
- Requires human oversight
- Generates quarantine requests

### Crystal Mode Guarantees
- Only executes human-approved workflows
- No structural modifications
- Safe for autonomous operation
- No unexpected behavior

## Implementation Notes

### Data Structure
```python
@dataclass
class Workflow:
    name: str
    coordinate: str
    status: WorkflowStatus  # Unran, Quarantine, Golden
    execution_count: int
    profit_generated: float
    dependency_chain: List[str]  # Other workflows this depends on
    last_executed: datetime
    approved_by: str  # Human who approved (if Golden)
    approved_at: datetime  # When approved (if Golden)
```

### Mode Enforcement
```python
class TreeShell:
    def __init__(self):
        self.execution_mode = "liquid"  # or "crystal"
        
    def can_create_workflow(self):
        return self.execution_mode == "liquid"
    
    def can_execute_workflow(self, workflow):
        if self.execution_mode == "crystal":
            return workflow.status == "Golden"
        return True  # Liquid mode can execute anything
```

This simplified system creates a clear separation between development (Liquid) and production (Crystal) environments, with human approval as the bridge between them.