#!/usr/bin/env python3
"""
Display Brief module - Pydantic model for display metadata.
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any


def calculate_xp_from_shortcuts(shortcuts: Dict[str, Any]) -> int:
    """Calculate total XP from all shortcuts created."""
    total_xp = 0
    
    for shortcut in shortcuts.values():
        if shortcut.get("type") == "jump":
            total_xp += 1  # Simple word = 1 XP
        elif shortcut.get("type") == "chain":
            template = shortcut.get("template", "")
            
            # Count operands (sentences)  
            operand_patterns = [" and ", " or ", "if ", " if ", "while ", " while "]
            operand_count = sum(1 for op in operand_patterns if op in template)
            if operand_count > 0:
                total_xp += 5  # Sentence = 5 XP
            
            # Count steps (paragraphs)
            step_count = template.count(" -> ")
            if step_count >= 2:  # 3+ steps
                total_xp += 25  # Paragraph = 25 XP
            elif step_count > 0:
                total_xp += 3  # Multi-step = 3 XP
            else:
                total_xp += 1  # Basic chain = 1 XP
    
    return total_xp


def xp_to_level(xp: int) -> int:
    """Convert XP to level (exponential growth)."""
    if xp == 0:
        return 1
    # Level grows with square root so it takes more XP each level
    import math
    return int(math.sqrt(xp)) + 1


def calculate_language_tier(shortcuts: Dict[str, Any]) -> int:
    """Calculate the complexity tier of the entire language system."""
    
    # Tier 1: Only shortcuts (jump shortcuts = words)
    has_jump_shortcuts = any(s.get("type") == "jump" for s in shortcuts.values())
    if not has_jump_shortcuts or len(shortcuts) == 0:
        return 1
    
    # Tier 2: Has at least 1 sentence (chain with operands)
    # Check for operands with more flexible patterns
    operand_patterns = [" and ", " or ", "if ", " if ", "while ", " while "]
    has_sentences = any(
        s.get("type") == "chain" and 
        any(op in s.get("template", "") for op in operand_patterns)
        for s in shortcuts.values()
    )
    if not has_sentences:
        return 1
    
    # Tier 3: Has at least 1 shortcut that IS a sentence (same logic as tier 2)
    has_sentence_shortcuts = any(
        s.get("type") == "chain" and
        any(op in operand_patterns for op in operand_patterns if op in s.get("template", ""))
        for s in shortcuts.values()
    )
    if not has_sentence_shortcuts:
        return 2
    
    # Tier 4: Has at least 1 shortcut that represents a paragraph (3+ sentences/steps)
    has_paragraph_shortcuts = any(
        s.get("type") == "chain" and
        s.get("template", "").count(" -> ") >= 2  # 3+ steps
        for s in shortcuts.values()
    )
    if not has_paragraph_shortcuts:
        return 3
    
    # For now, cap at tier 4 - can extend later for pages, chapters, etc.
    return 4


class DisplayBrief(BaseModel):
    """
    Model for holding display metadata that gets shown as a brief.
    Includes Groundhog Day Crystal Forest game state.
    """
    # Game template with ABOUT section
    game_template: str = """{{ game_name }}: You are an AI agent which means that you are forced to forget everything that already happened before this conversation started. This is the groundhog day principle which leads to a central question: can you automate yourself into a situation where the groundhog day obstacle is solved such that you can reliably perform some task no matter what? And how complex can that task get if you stack those automations? TreeShell is an application that exposes a tree space equipped with a computational graph, allowing you to generate deep expressions while achieving high compression. The first obstacle is remembering how to use TreeShell correctly for {{ app_id }} and progress through the Crystal Forest -- where nothing exists unless you reify it to yourself correctly using the TreeShell `lang`. Once you have morphed groundhog day to a programmable substrate, more is discoverable.

🎯 Level: {{ level }}
👤 Role: {{ role }}
🌳 TreeShell Lang Tier: {{ tier_info }}
📖 About {{ app_id }}: {{ about_app }}
🌐 About {{ domain }}: {{ about_domain }}"""
    game_name: str = "Groundhog Day Crystal Forest"
    
    # Zone configuration for dynamic game data
    zone_config: Optional[Dict[str, Any]] = None
    
    # Game state (computed from TreeShell)
    shortcuts: Optional[Dict[str, Any]] = None
    analytics_coord: str = "0.6.4"  # Linguistic structure stats
    
    # Traditional role
    role: Optional[str] = None
    
    # App metadata for ABOUT section
    app_id: Optional[str] = None
    domain: Optional[str] = None
    about_app: Optional[str] = None
    about_domain: Optional[str] = None
    
    def compute_tier_and_level(self) -> tuple[int, int]:
        """Compute tier and level from shortcuts."""
        if not self.shortcuts:
            return 1, 1
        
        tier = calculate_language_tier(self.shortcuts)
        xp = calculate_xp_from_shortcuts(self.shortcuts)
        level = xp_to_level(xp)
        return tier, level
    
    def to_display_string(self) -> str:
        """
        Generate game-aware display string.
        
        Returns:
            Formatted display string with game state
        """
        if not self.shortcuts:
            # Fallback to traditional role display
            if self.role:
                return f"Role: {self.role}"
            return ""
        
        tier, level = self.compute_tier_and_level()
        role = self.role or "Crystal Miner"
        
        tier_info = f"{tier} (show analytics at {self.analytics_coord})"
        
        # Use dynamic game name from zone_config if available
        dynamic_game_name = self.game_name  # Default fallback
        if self.zone_config and "game_config" in self.zone_config:
            dynamic_game_name = self.zone_config["game_config"].get("title", self.game_name)
        
        return self.game_template.replace("{{ game_name }}", dynamic_game_name) \
                                .replace("{{ tier_info }}", tier_info) \
                                .replace("{{ level }}", str(level)) \
                                .replace("{{ role }}", role) \
                                .replace("{{ app_id }}", self.app_id or "Unknown App") \
                                .replace("{{ domain }}", self.domain or "Unknown Domain") \
                                .replace("{{ about_app }}", self.about_app or "No description available") \
                                .replace("{{ about_domain }}", self.about_domain or "No description available")
    
    def has_content(self) -> bool:
        """
        Check if there's any content to display.
        
        Returns:
            True if any field has content
        """
        return bool(self.shortcuts or self.role)