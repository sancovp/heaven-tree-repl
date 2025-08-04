#!/usr/bin/env python3
"""
Approval System module - Workflow approval queue and management.
"""
import json
import datetime
import uuid
from typing import Dict, List, Any, Optional


class ApprovalQueue:
    """Manages workflow approval requests across the system."""
    
    def __init__(self):
        self.pending_approvals = []
        self.approved_workflows = {}
        
    def add_quarantine_request(self, workflow_data):
        """Add a workflow to the approval queue."""
        approval_id = uuid.uuid4().hex[:8]
        request = {
            "approval_id": approval_id,
            "pathway_name": workflow_data["pathway_name"],
            "coordinate": workflow_data["coordinate"],
            "session_id": workflow_data.get("session_id", "unknown"),
            "description": workflow_data.get("description", ""),
            "steps": workflow_data.get("steps", []),
            "created": datetime.datetime.utcnow().isoformat(),
            "status": "PENDING"
        }
        self.pending_approvals.append(request)
        return approval_id
        
    def approve_workflow(self, approval_id):
        """Approve a workflow by ID."""
        for i, request in enumerate(self.pending_approvals):
            if request["approval_id"] == approval_id:
                approved = self.pending_approvals.pop(i)
                approved["status"] = "APPROVED"
                approved["approved_at"] = datetime.datetime.utcnow().isoformat()
                self.approved_workflows[approved["coordinate"]] = approved
                return approved
        return None
        
    def reject_workflow(self, approval_id):
        """Reject a workflow by ID."""
        for i, request in enumerate(self.pending_approvals):
            if request["approval_id"] == approval_id:
                rejected = self.pending_approvals.pop(i)
                rejected["status"] = "REJECTED"
                return rejected
        return None
        
    def list_pending(self):
        """List all pending approvals."""
        return self.pending_approvals.copy()