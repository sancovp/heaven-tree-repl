#!/usr/bin/env python3
"""
RSI Analysis module - Pattern recognition, crystallization, and insights.
"""
import json
import datetime
from typing import Dict, List, Any, Optional, Tuple


class RSIAnalysisMixin:
    """Mixin class providing RSI analysis functionality."""
    
    def _handle_analyze_patterns(self) -> dict:
        """Analyze execution patterns for RSI insights."""
        if not self.execution_history:
            return {"error": "No execution history to analyze"}
        
        analysis = {
            "execution_frequency": self._analyze_execution_frequency(),
            "pathway_usage": self._analyze_pathway_usage(),
            "error_patterns": self._analyze_error_patterns(),
            "optimization_opportunities": self._identify_optimization_opportunities(),
            "crystallization_candidates": self._identify_crystallization_candidates()
        }
        
        # Store insights in ontology
        self.graph_ontology["learning_insights"][datetime.datetime.utcnow().isoformat()] = analysis
        
        return self._build_response({
            "action": "rsi_pattern_analysis",
            "analysis": analysis,
            "insights_generated": len(analysis),
            "message": "Pattern analysis complete - insights stored in ontology"
        })
    
    def _analyze_execution_frequency(self) -> dict:
        """Analyze which nodes/pathways are executed most frequently."""
        node_frequency = {}
        pathway_frequency = {}
        
        for execution in self.execution_history:
            node = execution["node"]
            node_frequency[node] = node_frequency.get(node, 0) + 1
        
        # Track pathway usage
        for name, pathway in self.saved_pathways.items():
            # Count how many executions match this pathway pattern
            usage_count = self._count_pathway_usage(pathway)
            if usage_count > 0:
                pathway_frequency[name] = usage_count
        
        return {
            "most_used_nodes": sorted(node_frequency.items(), key=lambda x: x[1], reverse=True)[:10],
            "most_used_pathways": sorted(pathway_frequency.items(), key=lambda x: x[1], reverse=True)[:5],
            "total_unique_nodes": len(node_frequency),
            "execution_distribution": node_frequency
        }
    
    def _analyze_pathway_usage(self) -> dict:
        """Analyze how pathways are being used and their effectiveness."""
        usage_analysis = {}
        
        for name, pathway in self.saved_pathways.items():
            template = self.saved_templates.get(name, {})
            usage_count = self._count_pathway_usage(pathway)
            
            # Calculate success rate and performance metrics
            success_rate = self._calculate_pathway_success_rate(pathway)
            avg_execution_time = self._calculate_avg_execution_time(pathway)
            
            usage_analysis[name] = {
                "usage_count": usage_count,
                "template_type": template.get("type", "unknown"),
                "success_rate": success_rate,
                "avg_execution_time": avg_execution_time,
                "efficiency_score": self._calculate_efficiency_score(usage_count, success_rate, avg_execution_time)
            }
        
        return usage_analysis
    
    def _analyze_error_patterns(self) -> dict:
        """Identify common error patterns that could be optimized."""
        error_patterns = []
        repeated_failures = {}
        
        for execution in self.execution_history:
            result = execution.get("result", {})
            if isinstance(result, dict) and "error" in result:
                error_key = f"{execution['node']}:{result.get('error', 'unknown')}"
                repeated_failures[error_key] = repeated_failures.get(error_key, 0) + 1
        
        # Identify patterns worth optimizing
        for error_key, count in repeated_failures.items():
            if count >= 2:  # Multiple occurrences suggest a pattern
                node, error_msg = error_key.split(":", 1)
                error_patterns.append({
                    "node": node,
                    "error_message": error_msg,
                    "occurrence_count": count,
                    "optimization_suggestion": self._suggest_error_fix(node, error_msg)
                })
        
        return {
            "total_errors": len([e for e in self.execution_history if isinstance(e.get("result", {}), dict) and "error" in e.get("result", {})]),
            "repeated_error_patterns": error_patterns,
            "error_prone_nodes": sorted(repeated_failures.items(), key=lambda x: x[1], reverse=True)[:5]
        }
    
    def _identify_optimization_opportunities(self) -> list:
        """Identify specific opportunities for optimization."""
        opportunities = []
        
        # Frequently used sequences that aren't pathways yet
        sequences = self._find_common_sequences()
        for seq in sequences:
            if seq["frequency"] >= 3 and not self._sequence_is_saved_pathway(seq):
                opportunities.append({
                    "type": "sequence_crystallization",
                    "description": f"Common sequence: {' -> '.join(seq['nodes'])}",
                    "frequency": seq["frequency"],
                    "suggestion": "Consider saving as pathway template",
                    "potential_savings": seq["frequency"] * len(seq["nodes"]) - 1
                })
        
        # Inefficient pathways that could be optimized
        for name, analysis in self._analyze_pathway_usage().items():
            if analysis["efficiency_score"] < 0.5:  # Low efficiency threshold
                opportunities.append({
                    "type": "pathway_optimization",
                    "pathway_name": name,
                    "description": f"Pathway '{name}' has low efficiency score",
                    "current_efficiency": analysis["efficiency_score"],
                    "suggestion": "Review pathway steps for redundancy or error-prone operations"
                })
        
        return opportunities
    
    def _identify_crystallization_candidates(self) -> list:
        """Identify execution patterns that should be crystallized into pathways."""
        candidates = []
        
        # Look for repeated patterns in execution history
        sequences = self._find_common_sequences()
        
        for seq in sequences:
            if (seq["frequency"] >= 3 and 
                len(seq["nodes"]) >= 2 and 
                not self._sequence_is_saved_pathway(seq)):
                
                # Analyze the sequence for crystallization potential
                complexity_score = len(seq["nodes"]) * seq["frequency"]
                reuse_potential = seq["frequency"] / len(self.execution_history)
                
                candidates.append({
                    "sequence": seq["nodes"],
                    "frequency": seq["frequency"],
                    "complexity_score": complexity_score,
                    "reuse_potential": reuse_potential,
                    "crystallization_priority": complexity_score * reuse_potential,
                    "suggested_name": f"auto_pathway_{len(candidates) + 1}",
                    "suggested_coordinate": self._suggest_crystallization_coordinate(seq)
                })
        
        # Sort by crystallization priority
        candidates.sort(key=lambda x: x["crystallization_priority"], reverse=True)
        
        return candidates[:5]  # Top 5 candidates
    
    def _handle_crystallize_pattern(self, args_str: str) -> dict:
        """Crystallize a discovered pattern into a pathway."""
        if not args_str:
            return {"error": "Pattern name or sequence required"}
        
        parts = args_str.split(None, 1)
        pattern_name = parts[0]
        
        # Check if this is an auto-generated candidate
        analysis = self.graph_ontology.get("learning_insights", {})
        latest_analysis = None
        for timestamp, insights in analysis.items():
            latest_analysis = insights
            break
        
        if latest_analysis:
            candidates = latest_analysis.get("crystallization_candidates", [])
            for candidate in candidates:
                if candidate["suggested_name"] == pattern_name:
                    # Crystallize this candidate
                    return self._crystallize_sequence_candidate(candidate)
        
        return {"error": f"Pattern '{pattern_name}' not found in crystallization candidates"}
    
    def _crystallize_sequence_candidate(self, candidate: dict) -> dict:
        """Convert a sequence candidate into a crystallized pathway."""
        # Create pathway steps from the sequence
        pathway_steps = []
        for i, node in enumerate(candidate["sequence"]):
            # Find a representative execution for this node
            representative_args = self._find_representative_args_for_node(node)
            
            pathway_steps.append({
                "command": f"jump {node} {json.dumps(representative_args)}",
                "position": node,
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "from_crystallization": True,
                "step": i
            })
        
        # Save as pathway
        pathway_name = candidate["suggested_name"]
        coordinate = candidate["suggested_coordinate"]
        
        # Create template
        template = self._analyze_pathway_template(pathway_steps)
        
        # Save to system
        self.saved_pathways[pathway_name] = {
            "steps": pathway_steps,
            "created": datetime.datetime.utcnow().isoformat(),
            "crystallized_from": candidate["sequence"],
            "crystallization_priority": candidate["crystallization_priority"],
            "source": "rsi_crystallization",
            "coordinate": coordinate
        }
        
        self.saved_templates[pathway_name] = template
        
        # Create coordinate node
        self._create_pathway_node(coordinate, pathway_name, template)
        
        # Record crystallization in history
        self.graph_ontology["crystallization_history"].append({
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "pathway_name": pathway_name,
            "coordinate": coordinate,
            "original_sequence": candidate["sequence"],
            "crystallization_priority": candidate["crystallization_priority"],
            "template_type": template["type"]
        })
        
        return self._build_response({
            "action": "crystallize_pattern",
            "pathway_name": pathway_name,
            "coordinate": coordinate,
            "template_type": template["type"],
            "crystallization_priority": candidate["crystallization_priority"],
            "message": f"Pattern crystallized as pathway '{pathway_name}' at {coordinate}"
        })
    
    def _handle_rsi_insights(self) -> dict:
        """Show comprehensive RSI analysis and suggestions."""
        insights = {
            "ontology_summary": {
                "total_pathways": len(self.saved_pathways),
                "total_executions": len(self.execution_history),
                "domains_discovered": len(self.graph_ontology["domains"]),
                "crystallization_events": len(self.graph_ontology["crystallization_history"])
            },
            "recent_insights": list(self.graph_ontology["learning_insights"].keys())[-3:],
            "optimization_suggestions": self.graph_ontology.get("optimization_suggestions", []),
            "crystallization_history": self.graph_ontology["crystallization_history"][-5:],
            "performance_trends": self._calculate_performance_trends()
        }
        
        return self._build_response({
            "action": "rsi_insights",
            "insights": insights,
            "message": "Comprehensive RSI analysis ready for agent consumption"
        })
    
    # === Helper methods for RSI analysis ===
    
    def _count_pathway_usage(self, pathway: dict) -> int:
        """Count how many times a pathway pattern appears in execution history."""
        # Simplified counting - could be enhanced with fuzzy matching
        return 1 if pathway.get("source") == "execution_history" else 0
    
    def _calculate_pathway_success_rate(self, pathway: dict) -> float:
        """Calculate success rate for pathway executions."""
        # Simplified - assumes all recorded pathways succeeded
        return 1.0
    
    def _calculate_avg_execution_time(self, pathway: dict) -> float:
        """Calculate average execution time for pathway."""
        # Simplified - would need actual timing data
        return len(pathway.get("steps", [])) * 0.1  # Rough estimate
    
    def _calculate_efficiency_score(self, usage: int, success_rate: float, avg_time: float) -> float:
        """Calculate overall efficiency score for a pathway."""
        # Weighted efficiency metric
        usage_weight = min(usage / 10.0, 1.0)  # Normalize usage
        time_weight = max(1.0 - (avg_time / 10.0), 0.1)  # Normalize time (lower is better)
        return (usage_weight * 0.4) + (success_rate * 0.4) + (time_weight * 0.2)
    
    def _suggest_error_fix(self, node: str, error_msg: str) -> str:
        """Suggest fixes for common error patterns."""
        if "requires arguments" in error_msg:
            return "Add argument validation or default parameters"
        elif "not found" in error_msg:
            return "Add existence checking or error handling"
        else:
            return "Review node implementation for robustness"
    
    def _find_common_sequences(self) -> list:
        """Find commonly executed sequences in history."""
        sequences = {}
        
        # Look for sequences of 2-4 consecutive nodes
        for i in range(len(self.execution_history)):
            for length in [2, 3, 4]:
                if i + length <= len(self.execution_history):
                    sequence = [self.execution_history[j]["node"] for j in range(i, i + length)]
                    seq_key = " -> ".join(sequence)
                    
                    if seq_key not in sequences:
                        sequences[seq_key] = {"nodes": sequence, "frequency": 0}
                    sequences[seq_key]["frequency"] += 1
        
        # Filter to meaningful sequences (frequency > 1)
        return [seq for seq in sequences.values() if seq["frequency"] > 1]
    
    def _sequence_is_saved_pathway(self, sequence: dict) -> bool:
        """Check if sequence is already saved as a pathway."""
        sequence_nodes = sequence["nodes"]
        
        for pathway in self.saved_pathways.values():
            pathway_nodes = [step.get("position") for step in pathway.get("steps", [])]
            if pathway_nodes == sequence_nodes:
                return True
        return False
    
    def _suggest_crystallization_coordinate(self, sequence: dict) -> str:
        """Suggest coordinate for crystallizing a sequence."""
        # Use domain of first node in sequence
        first_node = sequence["nodes"][0]
        domain = self._get_domain_root(first_node)
        return self._get_next_coordinate_in_domain(domain)
    
    def _find_representative_args_for_node(self, node: str) -> dict:
        """Find representative arguments for a node from execution history."""
        for execution in self.execution_history:
            if execution["node"] == node:
                return execution.get("args", {})
        return {}
    
    def _calculate_performance_trends(self) -> dict:
        """Calculate performance trends over time."""
        if len(self.execution_history) < 5:
            return {"insufficient_data": True}
        
        # Simple trend analysis
        recent_executions = self.execution_history[-10:]
        older_executions = self.execution_history[-20:-10] if len(self.execution_history) > 10 else []
        
        recent_error_rate = len([e for e in recent_executions if isinstance(e.get("result", {}), dict) and "error" in e.get("result", {})]) / len(recent_executions)
        older_error_rate = len([e for e in older_executions if isinstance(e.get("result", {}), dict) and "error" in e.get("result", {})]) / len(older_executions) if older_executions else recent_error_rate
        
        return {
            "recent_error_rate": recent_error_rate,
            "older_error_rate": older_error_rate,
            "error_trend": "improving" if recent_error_rate < older_error_rate else "declining" if recent_error_rate > older_error_rate else "stable",
            "total_pathway_growth": len(self.saved_pathways),
            "crystallization_events": len(self.graph_ontology["crystallization_history"])
        }