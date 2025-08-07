#!/usr/bin/env python3
"""
Chain operand executor for TreeShell language.
Executes parsed chain plans with control flow.
"""
from typing import List, Dict, Any, Optional


class OperandExecutor:
    """Execute chain plans with control flow operands."""
    
    def __init__(self, tree_shell):
        self.shell = tree_shell
        self.execution_state = {
            'step_results': {},
            'branch_taken': None,
            'loop_active': False,
            'should_break': False
        }
    
    async def execute_plan(self, execution_plan: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute a parsed chain plan with operands."""
        results = []
        current_segment = -1
        skip_remaining_in_group = False
        
        i = 0
        while i < len(execution_plan):
            step = execution_plan[i]
            
            # Track segment changes
            if step.get('segment', 0) != current_segment:
                current_segment = step.get('segment', 0)
                skip_remaining_in_group = False
            
            # Handle different step types
            if step.get('role') == 'condition':
                # Execute condition and store result
                result = await self._execute_step(step)
                self.execution_state['last_condition'] = result['success']
                results.append(result)
                
            elif step.get('role') == 'while_condition':
                # Execute while condition
                result = await self._execute_step(step)
                
                if result['success'] and result.get('data'):
                    # Condition true, continue to body
                    self.execution_state['loop_active'] = True
                    results.append(result)
                else:
                    # Condition false, skip body
                    self.execution_state['loop_active'] = False
                    # Skip all steps with matching condition_ref
                    while i + 1 < len(execution_plan) and execution_plan[i + 1].get('condition_ref') == i:
                        i += 1
                
            elif step.get('branch') == 'then':
                # Execute only if condition was true
                if self.execution_state.get('last_condition', False):
                    result = await self._execute_step(step)
                    results.append(result)
                else:
                    # Skip then branch
                    pass
                    
            elif step.get('branch') == 'else':
                # Execute only if condition was false
                if not self.execution_state.get('last_condition', True):
                    result = await self._execute_step(step)
                    results.append(result)
                    
            elif step.get('loop') == 'while_body':
                # Execute while body
                if self.execution_state.get('loop_active', False):
                    result = await self._execute_step(step)
                    results.append(result)
                    
                    # After body execution, loop back to condition
                    if i == len(execution_plan) - 1 or execution_plan[i + 1].get('loop') != 'while_body':
                        # Find condition step
                        cond_ref = step.get('condition_ref')
                        if cond_ref is not None and cond_ref < len(execution_plan):
                            # Jump back to condition
                            i = cond_ref - 1  # Will be incremented at end of loop
                            
            elif step.get('operator') == 'and':
                # Execute 'and' operation (also execute with existing data)
                if not skip_remaining_in_group:
                    result = await self._execute_step(step)
                    results.append(result)
                    
            elif step.get('operator') == 'or':
                # Execute 'or' operation (alternative with existing data)
                # Check if we should execute based on previous results in group
                group = step.get('operator_group', 0)
                
                # Look for previous results in same or group
                should_execute = True
                for prev_result in results:
                    if prev_result.get('operator_group') == group - 1:
                        if prev_result.get('success', False):
                            should_execute = False
                            break
                
                if should_execute and not skip_remaining_in_group:
                    result = await self._execute_step(step)
                    results.append(result)
                    if result.get('success', False):
                        skip_remaining_in_group = True
                        
            else:
                # Regular sequential execution
                if not skip_remaining_in_group:
                    result = await self._execute_step(step)
                    results.append(result)
            
            i += 1
        
        return {
            'execution_complete': True,
            'total_steps': len(execution_plan),
            'executed_steps': len(results),
            'results': results,
            'final_state': self.execution_state
        }
    
    async def _execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single step."""
        target = step['target']
        args = step.get('args', {})
        
        # Resolve shortcut if needed
        final_coord = self._resolve_target(target)
        
        if final_coord is None:
            return {
                'success': False,
                'error': f"Target '{target}' not found",
                'step': step
            }
        
        # Substitute variables in args
        if isinstance(args, dict):
            args = self._substitute_variables(args)
        
        # Execute the action
        try:
            result, success = await self.shell._execute_action(final_coord, args)
            
            # Store result for variable access
            step_num = len(self.execution_state['step_results']) + 1
            self.execution_state['step_results'][f'step{step_num}_result'] = result
            self.execution_state['last_result'] = result
            
            return {
                'success': success,
                'data': result,
                'target': target,
                'resolved': final_coord,
                'step': step,
                'operator': step.get('operator'),
                'operator_group': step.get('operator_group')
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'step': step
            }
    
    def _resolve_target(self, target: str) -> Optional[str]:
        """Resolve target to coordinate (handle shortcuts)."""
        # Check if it's already a coordinate
        if target in self.shell.nodes:
            return target
        
        # Check shortcuts
        shortcuts = self.shell.session_vars.get("_shortcuts", {})
        if target in shortcuts:
            shortcut = shortcuts[target]
            if isinstance(shortcut, dict) and shortcut.get("type") == "jump":
                return shortcut["coordinate"]
            elif isinstance(shortcut, str):  # Legacy format
                return shortcut
        
        return None
    
    def _substitute_variables(self, args: dict) -> dict:
        """Substitute variables from execution state."""
        if not isinstance(args, dict):
            return args
            
        substituted = {}
        for key, value in args.items():
            if isinstance(value, str) and value.startswith("$"):
                var_name = value[1:]
                
                # Check step results
                if var_name in self.execution_state['step_results']:
                    substituted[key] = self.execution_state['step_results'][var_name]
                elif var_name == 'last_result':
                    substituted[key] = self.execution_state.get('last_result')
                else:
                    # Check shell session vars
                    substituted[key] = self.shell.session_vars.get(var_name, value)
            else:
                substituted[key] = value
                
        return substituted