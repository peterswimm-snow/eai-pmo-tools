from copy import deepcopy
import json
from pathlib import Path
import shlex
import socket
import subprocess

import pytest

from eai_pmo_tools.aict_change_plan import PlanError, build_plan, main


@pytest.fixture
def request_data():
    return {
        "instance_url": "https://surf.service-now.com",
        "table": "alm_ai_system_digital_asset",
        "asset_sys_id": "a" * 32,
        "governance_sys_id": "d" * 32,
        "freshness": {"expected": "2026-10-08 10:00:00", "observed": "2026-10-08 10:00:00"},
        "baseline": {"u_business_owner": "b" * 32},
        "current": {"u_business_owner": "b" * 32},
        "conflicts": [],
        "changes": [{
            "field": "u_business_owner", "old_sys_id": "b" * 32, "new_sys_id": "c" * 32,
            "proposal_role": "validated", "evidence": ["Approved source dated 2026-10-08"],
            "candidate_mapping": [{"employee_sys_id": "e" * 32, "evidence": ["Older disputed mapping"]}],
            "identity_validation": {
                "table": "u_employee", "employee_sys_id": "c" * 32, "match_count": 1,
                "evidence": ["Unique employee lookup with confirmed name and identifier"],
            },
        }],
    }


def test_valid_plan_preserves_evidence_without_mutating_request(request_data):
    original = deepcopy(request_data)
    plan = build_plan(request_data)
    assert request_data == original
    assert plan["readiness"] == "ready_for_human_review"
    assert plan["record_url"] == "https://surf.service-now.com/alm_ai_system_digital_asset.do?sys_id=" + "a" * 32
    assert plan["governance_sys_id"] == "d" * 32
    assert plan["changes"][0]["before"] == "b" * 32
    assert plan["changes"][0]["after"] == "c" * 32
    assert plan["changes"][0]["candidate_mapping"][0]["requires_identity_validation"] is True
    assert plan["owner_implies_vp_plus"] is False
    plan["freshness"]["expected"] = "modified"
    assert request_data == original


@pytest.mark.parametrize("instance", [
    "http://surf.service-now.com", "https://evil.service-now.com",
    "https://surf.service-now.com.evil.test", "https://user:secret@surf.service-now.com",
    "https://surf.service-now.com/", "https://surf.service-now.com/path",
    "https://surf.service-now.com?query=1", "https://surf.service-now.com#fragment",
    "https://surf.service-now.com:443", "https://SURF.service-now.com",
    "https://surf.service-now.com\n", None,
])
def test_rejects_untrusted_or_injected_instance(request_data, instance):
    request_data["instance_url"] = instance
    with pytest.raises(PlanError):
        build_plan(request_data)


@pytest.mark.parametrize("bad_id", [None, "", "a" * 31, "a" * 33, "g" * 32, "a" * 32 + "^OR", 123])
@pytest.mark.parametrize("location", ["asset", "governance", "old", "new", "baseline", "current", "candidate", "identity"])
def test_invalid_ids(request_data, bad_id, location):
    change = request_data["changes"][0]
    if location in ("asset", "governance"):
        request_data[location + "_sys_id"] = bad_id
        if location == "governance" and bad_id is None:
            assert build_plan(request_data)["governance_sys_id"] is None
            return
    elif location in ("old", "new"):
        change[location + "_sys_id"] = bad_id
    elif location in ("baseline", "current"):
        request_data[location]["u_business_owner"] = bad_id
    elif location == "candidate":
        change["candidate_mapping"][0]["employee_sys_id"] = bad_id
    else:
        change["identity_validation"]["employee_sys_id"] = bad_id
    with pytest.raises(PlanError):
        build_plan(request_data)


@pytest.mark.parametrize("mutation", [
    "wrong_table", "same_governance", "changed_baseline", "changed_marker", "missing_marker",
    "unknown_top", "unknown_snapshot", "unknown_change", "unknown_identity", "unknown_candidate",
    "missing_old", "missing_new", "wrong_old", "no_op", "wrong_owner_field", "duplicate_field",
    "missing_identity", "wrong_identity_table", "ambiguous_identity", "boolean_match_count",
    "wrong_identity_id", "unknown_role", "empty_evidence", "empty_changes", "bad_conflicts",
    "bad_candidates", "bad_field_type", "bad_snapshot_type", "empty_marker", "control_marker",
])
def test_rejects_unsafe_requests(request_data, mutation):
    change = request_data["changes"][0]
    if mutation == "wrong_table":
        request_data["table"] = "sn_aict_governance_asset"
    elif mutation == "same_governance":
        request_data["governance_sys_id"] = request_data["asset_sys_id"]
    elif mutation == "changed_baseline":
        request_data["current"]["u_business_owner"] = "f" * 32
    elif mutation == "changed_marker":
        request_data["freshness"]["observed"] = "new revision"
    elif mutation == "missing_marker":
        del request_data["freshness"]
    elif mutation == "unknown_top":
        request_data["credentials"] = "not allowed"
    elif mutation == "unknown_snapshot":
        request_data["baseline"]["managed_by"] = "b" * 32
    elif mutation == "unknown_change":
        change["raw_patch"] = {}
    elif mutation == "unknown_identity":
        change["identity_validation"]["title"] = "VP"
    elif mutation == "unknown_candidate":
        change["candidate_mapping"][0]["validated"] = True
    elif mutation in ("missing_old", "missing_new"):
        del change[mutation.removeprefix("missing_") + "_sys_id"]
    elif mutation == "wrong_old":
        change["old_sys_id"] = "f" * 32
    elif mutation == "no_op":
        change["new_sys_id"] = change["old_sys_id"]
    elif mutation == "wrong_owner_field":
        change["field"] = "assigned_to"
    elif mutation == "duplicate_field":
        request_data["changes"].append(deepcopy(change))
    elif mutation == "missing_identity":
        del change["identity_validation"]
    elif mutation == "wrong_identity_table":
        change["identity_validation"]["table"] = "sys_user"
    elif mutation == "ambiguous_identity":
        change["identity_validation"]["match_count"] = 2
    elif mutation == "boolean_match_count":
        change["identity_validation"]["match_count"] = True
    elif mutation == "wrong_identity_id":
        change["identity_validation"]["employee_sys_id"] = "f" * 32
    elif mutation == "unknown_role":
        change["proposal_role"] = "approved"
    elif mutation == "empty_evidence":
        change["evidence"] = []
    elif mutation == "empty_changes":
        request_data["changes"] = []
    elif mutation == "bad_conflicts":
        request_data["conflicts"] = "disputed"
    elif mutation == "bad_candidates":
        change["candidate_mapping"] = {}
    elif mutation == "bad_field_type":
        change["field"] = []
    elif mutation == "bad_snapshot_type":
        request_data["baseline"] = []
    elif mutation == "empty_marker":
        request_data["freshness"] = {"expected": "", "observed": ""}
    elif mutation == "control_marker":
        request_data["freshness"] = {"expected": "x\n", "observed": "x\n"}
    with pytest.raises(PlanError):
        build_plan(request_data)


def test_requested_proposals_and_conflicts_stay_blocked(request_data):
    change = request_data["changes"][0]
    change["proposal_role"] = "requested"
    del change["identity_validation"]
    assert build_plan(request_data)["readiness"] == "requires_identity_validation"
    request_data["conflicts"] = ["Two sources disagree about accountable owner"]
    plan = build_plan(request_data)
    assert plan["readiness"] == "blocked_by_conflicts"
    assert plan["conflicts"] == request_data["conflicts"]
    assert plan["changes"][0]["candidate_mapping"][0]["employee_sys_id"] == "e" * 32


def test_technical_owner_and_uppercase_ids(request_data):
    request_data["baseline"] = {"u_technical_owner": "B" * 32}
    request_data["current"] = {"u_technical_owner": "b" * 32}
    request_data["changes"][0]["field"] = "u_technical_owner"
    assert build_plan(request_data)["changes"][0]["before"] == "b" * 32


def test_no_network_subprocess_or_plan_file_writes(request_data, monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Offline planning must not execute IO side effects")

    monkeypatch.setattr(subprocess, "run", forbidden)
    monkeypatch.setattr(subprocess, "Popen", forbidden)
    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(Path, "open", forbidden)
    plan = build_plan(request_data)
    commands = plan["handoff"]["read_only_commands"]
    assert commands[0] == "devx-cli whoami"
    assert all(command.startswith("devx-cli query ") for command in commands[1:])
    assert all(shlex.split(command)[1] in ("whoami", "query") for command in commands)


def test_cli_json_output_and_source_unchanged(request_data, tmp_path, monkeypatch):
    source, output = tmp_path / "request.json", tmp_path / "plan.json"
    original = json.dumps(request_data)
    source.write_text(original)
    monkeypatch.setattr(socket, "socket", lambda *args, **kwargs: pytest.fail("No remote writes"))
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: pytest.fail("No commands"))
    assert main(["--request", str(source), "--output", str(output)]) == 0
    assert json.loads(output.read_text())["mode"] == "offline_human_save_only"
    assert source.read_text() == original


@pytest.mark.parametrize("case", ["existing", "same", "alias", "symlink", "dangling", "invalid", "duplicate", "missing"])
def test_cli_refuses_unsafe_output_or_input(request_data, tmp_path, case, capsys):
    source, output = tmp_path / "request.json", tmp_path / "plan.json"
    original = json.dumps(request_data)
    source.write_text(original)
    if case == "existing":
        output.write_text("keep existing output")
    elif case == "same":
        output = source
    elif case == "alias":
        output = tmp_path / "subdir" / ".." / "request.json"
    elif case in ("symlink", "dangling"):
        output.symlink_to(source if case == "symlink" else tmp_path / "absent.json")
    elif case == "invalid":
        source.write_text("{invalid")
    elif case == "duplicate":
        source.write_text('{"table": "one", "table": "two"}')
    elif case == "missing":
        source.unlink()
    assert main(["--request", str(source), "--output", str(output)]) == 2
    assert "error" in json.loads(capsys.readouterr().err)
    if case == "existing":
        assert output.read_text() == "keep existing output"
    elif case not in ("same", "alias", "symlink", "dangling"):
        assert not output.exists()
    if case not in ("invalid", "duplicate", "missing"):
        assert source.read_text() == original


def test_cli_requires_both_explicit_paths():
    with pytest.raises(SystemExit) as exc:
        main([])
    assert exc.value.code == 2


@pytest.mark.parametrize("name", ["aict-browser-update-handoff", "aict-inventory-change-plan"])
def test_skill_structure_and_existing_helper_link(name):
    root = Path(__file__).resolve().parents[1]
    skill = root / ".claude" / "skills" / name / "SKILL.md"
    content = skill.read_text()
    frontmatter = content.split("---", 2)[1]
    assert f"name: {name}\n" in frontmatter
    description = frontmatter.split("description: ", 1)[1].strip()
    assert description.startswith('"') and description.endswith('"')
    assert len(json.loads(description)) < 1024
    assert len(content.splitlines()) < 500
    for heading in ("Role", "Audience", "Procedure", "Safety", "Output", "Example", "Validation"):
        assert f"## {heading}\n" in content
    assert content.count("- [ ]") >= 10
    helper_link = "../../../reporting/src/eai_pmo_tools/aict_change_plan.py"
    assert f"]({helper_link})" in content
    assert (skill.parent / helper_link).resolve().is_file()
    assert "not executed model evaluations" in content