"""
Web search module for Sports Quiz AI.

Provides a thin, well-typed wrapper around the `duckduckgo-search`
package for retrieving live sports information from the web. Designed
to be used as a modular component by a future QuizAgent.
"""

import logging
from typing import Any, Dict, List

from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)


class WebSearch:
    """
    Performs live web searches using DuckDuckGo and returns clean text
    snippets suitable for feeding into a RAG or quiz generation pipeline.
    """

    def search(self, query: str, max_results: int = 5) -> List[str]:
        """
        Search the web for a given query and return text snippets.

        Args:
            query: The search query string.
            max_results: Maximum number of results to retrieve.

        Returns:
            A list of clean text snippets from the search results.
            Returns an empty list if the query is empty, no results
            are found, or an error occurs during the search.
        """
        if not query or not query.strip():
            return []

        try:
            with DDGS() as ddgs:
                raw_results: List[Dict[str, Any]] = list(
                    ddgs.text(query.strip(), max_results=max_results)
                )
        except Exception:
            logger.exception("Web search failed for query: %s", query)
            return []

        return self._extract_snippets(raw_results)

    @staticmethod
    def _extract_snippets(raw_results: List[Dict[str, Any]]) -> List[str]:
        """
        Extract and clean text snippets from raw DuckDuckGo result dicts.

        Args:
            raw_results: Raw result dictionaries returned by DDGS.text().

        Returns:
            A list of non-empty, whitespace-normalized text snippets.
        """
        snippets: List[str] = []

        for result in raw_results:
            snippet = str(result.get("body", "")).strip()
            if snippet:
                snippets.append(" ".join(snippet.split()))

        return snippets