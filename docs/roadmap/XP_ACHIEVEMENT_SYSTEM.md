# XP and Achievement System

## XP-Based LEVEL System

### XP Sources (File Creation in HEAVEN_DATA_DIR)

Since we don't have user systems yet, XP is calculated from file creation counts in HEAVEN_DATA_DIR:

```python
xp_sources = {
    "workflow_execution": 10,      # Each workflow run (from execution_history)
    "workflow_creation": 50,       # Count of files in pathways/
    "golden_approval": 100,        # Count of Golden workflows
    "agent_creation": 75,          # Count of *_config.py + *_agent.py files in agents/
    "tool_creation": 25,           # Count of files in tools/
    "prompt_creation": 15,         # Count of files in prompts/
    "chain_execution": 20,         # Count of multi-step chains executed
}
```

### File Counting Logic

```python
def count_heaven_creations(heaven_data_dir="/home/GOD/.heaven/"):
    import os
    import glob
    
    counters = {
        "workflows_created": len(glob.glob(f"{heaven_data_dir}/pathways/*.json")),
        "tools_created": len(glob.glob(f"{heaven_data_dir}/tools/*.py")),
        "agents_created": (
            len(glob.glob(f"{heaven_data_dir}/agents/*_config.py")) +
            len(glob.glob(f"{heaven_data_dir}/agents/*_agent.py"))
        ) // 2,  # Each agent has both config and agent file
        "prompts_created": len(glob.glob(f"{heaven_data_dir}/prompts/*.txt")),
        
        # From tree_shell execution tracking
        "workflow_executions": len(self.execution_history),
        "chains_executed": len([h for h in self.execution_history if h.get("chain_length", 0) > 1]),
        "goldens_created": len([w for w in self.saved_pathways.values() if w.get("status") == "Golden"]),
    }
    
    return counters

def calculate_total_xp(counters):
    return (
        counters["workflow_executions"] * 10 +
        counters["workflows_created"] * 50 +
        counters["goldens_created"] * 100 +
        counters["agents_created"] * 75 +
        counters["tools_created"] * 25 +
        counters["prompts_created"] * 15 +
        counters["chains_executed"] * 20
    )

def calculate_level(total_xp):
    return total_xp // 100  # Every 100 XP = 1 level
```

## Achievement System (10, 100, 1000, 10000 Pattern)

### Achievement Definitions

```python
achievement_thresholds = {
    # Creation achievements based on file counts
    "workflow_creator_i": ("workflows_created", 10),
    "workflow_creator_ii": ("workflows_created", 100),
    "workflow_creator_iii": ("workflows_created", 1000),
    "workflow_creator_iv": ("workflows_created", 10000),
    
    "tool_smith_i": ("tools_created", 10),
    "tool_smith_ii": ("tools_created", 100),
    "tool_smith_iii": ("tools_created", 1000),
    
    "agent_master_i": ("agents_created", 10),
    "agent_master_ii": ("agents_created", 100),
    "agent_master_iii": ("agents_created", 1000),
    
    "prompt_engineer_i": ("prompts_created", 10),
    "prompt_engineer_ii": ("prompts_created", 100),
    "prompt_engineer_iii": ("prompts_created", 1000),
    
    # Execution achievements based on activity
    "executor_i": ("workflow_executions", 10),
    "executor_ii": ("workflow_executions", 100),
    "executor_iii": ("workflow_executions", 1000),
    "executor_iv": ("workflow_executions", 10000),
    
    "golden_builder_i": ("goldens_created", 10),
    "golden_builder_ii": ("goldens_created", 100),
    "golden_builder_iii": ("goldens_created", 1000),
    
    "chain_master_i": ("chains_executed", 10),
    "chain_master_ii": ("chains_executed", 100),
    "chain_master_iii": ("chains_executed", 1000),
}

def check_achievements(counters):
    earned_achievements = []
    
    for achievement_name, (counter_key, threshold) in achievement_thresholds.items():
        if counters.get(counter_key, 0) >= threshold:
            earned_achievements.append(achievement_name)
    
    return earned_achievements
```

## TITLE Calculation Based on Achievements

```python
def calculate_title(earned_achievements):
    """Title based on breadth of achievements earned"""
    achievement_count = len(earned_achievements)
    
    # Count different achievement types
    creation_achievements = len([a for a in earned_achievements if any(x in a for x in ["creator", "smith", "master", "engineer"])])
    execution_achievements = len([a for a in earned_achievements if any(x in a for x in ["executor", "builder", "chain"])])
    
    # Require both creation and execution for higher titles
    if achievement_count >= 15 and creation_achievements >= 8 and execution_achievements >= 7:
        return "Grandmaster"
    elif achievement_count >= 12 and creation_achievements >= 6 and execution_achievements >= 6:
        return "Master"
    elif achievement_count >= 8 and creation_achievements >= 4 and execution_achievements >= 4:
        return "Expert"
    elif achievement_count >= 5 and creation_achievements >= 2 and execution_achievements >= 3:
        return "Journeyman"
    elif achievement_count >= 2:
        return "Apprentice"
    else:
        return "Novice"
```

## STAGE System (Persona vs Business)

```python
def calculate_stage(counters, profit_generated=0.0):
    """Stage based on profit generation (stubbed for now)"""
    # Stubbed until API integrations provide real profit calculation
    has_profit = profit_generated > 0
    
    # Alternative advancement criteria while profit is stubbed:
    # Advanced creators with high execution might qualify for Business stage
    advanced_creator = (
        counters.get("goldens_created", 0) >= 50 and
        counters.get("workflow_executions", 0) >= 500 and
        counters.get("chains_executed", 0) >= 100
    )
    
    return "Business" if (has_profit or advanced_creator) else "Persona"
```

## HEAVEN Data Directory Structure

Expected file structure for counting:

```
$HEAVEN_DATA_DIR/
├── pathways/
│   ├── customer_support_flow.json
│   ├── blog_writing_chain.json
│   └── ... (count = workflows_created)
├── tools/
│   ├── email_sender_tool.py
│   ├── content_generator_tool.py
│   └── ... (count = tools_created)
├── agents/
│   ├── blog_writer_config.py
│   ├── blog_writer_agent.py
│   ├── support_agent_config.py
│   ├── support_agent_agent.py
│   └── ... (count pairs = agents_created)
└── prompts/
    ├── blog_outline_prompt.txt
    ├── customer_response_prompt.txt
    └── ... (count = prompts_created)
```

## Integration with TreeShell

### Progress Tracking Methods

```python
class TreeShell:
    def __init__(self, graph_config: dict):
        # ... existing init ...
        self.heaven_data_dir = os.getenv("HEAVEN_DATA_DIR", "/home/GOD/.heaven/")
        self.player_progress = self.load_player_progress()
    
    def update_player_progress(self):
        """Update player level, title, and achievements based on current state"""
        # Count creations from file system
        counters = count_heaven_creations(self.heaven_data_dir)
        
        # Add execution data from tree_shell
        counters["workflow_executions"] = len(self.execution_history)
        counters["chains_executed"] = len([h for h in self.execution_history if h.get("chain_length", 0) > 1])
        counters["goldens_created"] = len([w for w in self.saved_pathways.values() if w.get("status") == "Golden"])
        
        # Calculate progression
        total_xp = calculate_total_xp(counters)
        level = calculate_level(total_xp)
        earned_achievements = check_achievements(counters)
        title = calculate_title(earned_achievements)
        stage = calculate_stage(counters, profit_generated=0.0)  # Stubbed profit
        
        # Update player progress
        self.player_progress.update({
            "level": level,
            "total_xp": total_xp,
            "title": title,
            "stage": stage,
            "achievements": earned_achievements,
            "counters": counters,
            "last_updated": datetime.datetime.utcnow().isoformat()
        })
        
        self.save_player_progress()
    
    def _execute_action(self, node_coord: str, args: dict):
        """Override to update progress after each execution"""
        result, success = super()._execute_action(node_coord, args)
        
        if success:
            # Update progress after successful execution
            self.update_player_progress()
        
        return result, success
```

## Progress Persistence

Player progress stored in: `~/.tree_repl/player_progress.json`

```json
{
  "level": 15,
  "total_xp": 1520,
  "title": "Journeyman",
  "stage": "Persona",
  "achievements": [
    "workflow_creator_i",
    "tool_smith_i", 
    "executor_ii",
    "golden_builder_i"
  ],
  "counters": {
    "workflows_created": 12,
    "tools_created": 8,
    "agents_created": 3,
    "workflow_executions": 145,
    "goldens_created": 15,
    "chains_executed": 23
  },
  "last_updated": "2024-01-15T10:30:00Z"
}
```

This system provides rich progression tracking based on actual creative output and execution in the HEAVEN ecosystem, with clear achievement milestones that encourage both creation and execution mastery.