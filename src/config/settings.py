"""
Application settings for Sports Quiz AI.

Loads configuration values from environment variables (via a local .env
file if present) and exposes them as module-level constants for use
throughout the application.
"""

import os

from dotenv import load_dotenv

# Load variables from a .env file into the process environment, if one
# exists. This is a no-op (and safe) if no .env file is found.
load_dotenv()

# --- Google Gemini configuration -------------------------------------------

# API key used to authenticate requests to the Gemini API.
# No sensible default exists for a secret, so this defaults to an empty
# string and should be validated before use.
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

# Name of the Gemini model used for quiz generation.
MODEL_NAME: str = os.getenv(
    "MODEL_NAME",
    "gemini-3.5-flash",
)

# --- ChromaDB configuration ------------------------------------------------

# Local filesystem path where ChromaDB persists its data.
CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", "./chroma_db")

# --- Embedding configuration -------------------------------------------------

# Name of the sentence-transformers embedding model.
EMBEDDING_MODEL: str = os.getenv(
    "EMBEDDING_MODEL",
    "all-MiniLM-L6-v2"
)