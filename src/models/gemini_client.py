"""
Gemini client module for Sports Quiz AI.

Provides a thin, well-typed wrapper around the official Google Gen AI
Python SDK for sending prompts to a configured Gemini model and
retrieving generated text.
"""

from re import error

from google import genai

from src.config.settings import GEMINI_API_KEY, MODEL_NAME


class GeminiClient:
    """
    Wraps the Google Gen AI SDK to provide a simple text generation
    interface backed by a configured Gemini model.
    """

    def __init__(self) -> None:
        """
        Initialize the Gemini client using credentials and model settings
        loaded from src/config/settings.py.

        Raises:
            ValueError: If GEMINI_API_KEY is not configured.
        """
        if not GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY is not set. Please configure it in your "
                "environment or .env file."
            )

        self._model_name: str = MODEL_NAME
        print(f"Using Gemini model: {self._model_name}")
        self._client: genai.Client = genai.Client(api_key=GEMINI_API_KEY)

    def generate(self, prompt: str) -> str:
        """
        Generate text from the configured Gemini model for a given prompt.

        Args:
            prompt: The input prompt to send to the model.

        Returns:
            The generated text response.

        Raises:
            ValueError: If the prompt is empty or whitespace only.
            RuntimeError: If the Gemini API call fails or returns no
                          usable text.
        """
        if not prompt or not prompt.strip():
            raise ValueError("prompt must not be empty.")

        try:
            response = self._client.models.generate_content(
                model=self._model_name,
                contents=prompt,
            )
        except Exception as error:
            raise RuntimeError(
                f"Gemini model '{self._model_name}' failed: {error}"
            ) from error

        generated_text = getattr(response, "text", None)
        if not generated_text:
            raise RuntimeError("Gemini returned an empty response.")

        return generated_text