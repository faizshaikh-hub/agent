"""
Groq API client wrapper with retry logic and structured output parsing.
"""
import json
import re
from typing import Optional, Dict, Any
from groq import Groq
from app.config import settings


class GroqClient:
    """Wrapper around the Groq Python SDK for LLM calls."""

    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL
        self.fallback_model = settings.GROQ_FALLBACK_MODEL

    def chat(
        self,
        messages: list,
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2048,
        json_mode: bool = False,
    ) -> str:
        """
        Send a chat completion request to Groq.

        Args:
            messages: List of message dicts with 'role' and 'content'.
            model: Model override. Defaults to configured model.
            temperature: Sampling temperature.
            max_tokens: Max tokens in response.
            json_mode: If True, request JSON response format.

        Returns:
            The assistant's response text.
        """
        use_model = model or self.model
        kwargs: Dict[str, Any] = {
            "model": use_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        try:
            response = self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        except Exception as e:
            # Retry with fallback model if primary fails
            if use_model != self.fallback_model:
                print(f"Primary model failed ({e}), retrying with {self.fallback_model}")
                kwargs["model"] = self.fallback_model
                try:
                    response = self.client.chat.completions.create(**kwargs)
                    return response.choices[0].message.content
                except Exception as e2:
                    raise RuntimeError(f"Both models failed. Primary: {e}, Fallback: {e2}")
            raise

    def chat_json(
        self,
        messages: list,
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> dict:
        """
        Send a chat request expecting a JSON response.
        Parses the response and returns a Python dict.
        """
        raw = self.chat(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            json_mode=True,
        )
        return self._parse_json(raw)

    @staticmethod
    def _parse_json(text: str) -> dict:
        """Parse JSON from LLM response, handling markdown code blocks."""
        # Try direct parse first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try extracting from markdown code block
        json_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # Try finding JSON object in text
        brace_match = re.search(r"\{.*\}", text, re.DOTALL)
        if brace_match:
            try:
                return json.loads(brace_match.group(0))
            except json.JSONDecodeError:
                pass

        return {"error": "Failed to parse JSON response", "raw": text}


# Singleton instance
groq_client = GroqClient()
