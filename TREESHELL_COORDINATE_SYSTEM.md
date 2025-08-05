# TreeShell Coordinate System Documentation

## Overview

The TreeShell system uses a hierarchical coordinate notation for navigation and action execution. This document specifies the formal behavior of the coordinate system.

## Core Principle

As explained by the system architect:

> "INTROSPECT IS THE DEFAULT BEHAVIOR. Let's say you are going to node 10. You enter 0.0.10. THIS SHOULD TAKE YOU TO: 0.0.10.0 NOTICE WE NOW ARE AT 10.0 NOT 10. WHY? BECAUSE YOU ARE AT 10.0 THE GENERAL VERSION OF THAT NODE WITH NOTHING SELECTED. IE YOU ARE AT THE MENU. If you however went to 0.0.10.1 you would be at THE MENU of action 1 at 0.0.10 so you would really be at 0.0.10.1.0 because you DID NOT ENTER ANY ARGS={} PARAM"

## Coordinate Notation Rules

### Implicit .0 Extension
Every position automatically has an implicit `.0` when no action is specified:
- `0.0.10` = actually `0.0.10.0` (menu/introspect view)
- `0.0.10.1` = actually `0.0.10.1.0` (menu view of action 1)

### Universal Structure

> "EVERY SINGLE POSITION has child 0, 1 AT LEAST, plus every semantic command available in the general system (jump, chain, etc)."

Every position in the system has these standard children:
- **0**: Menu/introspect view (shows description and available args)
- **1**: Execute action (with provided arguments)
- **Universal commands**: jump, chain, build_pathway, save_emergent_pathway, back, menu, exit, etc.

### Recursion and Termination

> "Even those children have children which TERMINATE when you have only 0,1 options"

The coordinate system recurses with each level having 0/1 children until termination. The recursion terminates when only options 0 and 1 remain:
- **0**: Shows information about the action
- **1**: Actually executes the function

## Notation Examples

### Callable Node (Add Node)
```
0.0.2.10          → 0.0.2.10.0 (menu view)
├── 0.0.2.10.0    Shows: "Create a new node in the tree structure" + args schema
└── 0.0.2.10.1    → 0.0.2.10.1.0 (execution menu)
    ├── 0.0.2.10.1.0    Shows: "How to execute add_node"
    └── 0.0.2.10.1.1    Executes: add_node function with args
```

### Menu Node (Meta Operations)
```
0.0.2             → 0.0.2.0 (menu view)
├── 0.0.2.0       Shows: Menu description + available options (1-14)
├── 0.0.2.1       Navigate to: Save Variable (0.0.2.1.0)
├── 0.0.2.2       Navigate to: Get Variable (0.0.2.2.0)
├── ...
└── 0.0.2.14      Navigate to: Get Node (0.0.2.14.0)
```

### Full Execution Path
```
User types: 0.0.2.10
System goes to: 0.0.2.10.0
Display: Menu with description and options

User selects: 1
System goes to: 0.0.2.10.1.0  
Display: Execution instructions

User selects: 1 {"coordinate": "test", "node_data": {...}}
System executes: 0.0.2.10.1.1 with provided args
```

## Implementation Requirements

1. **Automatic .0 appending**: Any coordinate without explicit action gets `.0` appended
2. **Universal 0/1 children**: Every position must provide options 0 and 1
3. **Recursive structure**: Continue until only 0/1 options remain (termination)
4. **Proper descriptions**: Level 0 shows node description and args schema
5. **Function execution**: Terminal level 1 executes the actual function

## Current Implementation Status

The current system does not properly implement this coordinate expansion. The renderer needs to be updated to follow these rules for consistent navigation and execution behavior.