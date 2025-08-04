#!/usr/bin/env python3
"""
Display Brief module - Pydantic model for display metadata.
"""
from pydantic import BaseModel
from typing import Optional


class DisplayBrief(BaseModel):
    """
    Model for holding display metadata that gets shown as a brief.
    """
    role: Optional[str] = None
    
    def to_display_string(self) -> str:
        """
        Concatenate all display fields into a single string.
        
        Returns:
            Formatted display string or empty string if no fields set
        """
        parts = []
        
        if self.role:
            parts.append(f"Role: {self.role}")
        
        return " | ".join(parts) if parts else ""
    
    def has_content(self) -> bool:
        """
        Check if there's any content to display.
        
        Returns:
            True if any field has content
        """
        return bool(self.role)