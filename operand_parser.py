#!/usr/bin/env python3
"""
Chain operand parser for TreeShell language.
Handles: and, or, if...then...else, while...x
"""
import re
import json
from typing import List, Dict, Any, Tuple, Optional


class OperandParser:
    """Parse chain commands with control flow operands."""
    
    def __init__(self):
        # Token patterns
        self.patterns = {
            'if_then_else': re.compile(r'if\s+(.+?)\s+then\s+(.+?)(?:\s+else\s+(.+?))?(?=\s+(?:and|or|->|$))'),
            'while_x': re.compile(r'while\s+(.+?)\s+x\s+(.+?)(?=\s+(?:and|or|->|$))'),
            'and': re.compile(r'\s+and\s+'),
            'or': re.compile(r'\s+or\s+'),
            'arrow': re.compile(r'\s+->\s+'),
        }
    
    def parse_chain(self, chain_str: str) -> List[Dict[str, Any]]:
        """Parse chain string into execution plan with operands."""
        # First, handle sequential arrows to separate major segments
        segments = self._split_by_arrow(chain_str)
        
        execution_plan = []
        
        for segment_idx, segment in enumerate(segments):
            # Parse each segment for operands
            segment_plan = self._parse_segment(segment)
            
            # Add segment info
            for step in segment_plan:
                step['segment'] = segment_idx
                
            execution_plan.extend(segment_plan)
        
        return execution_plan
    
    def _split_by_arrow(self, chain_str: str) -> List[str]:
        """Split chain by -> but preserve operand structures."""
        # Use a more sophisticated split that respects operand boundaries
        segments = []
        current = []
        
        # Tokenize while respecting quoted strings and braces
        tokens = self._tokenize_respecting_quotes(chain_str)
        
        i = 0
        while i < len(tokens):
            if tokens[i] == '->':
                if current:
                    segments.append(' '.join(current))
                    current = []
            else:
                current.append(tokens[i])
            i += 1
        
        if current:
            segments.append(' '.join(current))
        
        return segments
    
    def _tokenize_respecting_quotes(self, text: str) -> List[str]:
        """Tokenize text while respecting quoted strings and JSON objects."""
        tokens = []
        current_token = []
        in_quotes = False
        in_braces = 0
        quote_char = None
        
        i = 0
        while i < len(text):
            char = text[i]
            
            # Handle quotes
            if char in ('"', "'") and (i == 0 or text[i-1] != '\\'):
                if not in_quotes:
                    in_quotes = True
                    quote_char = char
                elif char == quote_char:
                    in_quotes = False
                    quote_char = None
            
            # Handle braces (for JSON)
            elif char == '{' and not in_quotes:
                in_braces += 1
            elif char == '}' and not in_quotes:
                in_braces -= 1
            
            # Handle spaces as token separators
            elif char == ' ' and not in_quotes and in_braces == 0:
                if current_token:
                    tokens.append(''.join(current_token))
                    current_token = []
                i += 1
                continue
            
            current_token.append(char)
            i += 1
        
        if current_token:
            tokens.append(''.join(current_token))
        
        return tokens
    
    def _parse_segment(self, segment: str) -> List[Dict[str, Any]]:
        """Parse a segment for operands (and, or, if, while)."""
        steps = []
        
        # Check if segment starts with 'if'
        if segment.strip().startswith('if '):
            # Parse if-then-else manually
            parts = segment.split()
            
            # Find 'then' keyword
            then_idx = None
            for i, part in enumerate(parts):
                if part == 'then':
                    then_idx = i
                    break
            
            if then_idx:
                # Extract condition (everything between 'if' and 'then')
                condition_parts = parts[1:then_idx]
                condition = ' '.join(condition_parts)
                
                # Find 'else' keyword
                else_idx = None
                for i, part in enumerate(parts):
                    if part == 'else':
                        else_idx = i
                        break
                
                # Extract then branch
                if else_idx:
                    then_parts = parts[then_idx + 1:else_idx]
                    else_parts = parts[else_idx + 1:]
                else:
                    then_parts = parts[then_idx + 1:]
                    else_parts = []
                
                then_branch = ' '.join(then_parts)
                else_branch = ' '.join(else_parts) if else_parts else None
                
                # Parse condition as a step
                cond_step = self._parse_step(condition)
                cond_step['role'] = 'condition'
                steps.append(cond_step)
                
                # Parse then branch
                then_steps = self._parse_branch(then_branch)
                for step in then_steps:
                    step['branch'] = 'then'
                    step['condition_ref'] = 0  # Reference to condition
                    steps.append(step)
                
                # Parse else branch if exists
                if else_branch:
                    else_steps = self._parse_branch(else_branch)
                    for step in else_steps:
                        step['branch'] = 'else'
                        step['condition_ref'] = 0  # Reference to condition
                        steps.append(step)
        
        elif segment.strip().startswith('while '):
            # Parse while structure manually
            parts = segment.split()
            
            # Find 'x' keyword
            x_idx = None
            for i, part in enumerate(parts):
                if part == 'x':
                    x_idx = i
                    break
            
            if x_idx:
                # Extract condition and body
                condition_parts = parts[1:x_idx]
                condition = ' '.join(condition_parts)
                body_parts = parts[x_idx + 1:]
                body = ' '.join(body_parts)
                
                # Parse condition as a step
                cond_step = self._parse_step(condition)
                cond_step['role'] = 'while_condition'
                steps.append(cond_step)
                
                # Parse body
                body_steps = self._parse_branch(body)
                for step in body_steps:
                    step['loop'] = 'while_body'
                    step['condition_ref'] = 0
                    steps.append(step)
        
        else:
            # Parse regular and/or operations
            steps = self._parse_and_or_chain(segment)
        
        return steps
    
    def _parse_and_or_chain(self, segment: str) -> List[Dict[str, Any]]:
        """Parse segment with and/or operators."""
        steps = []
        
        # Split by 'and' and 'or' while tracking which operator
        parts = []
        current_part = segment
        
        # First find all 'or' operations (lower precedence)
        or_parts = self.patterns['or'].split(current_part)
        
        if len(or_parts) > 1:
            # We have 'or' operations
            for i, part in enumerate(or_parts):
                # Each part might have 'and' operations
                and_steps = self._parse_and_chain(part)
                for step in and_steps:
                    if i > 0:
                        step['operator'] = 'or'
                        step['operator_group'] = i
                    steps.append(step)
        else:
            # No 'or', just parse 'and'
            steps = self._parse_and_chain(segment)
        
        return steps
    
    def _parse_and_chain(self, segment: str) -> List[Dict[str, Any]]:
        """Parse segment with 'and' operators."""
        steps = []
        
        # Split by 'and'
        and_parts = self.patterns['and'].split(segment)
        
        for i, part in enumerate(and_parts):
            step = self._parse_step(part.strip())
            if i > 0:
                step['operator'] = 'and'
            steps.append(step)
        
        return steps
    
    def _parse_branch(self, branch: str) -> List[Dict[str, Any]]:
        """Parse a branch (then/else/while body)."""
        # Branches can contain and/or operations
        return self._parse_and_or_chain(branch)
    
    def _parse_step(self, step_str: str) -> Dict[str, Any]:
        """Parse individual step (coordinate/shortcut + args)."""
        parts = step_str.split(None, 1)
        
        step = {
            'type': 'execution',
            'target': parts[0] if parts else step_str,
            'args_str': parts[1] if len(parts) > 1 else '{}'
        }
        
        # Try to parse args
        try:
            if step['args_str'] == '()':
                step['args'] = '()'
            else:
                step['args'] = json.loads(step['args_str'])
        except:
            step['args'] = None
            step['args_error'] = 'Invalid JSON'
        
        return step


def create_execution_tree(execution_plan: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Convert flat execution plan to tree structure for visualization."""
    tree = {
        'type': 'root',
        'children': []
    }
    
    # Group by segments
    segments = {}
    for step in execution_plan:
        seg_idx = step.get('segment', 0)
        if seg_idx not in segments:
            segments[seg_idx] = []
        segments[seg_idx].append(step)
    
    # Build tree
    for seg_idx in sorted(segments.keys()):
        segment_node = {
            'type': 'segment',
            'index': seg_idx,
            'children': segments[seg_idx]
        }
        tree['children'].append(segment_node)
    
    return tree