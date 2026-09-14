"""
SQLAlchemy ORM models for the Complaint Management System.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base


class Complaint(Base):
    """Stores a pharmaceutical customer complaint with all QMS-required fields."""
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, autoincrement=True)
    complaint_id = Column(String(50), unique=True, default=lambda: f"CC-{uuid.uuid4().hex[:8].upper()}")

    # Section 1: Origin & Customer Details
    complaint_source = Column(String(100), nullable=True)
    customer_name = Column(String(200), nullable=True)

    # Section 2: Product & Batch Identification
    product_name = Column(String(200), nullable=True)
    product_strength = Column(String(50), nullable=True)
    batch_lot_number = Column(String(100), nullable=True)
    affected_quantity = Column(String(100), nullable=True)
    manufacturing_date = Column(String(50), nullable=True)
    expiry_date = Column(String(50), nullable=True)

    # Section 3: Facility & Material Impact
    originating_site_block = Column(String(100), nullable=True)
    impacted_npm = Column(String(200), nullable=True)

    # Section 4: Defect Analysis
    complaint_category = Column(String(200), nullable=True)
    complaint_description = Column(Text, nullable=True)

    # AI Risk Assessment
    severity = Column(String(50), nullable=True)
    suggested_next_action = Column(Text, nullable=True)
    initial_risk_assessment = Column(Text, nullable=True)

    # Bonus AI Features
    root_cause_recommendation = Column(Text, nullable=True)
    capa_recommendation = Column(Text, nullable=True)

    # Workflow status
    status = Column(String(30), default="pending_triage")
    session_id = Column(String(100), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    audit_logs = relationship("AuditLog", back_populates="complaint", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "complaint_id": self.complaint_id,
            "complaint_source": self.complaint_source,
            "customer_name": self.customer_name,
            "product_name": self.product_name,
            "product_strength": self.product_strength,
            "batch_lot_number": self.batch_lot_number,
            "affected_quantity": self.affected_quantity,
            "manufacturing_date": self.manufacturing_date,
            "expiry_date": self.expiry_date,
            "originating_site_block": self.originating_site_block,
            "impacted_npm": self.impacted_npm,
            "complaint_category": self.complaint_category,
            "complaint_description": self.complaint_description,
            "severity": self.severity,
            "suggested_next_action": self.suggested_next_action,
            "initial_risk_assessment": self.initial_risk_assessment,
            "root_cause_recommendation": self.root_cause_recommendation,
            "capa_recommendation": self.capa_recommendation,
            "status": self.status,
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class AuditLog(Base):
    """Tracks all changes for QMS traceability and 21 CFR Part 11 compliance."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    complaint_id = Column(Integer, ForeignKey("complaints.id"), nullable=False)
    action = Column(String(50), nullable=False)  # 'created', 'field_updated', 'committed'
    field_changed = Column(String(100), nullable=True)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    changed_by = Column(String(100), default="ai_copilot")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    complaint = relationship("Complaint", back_populates="audit_logs")
