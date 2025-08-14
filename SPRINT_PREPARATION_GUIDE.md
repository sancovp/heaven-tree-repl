# TreeShell Sprint Preparation Guide

## Executive Summary

After fixing the foundational Python object persistence and MCP shell management issues, we have systematically investigated the remaining architectural concerns. This guide catalogues our findings and provides a roadmap for the next development sprint.

## Investigation Results

### ✅ COMPLETED FIXES (v0.1.30 & v0.1.31)
- **Python Object Persistence**: Fixed JSON → Pickle migration for proper object preservation
- **MCP Shell Management**: Fixed broken shell initialization, now maintains persistent instances
- **Conversation History**: Fixed history_id not being passed to agents during chat continuation
- **Error Recovery**: Implemented graceful handling of corrupted session objects
- **Performance**: 378x speed improvement (7ms vs 2900ms per command)

### 🔍 INVESTIGATION FINDINGS

## 1. Meta Add/Update Node Operations Schema

**Status**: ❌ **NEEDS IMPROVEMENT**

**Current Issues**:
- Minimal validation in `_meta_add_node()` and `_meta_update_node()` (meta_operations.py:184-273)
- Basic required field checking only: `["type", "prompt"]`
- No comprehensive schema validation for node structure
- Args schema defaults to empty dict without type checking
- Options structure not validated

**Recommended Schema** (for next sprint):
```python
NODE_SCHEMA = {
    "type": "object",
    "required": ["type", "prompt"],
    "properties": {
        "type": {
            "type": "string", 
            "enum": ["Menu", "Callable"]
        },
        "prompt": {"type": "string", "minLength": 1},
        "description": {"type": "string"},
        "options": {
            "type": "object",
            "patternProperties": {
                "^[0-9]+$": {"type": "string"},  # Numerical keys
                "^[a-zA-Z_][a-zA-Z0-9_]*$": {"type": "string"}  # Semantic keys
            }
        },
        "callable": {
            "type": "object",
            "required": ["function_name", "is_async"],
            "properties": {
                "function_name": {"type": "string"},
                "is_async": {"type": "boolean"},
                "args_schema": {"type": "object"},
                "import_path": {"type": "string"},
                "import_object": {"type": "string"}
            }
        }
    }
}
```

## 2. Node Options and Menu Generation

**Status**: ✅ **WORKING CORRECTLY**

**Verified Behavior**:
- Menu nodes properly display numbered options (1-12 confirmed in system menu)
- Callable nodes correctly show "exec: execute" option
- Options traverse to correct sibling coordinates
- Menu generation logic handles both numeric and semantic option keys

**Evidence**:
```
System Menu (0.1):
  1: Manage Pathways → 2: Meta Operations → etc.
  
Callable Node (0.1.2.5):
  exec: execute
```

**Menu Generation Logic** (base.py:1188-1202):
- ✅ Correctly adds "exec" for callable nodes
- ✅ Enumerates options starting from 1  
- ✅ Resolves target nodes through combo_nodes lookup
- ✅ Falls back to descriptive format when target not found

## 3. Missing Node Options Investigation

**Status**: ✅ **NO MISSING OPTIONS DETECTED**

**Verified**:
- All family configs loaded correctly
- Menu options showing expected counts (system: 12 options, meta: 14 options)
- Callable nodes display exec option properly
- No regression from recent coordinate system changes

## 4. Architecture Verification

**Current State - All Systems Functional**:
- **Session Persistence**: ✅ Pickle-based, handles Python objects
- **MCP Integration**: ✅ Persistent shells, proper initialization  
- **Menu Generation**: ✅ Correct option enumeration and targeting
- **Conversation Flow**: ✅ History context preserved
- **Error Recovery**: ✅ Graceful handling of corrupted objects

## Next Sprint Priorities

### HIGH PRIORITY

#### 1. Node Schema Validation System
**File**: `heaven_tree_repl/meta_operations.py`
**Functions**: `_meta_add_node()`, `_meta_update_node()`
**Effort**: 2-3 hours

**Tasks**:
- Add JSON Schema validation library dependency
- Implement comprehensive node validation 
- Add proper error messages for schema violations
- Test edge cases with malformed node data

#### 2. Enhanced Meta Operations Error Handling
**Effort**: 1-2 hours

**Tasks**:
- Improve error messages in meta operations
- Add rollback capability for failed node additions
- Validate coordinate uniqueness before adding nodes

#### 3. Test Coverage for Meta Operations
**Effort**: 2-3 hours

**Tasks**:  
- Unit tests for all meta operations
- Schema validation test cases
- Edge case testing (malformed data, duplicate coordinates)

### MEDIUM PRIORITY

#### 4. Family Configuration Validation
**Effort**: 2-3 hours
- Validate family JSON files on load
- Check for orphaned node references
- Verify parent-child relationships in family hierarchy

#### 5. Documentation Updates
**Effort**: 1-2 hours
- Update README with new persistence architecture
- Document meta operations API
- Add troubleshooting guide for common issues

### LOW PRIORITY

#### 6. Performance Optimizations
- Optimize combo_nodes lookup for large family configs
- Add caching for frequently accessed node metadata
- Memory usage profiling for large session states

## Technical Debt Assessment

### CRITICAL DEBT - Address Next Sprint
- **Schema Validation**: Meta operations lack proper validation
- **Error Recovery**: Some edge cases in meta operations need better handling

### MINOR DEBT - Future Sprints
- **Type Hints**: Add comprehensive typing to meta_operations.py
- **Test Coverage**: Increase test coverage above 80%
- **Documentation**: API documentation for meta operations

## Development Environment Notes

**Test Command Structure**:
```bash
cd /home/GOD/heaven-tree-repl
PYTHONPATH=/home/GOD/heaven-tree-repl python test_user_treeshell.py "command"
```

**Key Files for Next Sprint**:
- `/heaven_tree_repl/meta_operations.py` - Add schema validation
- `/heaven_tree_repl/base.py` - Menu generation (already working)
- `/heaven_tree_repl/conversation_chat_app.py` - Conversation management (recently fixed)

## Success Metrics

**Definition of Done for Next Sprint**:
1. All meta operations have comprehensive schema validation
2. Schema validation tests pass 100%
3. Error messages are user-friendly and actionable
4. No regression in existing functionality
5. Documentation updated for new validation system

---

**Generated**: 2025-01-13
**Version**: Post v0.1.31 architectural review
**Status**: Ready for next sprint planning