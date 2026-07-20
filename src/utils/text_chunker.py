"""
Text chunking utility for Sports Quiz AI.

Splits long text into smaller, overlapping chunks so it can be embedded
and stored effectively in a vector database for RAG retrieval.
"""


def chunk_text(text: str, chunk_size: int = 150, overlap: int = 30) -> list[str]:
    """
    Split text into overlapping chunks of whole words.

    Chunking is word-based rather than character-based, so chunk
    boundaries never split a word in half. Overlap between consecutive
    chunks helps preserve context that would otherwise be lost at
    chunk boundaries, which improves retrieval quality in RAG pipelines.

    Args:
        text: The input text to split into chunks.
        chunk_size: Maximum number of words per chunk. Must be positive.
        overlap: Number of words repeated at the start of each chunk
                 from the end of the previous chunk. Must be
                 non-negative and smaller than chunk_size.

    Returns:
        A list of text chunks. Returns an empty list if the input text
        is empty or contains only whitespace.

    Raises:
        ValueError: If chunk_size is not positive, if overlap is
                    negative, or if overlap is greater than or equal
                    to chunk_size.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer.")

    if overlap < 0:
        raise ValueError("overlap must be a non-negative integer.")

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size.")

    words = text.split()
    if not words:
        return []

    chunks: list[str] = []
    step = chunk_size - overlap

    for start in range(0, len(words), step):
        chunk_words = words[start:start + chunk_size]
        chunks.append(" ".join(chunk_words))

        # Stop once this chunk reaches the end of the text, avoiding a
        # redundant trailing chunk that overlap-only text would create.
        if start + chunk_size >= len(words):
            break

    return chunks