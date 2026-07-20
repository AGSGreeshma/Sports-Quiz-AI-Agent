"""
Data loader for Sports Quiz AI.

Reads all `.txt` files from the `data/` folder and stores their contents
as documents in the ChromaDB "sports_knowledge" collection via
ChromaManager, so they can later be retrieved for RAG-based quiz
generation.
"""

from pathlib import Path
from typing import List

from src.database.chroma_manager import ChromaManager
from src.utils.text_chunker import chunk_text

# Folder containing the raw sports knowledge text files.
DATA_DIR: Path = Path("data")


def load_text_files(data_dir: Path) -> List[Path]:
    """
    Find all `.txt` files within a directory.

    Args:
        data_dir: Path to the directory to search.

    Returns:
        A list of paths to `.txt` files found in `data_dir`.

    Raises:
        FileNotFoundError: If `data_dir` does not exist.
    """
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    return sorted(data_dir.glob("*.txt"))


def load_file_chunks(file_path: Path) -> List[str]:
    """
    Read a text file and split its contents into overlapping chunks.

    Args:
        file_path: Path to the `.txt` file to read.

    Returns:
        A list of text chunks produced from the file's contents. Returns
        an empty list if the file is empty or contains only whitespace.
    """
    content = file_path.read_text(encoding="utf-8").strip()

    if not content:
        return []

    return chunk_text(content)


def load_documents_into_chroma(
    manager: ChromaManager, file_paths: List[Path]
) -> None:
    """
    Read each text file, split it into chunks, and store each chunk as a
    separate document in ChromaDB.

    Each chunk is assigned a unique ID derived from the source file's
    stem and its chunk index, e.g. "cricket_0", "cricket_1", "cricket_2".
    Each chunk is stored with metadata containing the sport (file stem),
    the source filename, and the chunk index within that file.

    Args:
        manager: An initialized ChromaManager instance.
        file_paths: List of paths to `.txt` files to load.
    """
    if not file_paths:
        print(f"No .txt files found in '{DATA_DIR}'.")
        return

    for file_path in file_paths:
        chunks = load_file_chunks(file_path)

        if not chunks:
            print(f"Skipped empty file: {file_path.name}")
            continue

        chunk_ids = [f"{file_path.stem}_{index}" for index in range(len(chunks))]
        metadatas = [
            {
                "sport": file_path.stem,
                "source": file_path.name,
                "chunk": index,
            }
            for index in range(len(chunks))
        ]

        manager.add_documents(
            documents=chunks,
            metadatas=metadatas,
            ids=chunk_ids,
        )
        print(f"Loaded {len(chunks)} chunk(s) from: {file_path.name}")


def main() -> None:
    print(">>> main() started")

    manager = ChromaManager()
    manager.initialize()
    manager.reset_collection()

    file_paths = load_text_files(DATA_DIR)
    load_documents_into_chroma(manager, file_paths)

    print(f"Finished loading {len(file_paths)} file(s) into ChromaDB.")
if __name__ == "__main__":
    main()