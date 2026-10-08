import pytest

from eai_pmo_tools import devx


@pytest.mark.parametrize(
    "text, expected",
    [
        ('[{"model_name": "SPM Cross Sell"}]', [{"model_name": "SPM Cross Sell"}]),
        ('Returned 1 record(s)\n[{"sys_id": "abc"}]\nUpdate available', [{"sys_id": "abc"}]),
        ('\x1b[32mReturned 0 record(s)\x1b[0m\nUpdate available', []),
        ('Returned 0 record(s)\n[]', []),
        ('{"result": []}', {"result": []}),
    ],
)
def test_parse_output(text, expected):
    assert devx.parse_output(text) == expected


@pytest.mark.parametrize(
    "text",
    [
        "User Not Authorized",
        "Invalid table fake",
        "Not authenticated",
        'Returned 2 record(s)\n[{"sys_id": "abc"}]',
        'Returned 1 record(s)\n[{"model_name": "SPM\nCross Sell"}]',
        "Returned 0 record(s)\nUser Not Authorized",
    ],
)
def test_errors_are_not_empty_records(text):
    with pytest.raises(devx.DevxCliError):
        devx.parse_output(text)


def test_query_flags_are_optional(monkeypatch):
    calls = []
    monkeypatch.setattr(devx, "run", lambda arguments: calls.append(arguments) or [])
    devx.query_table("task", "active=true", 3, fields="sys_id", offset=3, display_value="Both")
    assert calls == [["query", "--table", "task", "--query", "active=true", "--limit", "3", "--fields", "sys_id", "--offset", "3", "--display-value", "Both"]]