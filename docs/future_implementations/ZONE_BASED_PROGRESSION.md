# Zone-Based Progression System

## Level Zones (Skill-Based Progression)

### Levels 1-10: PROMPT ENGINEERING ZONE
**Focus**: Master the art of AI communication
**XP Sources**: 
- Prompt files created (`/prompts/*.txt`)
- Prompt executions in workflows
- Prompt effectiveness scores

**Zone Objectives**:
- Create your first prompt
- Build 10 different prompts
- Master system prompt patterns
- Create prompt chains
- **Zone Finale**: Build a prompt that achieves >95% success rate

### Levels 10-20: TOOLING ZONE  
**Focus**: Create reusable automation components
**XP Sources**:
- Tool files created (`/tools/*.py`)
- Tool executions in workflows
- Tool integration complexity

**Zone Objectives**:
- Create your first tool
- Build 10 different tools
- Master tool-agent integration
- Create tool chains
- **Zone Finale**: Build a tool used by multiple agents

### Levels 20-30: AGENT ENGINEERING ZONE
**Focus**: Design intelligent agent systems  
**XP Sources**:
- Agent pairs created (`*_config.py` + `*_agent.py`)
- Agent executions
- Agent specialization depth

**Zone Objectives**:
- Create your first agent
- Build 10 specialized agents
- Master agent-tool coordination
- Create multi-agent workflows
- **Zone Finale**: Build an agent that manages other agents

### Levels 30-40: APP CREATION ZONE
**Focus**: Build complete tree repl applications
**XP Sources**:
- Tree repl app configs created
- App complexity (nodes, pathways)
- App usage and adoption

**Zone Objectives**:
- Create your first tree repl app
- Build 5 different app types
- Master workflow orchestration
- Create golden workflow portfolios
- **Zone Finale**: Build an app that generates consistent value

### Levels 40+: META-APP ZONE (Endgame)
**Focus**: Connect apps and build business systems
**XP Sources**:
- App interconnections created
- Cross-app workflow chains
- Business system complexity
- Profit generation (when calculable)

**Zone Objectives**:
- Connect 2 apps via shared workflows
- Build meta-workflows that manage multiple apps
- Create business process automation
- Scale to Business stage (when profit calculation available)
- **Endgame**: Achieve sustained profit and business operations

## TITLE System (Intelligence-Based)

### Title Calculation (Smart Scoring)
Titles are assigned based on **system sophistication analysis**, not level:

```python
def calculate_title_score():
    domain_coverage = count_domains_with_golden_workflows()
    automation_depth = longest_golden_workflow_chain()  
    integration_score = cross_domain_workflow_connections()
    meta_system_count = workflows_that_manage_workflows()
    
    sophistication_score = (
        domain_coverage * 20 +      # Breadth
        automation_depth * 15 +     # Depth  
        integration_score * 10 +    # Integration
        meta_system_count * 25      # Meta-intelligence
    )
    
    return sophistication_score
```

### Title Thresholds
- **Novice**: 0-29 (Basic single-domain work)
- **Apprentice**: 30-59 (Multiple domains, simple automation)
- **Journeyman**: 60-99 (Cross-domain integration, reliable workflows)
- **Expert**: 100-149 (Sophisticated automation, deep specialization)
- **Master**: 150-199 (Meta-systems, teaching other agents)
- **Grandmaster**: 200+ (Innovation, system-of-systems mastery)

### Title Examples
- **Level 45 Apprentice**: High-level creator but systems aren't sophisticated
- **Level 25 Expert**: Lower level but built incredibly sophisticated integrated systems
- **Level 100 Novice**: Prolific creator but no system integration

## STAGE System (Economic Reality)

### Current Implementation
```python
stage = "Persona"  # Default for now

# Future when profit calculation available:
# stage = "Business" if sustained_profit > threshold else "Persona"
```

### Stage Characteristics
**PERSONA Stage**:
- Building and learning phase
- Focus on skill development across zones
- Golden workflow accumulation
- System sophistication improvement

**BUSINESS Stage** (Future):
- Profit-generating operations
- Equipment slot management (SOPs)
- Business optimization focus
- Scaling and expansion

## Zone Progression Mechanics

### Zone Completion Requirements
Each zone has **skill gates** rather than arbitrary level requirements:

**Prompt Zone → Tool Zone**: Must have 5+ effective prompts
**Tool Zone → Agent Zone**: Must have 5+ functional tools  
**Agent Zone → App Zone**: Must have 3+ working agents
**App Zone → Meta Zone**: Must have 1+ profitable app (future)

### Cross-Zone Synergies
- Prompts created in early zones become components in later zones
- Tools built in tool zone get used by agents in agent zone
- Agents created become components in app zone
- Apps become components in meta-zone business systems

### Zone "Rested XP" Equivalent
- Returning to lower zones gives bonus XP for creating improved versions
- "Refactoring bonus": Improving prompts/tools/agents you built earlier
- Encourages iterative improvement rather than just forward progress

## Integration with Tree Shell

### Progress Tracking
```python
class TreeShell:
    def __init__(self):
        self.player_progress = {
            "level": 1,
            "current_zone": "prompt_engineering",
            "zone_progress": {},
            "title": "Novice", 
            "title_score": 0,
            "stage": "Persona"
        }
    
    def update_zone_progress(self):
        level = self.calculate_level_from_xp()
        current_zone = self.get_zone_for_level(level)
        title_score = self.calculate_title_score()
        title = self.get_title_for_score(title_score)
        
        self.player_progress.update({
            "level": level,
            "current_zone": current_zone,
            "title": title,
            "title_score": title_score
        })
```

### Zone-Aware Commands
- `zone_status` - Show current zone progress and objectives  
- `zone_objectives` - List current zone's quests/goals
- `assess_system` - Analyze system sophistication for title calculation
- `zone_graduate` - Check if ready to advance to next zone

This system provides clear skill progression paths while maintaining meaningful title recognition based on actual system sophistication, not just grinding levels.