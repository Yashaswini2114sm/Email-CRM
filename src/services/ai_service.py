import json

from openai import OpenAI

from src.core.config import settings
from src.core.logger import setup_logger

logger = setup_logger(__name__)


def _get_client() -> OpenAI | None:
    """Get OpenAI client. Returns None if API key is not configured."""
    if not settings.OPENAI_API_KEY:
        logger.warning("OpenAI API key not configured")
        return None
    return OpenAI(api_key=settings.OPENAI_API_KEY)


def detect_intent(message: str) -> dict:
    """
    Analyze a customer message and classify their intent.
    Returns: {"intent": str, "confidence": float, "summary": str}
    """
    client = _get_client()
    if not client:
        return {
            "intent": "unknown",
            "confidence": 0.0,
            "summary": "AI not configured",
        }

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a customer support intent classifier. "
                        "Analyze the customer message and respond with ONLY "
                        "a JSON object:\n"
                        '{"intent": one of ["complaint", "inquiry", '
                        '"document_submission", "follow_up", "cancellation", '
                        '"technical_support", "billing", "other"], '
                        '"confidence": float 0.0-1.0, '
                        '"summary": "one-line summary"}'
                    ),
                },
                {"role": "user", "content": message},
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
        )

        result = json.loads(response.choices[0].message.content)
        logger.info(
            f"Intent detected: {result['intent']} "
            f"(confidence: {result['confidence']})"
        )
        return result
    except Exception as e:
        logger.error(f"Intent detection failed: {e}")
        return {
            "intent": "unknown",
            "confidence": 0.0,
            "summary": f"Error: {str(e)}",
        }


def generate_reply(
    customer_message: str,
    intent: str,
    conversation_history: list[dict] | None = None,
) -> str:
    """Generate a professional AI reply based on intent and conversation context."""
    client = _get_client()
    if not client:
        return "Thank you for reaching out. An agent will respond shortly."

    history_text = ""
    if conversation_history:
        history_text = "\n".join(
            f"{msg['sender']}: {msg['content']}"
            for msg in conversation_history[-5:]
        )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional customer support agent. "
                        f"The customer's intent is: {intent}. "
                        "Write a helpful, empathetic, and professional response. "
                        "Keep it concise (2-3 paragraphs max). "
                        "If previous conversation exists, maintain context.\n\n"
                        f"Previous conversation:\n{history_text}"
                    ),
                },
                {"role": "user", "content": customer_message},
            ],
            temperature=0.7,
            max_tokens=500,
        )

        reply = response.choices[0].message.content
        logger.info("AI reply generated successfully")
        return reply
    except Exception as e:
        logger.error(f"Reply generation failed: {e}")
        return "Thank you for reaching out. An agent will respond shortly."


def validate_document(
    filename: str, file_type: str, context: str = ""
) -> dict:
    """
    Use AI to assess whether a document appears valid.
    Returns: {"is_valid": bool, "notes": str}
    """
    client = _get_client()
    if not client:
        return {"is_valid": None, "notes": "AI validation not available"}

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a document validation assistant. "
                        "Based on the filename and type, assess if this "
                        "appears to be a valid document. Respond with ONLY "
                        "a JSON object: "
                        '{"is_valid": true/false, "notes": "explanation"}'
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Filename: {filename}\n"
                        f"File type: {file_type}\n"
                        f"Context: {context}"
                    ),
                },
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
        )

        return json.loads(response.choices[0].message.content)
    except Exception as e:
        logger.error(f"Document validation failed: {e}")
        return {"is_valid": None, "notes": f"Validation error: {str(e)}"}
