#!/usr/bin/env python3
"""
LangGraph OmniTool Executor - Single node graph execution
Creates a LangGraph with one omnitool node and executes it
"""

async def execute_omnitool_graph(args):
    """
    Execute a LangGraph with a single omnitool node.
    
    Args:
        args: Dict with tool_name and parameters
        
    Returns:
        Tuple of (result_string, success_bool)
    """
    tool_name = args.get("tool_name", "").strip()
    parameters = args.get("parameters", {})
    
    if not tool_name:
        return "❌ Please provide a tool_name", False
    
    try:
        # Import HEAVEN LangGraph system
        from heaven_base.langgraph.foundation import omnitool_call_runner, HeavenState
        
        # Create HEAVEN state for the graph
        state = HeavenState({
            "results": [],
            "context": {},
            "agents": {}
        })
        
        # Execute the single omnitool node in the graph
        result = await omnitool_call_runner(
            state,
            tool_name=tool_name,
            parameters=parameters
        )
        
        # Extract and format the result
        if "error" in result:
            return f"❌ LangGraph Execution Error: {result['error']}", False
        
        # Format success result
        result_text = f"""🧩 **LangGraph OmniTool Execution**
**Tool:** {tool_name}
**Parameters:** {parameters}

**Result:** {result.get('result', 'No result returned')}

**Graph State:** {result}"""
        
        return result_text, True
        
    except Exception as e:
        import traceback
        error_msg = f"""❌ Error executing LangGraph: {str(e)}

**Exception Type:** {type(e).__name__}
**Traceback:**
```
{traceback.format_exc()}
```"""
        return error_msg, False