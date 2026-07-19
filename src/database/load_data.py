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


def load_documents_into_chroma(
    manager: ChromaManager, file_paths: List[Path]
) -> None:
    """
    Read each text file and store its contents as a document in ChromaDB.

    Args:
        manager: An initialized ChromaManager instance.
        file_paths: List of paths to `.txt` files to load.
    """
    if not file_paths:
        print(f"No .txt files found in '{DATA_DIR}'.")
        return

    for file_path in file_paths:
        content = file_path.read_text(encoding="utf-8").strip()

        if not content:
            print(f"Skipped empty file: {file_path.name}")
            continue

        manager.add_documents(
            documents=[content],
            metadatas=[{"source": file_path.name}],
            ids=[file_path.stem],
        )
        print(f"Loaded document: {file_path.name}")


def main() -> None:
    """Load all sports knowledge text files from data/ into ChromaDB."""
    manager = ChromaManager()
    manager.initialize()

    file_paths = load_text_files(DATA_DIR)
    load_documents_into_chroma(manager, file_paths)

    print(f"Finished loading {len(file_paths)} document(s) into ChromaDB.")


if __name__ == "__main__":
    main()