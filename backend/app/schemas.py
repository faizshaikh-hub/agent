"""
Pydantic schemas for API request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ─── Complaint Form Data ───────────────────────────────────────────

class ComplaintFormData(BaseModel):
    """Represents all fields in the complaint form."""
    complaint_source: Optional[str] = None
    customer_name: Optional[str] = None
    product_name: Optional[str] = None
    product_strength: Optional[str] = None
    batch_lot_number: Optional[str] = None
    affected_quantity: Optional[str] = None
    manufacturing_date: Optional[str] = None
    expiry_date: Optional[str] = None
    originating_site_block: Optional[str] = None
    impacted_npm: Optional[str] = None
    complaint_category: Optional[str] = None
    complaint_description: Optional[str] = None


class RiskAssessment(BaseModel):
    """AI-generated risk assessment for the complaint."""
    severity: Optional[str] = None  # Minor, Major, Critical
    suggested_next_action: Optional[str] = None
    initial_risk_assessment: Optional[str] = None
    root_cause_recommendation: Optional[str] = None
    capa_recommendation: Optional[str] = None


# ─── Copilot API ───────────────────────────────────────────────────

class CopilotChatRequest(BaseModel):
    """Request body for the copilot chat endpoint."""
    message: str = Field(..., description="User message or pasted complaint text")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    current_form_state: Optional[ComplaintFormData] = Field(None, description="Current state of the form")


class CopilotChatResponse(BaseModel):
    """Response from the copilot chat endpoint."""
    reply: str = Field(..., description="AI assistant reply text")
    form_updates: Optional[ComplaintFormData] = Field(None, description="Fields to update in the form")
    risk_assessment: Optional[RiskAssessment] = Field(None, description="AI risk assessment")
    status: str = Field("pending_triage", description="New complaint status")
    session_id: str = Field(..., description="Session ID for conversation continuity")
    completeness: Optional[Dict[str, Any]] = Field(None, description="Completeness check results")
    duplicate_warning: Optional[str] = Field(None, description="Duplicate complaint warning")


# ─── Complaint CRUD ───────────────────────────────────────────────

class ComplaintCreate(BaseModel):
    """Request to create/commit a complaint to the database."""
    form_data: ComplaintFormData
    risk_assessment: Optional[RiskAssessment] = None
    session_id: Optional[str] = None


class ComplaintResponse(BaseModel):
    """Response containing a committed complaint."""
    id: int
    complaint_id: str
    complaint_source: Optional[str] = None
    customer_name: Optional[str] = None
    product_name: Optional[str] = None
    product_strength: Optional[str] = None
    batch_lot_number: Optional[str] = None
    affected_quantity: Optional[str] = None
    manufacturing_date: Optional[str] = None
    expiry_date: Optional[str] = None
    originating_site_block: Optional[str] = None
    impacted_npm: Optional[str] = None
    complaint_category: Optional[str] = None
    complaint_description: Optional[str] = None
    severity: Optional[str] = None
    suggested_next_action: Optional[str] = None
    initial_risk_assessment: Optional[str] = None
    root_cause_recommendation: Optional[str] = None
    capa_recommendation: Optional[str] = None
    status: str = "pending_triage"
    session_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ComplaintListResponse(BaseModel):
    """Response containing a list of complaints."""
    complaints: List[ComplaintResponse]
    total: int
