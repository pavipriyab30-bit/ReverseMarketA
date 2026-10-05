from typing import Optional

from config import config


try:
    from google import genai
except ImportError:
    genai = None


class GeminiService:
    """Handles communication with Google's Gemini API."""

    def __init__(self):
        self.api_key = config.GEMINI_API_KEY
        self.model_name = config.GEMINI_MODEL
        self.client = None

        if self.api_key and genai is not None:
            self.client = genai.Client(api_key=self.api_key)

    @property
    def is_available(self) -> bool:
        """Return True when Gemini is configured and available."""

        return self.client is not None

    def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
    ) -> str:
        """
        Generate text using Gemini.

        Raises:
            RuntimeError: If Gemini is not configured or unavailable.
            ValueError: If the prompt is empty.
        """

        if not prompt or not prompt.strip():
            raise ValueError("Gemini prompt cannot be empty.")

        if not self.is_available:
            if genai is None:
                raise RuntimeError(
                    "The google-genai package is not installed."
                )

            raise RuntimeError(
                "Gemini is not configured. "
                "Please provide a Gemini API key."
            )

        request_config = None

        if system_instruction:
            request_config = {
                "system_instruction": system_instruction
            }

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=request_config,
            )
        except Exception as exc:
            raise RuntimeError(
                f"Gemini request failed: {exc}"
            ) from exc

        text = getattr(response, "text", None)

        if not text:
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return text.strip()


# Shared service instance used by the application.
gemini_service = GeminiService() 