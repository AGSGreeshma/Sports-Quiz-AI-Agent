"""
Sports Quiz AI
--------------
Streamlit frontend for the AI-Powered Sports Quiz Generation Agent.

This module is UI-only: it renders a polished, dashboard-style
interface around the existing RAG backend (QuizAgent), without
altering any backend logic, prompts, retrieval, or data pipelines.

Design system
-------------
Primary gradient : #4F46E5 -> #7C3AED (indigo -> violet)
Accent (gold)     : #D97706 (used only for "Correct Answer")
Background        : #F7F8FA   Card: #FFFFFF
Text              : #111827   Muted: #6B7280   Border: #E5E7EB

The design system now also exposes a dedicated set of sidebar tokens
(--sqai-sidebar-*) with automatic light/dark variants via
`prefers-color-scheme`, so the sidebar, empty state, and footer all
share one coherent, theme-aware visual language.
"""

import html
import random
import re

import streamlit as st

from src.agents.quiz_agent import QuizAgent

# ---------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------

SPORT_OPTIONS = [
    "Cricket",
    "Football",
    "Basketball",
    "Tennis",
    "Olympics",
    "Volleyball",
    "Hockey",
    "Formula 1",
    "Swimming",
    "Athletics (Track & Field)"
]

DIFFICULTY_OPTIONS = [
    "Easy",
    "Medium",
    "Hard",
]

QUIZ_STATE_KEY = "quiz_state"
APP_VERSION = "v1.2.0"

# (icon, name) pairs reused across the sidebar and the footer, so the
# tech-stack list only needs to be maintained in one place.
POWERED_BY = [
    ("🤖", "Google Gemini"),
    ("🗂️", "ChromaDB"),
    ("🔎", "DuckDuckGo Search"),
    ("🎈", "Streamlit"),
]

FEATURE_LIST = [
    "Generate custom multiple-choice quizzes",
    "Regenerate instantly with one click",
    "Download your quiz as a text file",
    "Answers grounded in retrieved sports knowledge",
]

SPORT_EMOJIS = ["🏏", "⚽", "🏀", "🎾", "🥇", "🏆", "🥊", "🏓"]

FUN_FACT_ICON = "💡"

FUN_FACTS = [
    "The modern Olympic Games have been held since 1896.",
    "A cricket Test match can last up to five days.",
    "Basketball was invented in 1891 by James Naismith.",
    "Wimbledon is the oldest tennis tournament in the world.",
    "The FIFA World Cup is held once every four years.",
    "A badminton shuttlecock is the fastest-moving object in sports, reaching speeds over 500 km/h.",
    "A standard basketball hoop has been 10 feet high since the sport was invented.",
    "The Olympic rings represent the unity of the five inhabited continents.",
    "The marathon race covers a distance of 42.195 kilometers.",
    "The first FIFA World Cup was held in Uruguay in 1930.",
    "Sachin Tendulkar is the first cricketer to score 100 international centuries.",
    "Tennis balls were originally made in white before yellow became the standard for television visibility.",
    "The Stanley Cup is the oldest professional sports trophy in North America.",
    "Golf balls typically have between 300 and 500 dimples to improve flight.",
    "The Tour de France is one of the world's most prestigious cycling races.",
    "Table tennis became an Olympic sport in 1988.",
    "The first modern basketball game was played using a soccer ball and peach baskets.",
    "The Olympic torch relay begins in Olympia, Greece, before each Summer Olympics.",
    "The Ashes is one of the oldest and most famous rivalries in international cricket.",
    "Michael Phelps is the most decorated Olympian, with 28 Olympic medals.",
    "The first official Wimbledon Championship was held in 1877.",
    "The fastest recorded tennis serve exceeded 260 km/h.",
    "The FIFA Women's World Cup was first held in 1991.",
    "Chess has been recognized as a sport by the International Olympic Committee.",
    "The Olympic motto is 'Faster, Higher, Stronger – Together.'"
]

# Placeholders — replace with your own project links before publishing.
GITHUB_URL_PLACEHOLDER = "https://github.com/AGSGreeshma?tab=repositories"
DEVELOPER_NAME_PLACEHOLDER = "AGS Greeshma"


# ---------------------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------------------


# ---------------------------------------------------------------------
# HTML Rendering Helper
# ---------------------------------------------------------------------


def _render_raw_html(markup: str) -> None:
    """
    Render a raw HTML string via st.markdown, safely.

    Markdown's spec treats any line indented four or more spaces as a
    preformatted code block. Python's triple-quoted f-strings inherit
    indentation from the surrounding code, and nested f-strings (e.g.
    an inner fragment interpolated into an outer template) compound
    that indentation — so without normalizing it here, custom HTML can
    render as literal escaped text instead of being parsed as markup.
    This strips leading whitespace from every line before rendering,
    regardless of how deeply the source string was nested or indented.

    Args:
        markup: Raw HTML to render.
    """

    normalized = "\n".join(line.strip() for line in markup.strip().splitlines())
    st.markdown(normalized, unsafe_allow_html=True)


def configure_page() -> None:
    """Configure the Streamlit page (title, icon, layout)."""

    st.set_page_config(
        page_title="Sports Quiz AI",
        page_icon="🏆",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def inject_custom_css() -> None:
    """
    Inject a small, self-contained CSS layer on top of native Streamlit
    components.

    Scope is deliberately narrow: color tokens (including a dedicated
    sidebar token set with light/dark variants), card styling for
    bordered containers, button hover states, the hero banner, the
    quiz-card component, the sidebar, the empty state, and the footer.
    Every rule is prefixed or scoped to avoid clashing with Streamlit's
    own styles, and `prefers-reduced-motion` disables the non-essential
    animations.
    """

    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;0,800;1,600&display=swap');

        :root {
            --sqai-primary-start: #4F46E5;
            --sqai-primary-end: #7C3AED;
            --sqai-gold: #D97706;
            --sqai-gold-bg: #FFFBEB;
            --sqai-text: #111827;
            --sqai-muted: #6B7280;
            --sqai-border: #E5E7EB;
            --sqai-card-bg: #FFFFFF;
            --sqai-badge-bg: #EEF2FF;
            --sqai-explanation-bg: #F5F3FF;
            --sqai-option-bg: #F9FAFB;
            --sqai-answer-label: #92400E;
            --sqai-explanation-label: #4338CA;
            --sqai-radius: 14px;
            --sqai-shadow: 0 1px 3px rgba(17, 24, 39, 0.06),
                           0 1px 2px rgba(17, 24, 39, 0.04);
            --sqai-shadow-hover: 0 8px 20px rgba(17, 24, 39, 0.10),
                                 0 2px 6px rgba(17, 24, 39, 0.06);

            /* ---- Sidebar tokens (light mode default) ---- */
            --sqai-sidebar-bg: #FAFAFF;
            --sqai-sidebar-surface: #FFFFFF;
            --sqai-sidebar-surface-alt: #F5F3FF;
            --sqai-sidebar-border: #E5E7EB;
            --sqai-sidebar-text: #111827;
            --sqai-sidebar-muted: #6B7280;
            --sqai-sidebar-accent: #4F46E5;
            --sqai-sidebar-shadow: 0 1px 2px rgba(17, 24, 39, 0.05);

            /* ---- Typography ---- */
            --sqai-font-sans: "Plus Jakarta Sans", "Inter", -apple-system,
                               BlinkMacSystemFont, "Segoe UI", sans-serif;
            --sqai-font-mono: ui-monospace, SFMono-Regular, Menlo, Consolas,
                               monospace;
        }

        /*
         * Dark mode is bound to TWO signals:
         *   1) Streamlit's own in-app theme toggle, which sets
         *      data-theme="dark" on the root .stApp container — this is
         *      what actually changes when a user flips the app's theme.
         *   2) prefers-color-scheme, as a fallback for contexts where the
         *      app inherits the OS/browser theme directly.
         * Both point at the same token values so every themed surface
         * (sidebar, cards, hero, footer, empty state) reacts consistently.
         */
        .stApp[data-theme="dark"],
        [data-theme="dark"] .stApp {
            --sqai-text: #F3F4F6;
            --sqai-muted: #9CA3AF;
            --sqai-border: #2D2D3A;
            --sqai-card-bg: #1B1B26;
            --sqai-badge-bg: #23233A;
            --sqai-explanation-bg: #23232F;
            --sqai-option-bg: #1F1F2B;
            --sqai-gold-bg: #2A2110;
            --sqai-answer-label: #FBBF24;
            --sqai-explanation-label: #A78BFA;

            --sqai-sidebar-bg: #14141C;
            --sqai-sidebar-surface: #1B1B26;
            --sqai-sidebar-surface-alt: #23232F;
            --sqai-sidebar-border: #2D2D3A;
            --sqai-sidebar-text: #F3F4F6;
            --sqai-sidebar-muted: #9CA3AF;
            --sqai-sidebar-accent: #A78BFA;
            --sqai-sidebar-shadow: 0 1px 3px rgba(0, 0, 0, 0.35);
        }

        @media (prefers-color-scheme: dark) {
            :root {
                --sqai-text: #F3F4F6;
                --sqai-muted: #9CA3AF;
                --sqai-border: #2D2D3A;
                --sqai-card-bg: #1B1B26;
                --sqai-badge-bg: #23233A;
                --sqai-explanation-bg: #23232F;
                --sqai-option-bg: #1F1F2B;
                --sqai-gold-bg: #2A2110;
                --sqai-answer-label: #FBBF24;
                --sqai-explanation-label: #A78BFA;

                --sqai-sidebar-bg: #14141C;
                --sqai-sidebar-surface: #1B1B26;
                --sqai-sidebar-surface-alt: #23232F;
                --sqai-sidebar-border: #2D2D3A;
                --sqai-sidebar-text: #F3F4F6;
                --sqai-sidebar-muted: #9CA3AF;
                --sqai-sidebar-accent: #A78BFA;
                --sqai-sidebar-shadow: 0 1px 3px rgba(0, 0, 0, 0.35);
            }
        }

        html, body, .stApp {
            font-family: var(--sqai-font-sans);
        }

        /*
         * Streamlit's own icons (e.g. the sidebar collapse/expand arrow,
         * and the icons inside the header's "⋮" menu such as the theme
         * picker) render via a Material Symbols ligature font — the
         * ligature text (like "keyboard_double_arrow_right" or
         * "contrast") only becomes a glyph when that specific icon font
         * is applied. The broad font-family override above would
         * otherwise turn those into literal, overlapping text, so every
         * icon-bearing element — including ones Streamlit renders into
         * portal/popover layers outside the main app container — is
         * matched here via wildcard testid/class patterns and kept on
         * the icon font Streamlit ships with.
         */
        [data-testid="stIconMaterial"],
        span[data-testid="stIconMaterial"],
        [data-testid*="Icon"],
        [data-testid*="icon"],
        [class*="material-icon"],
        [class*="Icon" i],
        [class*="icon" i] {
            font-family: "Material Symbols Rounded", "Material Icons" !important;
        }

        /*
         * Apply the elegant font explicitly to genuine text-bearing
         * elements (as opposed to the icon-bearing ones excluded above),
         * so headings, body copy, and form controls pick it up reliably
         * even where Streamlit sets its own font-family on them directly.
         */
        h1, h2, h3, h4, h5, h6, p, label, li,
        button, input, textarea, select,
        [data-testid="stMarkdownContainer"],
        [data-testid="stCaptionContainer"],
        [data-testid="stMetricValue"],
        [data-testid="stMetricLabel"] {
            font-family: var(--sqai-font-sans) !important;
        }

        /* ---------------- Header toolbar (Deploy / "⋮" menu) ---------------- */
        header[data-testid="stHeader"] button {
            border-radius: 8px !important;
            transition: background 0.15s ease, transform 0.15s ease;
        }
        header[data-testid="stHeader"] button:hover {
            background: var(--sqai-explanation-bg) !important;
            transform: translateY(-1px);
        }

        /* The dropdown opened by the "⋮" menu (theme picker, Rerun, etc.)
           is a BaseWeb popover rendered outside the normal app tree, so it
           is styled via BaseWeb's own stable data attribute rather than a
           Streamlit testid. */
        [data-baseweb="menu"] {
            border-radius: var(--sqai-radius) !important;
            box-shadow: var(--sqai-shadow-hover) !important;
            border: 1px solid var(--sqai-border) !important;
            overflow: hidden;
        }
        [data-baseweb="menu"] li:hover,
        [data-baseweb="menu"] [role="option"]:hover,
        [data-baseweb="menu"] [role="menuitem"]:hover {
            background: var(--sqai-explanation-bg) !important;
        }

        /* ---------------- Sidebar collapse / expand control ---------------- */
        [data-testid="collapsedControl"],
        [data-testid="stSidebarCollapseButton"] button,
        [data-testid="baseButton-headerNoPadding"] {
            background: linear-gradient(
                135deg, var(--sqai-primary-start), var(--sqai-primary-end)
            ) !important;
            border-radius: 10px !important;
            box-shadow: var(--sqai-shadow-hover) !important;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }
        [data-testid="collapsedControl"]:hover,
        [data-testid="stSidebarCollapseButton"] button:hover,
        [data-testid="baseButton-headerNoPadding"]:hover {
            transform: scale(1.08);
        }
        [data-testid="collapsedControl"] [data-testid="stIconMaterial"],
        [data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"],
        [data-testid="baseButton-headerNoPadding"] [data-testid="stIconMaterial"] {
            color: #FFFFFF !important;
            font-size: 1.4rem !important;
        }

        /* Wide layout, capped at a readable column width */
        .block-container {
            max-width: 980px;
            margin: 0 auto;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        /* Tighter, heavier headings for a "product" feel */
        h1, h2, h3 {
            font-weight: 700 !important;
            letter-spacing: -0.01em;
        }

        /* ---------------- Hero banner ---------------- */
        .sqai-hero {
            background: linear-gradient(
                135deg, var(--sqai-primary-start), var(--sqai-primary-end)
            );
            border-radius: 20px;
            padding: 2.5rem 2.25rem;
            color: #FFFFFF;
            box-shadow: var(--sqai-shadow-hover);
            animation: sqai-fade-up 0.5s ease both;
            margin-bottom: 2rem;
        }
        .sqai-hero-eyebrow {
            font-size: 0.8rem;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            opacity: 0.85;
            margin-bottom: 0.5rem;
        }
        .sqai-hero-title {
            font-size: 2.1rem;
            font-weight: 800;
            line-height: 1.2;
            margin: 0 0 0.5rem 0;
        }
        .sqai-hero-subtitle {
            font-size: 1.02rem;
            line-height: 1.6;
            opacity: 0.92;
            max-width: 640px;
            margin: 0 0 1.25rem 0;
        }
        .sqai-pill-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }
        .sqai-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            background: rgba(255, 255, 255, 0.16);
            backdrop-filter: blur(6px);
            border: 1px solid rgba(255, 255, 255, 0.28);
            border-radius: 999px;
            padding: 0.35rem 0.85rem;
            font-size: 0.82rem;
            font-weight: 500;
        }

        /* ------------- Bordered containers (native st.container) ------------- */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: var(--sqai-radius) !important;
            border: 1px solid var(--sqai-border) !important;
            box-shadow: var(--sqai-shadow) !important;
            padding: 0.25rem !important;
            transition: box-shadow 0.2s ease, transform 0.2s ease;
        }
        div[data-testid="stVerticalBlockBorderWrapper"]:hover {
            box-shadow: var(--sqai-shadow-hover) !important;
            transform: translateY(-2px);
        }

        /* ---------------- Buttons ---------------- */
        button[kind="primary"] {
            background: linear-gradient(
                135deg, var(--sqai-primary-start), var(--sqai-primary-end)
            ) !important;
            border: none !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }
        button[kind="primary"]:hover:not(:disabled) {
            transform: translateY(-1px);
            box-shadow: var(--sqai-shadow-hover);
        }
        button[kind="secondary"] {
            border-radius: 10px !important;
            font-weight: 600 !important;
            border: 1px solid var(--sqai-border) !important;
            transition: transform 0.15s ease, background 0.15s ease;
        }
        button[kind="secondary"]:hover:not(:disabled) {
            transform: translateY(-1px);
            background: var(--sqai-explanation-bg) !important;
        }

        /* ---------------- Quiz question card ---------------- */
        .sqai-quiz-card {
            background: var(--sqai-card-bg);
            border: 1px solid var(--sqai-border);
            border-radius: var(--sqai-radius);
            box-shadow: var(--sqai-shadow);
            padding: 1.5rem 1.5rem 1.25rem 1.5rem;
            margin-bottom: 1.25rem;
            animation: sqai-fade-up 0.35s ease both;
        }
        .sqai-quiz-card:hover {
            box-shadow: var(--sqai-shadow-hover);
        }
        .sqai-quiz-badge {
            display: inline-block;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            color: var(--sqai-primary-start);
            background: var(--sqai-badge-bg);
            border-radius: 999px;
            padding: 0.25rem 0.7rem;
            margin-bottom: 0.75rem;
        }
        .sqai-quiz-question {
            font-size: 1.05rem;
            font-weight: 600;
            color: var(--sqai-text);
            line-height: 1.5;
            margin-bottom: 0.9rem;
        }
        .sqai-quiz-options {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 0.5rem;
            margin-bottom: 1.1rem;
        }
        .sqai-quiz-option {
            font-family: var(--sqai-font-mono);
            font-size: 0.9rem;
            color: var(--sqai-text);
            background: var(--sqai-option-bg);
            border: 1px solid var(--sqai-border);
            border-radius: 8px;
            padding: 0.5rem 0.7rem;
        }
        .sqai-quiz-answer, .sqai-quiz-explanation {
            border-radius: 10px;
            padding: 0.75rem 1rem;
            margin-top: 0.75rem;
        }
        .sqai-quiz-answer {
            background: var(--sqai-gold-bg);
            border-left: 4px solid var(--sqai-gold);
        }
        .sqai-quiz-explanation {
            background: var(--sqai-explanation-bg);
            border-left: 4px solid var(--sqai-primary-start);
        }
        .sqai-quiz-label {
            display: block;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.03em;
            text-transform: uppercase;
            margin-bottom: 0.25rem;
        }
        .sqai-quiz-answer .sqai-quiz-label { color: var(--sqai-answer-label); }
        .sqai-quiz-explanation .sqai-quiz-label { color: var(--sqai-explanation-label); }
        .sqai-quiz-value {
            font-size: 0.95rem;
            color: var(--sqai-text);
            line-height: 1.5;
            margin: 0;
        }

        /* =====================================================
           SIDEBAR — redesigned
           ===================================================== */
        section[data-testid="stSidebar"] {
            background: linear-gradient(
                180deg, var(--sqai-sidebar-bg) 0%, var(--sqai-sidebar-bg) 100%
            );
        }
        section[data-testid="stSidebar"] > div {
            padding-top: 0.5rem;
        }

        .sqai-sidebar-header {
            background: linear-gradient(
                135deg, var(--sqai-primary-start), var(--sqai-primary-end)
            );
            border-radius: var(--sqai-radius);
            padding: 1.25rem 1.1rem;
            color: #FFFFFF;
            margin-bottom: 1.25rem;
            box-shadow: var(--sqai-shadow);
        }
        .sqai-sidebar-brand-row {
            display: flex;
            align-items: center;
            gap: 0.65rem;
        }
        .sqai-sidebar-logo-icon {
            font-size: 1.6rem;
            line-height: 1;
        }
        .sqai-sidebar-brand {
            font-size: 1.08rem;
            font-weight: 800;
            letter-spacing: -0.01em;
            line-height: 1.2;
        }
        .sqai-sidebar-subtitle {
            font-size: 0.78rem;
            opacity: 0.88;
            margin-top: 0.15rem;
        }
        .sqai-version-tag {
            display: inline-block;
            font-family: var(--sqai-font-mono);
            font-size: 0.7rem;
            font-weight: 600;
            color: #FFFFFF;
            background: rgba(255, 255, 255, 0.18);
            border: 1px solid rgba(255, 255, 255, 0.28);
            border-radius: 999px;
            padding: 0.15rem 0.55rem;
            margin-top: 0.6rem;
        }
        /* Version badge for use on light/dark surfaces (e.g. the footer),
           as opposed to .sqai-version-tag which is tuned specifically for
           the white text needed against the purple sidebar header. */
        .sqai-version-badge {
            display: inline-block;
            font-family: var(--sqai-font-mono);
            font-size: 0.75rem;
            font-weight: 600;
            color: var(--sqai-muted);
            background: var(--sqai-option-bg);
            border: 1px solid var(--sqai-border);
            border-radius: 999px;
            padding: 0.2rem 0.6rem;
        }
        .sqai-sidebar-caption {
            font-size: 0.82rem;
            color: var(--sqai-sidebar-muted);
            line-height: 1.55;
            margin-bottom: 1.25rem;
        }

        .sqai-sidebar-section {
            margin: 1.4rem 0 0.9rem 0;
        }
        .sqai-sidebar-title {
            display: flex;
            align-items: center;
            gap: 0.4rem;
            color: var(--sqai-sidebar-text);
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            margin-bottom: 0.7rem;
        }

        .sqai-sidebar-card {
            background: var(--sqai-sidebar-surface);
            border: 1px solid var(--sqai-sidebar-border);
            border-radius: 12px;
            box-shadow: var(--sqai-sidebar-shadow);
            padding: 0.4rem 0.75rem;
            margin-bottom: 0.9rem;
        }

        .sqai-sidebar-item {
            display: flex;
            align-items: center;
            gap: 0.55rem;
            padding: 0.55rem 0.1rem;
            color: var(--sqai-sidebar-text);
            font-size: 0.88rem;
            border-bottom: 1px solid var(--sqai-sidebar-border);
        }
        .sqai-sidebar-item:last-child {
            border-bottom: none;
        }

        .sqai-feature {
            display: flex;
            align-items: flex-start;
            gap: 0.5rem;
            padding: 0.45rem 0.1rem;
            color: var(--sqai-sidebar-text);
            font-size: 0.84rem;
            line-height: 1.45;
        }
        .sqai-feature::before {
            content: "✓";
            color: var(--sqai-sidebar-accent);
            font-weight: 700;
            flex-shrink: 0;
        }

        .sqai-sidebar-divider {
            height: 1px;
            background: var(--sqai-sidebar-border);
            border: none;
            margin: 1.1rem 0;
        }

        .sqai-sidebar-footer {
            text-align: center;
            font-size: 0.76rem;
            color: var(--sqai-sidebar-muted);
            padding: 1rem 0 0.4rem 0;
            margin-top: 0.4rem;
        }
        .sqai-sidebar-footer span.sqai-heart {
            color: #EF4444;
        }

        /* Native Streamlit widgets inside the sidebar */
        section[data-testid="stSidebar"] label {
            color: var(--sqai-sidebar-text) !important;
            font-size: 0.85rem !important;
            font-weight: 600 !important;
        }
        section[data-testid="stSidebar"] [data-baseweb="select"] > div {
            border-radius: 10px !important;
            border-color: var(--sqai-sidebar-border) !important;
        }

        /* ---------------- Empty state ---------------- */
        .sqai-empty-state {
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            padding: 3.25rem 1.75rem;
            background: linear-gradient(
                180deg, var(--sqai-card-bg) 0%, var(--sqai-option-bg) 100%
            );
            border: 1px dashed var(--sqai-border);
            border-radius: var(--sqai-radius);
            box-shadow: var(--sqai-shadow);
        }
        .sqai-empty-icon {
            font-size: 2.75rem;
            margin-bottom: 0.6rem;
            line-height: 1;
            display: inline-block;
            animation: sqai-bounce 2.6s ease-in-out infinite;
        }
        .sqai-empty-title {
            font-size: 1.2rem;
            font-weight: 700;
            color: var(--sqai-text) !important;
            opacity: 1 !important;
            margin: 0 0 0.4rem 0;
            text-align: center !important;
        }
        .sqai-empty-description {
            font-size: 0.92rem;
            color: var(--sqai-muted);
            line-height: 1.55;
            max-width: 420px;
            width: 100%;
            margin: 0 auto;
            text-align: center !important;
        }
        .sqai-empty-description strong {
            color: var(--sqai-primary-start);
        }

        /* ---------------- Fun fact card ---------------- */
        .sqai-fun-fact {
            position: relative;
            overflow: hidden;
            display: flex;
            align-items: flex-start;
            gap: 0.9rem;
            text-align: left;
            background: linear-gradient(
                135deg, var(--sqai-badge-bg) 0%, var(--sqai-explanation-bg) 100%
            );
            border: 1px solid var(--sqai-border);
            border-radius: var(--sqai-radius);
            padding: 1.25rem 1.4rem;
            margin-top: 1.25rem;
            box-shadow: var(--sqai-shadow);
            animation: sqai-fade-up 0.4s ease both;
        }
        .sqai-fun-fact::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 5px;
            height: 100%;
            background: linear-gradient(
                180deg, var(--sqai-primary-start), var(--sqai-primary-end)
            );
        }
        .sqai-fun-fact-icon {
            font-size: 1.9rem;
            line-height: 1;
            flex-shrink: 0;
            animation: sqai-pulse 2.2s ease-in-out infinite;
        }
        .sqai-fun-fact-body {
            flex: 1;
        }
        .sqai-fun-fact-label {
            display: inline-block;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            color: var(--sqai-primary-start);
            margin-bottom: 0.35rem;
        }
        .sqai-fun-fact-text {
            font-size: 1.05rem;
            font-weight: 500;
            color: var(--sqai-text);
            line-height: 1.5;
            margin: 0;
        }

        @keyframes sqai-bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-6px); }
        }
        @keyframes sqai-pulse {
            0%, 100% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.12); opacity: 0.85; }
        }

        /* ---------------- Footer ---------------- */
        .sqai-footer {
            background: var(--sqai-card-bg);
            border: 1px solid var(--sqai-border);
            border-radius: var(--sqai-radius);
            box-shadow: var(--sqai-shadow);
            padding: 1.75rem 1.75rem 1.25rem 1.75rem;
            margin-top: 1rem;
        }
        .sqai-footer-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
        }
        .sqai-footer-col h4 {
            font-size: 0.76rem;
            font-weight: 700;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            color: var(--sqai-primary-start);
            margin: 0 0 0.6rem 0;
        }
        .sqai-footer-col p, .sqai-footer-col a {
            font-size: 0.88rem;
            color: var(--sqai-text);
            line-height: 1.6;
            margin: 0 0 0.3rem 0;
        }
        .sqai-footer-col a {
            color: var(--sqai-primary-start);
            text-decoration: none;
            font-weight: 600;
        }
        .sqai-footer-col a:hover {
            text-decoration: underline;
        }

        /* ---------------- Motion & responsiveness ---------------- */
        @keyframes sqai-fade-up {
            from { opacity: 0; transform: translateY(8px); }
            to   { opacity: 1; transform: translateY(0); }
        }

        @media (max-width: 768px) {
            .sqai-hero { padding: 1.75rem 1.5rem; }
            .sqai-hero-title { font-size: 1.6rem; }
            .sqai-quiz-options { grid-template-columns: 1fr; }
            .sqai-footer-grid { grid-template-columns: 1fr; }
            .sqai-footer { padding: 1.4rem; }
            .sqai-empty-state { padding: 2.25rem 1.25rem; }
        }

        @media (prefers-reduced-motion: reduce) {
            .sqai-hero, .sqai-quiz-card,
            button[kind="primary"], button[kind="secondary"],
            div[data-testid="stVerticalBlockBorderWrapper"],
            .sqai-empty-icon, .sqai-fun-fact, .sqai-fun-fact-icon {
                animation: none !important;
                transition: none !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------
# Session State
# ---------------------------------------------------------------------


def initialize_session_state() -> None:
    """Ensure required keys exist in session state before first use."""

    if QUIZ_STATE_KEY not in st.session_state:
        st.session_state[QUIZ_STATE_KEY] = None


# ---------------------------------------------------------------------
# Hero Section
# ---------------------------------------------------------------------


def render_hero_section() -> None:
    """Render the gradient hero banner: eyebrow, title, tagline, pills."""

    _render_raw_html(
        """
        <div class="sqai-hero">
            <div class="sqai-hero-eyebrow">Smarter Quizzes. Better Learning</div>
            <div class="sqai-hero-title">🏆 Sports Quiz AI</div>
            <p class="sqai-hero-subtitle">
                Turn any sport into an instant, AI-crafted trivia
                challenge grounded in a real knowledge base, sharpened
                with live search, and written by Google Gemini.
            </p>
            <div class="sqai-pill-row">
                <span class="sqai-pill">📚 Knowledge Base</span>
                <span class="sqai-pill">🔎 Live Web Search</span>
                <span class="sqai-pill">🤖 Gemini AI</span>
            </div>
        </div>
        """
    )


# ---------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------


def render_sidebar() -> tuple[str, str, int]:
    """
    Render the sidebar: branding, description, settings, tech stack,
    features, and version info.

    Returns:
        The selected sport, difficulty, and number of questions.
    """

    with st.sidebar:
        _render_raw_html(
            f"""
            <div class="sqai-sidebar-header">
                <div class="sqai-sidebar-brand-row">
                    <span class="sqai-sidebar-logo-icon">🏆</span>
                    <div>
                        <div class="sqai-sidebar-brand">Sports Quiz AI</div>
                        <div class="sqai-sidebar-subtitle">
                            AI Powered Sports Trivia
                        </div>
                    </div>
                </div>
                <span class="sqai-version-tag">{APP_VERSION}</span>
            </div>
            """
        )

        _render_raw_html(
            """
            <div class="sqai-sidebar-caption">
                Generate custom multiple-choice sports quizzes instantly,
                with answers grounded in a real knowledge base and live
                web search.
            </div>
            """
        )

        _render_raw_html(
            """
            <div class="sqai-sidebar-section">
                <div class="sqai-sidebar-title">⚙️ Quiz Settings</div>
            </div>
            """
        )

        sport = st.selectbox("🏅 Sport", SPORT_OPTIONS)
        difficulty = st.selectbox("🎯 Difficulty", DIFFICULTY_OPTIONS)
        num_questions = st.slider("❓ Number of Questions", 1, 20, 5)

        _render_raw_html('<hr class="sqai-sidebar-divider" />')

        _render_raw_html(
            """
            <div class="sqai-sidebar-section">
                <div class="sqai-sidebar-title">🚀 Powered By</div>
            </div>
            """
        )
        tech_items_html = "".join(
            f'<div class="sqai-sidebar-item"><span>{icon}</span><span>{name}</span></div>'
            for icon, name in POWERED_BY
        )
        _render_raw_html(f'<div class="sqai-sidebar-card">{tech_items_html}</div>')

        _render_raw_html('<hr class="sqai-sidebar-divider" />')

        _render_raw_html(
            """
            <div class="sqai-sidebar-section">
                <div class="sqai-sidebar-title">✨ Features</div>
            </div>
            """
        )
        feature_items_html = "".join(
            f'<div class="sqai-feature">{feature}</div>' for feature in FEATURE_LIST
        )
        _render_raw_html(f'<div class="sqai-sidebar-card">{feature_items_html}</div>')

        _render_raw_html('<hr class="sqai-sidebar-divider" />')

        _render_raw_html(
            """
            <div class="sqai-sidebar-footer">
                Made with <span class="sqai-heart">❤️</span> using Streamlit
            </div>
            """
        )

    return sport, difficulty, num_questions


# ---------------------------------------------------------------------
# Quiz Agent
# ---------------------------------------------------------------------


@st.cache_resource
def create_quiz_agent() -> QuizAgent:
    """
    Create and cache the QuizAgent used to drive quiz generation.

    Returns:
        A cached QuizAgent instance shared across reruns.
    """

    return QuizAgent()


# ---------------------------------------------------------------------
# Quiz Generation
# ---------------------------------------------------------------------


def request_quiz(sport: str, difficulty: str, num_questions: int) -> str:
    """
    Call the QuizAgent to generate raw quiz text for the given settings.

    Args:
        sport: Selected sport.
        difficulty: Selected difficulty.
        num_questions: Number of questions.

    Returns:
        The generated quiz text.
    """

    agent = create_quiz_agent()

    return agent.generate_quiz(
        topic=sport,
        difficulty=difficulty.lower(),
        num_questions=num_questions,
    )


def generate_quiz(sport: str, difficulty: str, num_questions: int) -> bool:
    """
    Generate a quiz via QuizAgent and store the result in session state.

    Args:
        sport: Selected sport.
        difficulty: Selected difficulty.
        num_questions: Number of questions.

    Returns:
        True if generation succeeded and session state was updated,
        False if generation failed (an error is already shown via
        st.error() in that case).
    """

    try:
        with st.spinner("🤖 Generating your quiz — this can take a few seconds..."):
            quiz = request_quiz(sport, difficulty, num_questions)

        st.session_state[QUIZ_STATE_KEY] = {
            "sport": sport,
            "difficulty": difficulty,
            "num_questions": num_questions,
            "quiz": quiz,
        }

        st.toast("Quiz generated successfully! 🎉")
        return True

    except Exception as error:
        st.error(f"❌ Failed to generate quiz.\n\n{error}")
        return False


# ---------------------------------------------------------------------
# Quiz Parsing
# ---------------------------------------------------------------------


def _strip_stray_markdown(text: str) -> str:
    """
    Remove stray bold markers ("**") the LLM may still include despite
    prompt instructions, so rendered text always stays clean.

    Args:
        text: Raw text possibly containing stray "**" markers.

    Returns:
        The text with all "**" sequences removed and whitespace trimmed.
    """

    return re.sub(r"\*\*", "", text).strip()


def _parse_quiz_questions(quiz_text: str) -> list[dict]:
    """
    Parse raw Markdown quiz text into structured question records.

    Expects the "## Question N" / "A) ... D)" / "✅ Correct Answer:" /
    "📖 Explanation:" structure produced by the QuizAgent prompt, but
    degrades gracefully — any line it doesn't recognize is simply
    appended to whichever section is currently active.

    Args:
        quiz_text: The raw quiz text returned by QuizAgent.

    Returns:
        A list of dicts, one per question, each with "question",
        "options" (list[str]), "correct_answer", and "explanation".
        Returns an empty list if no question headings are found.
    """

    questions: list[dict] = []
    current: dict | None = None
    section: str | None = None

    for raw_line in quiz_text.splitlines():
        line = raw_line.strip()

        if re.match(r"^#{1,3}\s*Question\s*\d+\s*$", line, re.IGNORECASE):
            if current is not None:
                questions.append(current)
            current = {
                "question": "",
                "options": [],
                "correct_answer": "",
                "explanation": "",
            }
            section = "question"
            continue

        if current is None:
            continue

        if re.match(r"^[A-D]\)", line):
            current["options"].append(line)
            section = "options"
            continue

        answer_match = re.match(
            r"^(✅\s*)?correct answer:?\s*(.*)$", line, re.IGNORECASE
        )
        if answer_match:
            current["correct_answer"] = answer_match.group(2).strip()
            section = "answer"
            continue

        if re.match(r"^(📖\s*)?explanation:?\s*$", line, re.IGNORECASE):
            section = "explanation"
            continue

        if not line:
            continue

        if section == "question":
            current["question"] = f"{current['question']} {line}".strip()
        elif section == "answer":
            current["correct_answer"] = f"{current['correct_answer']} {line}".strip()
        elif section == "explanation":
            current["explanation"] = f"{current['explanation']} {line}".strip()

    if current is not None:
        questions.append(current)

    for question in questions:
        question["question"] = _strip_stray_markdown(question["question"])
        question["options"] = [_strip_stray_markdown(o) for o in question["options"]]
        question["correct_answer"] = _strip_stray_markdown(question["correct_answer"])
        question["explanation"] = _strip_stray_markdown(question["explanation"])

    return questions


# ---------------------------------------------------------------------
# Quiz Result
# ---------------------------------------------------------------------


def _render_quiz_metrics(quiz_state: dict) -> None:
    """
    Render the Sport / Difficulty / Number of Questions metric row,
    each inside its own bordered "card" (styled via inject_custom_css).

    Args:
        quiz_state: The current quiz's session-state dict.
    """

    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container(border=True):
            st.metric("🏅 Sport", quiz_state["sport"])

    with col2:
        with st.container(border=True):
            st.metric("🎯 Difficulty", quiz_state["difficulty"])

    with col3:
        with st.container(border=True):
            st.metric("❓ Questions", quiz_state["num_questions"])


def _escape_html(text: str) -> str:
    """
    Escape text before interpolating it into raw HTML.

    Quiz content originates from Gemini and is rendered via
    unsafe_allow_html=True, so any "<", ">", "&", or quote characters
    it might contain must be neutralized to keep the layout intact.

    Args:
        text: Raw text to escape.

    Returns:
        HTML-safe text.
    """

    return html.escape(text)


def _render_quiz_question_card(question: dict, number: int) -> None:
    """
    Render a single quiz question as a fully custom-styled card.

    Args:
        question: Parsed question dict with question/options/answer/
                  explanation fields.
        number: The 1-based question number to display in the badge.
    """

    options_html = "".join(
        f'<div class="sqai-quiz-option">{_escape_html(option)}</div>'
        for option in question["options"]
    )

    explanation_html = ""
    if question["explanation"]:
        explanation_html = f"""
            <div class="sqai-quiz-explanation">
                <span class="sqai-quiz-label">📖 Explanation</span>
                <p class="sqai-quiz-value">
                    {_escape_html(question["explanation"])}
                </p>
            </div>
        """

    _render_raw_html(
        f"""
        <div class="sqai-quiz-card">
            <span class="sqai-quiz-badge">Question {number}</span>
            <p class="sqai-quiz-question">
                {_escape_html(question["question"])}
            </p>
            <div class="sqai-quiz-options">
                {options_html}
            </div>
            <div class="sqai-quiz-answer">
                <span class="sqai-quiz-label">✅ Correct Answer</span>
                <p class="sqai-quiz-value">
                    {_escape_html(question["correct_answer"])}
                </p>
            </div>
            {explanation_html}
        </div>
        """
    )


def _render_empty_state() -> None:
    """Render an engaging placeholder card when no quiz exists yet."""

    emoji = random.choice(SPORT_EMOJIS)
    fact = random.choice(FUN_FACTS)

    _render_raw_html(
        f"""
        <div class="sqai-empty-state">
            <div class="sqai-empty-icon">{emoji}</div>
            <h3 class="sqai-empty-title">NO QUIZ YET!</h3>
            <p class="sqai-empty-description">
                Configure your settings in the sidebar and click
                <strong>Generate Quiz</strong> to get started.
            </p>
        </div>
        <div class="sqai-fun-fact">
            <div class="sqai-fun-fact-icon">{FUN_FACT_ICON}</div>
            <div class="sqai-fun-fact-body">
                <span class="sqai-fun-fact-label">Did you know?</span>
                <p class="sqai-fun-fact-text">{_escape_html(fact)}</p>
            </div>
        </div>
        """
    )


def render_quiz_result() -> None:
    """Render the most recently generated quiz, or an empty-state card."""

    quiz_state = st.session_state.get(QUIZ_STATE_KEY)

    if quiz_state is None:
        st.write("")
        _render_empty_state()
        return

    st.write("")
    st.subheader("📝 Your Quiz")

    _render_quiz_metrics(quiz_state)

    st.write("")

    questions = _parse_quiz_questions(quiz_state["quiz"])

    if questions:
        for index, question in enumerate(questions, start=1):
            _render_quiz_question_card(question, index)
    else:
        # Fallback for unexpected LLM output: show the raw quiz rather
        # than fail, still inside a bordered container for consistency.
        with st.container(border=True):
            st.markdown(quiz_state["quiz"])

    st.download_button(
        label="⬇️ Download Quiz",
        data=quiz_state["quiz"],
        file_name=(
            f"{quiz_state['sport'].lower()}_"
            f"{quiz_state['difficulty'].lower()}_quiz.txt"
        ),
        mime="text/plain",
        use_container_width=True,
    )


# ---------------------------------------------------------------------
# Quiz Controls
# ---------------------------------------------------------------------


def render_quiz_controls(sport: str, difficulty: str, num_questions: int) -> None:
    """
    Render the Generate and Regenerate buttons.

    Regenerate stays disabled until a quiz has been generated at least
    once. On a successful click, the page is immediately rerun so the
    Regenerate button (and the rest of the UI) reflects the new state
    right away rather than on the next unrelated interaction.

    Args:
        sport: Selected sport.
        difficulty: Selected difficulty.
        num_questions: Number of questions.
    """

    generate_col, regenerate_col = st.columns(2)

    with generate_col:
        generate_clicked = st.button(
            "🚀 Generate Quiz",
            type="primary",
            use_container_width=True,
        )

    with regenerate_col:
        regenerate_disabled = st.session_state[QUIZ_STATE_KEY] is None
        regenerate_clicked = st.button(
            "🔄 Regenerate",
            type="secondary",
            use_container_width=True,
            disabled=regenerate_disabled,
        )

    if generate_clicked or regenerate_clicked:
        if generate_quiz(sport, difficulty, num_questions):
            # Rerun immediately so the Regenerate button (and everything
            # else on the page) reflects the freshly updated session
            # state right away. st.toast() is designed to survive
            # exactly one rerun, so the success toast still appears.
            st.rerun()


# ---------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------


def render_footer() -> None:
    """Render the footer: About, tech stack, version, and project links."""

    st.divider()

    tech_stack_html = "".join(
        f"<p>{icon} {name}</p>" for icon, name in POWERED_BY
    )

    _render_raw_html(
        f"""
        <div class="sqai-footer">
            <div class="sqai-footer-grid">
                <div class="sqai-footer-col">
                    <h4>About This Project</h4>
                    <p>
                        An end-to-end Retrieval-Augmented Generation (RAG)
                        application that grounds AI-generated sports quizzes
                        in a real knowledge base and live search.
                    </p>
                </div>
                <div class="sqai-footer-col">
                    <h4>Technologies Used</h4>
                    {tech_stack_html}
                </div>
                <div class="sqai-footer-col">
                    <h4>Version</h4>
                    <p><span class="sqai-version-badge">{APP_VERSION}</span></p>
                </div>
                <div class="sqai-footer-col">
                    <h4>Project Links</h4>
                    <p><a href="{GITHUB_URL_PLACEHOLDER}" target="_blank">
                        GitHub Repository ↗
                    </a></p>
                    <p>Built by {DEVELOPER_NAME_PLACEHOLDER}</p>
                </div>
            </div>
        </div>
        """
    )


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------


def main() -> None:
    """Application entry point."""

    configure_page()
    inject_custom_css()
    initialize_session_state()

    render_hero_section()

    sport, difficulty, num_questions = render_sidebar()

    render_quiz_controls(sport, difficulty, num_questions)
    render_quiz_result()
    render_footer()


if __name__ == "__main__":
    main()