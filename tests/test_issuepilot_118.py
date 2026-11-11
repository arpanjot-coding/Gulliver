import json

import pytest

from gulliver import fixer
from gulliver.cli import main


@pytest.mark.parametrize("limit", [-5, 0])
def test_invalid_limit_is_refused_before_rewriting(monkeypatch, limit):
    def forbidden_rewrite(*args, **kwargs):
        pytest.fail("an invalid limit must be rejected before rewriting")

    monkeypatch.setattr(fixer, "rewrite", forbidden_rewrite)
    result = fixer.fix(None, "SELECT * FROM events", mode="all", limit=limit)
    assert result["status"] == "error"
    assert str(limit) in result["error"]
    assert "limit" in result["error"]
    assert result["next_step"]


@pytest.mark.parametrize("limit", [-5, 0])
def test_cli_invalid_limit_returns_a_clean_error(state, capsys, limit):
    assert main(["fix", "--mode", "all", "--dialect", "duckdb", "--limit", str(limit),
                 "--json", "SELECT * FROM events"]) == 1
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "error"
    assert str(limit) in result["error"] and "limit" in result["error"]
    assert result["next_step"]


def test_valid_or_omitted_limits_and_safe_mode_keep_their_behavior():
    sql = "SELECT * FROM events"
    assert "LIMIT 1" in fixer.fix(None, sql, mode="all", limit=1)["fixed_sql"]
    assert "LIMIT 1000" in fixer.fix(None, sql, mode="all")["fixed_sql"]
    safe = fixer.fix(None, sql, mode="safe")
    assert fixer.fix(None, sql, mode="safe", limit=0) == safe
    assert fixer.fix(None, sql, mode="safe", limit=-5) == safe
