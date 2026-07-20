"""
Prompt construction module for Sports Quiz AI.

Provides a dedicated builder for the multi-line prompt sent to Gemini
when generating multiple-choice sports quizzes, keeping prompt text
separate from agent orchestration logic.
"""

from typing import List

# Placeholder text used when no stored knowledge base context is available.
NO_STORED_CONTEXT_MESSAGE: str = (
    "No relevant knowledge base context was found for this topic."
)

# Placeholder text used when no live web search context is available.
NO_WEB_CONTEXT_MESSAGE: str = (
    "No relevant live web search context was found for this topic."
)


class QuizPromptBuilder:
    """
    Builds clean, well-structured prompts instructing Gemini to generate
    multiple-choice sports quizzes from combined knowledge base and web
    search context.
    """

    @staticmethod
    def build_prompt(
        topic: str,
        difficulty: str,
        num_questions: int,
        stored_context: List[str],
        web_context: List[str],
    ) -> str:
        """
        Build a complete prompt for multiple-choice quiz generation.

        Args:
            topic: The sports topic the quiz should cover.
            difficulty: The desired difficulty level (e.g. "easy",
                        "medium", "hard").
            num_questions: The number of quiz questions to generate.
            stored_context: Relevant documents retrieved from the
                            ChromaDB knowledge base. May be empty.
            web_context: Relevant snippets retrieved from live web
                         search. May be empty.

        Returns:
            A complete, formatted prompt string ready to send to
            GeminiClient.
        """
        stored_section = QuizPromptBuilder._format_context(
            stored_context, NO_STORED_CONTEXT_MESSAGE
        )
        web_section = QuizPromptBuilder._format_context(
            web_context, NO_WEB_CONTEXT_MESSAGE
        )

        return f"""You are an expert sports quiz generator.

Topic: {topic}
Difficulty: {difficulty}
Number of Questions: {num_questions}

Knowledge Base Context:
{stored_section}

Live Web Search Context:
{web_section}

Instructions:
- Generate exactly {num_questions} multiple-choice questions about {topic} at {difficulty} difficulty.
- Use the Knowledge Base Context as the primary source of information.
- Use the Live Web Search Context only to include recent information when relevant.
- Do not invent unsupported facts.
- If there is insufficient context to generate accurate questions, state that clearly instead of making assumptions.
- Format the output as valid Markdown, using EXACTLY this structure for every question, with no deviations:

## Question 1
Question text
A)
B)
C)
D)
✅ Correct Answer: B
📖 Explanation:
One or two concise sentences.

- Repeat this structure for each question, incrementing the "## Question N" heading number in order.
- Do not use bold ("**") anywhere in the output.
- Do not wrap headings in bold or any other Markdown emphasis.
- Do not add any extra commentary, titles, or text outside of this structure.
- Return clean Markdown only.
"""

    @staticmethod
    def _format_context(context_items: List[str], placeholder: str) -> str:
        """
        Format a list of context strings as a bullet-point section.

        Args:
            context_items: List of context snippets to format. May be
                            empty.
            placeholder: Message to use if `context_items` is empty.

        Returns:
            A newline-joined, bullet-point formatted string, or the
            placeholder message if no context items are provided.
        """
        if not context_items:
            return placeholder

        return "\n".join(f"- {item}" for item in context_items)