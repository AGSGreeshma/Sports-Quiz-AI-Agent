"""
Sports Quiz AI
--------------
Streamlit frontend for the AI-Powered Sports Quiz Generation Agent.

Collects quiz parameters from the user, invokes the QuizAgent's
RAG pipeline, and displays the generated sports quiz.
"""

import streamlit as st

from src.agents.quiz_agent import QuizAgent

# Available sports
SPORT_OPTIONS = [
    "Cricket",
    "Football",
    "Basketball",
    "Tennis",
    "Olympics",
]

# Difficulty levels
DIFFICULTY_OPTIONS = [
    "Easy",
    "Medium",
    "Hard",
]


def configure_page() -> None:
    """Configure the Streamlit page."""

    st.set_page_config(
        page_title="Sports Quiz AI",
        page_icon="🏆",
        layout="centered",
    )


def render_header() -> None:
    """Render the application header."""

    st.title("🏆 Sports Quiz AI")

    st.caption(
        "Generate AI-powered sports quizzes using "
        "Retrieval-Augmented Generation (RAG) and Google Gemini."
    )

    st.write(
        "Choose a sport, difficulty level, and number of questions "
        "from the sidebar, then click **Generate Quiz**."
    )

    st.divider()


def render_sidebar() -> tuple[str, str, int]:
    """
    Render the sidebar controls.

    Returns:
        Selected sport, difficulty, and number of questions.
    """

    st.sidebar.header("⚙️ Quiz Settings")

    sport = st.sidebar.selectbox(
        "Sport",
        SPORT_OPTIONS,
    )

    difficulty = st.sidebar.selectbox(
        "Difficulty",
        DIFFICULTY_OPTIONS,
    )

    num_questions = st.sidebar.slider(
        "Number of Questions",
        min_value=1,
        max_value=10,
        value=5,
    )

    return sport, difficulty, num_questions


@st.cache_resource
def create_quiz_agent() -> QuizAgent:
    """
    Create and cache a QuizAgent.

    Returns:
        Cached QuizAgent instance.
    """

    return QuizAgent()


def generate_and_display_quiz(
    sport: str,
    difficulty: str,
    num_questions: int,
) -> None:
    """
    Generate and display a quiz.

    Args:
        sport: Selected sport.
        difficulty: Selected difficulty.
        num_questions: Number of questions.
    """

    try:
        agent = create_quiz_agent()

        with st.spinner("Generating quiz..."):

            quiz = agent.generate_quiz(
                topic=sport,
                difficulty=difficulty.lower(),
                num_questions=num_questions,
            )

        st.success("Quiz generated successfully!")

        st.divider()

        st.subheader(f"{sport} Quiz ({difficulty})")

        with st.container():
            st.markdown(quiz)

    except Exception as error:
        st.error(f"❌ Failed to generate quiz.\n\n{error}")


def render_quiz_generator(
    sport: str,
    difficulty: str,
    num_questions: int,
) -> None:
    """
    Render the Generate Quiz button.

    Args:
        sport: Selected sport.
        difficulty: Selected difficulty.
        num_questions: Number of questions.
    """

    if st.button(
        "🚀 Generate Quiz",
        type="primary",
        use_container_width=True,
    ):
        generate_and_display_quiz(
            sport=sport,
            difficulty=difficulty,
            num_questions=num_questions,
        )


def main() -> None:
    """Application entry point."""

    configure_page()

    render_header()

    sport, difficulty, num_questions = render_sidebar()

    render_quiz_generator(
        sport,
        difficulty,
        num_questions,
    )


if __name__ == "__main__":
    main()