from eai_pmo_tools.generators.governance_portfolio import ACCESS_PENDING, assemble


def test_flags_missing_ownership_and_mismatched_inventory():
    cached = {
        "model_inventory": [
            {"sys_id": "a1", "managed_by": "", "install_status": "Deployed"},
            {"sys_id": "a2", "managed_by": "Jane Doe", "install_status": "Deployed"},
        ],
        "ai_control_tower": [
            {"asset": "a1", "governed": True, "risk_score": "3", "asset_state": "retired"},
            {"asset": "a2", "governed": False, "risk_score": "", "asset_state": "active"},
        ],
    }
    result = assemble(cached)

    assert [a["sys_id"] for a in result["missing_ownership"]] == ["a1"]
    assert [a["sys_id"] for a in result["mismatched_inventory"]] == ["a1"]
    assert len(result["control_exceptions"]) == 1  # a2: not governed, no risk_score
    assert result["audit_findings"] == ACCESS_PENDING


def test_handles_empty_cache():
    result = assemble({})
    assert result["governance_summary"]["total_assets"] == 0
    assert result["new_models"] == []
