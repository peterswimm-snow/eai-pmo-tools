import pytest

from eai_pmo_tools.data_sources import (
    QUERY_CATEGORIES,
    Status,
    pull_via_query,
)


def test_access_denied_raises_permission_error():
    with pytest.raises(PermissionError, match="access-denied"):
        pull_via_query("audit_findings")


def test_confirmed_categories_do_not_warn_or_raise(monkeypatch, recwarn):
    monkeypatch.setattr(
        "eai_pmo_tools.data_sources.devx.query_table",
        lambda table, encoded_query=None, limit=50: [],
    )
    for category, cat in QUERY_CATEGORIES.items():
        if cat.status is Status.CONFIRMED:
            pull_via_query(category)
    assert len(recwarn) == 0


def test_every_query_category_has_a_status():
    for name, cat in QUERY_CATEGORIES.items():
        assert isinstance(cat.status, Status), name


def test_every_confirmed_or_access_denied_category_has_a_table():
    for name, cat in QUERY_CATEGORIES.items():
        if cat.status in (Status.CONFIRMED, Status.ACCESS_DENIED, Status.UNVERIFIED_TABLE):
            assert cat.table, f"{name} should have a table name"


def test_aict_trace_collector_naming_trap_is_not_used():
    # sn_aict_trace_coll_* is an unrelated observability app that happens to
    # share the "aict" prefix with AI Control Tower — make sure nothing here
    # accidentally points at it.
    for cat in QUERY_CATEGORIES.values():
        if cat.table:
            assert not cat.table.startswith("sn_aict_trace_coll_")
