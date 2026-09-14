"""
LangGraph AI Agent for pharmaceutical complaint processing.

This agent implements a multi-step workflow:
  receive_input → classify_intent → extract/correct/answer → assess_risk → format_response
"""
import uuid
from typing import TypedDict, Optional, Dict, Any, Literal
from langgraph.graph import StateGraph, END

from app.services.complaint_parser import extract_complaint_data, apply_correction
from app.services.risk_assessor import assess_risk, check_completeness
from app.services.groq_client import groq_client


# ─── Agent State ───────────────────────────────────────────────────

class AgentState(TypedDict):
    """State that flows through the LangGraph agent."""
    # Input
    raw_input: str
    session_id: str
    current_form_state: Optional[Dict[str, Any]]

    # Processing
    intent: Optional[str]  # 'new_complaint', 'correction', 'question', 'completeness_check'
    extracted_data: Optional[Dict[str, Any]]
    correction_data: Optional[Dict[str, Any]]
    risk_assessment: Optional[Dict[str, Any]]
    completeness: Optional[Dict[str, Any]]

    # Output
    reply: str
    form_updates: Optional[Dict[str, Any]]
    new_status: str


# ─── Node Functions ────────────────────────────────────────────────

def receive_input(state: AgentState) -> AgentState:
    """Parse and prepare the raw input for processing."""
    if not state.get("session_id"):
        state["session_id"] = str(uuid.uuid4())
    return state


def classify_intent(state: AgentState) -> AgentState:
    """Determine whether the message is a new complaint, correction, or question."""
    raw = state["raw_input"].strip().lower()
    has_form = state.get("current_form_state") and any(
        v for v in (state["current_form_state"] or {}).values() if v
    )

    # Use LLM for intent classification
    messages = [
        {
            "role": "system",
            "content": """You are a pharmaceutical complaint processing assistant. Classify the user's intent.

Return a JSON object with a single field:
{"intent": "new_complaint" | "correction" | "question" | "completeness_check"}

RULES:
- "new_complaint": The message contains complaint details to extract (product, batch, defect, customer info, etc.)
- "correction": The user is correcting or updating specific fields in an already-filled form (e.g., "change the batch number to...", "sorry the quantity is actually...", "update the...")
- "question": The user is asking a question about the system, the complaint, QMS, or needs help
- "completeness_check": The user wants to check if the form is complete or ready to submit

IMPORTANT: If there is existing form data AND the message seems to modify specific values, classify as "correction". If the message contains substantial new complaint information (multiple fields), classify as "new_complaint".""",
        },
        {
            "role": "user",
            "content": f"Has existing form data: {has_form}\nUser message: {state['raw_input']}",
        },
    ]

    result = groq_client.chat_json(messages=messages, temperature=0.1, max_tokens=100)
    state["intent"] = result.get("intent", "new_complaint")
    return state


def extract_complaint(state: AgentState) -> AgentState:
    """Extract structured complaint data from unstructured text."""
    extracted = extract_complaint_data(state["raw_input"])
    state["extracted_data"] = extracted
    state["form_updates"] = extracted
    return state


def handle_correction(state: AgentState) -> AgentState:
    """Apply user corrections to specific form fields."""
    current = state.get("current_form_state") or {}
    corrections = apply_correction(state["raw_input"], current)
    state["correction_data"] = corrections
    state["form_updates"] = corrections
    return state


def handle_question(state: AgentState) -> AgentState:
    """Answer a general question about the complaint or QMS."""
    current_state_str = ""
    if state.get("current_form_state"):
        current_state_str = "\n".join(
            f"  {k}: {v}" for k, v in state["current_form_state"].items() if v
        )

    messages = [
        {
            "role": "system",
            "content": """You are AIVOA Copilot, an AI assistant for pharmaceutical Quality Management Systems (QMS), specifically the Customer Complaint module for API and FDF manufacturing.

Answer the user's question helpfully and concisely. If they have an existing complaint form, reference it in your answer when relevant.

Keep your response to 2-3 sentences max.""",
        },
        {
            "role": "user",
            "content": f"Current form state:\n{current_state_str}\n\nQuestion: {state['raw_input']}",
        },
    ]

    state["reply"] = groq_client.chat(messages=messages, temperature=0.3, max_tokens=300)
    state["form_updates"] = None
    state["risk_assessment"] = None
    state["new_status"] = state.get("new_status", "pending_triage")
    return state


def perform_risk_assessment(state: AgentState) -> AgentState:
    """Evaluate risk based on extracted or corrected complaint data."""
    # Merge form updates with existing state for full picture
    full_data = dict(state.get("current_form_state") or {})
    if state.get("form_updates"):
        full_data.update({k: v for k, v in state["form_updates"].items() if v is not None})

    # Only assess if we have meaningful data
    if any(v for k, v in full_data.items() if k in ("product_name", "complaint_category", "complaint_description")):
        risk = assess_risk(full_data)
        state["risk_assessment"] = risk
    else:
        state["risk_assessment"] = None

    return state


def check_form_completeness(state: AgentState) -> AgentState:
    """Check if the complaint form has all required fields."""
    full_data = dict(state.get("current_form_state") or {})
    completeness = check_completeness(full_data)
    state["completeness"] = completeness
    state["reply"] = completeness.get("message", "Completeness check complete.")
    state["form_updates"] = None
    state["risk_assessment"] = None
    state["new_status"] = "pending_triage"
    return state


def format_response(state: AgentState) -> AgentState:
    """Compose the final response with appropriate reply text and status."""
    intent = state.get("intent", "new_complaint")

    if intent == "new_complaint":
        extracted = state.get("extracted_data", {})
        product = extracted.get("product_name", "the product")
        category = extracted.get("complaint_category", "the reported issue")

        state["reply"] = (
            f"Complaint parsed successfully. I've extracted the product details, "
            f"mapped the batch information, and generated an initial risk assessment "
            f"for {category.lower() if category else 'the reported issue'} "
            f"in {product if product else 'the product'}."
        )
        state["new_status"] = "ready_to_commit"

    elif intent == "correction":
        corrections = state.get("correction_data", {})
        field_names = list(corrections.keys())
        readable_fields = [f.replace("_", " ").title() for f in field_names]

        state["reply"] = (
            f"Updated {', '.join(readable_fields)}. "
            f"The form and risk assessment have been refreshed with the corrected values."
        )
        state["new_status"] = "ready_to_commit"

    elif intent == "completeness_check":
        pass  # Already handled in check_form_completeness

    # For 'question' intent, reply is already set in handle_question

    return state


# ─── Intent Router ─────────────────────────────────────────────────

def route_by_intent(state: AgentState) -> str:
    """Route to the appropriate node based on classified intent."""
    intent = state.get("intent", "new_complaint")
    if intent == "correction":
        return "handle_correction"
    elif intent == "question":
        return "handle_question"
    elif intent == "completeness_check":
        return "check_form_completeness"
    else:
        return "extract_complaint"


# ─── Build the LangGraph ──────────────────────────────────────────

def build_agent_graph() -> StateGraph:
    """
    Build the LangGraph agent for complaint processing.

    Flow:
        receive_input → classify_intent → [extract|correct|question|completeness]
                                              ↓           ↓
                                         assess_risk → format_response → END
                                                        question → END
    """
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("receive_input", receive_input)
    workflow.add_node("classify_intent", classify_intent)
    workflow.add_node("extract_complaint", extract_complaint)
    workflow.add_node("handle_correction", handle_correction)
    workflow.add_node("handle_question", handle_question)
    workflow.add_node("check_form_completeness", check_form_completeness)
    workflow.add_node("assess_risk", perform_risk_assessment)
    workflow.add_node("format_response", format_response)

    # Set entry point
    workflow.set_entry_point("receive_input")

    # Define edges
    workflow.add_edge("receive_input", "classify_intent")

    # Conditional routing after intent classification
    workflow.add_conditional_edges(
        "classify_intent",
        route_by_intent,
        {
            "extract_complaint": "extract_complaint",
            "handle_correction": "handle_correction",
            "handle_question": "handle_question",
            "check_form_completeness": "check_form_completeness",
        },
    )

    # After extraction/correction → risk assessment → format response
    workflow.add_edge("extract_complaint", "assess_risk")
    workflow.add_edge("handle_correction", "assess_risk")
    workflow.add_edge("assess_risk", "format_response")
    workflow.add_edge("format_response", END)

    # Question and completeness go directly to END
    workflow.add_edge("handle_question", END)
    workflow.add_edge("check_form_completeness", END)

    return workflow.compile()


# Compiled agent instance
complaint_agent = build_agent_graph()


def process_complaint_message(
    message: str,
    session_id: Optional[str] = None,
    current_form_state: Optional[Dict] = None,
) -> Dict[str, Any]:
    """
    Process a user message through the LangGraph agent.

    Args:
        message: User's chat message or pasted complaint text.
        session_id: Session identifier for conversation continuity.
        current_form_state: Current state of the complaint form fields.

    Returns:
        Dict with reply, form_updates, risk_assessment, status.
    """
    initial_state: AgentState = {
        "raw_input": message,
        "session_id": session_id or str(uuid.uuid4()),
        "current_form_state": current_form_state,
        "intent": None,
        "extracted_data": None,
        "correction_data": None,
        "risk_assessment": None,
        "completeness": None,
        "reply": "",
        "form_updates": None,
        "new_status": "pending_triage",
    }

    # Run the agent
    result = complaint_agent.invoke(initial_state)

    return {
        "reply": result.get("reply", "I processed your request."),
        "form_updates": result.get("form_updates"),
        "risk_assessment": result.get("risk_assessment"),
        "status": result.get("new_status", "pending_triage"),
        "session_id": result.get("session_id"),
        "completeness": result.get("completeness"),
    }
