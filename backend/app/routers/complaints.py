"""
API router for CRUD operations on complaints (commit to QMS ledger, list, get).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import Complaint, AuditLog
from app.schemas import ComplaintCreate, ComplaintResponse, ComplaintListResponse

router = APIRouter(prefix="/api/complaints", tags=["Complaints"])


@router.post("/", response_model=ComplaintResponse)
def create_complaint(payload: ComplaintCreate, db: Session = Depends(get_db)):
    """
    Commit a complaint to the QMS Ledger.
    Creates the complaint record and audit trail entry.
    """
    complaint = Complaint(
        complaint_source=payload.form_data.complaint_source,
        customer_name=payload.form_data.customer_name,
        product_name=payload.form_data.product_name,
        product_strength=payload.form_data.product_strength,
        batch_lot_number=payload.form_data.batch_lot_number,
        affected_quantity=payload.form_data.affected_quantity,
        manufacturing_date=payload.form_data.manufacturing_date,
        expiry_date=payload.form_data.expiry_date,
        originating_site_block=payload.form_data.originating_site_block,
        impacted_npm=payload.form_data.impacted_npm,
        complaint_category=payload.form_data.complaint_category,
        complaint_description=payload.form_data.complaint_description,
        status="committed",
        session_id=payload.session_id,
    )

    # Apply risk assessment if provided
    if payload.risk_assessment:
        complaint.severity = payload.risk_assessment.severity
        complaint.suggested_next_action = payload.risk_assessment.suggested_next_action
        complaint.initial_risk_assessment = payload.risk_assessment.initial_risk_assessment
        complaint.root_cause_recommendation = payload.risk_assessment.root_cause_recommendation
        complaint.capa_recommendation = payload.risk_assessment.capa_recommendation

    db.add(complaint)
    db.flush()

    # Create audit log entry
    audit = AuditLog(
        complaint_id=complaint.id,
        action="committed",
        field_changed="all",
        new_value="Complaint committed to QMS Ledger",
        changed_by="user",
    )
    db.add(audit)
    db.commit()
    db.refresh(complaint)

    return complaint


@router.get("/", response_model=ComplaintListResponse)
def list_complaints(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List all complaints with optional status filter."""
    query = db.query(Complaint)
    if status:
        query = query.filter(Complaint.status == status)
    total = query.count()
    complaints = query.order_by(Complaint.created_at.desc()).offset(skip).limit(limit).all()
    return ComplaintListResponse(complaints=complaints, total=total)


@router.get("/{complaint_id}", response_model=ComplaintResponse)
def get_complaint(complaint_id: int, db: Session = Depends(get_db)):
    """Get a single complaint by ID."""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint


@router.get("/check-duplicate/{batch_lot_number}")
def check_duplicate(batch_lot_number: str, product_name: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Check for duplicate complaints based on batch/lot number.
    Returns matching complaints if found.
    """
    query = db.query(Complaint).filter(Complaint.batch_lot_number == batch_lot_number)
    if product_name:
        query = query.filter(Complaint.product_name == product_name)
    duplicates = query.all()

    if duplicates:
        return {
            "has_duplicates": True,
            "count": len(duplicates),
            "duplicates": [
                {
                    "id": d.id,
                    "complaint_id": d.complaint_id,
                    "product_name": d.product_name,
                    "batch_lot_number": d.batch_lot_number,
                    "status": d.status,
                    "created_at": d.created_at.isoformat() if d.created_at else None,
                }
                for d in duplicates
            ],
        }
    return {"has_duplicates": False, "count": 0, "duplicates": []}
