"""Tests for the PR description summary block composition (append/replace)."""

from __future__ import annotations

from mira.core.engine import compose_pr_description
from mira.models import PR_SUMMARY_END, PR_SUMMARY_START


def _block(content: str = "## Summary by Mira\n\n- bullet") -> str:
    return f"{PR_SUMMARY_START}\n{content}\n{PR_SUMMARY_END}"


class TestComposePrDescription:
    def test_append_empty_body(self) -> None:
        block = _block()
        assert compose_pr_description("", block, "append") == block

    def test_append_empty_whitespace_body(self) -> None:
        block = _block()
        assert compose_pr_description("   \n  ", block, "append") == block

    def test_append_preserves_author_text(self) -> None:
        block = _block()
        author = "My PR description text."
        out = compose_pr_description(author, block, "append")
        assert out.startswith(author)
        assert block in out
        assert out.index(author) < out.index(PR_SUMMARY_START)
        assert "\n\n" in out

    def test_append_idempotent_replaces_existing_block(self) -> None:
        old = _block("old bullets")
        new = _block("new bullets")
        author = "Author text."
        current = f"{author}\n\n{old}"
        out = compose_pr_description(current, new, "append")
        assert "old bullets" not in out
        assert out.count(PR_SUMMARY_START) == 1
        assert out.count(PR_SUMMARY_END) == 1
        assert out.startswith(author)
        assert "new bullets" in out

    def test_append_replaces_block_and_keeps_trailing_author_text(self) -> None:
        old = _block("old bullets")
        new = _block("new bullets")
        trailing = "Trailing author note."
        current = f"Author intro.\n\n{old}\n\n{trailing}"
        out = compose_pr_description(current, new, "append")
        assert "old bullets" not in out
        assert out.count(PR_SUMMARY_START) == 1
        assert "Author intro." in out
        assert out.endswith(trailing)

    def test_append_malformed_lone_start_marker_appends(self) -> None:
        # A lone start marker without an end marker is a malformed edge case;
        # treat as no existing block and append after it.
        new = _block("new bullets")
        current = f"Author text.\n{PR_SUMMARY_START}"
        out = compose_pr_description(current, new, "append")
        assert new in out
        assert out.startswith("Author text.")

    def test_replace_ignores_author_text(self) -> None:
        block = _block()
        author = "My PR description text."
        assert compose_pr_description(author, block, "replace") == block

    def test_replace_with_existing_block_returns_only_block(self) -> None:
        old = _block("old bullets")
        new = _block("new bullets")
        current = f"Author text.\n\n{old}"
        assert compose_pr_description(current, new, "replace") == new
