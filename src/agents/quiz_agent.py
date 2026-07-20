"""
Quiz generation agent for Sports Quiz AI.

Orchestrates a RAG pipeline that combines semantic retrieval from
ChromaDB, live web search results, and the Gemini LLM to generate
multiple-choice sports quizzes.
"""

from typing import List

from src.database.chroma_manager import ChromaManager
from src.models.gemini_client import GeminiClient
from src.search.web_search import WebSearch

# Number of documents to retrieve from ChromaDB for context.
CHROMA_CONTEXT_RESULTS: int = 5

# Number of web search snippets to retrieve for live context.
WEB_SEARCH_RESULTS: int = 5


class QuizAgent:
    """
    Coordinates retrieval-augmented generation to produce multiple-choice
    sports quizzes, combining stored knowledge from ChromaDB with live
    web search results, then generating questions via Gemini.
    """

    def __init__(self) -> None:
        """
        Initialize the QuizAgent and its underlying components.

        Sets up the ChromaDB manager (and initializes its persistent
        collection), the web search client, and the Gemini client.
        """
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
        Generate a multiple-choice sports quiz on a given topic.

        Args:
            topic: The sports topic to generate quiz questions about.
            difficulty: The desired difficulty level (e.g. "easy",
                        "medium", "hard").
            num_questions: The number of quiz questions to generate.

        Returns:
            The generated quiz as plain text, formatted as instructed
            in the prompt sent to Gemini.

        Raises:
            ValueError: If topic is empty or num_questions is not positive.
        """
        if not topic or not topic.strip():
            raise ValueError("topic must not be empty.")

        if num_questions <= 0:
            raise ValueError("num_questions must be a positive integer.")

        stored_context = self._retrieve_context(topic)
        web_context = self._get_web_context(topic, difficulty)

        prompt = self._build_prompt(
            topic=topic,
            difficulty=difficulty,
            num_questions=num_questions,
            stored_context=stored_context,
            web_context=web_context,
        )

        return self._gemini_client.generate(prompt)

    def _retrieve_context(self, topic: str) -> List[str]:
        """
        Retrieve relevant stored knowledge for a topic from ChromaDB.

        Args:
            topic: The topic to search the vector store for.

        Returns:
            A list of relevant document texts. Returns an empty list if
            no documents are found or retrieval fails.
        """
        try:
            return self._chroma_manager.query(
                query_text=topic,
                n_results=CHROMA_CONTEXT_RESULTS,
            )
        except Exception:
            return []

    def _get_web_context(self, topic: str, difficulty: str) -> List[str]:
        """
        Retrieve live web search snippets for recent information on a
        topic, tailored to the requested difficulty level.

        Easy queries look for basic, widely-covered information; Medium
        and Hard queries specifically target statistics, tournament
        history, and lesser-known facts, since that content is unlikely
        to exist in the small local knowledge base and needs live
        search to be well grounded.

        Args:
            topic: The topic to search the web for.
            difficulty: The desired difficulty level (e.g. "easy",
                        "medium", "hard").

        Returns:
            A list of clean text snippets. Returns an empty list if no
            results are found or the search fails.
        """
        query_focus_by_difficulty = {
            "easy": "basic rules famous players",
            "medium": "statistics tournament history player records",
            "hard": "rare records historic matches advanced rules",
        }
        query_focus = query_focus_by_difficulty.get(
            difficulty.strip().lower(), "facts and records"
        )

        query = f"{topic} {query_focus}"
        return self._web_search.search(query, max_results=WEB_SEARCH_RESULTS)

    def _difficulty_guidance(self, difficulty: str) -> str:
        """
        Return a content-focus instruction for the requested difficulty.

        Gives Gemini a concrete definition of what each difficulty
        level means in terms of content, instead of leaving it to
        infer "harder" as "needs more specific facts than are
        available" — which was previously causing it to refuse to
        generate a quiz for Medium and Hard difficulty.

        Args:
            difficulty: The desired difficulty level (e.g. "easy",
                        "medium", "hard").

        Returns:
            A single instruction line describing what the quiz content
            should focus on for that difficulty.
        """
        guidance_by_difficulty = {
            "easy": (
                "- Focus on basic rules, famous players, and general "
                "knowledge that a casual fan would know."
            ),
            "medium": (
                "- Focus on match situations, statistics, tournament "
                "history, and notable player records."
            ),
            "hard": (
                "- Focus on advanced rules, historic matches, rare "
                "records, tactical concepts, and lesser-known facts."
            ),
        }
        return guidance_by_difficulty.get(
            difficulty.strip().lower(),
            "- Match the requested difficulty level as closely as "
            "possible.",
        )

    def _build_prompt(
        self,
        topic: str,
        difficulty: str,
        num_questions: int,
        stored_context: List[str],
        web_context: List[str],
    ) -> str:
        """
        Build a clear, structured prompt instructing Gemini to generate
        a multiple-choice quiz.

        Args:
            topic: The sports topic for the quiz.
            difficulty: The desired difficulty level.
            num_questions: The number of questions to generate.
            stored_context: Relevant documents retrieved from ChromaDB.
            web_context: Relevant snippets retrieved from web search.

        Returns:
            A complete prompt string ready to send to GeminiClient.
        """
        stored_section = (
            "\n".join(f"- {item}" for item in stored_context)
            if stored_context
            else "No stored knowledge base context was found for this topic."
        )

        web_section = (
            "\n".join(f"- {item}" for item in web_context)
            if web_context
            else "No live web search context was found for this topic."
        )

        return (
            "You are an expert sports quiz generator. Using the context "
            "provided below, generate a multiple-choice quiz.\n\n"
            f"Topic: {topic}\n"
            f"Difficulty: {difficulty}\n"
            f"Number of questions: {num_questions}\n\n"
            "Knowledge base context:\n"
            f"{stored_section}\n\n"
            "Recent web search context:\n"
            f"{web_section}\n\n"
            "Instructions:\n"
            f"- Generate exactly {num_questions} multiple-choice questions "
            f"about {topic} at {difficulty} difficulty.\n"
            "- Use the knowledge base and web search context above as "
            "your primary source of information.\n"
            "- If the retrieved context does not fully cover a fact you "
            "need, use your own accurate general sports knowledge to "
            "fill the gap confidently. Do not say the context is "
            "insufficient, and do not refuse to generate the quiz.\n"
            "- Never invent statistics, records, or scores you are not "
            "confident are factually correct.\n"
            "- Only decline to generate questions if the requested "
            "topic is entirely unrelated to sports.\n"
            f"{self._difficulty_guidance(difficulty)}\n"
            "- Format the output as valid Markdown, using EXACTLY this "
            "structure for every question, with no deviations:\n\n"
            "## Question 1\n"
            "Question text\n"
            "A)\n"
            "B)\n"
            "C)\n"
            "D)\n"
            "✅ Correct Answer: B\n"
            "📖 Explanation:\n"
            "One or two concise sentences.\n\n"
            "- Repeat this structure for each question, incrementing the "
            '"## Question N" heading number in order.\n'
            '- Do not use bold ("**") anywhere in the output.\n'
            "- Do not wrap headings in bold or any other Markdown "
            "emphasis.\n"
            "- Do not add any extra commentary, titles, or text outside "
            "of this structure.\n"
            "- Return clean Markdown only."
        )