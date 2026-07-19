"""
Manual retrieval test for Sports Quiz AI.

Prompts the user for a search query, runs it against the ChromaDB
"sports_knowledge" collection via ChromaManager, and prints the top
matching documents so retrieval quality can be checked by hand.
"""

from typing import List

from src.database.chroma_manager import ChromaManager

# Number of top matching documents to retrieve per query.
TOP_K_RESULTS: int = 3


def print_results(documents: List[str]) -> None:
    """
    Print retrieved documents in a readable, numbered format.

    Args:
        documents: List of document texts returned by the search.
                   May be empty if no matches were found.
    """
    if not documents:
        print("No relevant documents were found for that query.")
        return

    print(f"\nTop {len(documents)} relevant document(s):\n")
    for rank, document in enumerate(documents, start=1):
        print(f"{rank}. {document}\n")


def main() -> None:
    """Prompt for a query and display the top matching documents."""
    manager = ChromaManager()
    manager.initialize()

    query_text = input("Enter a search query: ").strip()

    if not query_text:
        print("No query entered. Please provide a search query and try again.")
        return

    documents = manager.retrieve_documents(query_text=query_text, n_results=TOP_K_RESULTS)
    print_results(documents)


if __name__ == "__main__":
    main()