"""Strip Nemotron Parse's layout tags, keeping the text and LaTeX tables the LLM needs."""

import re
import sys
from pathlib import Path

# <x_0.3574>, <y_0.0359> are box corners; <class_Title>, <class_Page-header> are block types.
TAG = re.compile(r"<x_[\d.]+>|<y_[\d.]+>|<class_[\w-]+>")


def clean(content: str) -> str:
    """Drop picture blocks (logos, stamps carry no text we need), then remove every layout tag."""
    blocks = [block for block in content.split("\n\n") if "<class_Picture>" not in block]
    return TAG.sub("", "\n\n".join(blocks)).strip()


if __name__ == "__main__":
    raw = Path(sys.argv[1]).read_text()
    cleaned = clean(raw)
    print(f"--- before: {len(raw)} characters, {len(TAG.findall(raw))} tags ---")
    print(raw)
    print(f"\n--- after: {len(cleaned)} characters, {len(TAG.findall(cleaned))} tags ---")
    print(cleaned)
