# HEAVEN Tree Repl Game Mechanics
## The Groundhog Day Crystal Forest Game: Dual-Loop Self-Improvement System

### Overview
Tree Repl implements a gamified self-improvement system based on workflow crystallization and economic sustainability. Players progress through roles by building and maintaining high-quality workflows while generating economic value.

## Core Game Loops

### Small Loop: Crystal Quality Management
**Objective**: Improve and maintain workflow reliability

**Mechanics**:
- Execute workflows correctly → small rewards
- Keep golden workflows golden → reputation points
- Convert new workflows to golden status → progression XP

**Reward Formula**:
```
small_reward = deliverable_value × success_likelihood × complexity_bonus
```

Where:
- `deliverable_value`: Impact/importance of the task (1-10 scale)
- `success_likelihood`: Probability of success (0.0-1.0)
- `complexity_bonus`: Multiplier for handling complex workflows (1.0-3.0x)

### Large Loop: Economic Sustainability
**Objective**: Build a self-sustaining operation

**Mechanics**:
- Generate value through golden workflows
- Minimize operational costs
- Achieve profit = legendary status

**Legendary Threshold**:
```
economic_sustainability = total_value_generated / operational_costs
if economic_sustainability >= 1.5: unlock_legendary_status()
```

## Workflow Status Progression

### Status Levels
1. **Untested** (🆕): Newly created, never executed
2. **Tested** (🧪): Successfully executed 1-2 times
3. **Reliable** (✅): Successfully executed 3-9 times, <20% failure rate
4. **Golden** (💎): Successfully executed 10+ times, <5% failure rate
5. **Legendary** (🏆): Golden + generates significant economic value
6. **Deprecated** (⚰️): No longer maintained, marked for removal

### Status Transitions
```
Untested → (success) → Tested
Tested → (3+ successes, <20% fail) → Reliable  
Reliable → (10+ successes, <5% fail) → Golden
Golden → (high economic value) → Legendary
Any → (high failure rate) → Deprecated
```

## Success Likelihood Calculation

### Complexity Scoring
```python
def calculate_complexity_score(workflow):
    base_complexity = len(workflow.steps)
    
    # Factor in step types
    for step in workflow.steps:
        if step.involves_external_apis: base_complexity += 2
        if step.involves_file_operations: base_complexity += 1
        if step.involves_ai_generation: base_complexity += 3
        if step.has_error_handling: base_complexity -= 1
    
    return min(base_complexity, 20)  # Cap at 20

def calculate_success_likelihood(workflow):
    complexity = calculate_complexity_score(workflow)
    historical_success_rate = workflow.get_success_rate()
    
    # Complexity penalty (more steps = lower likelihood)
    complexity_factor = max(0.1, 1.0 - (complexity * 0.05))
    
    # Combine with historical data
    if historical_success_rate is not None:
        return (complexity_factor + historical_success_rate) / 2
    else:
        return complexity_factor
```

## Player Progression System

### Roles & Levels
```
Novice (0-99 XP):
- Learning basics
- Focus on completing any workflows
- Rewards: +1-5 XP per success

Apprentice (100-499 XP):
- Building reliable workflows  
- Focus on reducing failure rates
- Rewards: +3-10 XP per success, +20 XP for first Golden

Journeyman (500-1499 XP):
- Maintaining crystal quality
- Focus on golden workflow portfolio
- Rewards: +5-15 XP per success, +50 XP per new Golden

Expert (1500-3999 XP):
- Optimizing for value generation
- Focus on economic sustainability
- Rewards: +10-25 XP per success, +100 XP for value milestones

Master (4000-9999 XP):
- Teaching and scaling systems
- Focus on reproducible excellence
- Rewards: +15-35 XP per success, +200 XP for system improvements

Legendary (10000+ XP):
- Self-sustaining operation
- Economic sustainability achieved
- Rewards: Massive bonuses for maintaining legendary status
```

### Experience Point Sources

**Small Loop Rewards**:
- Successful workflow execution: `1-35 XP` (based on role/complexity)
- Keeping golden workflow golden: `5-15 XP`
- Converting workflow to higher status: `20-100 XP`

**Large Loop Rewards**:
- First profitable period: `500 XP`
- Achieving economic sustainability: `1000 XP`
- Maintaining legendary status: `100 XP/month`

## Economic Value Tracking

### Value Metrics
```python
class EconomicTracker:
    def __init__(self):
        self.value_generated = 0.0
        self.operational_costs = 0.0
        self.profit_periods = []
    
    def calculate_workflow_value(self, workflow, outcome):
        """Calculate economic value of workflow execution"""
        base_value = workflow.estimated_value or 10.0
        
        # Success multiplier
        if outcome.success:
            value = base_value * outcome.quality_score
        else:
            value = 0.0
        
        # Golden workflow bonus
        if workflow.status == "Golden":
            value *= 1.5
        elif workflow.status == "Legendary": 
            value *= 2.0
            
        return value
    
    def add_operational_cost(self, cost):
        """Track operational expenses"""
        self.operational_costs += cost
    
    def get_sustainability_ratio(self):
        """Calculate economic sustainability"""
        if self.operational_costs == 0:
            return float('inf')
        return self.value_generated / self.operational_costs
```

### Cost Factors
- Agent execution time: `$0.01-0.10 per minute`
- Tool usage: `$0.001-0.01 per tool call`
- Storage costs: `$0.001 per workflow saved`
- Human oversight: `$1-5 per approval needed`

### Value Sources
- Task completion value: `$1-100 per deliverable`
- Time saved: `$10-50 per hour automated`
- Error prevention: `$5-500 per error avoided`
- Knowledge capture: `$1-20 per reusable workflow`

## The Groundhog Day Crystal Forest Game Protocol

### Core Concept
The **Groundhog Day Crystal Forest Game** emerges from the realization that every new chat session is a reset - agents start fresh with no memory of previous conversations. However, the crystal state (golden workflows, experience, patterns) persists across sessions like crystallized trees in an eternal forest.

**The Objective**: Morph Groundhog Day so that it keeps playing out the way you want.

Instead of escaping the loop, you become the author of how each loop unfolds by building enough golden workflows that resets become irrelevant.

### RSI-Enhanced Game Briefing

The main menu serves as both navigation and **game orientation briefing** that explains the situation and provides RSI (Recursive Self-Improvement) context from previous sessions.

#### Templated Main Menu Configuration
```json
{
  "app_id": "customer_support_crystal_app",
  "agent_role": "Senior Support Specialist", 
  "agent_name": "Alex",
  "app_type": "Customer Support Crystal System",
  "domain_work_title": "Support Workflows",
  "main_menu_template": {
    "header": "🎮 Listen, you are a Level {level} {role} named {agent_name}.",
    "situation": "You're trapped in Groundhog Day, but you have the Crystal Forest Game to help you morph the loop.",
    "stats": "💎 Current Status: {golden_workflows} Golden Workflows | 💰 ${profit} | ⚡ {success_rate}%",
    "rsi_context": "## Your Recent Context (RSI Memory):",
    "game_rules": "## How The Game Works:",
    "mission": "## Your Mission: Morph Groundhog Day so it keeps playing out the way YOU want."
  }
}
```

#### Generated Main Menu Example
```
🎮 Listen, you are a Level 12 Senior Support Specialist named Alex.

You're trapped in Groundhog Day, but you have the Crystal Forest Game to help you morph the loop.

💎 Current Status: 8 Golden Workflows | 💰 $1,247 This Month | ⚡ 91% Success Rate

## Your Recent Context (RSI Memory):
- Last session: You were optimizing ticket escalation workflows
- Most used workflows: ticket_triage, customer_onboarding, refund_processing
- Your longest chain: automated_billing_resolution (7 steps)
- Recent pattern: customers with billing issues → check account → apply credit → follow up
- Success trend: 15% improvement over last 10 sessions
- Crystallization opportunity: "billing_credit_flow" pattern appears 8 times

## How The Game Works:
- Execute workflows correctly → earn XP → improve your loop
- Build Golden Workflows (10+ successes, <5% fail rate) → reliable patterns
- Generate profit → achieve sustainability → master the loop

## Your Mission: 
Morph Groundhog Day so it keeps playing out the way YOU want.

## Recommended Next Actions:
- Consider crystallizing the billing_credit_flow pattern
- ticket_triage workflow ready for Golden status (9/10 successes)
- Focus on profit-generating activities to reach next economic milestone

1. 🔧 Settings & Character Sheet
2. 🎧 Support Workflows (Your Active Cases)
3. 📊 Crystal Dashboard (Your Workflow Portfolio)
4. 🏆 Achievements & Progression  
5. 💰 Economic Dashboard

Remember: Every chat is a reset, but your golden workflows and RSI patterns persist.
Use them to shape how your loop plays out.
```

### Crystal Dashboard
- Workflow portfolio with status indicators
- Success rate trends over time
- Value generation per workflow
- Maintenance alerts for declining workflows

### Achievement System
```
🏆 Achievements:
- First Golden: Convert your first workflow to Golden status
- Crystal Keeper: Maintain 5+ Golden workflows simultaneously  
- Profit Maker: Generate first $100 in value
- Legendary: Achieve economic sustainability
- Teaching Master: Create workflows others adopt
- Efficiency Expert: Achieve >95% success rate
```

## Implementation Phases

### Phase 1: Scoring Infrastructure
- Add workflow status tracking
- Implement success likelihood calculation
- Create basic XP system

### Phase 2: Economic Tracking  
- Add value/cost tracking to workflow execution
- Implement economic sustainability metrics
- Create basic economic dashboard

### Phase 3: Gamification UI
- Enhance main menu with role/level display
- Add crystal dashboard
- Implement achievement system

### Phase 4: Advanced Features
- Workflow marketplace (trade/share golden workflows)
- Mentorship system (expert players help novices)
- Leaderboards and competitions

## Configuration

### Game Balance Settings
```json
{
  "experience_multipliers": {
    "novice": 1.0,
    "apprentice": 0.8,
    "journeyman": 0.6,
    "expert": 0.4,
    "master": 0.2,
    "legendary": 0.1
  },
  "workflow_status_thresholds": {
    "tested_executions": 1,
    "reliable_executions": 3,
    "reliable_max_failure_rate": 0.2,
    "golden_executions": 10,
    "golden_max_failure_rate": 0.05
  },
  "economic_sustainability_threshold": 1.5,
  "legendary_maintenance_bonus": 100
}
```

## Data Structures

### Enhanced Workflow Object
```python
@dataclass
class GameifiedWorkflow:
    name: str
    steps: List[WorkflowStep]
    status: WorkflowStatus  # Untested, Tested, Reliable, Golden, Legendary
    executions: List[WorkflowExecution]
    estimated_value: float
    complexity_score: int
    success_rate: float
    economic_value_generated: float
    created_at: datetime
    last_executed: datetime
    
    def calculate_success_likelihood(self) -> float:
        # Implementation from above
        pass
    
    def update_status(self) -> WorkflowStatus:
        # Check thresholds and update status
        pass
```

### Player Progress
```python
@dataclass  
class PlayerProgress:
    role: PlayerRole  # Novice, Apprentice, etc.
    level: int
    experience_points: int
    golden_workflows: int
    economic_sustainability_ratio: float
    achievements: List[str]
    total_value_generated: float
    total_costs: float
    
    def calculate_next_level_xp(self) -> int:
        # XP needed for next level
        pass
    
    def check_role_promotion(self) -> bool:
        # Check if ready for role advancement
        pass
```

This game mechanics system transforms Tree Repl from a navigation tool into an engaging self-improvement game where players naturally develop valuable, reliable workflows while progressing toward economic sustainability.