"""
API router for the AI Copilot — chat and file upload endpoints.
"""
import uuid
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional

from app.schemas import CopilotChatRequest, CopilotChatResponse, ComplaintFormData
from app.services.ai_agent import process_complaint_message
from app.utils.file_parser import extract_text_from_file

router = APIRouter(prefix="/api/copilot", tags=["AI Copilot"])


@router.post("/chat", response_model=CopilotChatResponse)
def copilot_chat(request: CopilotChatRequest):
    """
    Process a user message through the LangGraph AI agent.

    Handles:
    - New complaint text extraction
    - Corrections to existing form fields
    - General QMS questions
    - Completeness checks
    """
    try:
        # Convert current form state to dict if provided
        current_state = None
        if request.current_form_state:
            current_state = request.current_form_state.model_dump(exclude_none=False)

        # Process through LangGraph agent
        result = process_complaint_message(
            message=request.message,
            session_id=request.session_id,
            current_form_state=current_state,
        )

        # Build response
        form_updates = None
        if result.get("form_updates"):
            form_updates = ComplaintFormData(**{
                k: v for k, v in result["form_updates"].items()
                if k in ComplaintFormData.model_fields
            })

        from app.schemas import RiskAssessment
        risk = None
        if result.get("risk_assessment"):
            risk = RiskAssessment(**{
                k: v for k, v in result["risk_assessment"].items()
                if k in RiskAssessment.model_fields
            })

        return CopilotChatResponse(
            reply=result.get("reply", "Processed your request."),
            form_updates=form_updates,
            risk_assessment=risk,
            status=result.get("status", "pending_triage"),
            session_id=result.get("session_id", request.session_id or str(uuid.uuid4())),
            completeness=result.get("completeness"),
            duplicate_warning=result.get("duplicate_warning"),
        )

    except Exception as e:
        print(f"Copilot error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"AI processing error: {str(e)}",
        )


@router.post("/upload")
def copilot_upload(
    file: UploadFile = File(...),
    session_id: Optional[str] = Form(None),
):
    """
    Upload a complaint file (PDF, text, email) for AI extraction.

    The file content is extracted and processed through the same
    LangGraph agent as chat messages.
    """
    try:
        # Read file content
        content = file.file.read()
        filename = file.filename or "uploaded_file.txt"

        # Extract text from file
        extracted_text = extract_text_from_file(content, filename)

        if not extracted_text or extracted_text.startswith("[Error"):
            raise HTTPException(
                status_code=400,
                detail=f"Could not extract text from file: {filename}",
            )

        # Process through LangGraph agent
        result = process_complaint_message(
            message=extracted_text,
            session_id=session_id,
            current_form_state=None,
        )

        # Build response
        form_updates = None
        if result.get("form_updates"):
            form_updates = ComplaintFormData(**{
                k: v for k, v in result["form_updates"].items()
                if k in ComplaintFormData.model_fields
            })

        from app.schemas import RiskAssessment
        risk = None
        if result.get("risk_assessment"):
            risk = RiskAssessment(**{
                k: v for k, v in result["risk_assessment"].items()
                if k in RiskAssessment.model_fields
            })

        return CopilotChatResponse(
            reply=result.get("reply", "File processed successfully."),
            form_updates=form_updates,
            risk_assessment=risk,
            status=result.get("status", "pending_triage"),
            session_id=result.get("session_id", session_id or str(uuid.uuid4())),
            completeness=result.get("completeness"),
            duplicate_warning=None,
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Upload error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"File processing error: {str(e)}",
        )
