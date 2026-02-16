from pathlib import Path

import pytest

from tests.conftest import parse_frontmatter, parse_models_conf


def test_parse_frontmatter_reads_yaml_block(tmp_path: Path) -> None:
    content = """---
name: example
count: 2
---

Body text here.
"""
    path = tmp_path / "sample.md"
    path.write_text(content, encoding="utf-8")

    result = parse_frontmatter(path)

    assert result == {"name": "example", "count": 2}


def test_parse_frontmatter_requires_delimiters(tmp_path: Path) -> None:
    path = tmp_path / "missing.md"
    path.write_text("no frontmatter", encoding="utf-8")

    with pytest.raises(ValueError, match="No valid frontmatter"):
        parse_frontmatter(path)


def test_parse_models_conf_parses_key_values(tmp_path: Path) -> None:
    content = """
# comment
HIGH_EFFORT=github-copilot/claude-opus-4.6

LOW_EFFORT = github-copilot/haiku
"""
    path = tmp_path / "models.conf"
    path.write_text(content, encoding="utf-8")

    result = parse_models_conf(path)

    assert result == {
        "HIGH_EFFORT": "github-copilot/claude-opus-4.6",
        "LOW_EFFORT": "github-copilot/haiku",
    }
