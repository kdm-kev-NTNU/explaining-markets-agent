"""MODEL_CARD.md keeps the em-model-card v1 skeleton at minimal disclosure.

Queue item 9 is a draft for the portal, which rejects a card that breaks
this shape. The test locks the marker, the six-row table, and the required
sections, and it rejects a showcase-only prompt section or an exact model id
in the minimal draft.
"""

from __future__ import annotations

import re
from pathlib import Path

CARD = Path(__file__).resolve().parents[2] / "MODEL_CARD.md"

REQUIRED_SECTIONS = (
    "## What is predicted",
    "## Input context",
    "## Model & harness",
    "## Data flow",
    "## Limitations",
)

CLASSIFICATION_ROWS = (
    "| Approach | LLM / GenAI |",
    "| Models | GPT-5.x |",
    "| Information set | competition facts; earnings / fundamentals; estimates; prices / returns; historical company information |",
    "| Learning / adaptation | zero-shot / prompted |",
    "| Agent architecture | single-pass |",
    "| Prediction construction | direct LLM score |",
)


def test_model_card_minimal_skeleton() -> None:
    text = CARD.read_text(encoding="utf-8")
    lines = text.splitlines()
    assert lines[0] == "<!-- em-model-card v1 disclosure=minimal -->"
    assert "## Representative prompt" not in text
    assert not any(line.startswith("# ") for line in lines)
    assert "```" not in text

    lowered = text.lower()
    assert "openai" not in lowered
    assert "astra" not in lowered
    assert "luna" not in lowered
    assert not re.search(r"gpt-\d+\.\d+", lowered)
    assert not re.search(r"gpt-\d+-[a-z]", lowered)
    assert "http://" not in lowered
    assert "https://" not in lowered

    positions = [text.index(section) for section in REQUIRED_SECTIONS]
    assert positions == sorted(positions)

    header_at = text.index("| Category | Classification |")
    row_at = [text.index(row) for row in CLASSIFICATION_ROWS]
    assert header_at < row_at[0]
    assert row_at == sorted(row_at)
    assert row_at[-1] < positions[0]
