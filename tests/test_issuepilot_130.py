import json

from gulliver import features
from gulliver.cli import main


def test_empty_check_records_history_without_claiming_validation(settings):
    result = features.check(settings, "users")
    assert result["status"] == "ok"
    assert result.get("checks_requested") == 0
    assert "No checks were requested" in result["next_step"]
    assert "row count was recorded" in result["next_step"]
    assert "--unique" in result["next_step"]
    assert "All checks passed" not in result["next_step"]
    following = features.check(settings, "users", max_change_pct=0)
    row_count = next(check for check in following["checks"] if check["check"] == "row_count")
    assert row_count["previous_rows"] == row_count["rows"]


def test_cli_empty_check_explains_no_validation(demo_db, state, capsys):
    assert main(["--dsn", demo_db, "check", "users", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result.get("checks_requested") == 0
    assert "No checks were requested" in result["next_step"]


def test_requested_checks_keep_the_existing_result(settings):
    for options in ({"unique": ["user_id"]}, {"min_rows": 0}):
        result = features.check(settings, "users", **options)
        assert result["status"] == "ok"
        assert result["next_step"] == "All checks passed."
        assert "checks_requested" not in result
