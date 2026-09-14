"""
Domain-specific prompt templates for pharmaceutical complaint extraction.
"""
from typing import Dict, Optional
from app.services.groq_client import groq_client


EXTRACTION_SYSTEM_PROMPT = """You are an expert pharmaceutical Quality Management System (QMS) analyst specializing in customer complaint processing for API (Active Pharmaceutical Ingredients) and FDF (Finished Dosage Forms) manufacturing.

Your role is to extract structured data from unstructured customer complaint text (emails, reports, conversations) and map them to QMS-standard fields.

IMPORTANT RULES:
1. Extract ONLY information explicitly stated in the text. Do NOT infer or fabricate data.
2. For fields not mentioned, use null.
3. For complaint_category, classify into one of these standard QMS categories:
   - Product Defect - Discoloration
   - Product Defect - Broken/Crushed
   - Product Defect - Foreign Particle
   - Product Defect - Wrong Count
   - Product Defect - Odor/Taste
   - Product Defect - Dissolution Failure
   - Packaging Defect - Damaged Seal
   - Packaging Defect - Label Error
   - Packaging Defect - Missing Insert
   - Adverse Event - Patient Reaction
   - Adverse Event - Lack of Efficacy
   - Stability Failure - Out of Specification
   - Delivery Issue - Temperature Excursion
   - Delivery Issue - Damaged in Transit
   - Other
4. For originating_site_block, classify into: Manufacturing, Packaging, Quality Control, Warehouse, or null if not determinable.
5. For complaint_description, synthesize the complaint into a formal QMS-style summary.
6. Identify the complaint_source from context (e.g., Pharmacy, Hospital, Distributor, Patient, Regulatory).

Return a JSON object with these exact fields:
{
    "complaint_source": "string or null",
    "customer_name": "string or null",
    "product_name": "string or null",
    "product_strength": "string or null",
    "batch_lot_number": "string or null",
    "affected_quantity": "string or null",
    "manufacturing_date": "string or null",
    "expiry_date": "string or null",
    "originating_site_block": "string or null",
    "impacted_npm": "string or null",
    "complaint_category": "string or null",
    "complaint_description": "string or null"
}"""


CORRECTION_SYSTEM_PROMPT = """You are an expert pharmaceutical QMS analyst. The user is correcting or updating specific fields in an existing customer complaint form.

Given the user's correction message and the current form state, identify which fields need to be updated and return ONLY the changed fields.

IMPORTANT:
1. Only return fields that the user explicitly wants to change.
2. Keep unchanged fields out of the response.
3. The user may refer to fields informally (e.g., "batch number" = "batch_lot_number", "quantity" = "affected_quantity").
4. Preserve the field naming convention exactly.

Return a JSON object with ONLY the fields to update:
{
    "field_name": "new_value",
    ...
}

Valid field names: complaint_source, customer_name, product_name, product_strength, batch_lot_number, affected_quantity, manufacturing_date, expiry_date, originating_site_block, impacted_npm, complaint_category, complaint_description"""


def extract_complaint_data(raw_text: str) -> Dict:
    """
    Extract structured complaint data from unstructured text using Groq LLM.

    Args:
        raw_text: Raw complaint text (email, report, conversation).

    Returns:
        Dict with extracted form field values.
    """
    messages = [
        {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
        {"role": "user", "content": f"Extract complaint data from the following text:\n\n{raw_text}"},
    ]
    result = groq_client.chat_json(messages=messages, temperature=0.1)
    # Clean nulls from string
    for key, value in result.items():
        if value == "null" or value == "None":
            result[key] = None
    return result


def apply_correction(correction_text: str, current_state: Dict) -> Dict:
    """
    Parse a correction message and return only the fields to update.

    Args:
        correction_text: User's correction message.
        current_state: Current form field values.

    Returns:
        Dict with only the fields that need updating.
    """
    current_state_str = "\n".join(
        f"  {k}: {v}" for k, v in current_state.items() if v is not None
    )
    messages = [
        {"role": "system", "content": CORRECTION_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"Current form state:\n{current_state_str}\n\nUser correction: {correction_text}",
        },
    ]
    result = groq_client.chat_json(messages=messages, temperature=0.1)
    # Filter out null/None values
    return {k: v for k, v in result.items() if v is not None and v != "null"}
