"""
AI-powered risk assessment for pharmaceutical complaints.
"""
from typing import Dict, Optional
from app.services.groq_client import groq_client


RISK_ASSESSMENT_SYSTEM_PROMPT = """You are an expert pharmaceutical Quality Management System (QMS) risk assessor. Based on the complaint data provided, generate a comprehensive risk assessment.

Consider the following when assessing risk:
1. Patient safety impact
2. Product quality implications
3. Regulatory requirements (FDA, ICH guidelines)
4. Batch-wide impact potential
5. Root cause probability

Return a JSON object with these fields:
{
    "severity": "Minor|Major|Critical",
    "suggested_next_action": "string describing the recommended immediate action",
    "initial_risk_assessment": "string with a detailed 2-3 sentence risk assessment narrative",
    "root_cause_recommendation": "string suggesting probable root causes to investigate",
    "capa_recommendation": "string recommending corrective and preventive actions"
}

SEVERITY GUIDELINES:
- Minor: Cosmetic issue, no patient safety concern, limited impact (e.g., minor label defect, color variation within spec)
- Major: Quality deviation that may affect product efficacy, requires investigation (e.g., wrong count, packaging seal issue, physical defects)
- Critical: Potential patient safety concern, requires immediate action (e.g., foreign particles, adverse events, contamination, stability failure)

Be specific and pharmaceutical-industry appropriate in your recommendations."""


COMPLETENESS_CHECK_PROMPT = """You are a QMS compliance checker. Review the following complaint form data and identify any missing mandatory fields.

Mandatory fields for a valid pharmaceutical complaint:
1. complaint_source - Where the complaint originated
2. customer_name - Who reported the complaint
3. product_name - Which product is affected
4. batch_lot_number - Batch/Lot identification
5. complaint_category - Type of defect
6. complaint_description - Description of the issue

Optional but recommended fields:
- product_strength
- affected_quantity
- manufacturing_date
- expiry_date
- originating_site_block
- impacted_npm

Return a JSON object:
{
    "is_complete": true/false,
    "missing_mandatory": ["list of missing mandatory field names"],
    "missing_optional": ["list of missing optional field names"],
    "completeness_score": 0-100,
    "message": "Human-readable summary of completeness status"
}"""


def assess_risk(complaint_data: Dict) -> Dict:
    """
    Generate AI risk assessment for a complaint.

    Args:
        complaint_data: Extracted complaint form fields.

    Returns:
        Dict with severity, next action, risk narrative, root cause, and CAPA recommendations.
    """
    complaint_summary = "\n".join(
        f"  {k}: {v}" for k, v in complaint_data.items()
        if v is not None and k not in ("session_id", "status")
    )
    messages = [
        {"role": "system", "content": RISK_ASSESSMENT_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"Assess the risk for this pharmaceutical complaint:\n\n{complaint_summary}",
        },
    ]
    return groq_client.chat_json(messages=messages, temperature=0.2)


def check_completeness(complaint_data: Dict) -> Dict:
    """
    Check if the complaint form has all mandatory fields filled.

    Args:
        complaint_data: Current form field values.

    Returns:
        Dict with completeness check results.
    """
    form_summary = "\n".join(
        f"  {k}: {v if v else '(empty)'}" for k, v in complaint_data.items()
        if k not in ("session_id", "status")
    )
    messages = [
        {"role": "system", "content": COMPLETENESS_CHECK_PROMPT},
        {
            "role": "user",
            "content": f"Check completeness of this complaint form:\n\n{form_summary}",
        },
    ]
    return groq_client.chat_json(messages=messages, temperature=0.1)
