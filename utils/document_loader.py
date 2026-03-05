"""Document loader — supports .txt, .md files."""
from pathlib import Path

def load_document(path: Path) -> str:
    """Load a text document from disk."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
