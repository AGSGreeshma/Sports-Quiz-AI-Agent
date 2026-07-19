"""
Quiz generation agent for Sports Quiz AI.

Coordinates the Retrieval-Augmented Generation (RAG) pipeline by
combining:
- ChromaDB semantic retrieval
- DuckDuckGo web search
- Google Gemini
"""

from src.database.chroma_manager import ChromaManager
from src.models.gemini_client import GeminiClient
from src.prompts.quiz_prompt import QuizPromptBuilder
from src.search.web_search import WebSearch

# Configuration
CHROMA_CONTEXT_RESULTS = 5
WEB_SEARCH_RESULTS = 5

VALID_DIFFICULTIES = {"easy", "medium", "hard"}


class QuizAgent:
    """
    Main orchestration class for quiz generation.
    """

    def __init__(self) -> None:
        """Initialize all project components."""

        self._chroma_manager = ChromaManager()
        self._chroma_manager.initialize()

        self._web_search = WebSearch()
        self._gemini_client = GeminiClient()

    def generate_quiz(
        self,
        topic: str,
        difficulty: str,
        num_questions: int,
    ) -> str:
        """
        Generate a sports quiz.

        Args:
            topic: Quiz topic.
            difficulty: easy, medium or hard.
            num_questions: Number of questions.

        Returns:
            Generated quiz.
        """

        if not topic.strip():
            raise ValueError("Topic cannot be empty.")

        difficulty = difficulty.lower()

        if difficulty not in VALID_DIFFICULTIES:
            raise ValueError(
                f"Difficulty must be one of {VALID_DIFFICULTIES}"
            )

        if num_questions <= 0:
            raise ValueError(
                "Number of questions must be greater than zero."
            )

        # ----------------------------
        # Retrieve ChromaDB context
        # ----------------------------

        stored_context = self._retrieve_context(topic)

        print("\n========== CHROMADB CONTEXT ==========")
        print(stored_context)

        # ----------------------------
        # Retrieve Web Context
        # ----------------------------

        web_context = self._get_web_context(topic)

        print("\n========== WEB SEARCH CONTEXT ==========")
        print(web_context)

        # ----------------------------
        # Build Prompt
        # ----------------------------

        prompt = QuizPromptBuilder.build_prompt(
            topic=topic,
            difficulty=difficulty,
            num_questions=num_questions,
            stored_context=stored_context,
            web_context=web_context,
        )

        print("\n========== PROMPT ==========\n")
        print(prompt)

        # ----------------------------
        # Generate Quiz
        # ----------------------------

        return self._gemini_client.generate(prompt)

    def _retrieve_context(self, topic: str) -> list[str]:
        """
        Retrieve semantic context from ChromaDB.
        """

        try:
            return self._chroma_manager.query(
                query_text=topic,
                n_results=CHROMA_CONTEXT_RESULTS,
            )

        except Exception as error:
            print(f"ChromaDB Error: {error}")
            return []

    def _get_web_context(self, topic: str) -> list[str]:
        """
        Retrieve recent web search context.
        """

        query = f"latest {topic} sports facts and records"

        try:
            return self._web_search.search(
                query=query,
                max_results=WEB_SEARCH_RESULTS,
            )

        except Exception as error:
            print(f"Web Search Error: {error}")
            return []