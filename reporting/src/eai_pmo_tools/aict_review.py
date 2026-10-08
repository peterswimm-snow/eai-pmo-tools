"""Offline, evidence-only AICT review. Schema and examples live in the two skills."""

import argparse
from collections import Counter
from datetime import date
import json
from pathlib import Path
import re
from urllib.parse import urlparse


ROLES = {
    "business_sponsor": "VP+ business sponsor",
    "business_lead": "hands-on business lead",
    "da_lead": "direct report of the designated D&A leader",
    "da_owner": "hands-on D&A owner",
}
STATES = {"Candidate", "Needs confirmation", "Disputed", "Confirmed"}


def _object(value):
    return value if isinstance(value, dict) else {}


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _url(value):
    if not _text(value):
        return False
    try:
        parsed = urlparse(value)
    except ValueError:
        return False
    return parsed.scheme in {"https", "http"} and bool(parsed.netloc)


def _identity(value):
    person = _object(value)
    words = str(person.get("full_name", "")).split()
    return (
        len(words) >= 2
        and all(len(word.strip(".")) > 1 for word in words)
        and isinstance(person.get("email"), str)
        and re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", person["email"]) is not None
    )


def _date(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError("dates must be YYYY-MM-DD")
    return date.fromisoformat(value)


def _dated_gaps(value, review_date, max_age_days, label):
    try:
        evidence_date = _date(value)
    except ValueError:
        return [f"{label}: missing or invalid date"]
    if evidence_date > review_date:
        return [f"{label}: future evidence date"]
    if max_age_days is not None and (review_date - evidence_date).days > max_age_days:
        return [f"{label}: stale evidence"]
    return []


def _approval_gaps(value, review_date, max_age_days, label):
    approval = _object(value)
    gaps = []
    if not _identity(approval.get("person")):
        gaps.append(f"{label}: full confirming identity required")
    if not _url(approval.get("evidence_link")):
        gaps.append(f"{label}: evidence_link required")
    gaps.extend(_dated_gaps(approval.get("date"), review_date, max_age_days, label))
    return gaps


def _rows(payload):
    if not isinstance(payload, dict) or not isinstance(payload.get("models"), list):
        raise ValueError("input must be an object with a models list")
    review_date = _date(payload.get("review_date"))
    max_age_days = payload.get("max_age_days")
    if max_age_days is not None and (type(max_age_days) is not int or max_age_days < 0):
        raise ValueError("max_age_days must be a nonnegative integer")
    if any(not isinstance(model, dict) for model in payload["models"]):
        raise ValueError("each model row must be an object")
    ids = Counter(model.get("id") for model in payload["models"] if _text(model.get("id")))
    for index, model in enumerate(payload["models"], 1):
        gaps = []
        model_id = model.get("id")
        if not _text(model_id):
            gaps.append("missing model id")
        elif ids[model_id] > 1:
            gaps.append("duplicate model id")
        if not _text(model.get("name")):
            gaps.append("missing model name")
        yield f"row-{index:06d}", model, gaps, review_date, max_age_days


def review_stakeholders(payload):
    results = []
    for row_key, model, model_gaps, review_date, max_age_days in _rows(payload):
        supplied_roles = _object(model.get("roles"))
        unknown = sorted(set(supplied_roles) - set(ROLES))
        model_gaps.extend(f"unsupported role: {role}" for role in unknown)
        matrix = []
        outreach = []
        for role, requirement in ROLES.items():
            evidence = _object(supplied_roles.get(role))
            gaps = []
            if not _identity(evidence.get("person")):
                gaps.append("full identity required (full_name and email; no initials)")
            for field in ("title", "remit"):
                if not _text(evidence.get(field)):
                    gaps.append(f"{field} required")
                if not _url(evidence.get(f"{field}_evidence_link")):
                    gaps.append(f"{field} evidence required")
            if role == "business_sponsor":
                if evidence.get("vp_plus") is not True or not _url(evidence.get("rank_evidence_link")):
                    gaps.append("explicit VP+ rank and rank evidence required")
            if role == "da_lead":
                if (
                    evidence.get("reporting_role") != "designated_da_leader_direct_report"
                    or not _url(evidence.get("reporting_evidence_link"))
                ):
                    gaps.append("designated D&A leader direct-report evidence required")
            if role in {"business_lead", "da_owner"} and evidence.get("hands_on") is not True:
                gaps.append("explicit hands-on remit required")
            gaps.extend(_approval_gaps(evidence.get("confirmation"), review_date, max_age_days, "confirmation"))
            claimed = evidence.get("state", "Needs confirmation")
            if not isinstance(claimed, str) or claimed not in STATES:
                gaps.append("unsupported stakeholder state")
            if claimed != "Confirmed":
                gaps.append("explicit Confirmed decision required")
            state = claimed if claimed in ("Disputed", "Candidate") else "Needs confirmation"
            if claimed == "Confirmed" and not gaps:
                state = "Confirmed"
            matrix.append({"role": role, "requirement": requirement, "state": state,
                           "person": evidence.get("person"), "gaps": gaps,
                           "supplied_evidence": evidence})
            if state != "Confirmed":
                outreach.append({"role": role, "state": "Draft - not sent",
                                 "text": f"Please confirm {role} for {model.get('name') or row_key} "
                                         f"({model.get('id') or 'missing model ID'}): {requirement}. "
                                         "Provide full identity, title/remit and eligibility evidence, "
                                         "confirming person, date and evidence link. "
                                         f"Open gaps: {'; '.join(gaps)}."})
        findings = model_gaps + [f"{item['role']}: {gap}" for item in matrix for gap in item["gaps"]]
        results.append({"row_key": row_key, "id": model.get("id"), "name": model.get("name"),
                        "state": "Confirmed" if not findings else "Needs confirmation",
                        "findings": findings, "gap_matrix": matrix, "draft_outreach": outreach})
    return {"mode": "stakeholders", "offline": True, "live_validated": False,
            "review_date": payload["review_date"], "models": results}


def _linkage_gaps(model):
    gaps = []
    asset = _object(model.get("aict_asset"))
    ci = _object(model.get("surf_ci"))
    if not (
        _text(asset.get("id")) and asset.get("registry") == "AICT"
        and asset.get("authoritative") is True and asset.get("model_specific") is True
        and _url(asset.get("evidence_link"))
    ):
        gaps.append("authoritative model-specific AICT asset linkage required; MLMD is not AICT")
    if not (
        _text(ci.get("id")) and ci.get("component") is True
        and ci.get("model_specific") is True and _url(ci.get("evidence_link"))
    ):
        gaps.append("model-specific SURF CI component linkage required; generic platform CI is insufficient")
    return gaps


def _document_review(value, model, review_date, max_age_days):
    document = _object(value)
    gaps = []
    kind = document.get("kind")
    if kind not in ("kb", "sharepoint_product", "sharepoint_technical"):
        gaps.append("unsupported document kind")
    if not _url(document.get("url")):
        gaps.append("document URL missing or invalid")
    if kind == "kb":
        if not _text(document.get("kb_reference")):
            gaps.append("existing KB reference required")
        if _url(document.get("url")) and "sharepoint" in urlparse(document["url"]).netloc.lower():
            gaps.append("SharePoint supporting document is not a KB article")
    for field in ("scope", "version"):
        if not _text(document.get(field)):
            gaps.append(f"document {field} required")
    if not (
        document.get("model_specific") is True and _text(model.get("id"))
        and document.get("model_id") == model.get("id")
        and _url(document.get("scope_evidence_link"))
    ):
        gaps.append("model-specific scope evidence and matching model_id required")
    if not _identity(document.get("owner")) or not _url(document.get("owner_evidence_link")):
        gaps.append("document owner identity and evidence required")
    gaps.extend(_dated_gaps(document.get("reviewed_at"), review_date, max_age_days, "document review"))
    approval = _object(document.get("review_approval"))
    if approval.get("approved") is not True:
        gaps.append("explicit review approval required")
    gaps.extend(_approval_gaps(approval, review_date, max_age_days, "review approval"))
    publication = _object(document.get("publication"))
    if publication.get("state") != "Published" or not _url(publication.get("evidence_link")):
        gaps.append("explicit publication evidence required")
    gaps.extend(_dated_gaps(publication.get("date"), review_date, max_age_days, "publication"))
    access = _object(document.get("access"))
    if access.get("verified") is not True or not _url(access.get("evidence_link")):
        gaps.append("explicit access evidence required; URL presence is not access verification")
    gaps.extend(_dated_gaps(access.get("date"), review_date, max_age_days, "access"))
    return {"kind": kind, "url": document.get("url"), "kb_reference": document.get("kb_reference"),
            "state": "Ready from supplied evidence" if not gaps else "Needs review",
            "gaps": gaps, "supplied_evidence": document}


def review_documentation(payload):
    results = []
    for row_key, model, model_gaps, review_date, max_age_days in _rows(payload):
        findings = model_gaps + _linkage_gaps(model)
        supplied = model.get("documents", [])
        if not isinstance(supplied, list):
            supplied = []
            findings.append("documents must be a list")
        references = [_document_review(document, model, review_date, max_age_days) for document in supplied]
        for kind in ("kb", "sharepoint_product", "sharepoint_technical"):
            if not any(reference["kind"] == kind for reference in references):
                findings.append(f"missing {kind} reference")
        findings.extend(f"document {index}: {gap}" for index, reference in enumerate(references, 1)
                        for gap in reference["gaps"])
        results.append({"row_key": row_key, "id": model.get("id"), "name": model.get("name"),
                        "state": "Ready from supplied evidence" if not findings else "Needs review",
                        "findings": findings, "reuse_references": references,
                        "linkage_evidence": {"aict_asset": model.get("aict_asset"), "surf_ci": model.get("surf_ci")}})
    return {"mode": "documentation", "offline": True, "live_validated": False,
            "review_date": payload["review_date"], "models": results}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Offline AICT evidence review; no network or writes to ServiceNow")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("stakeholders", "documentation"):
        command = commands.add_parser(name)
        command.add_argument("--input", required=True, type=Path)
        command.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.input.resolve() == args.output.resolve():
            raise ValueError("source and output paths must differ")
        if args.output.exists() or args.output.is_symlink():
            raise ValueError("refusing existing output")
        with args.input.open(encoding="utf-8") as source:
            payload = json.load(source)
        review = review_stakeholders if args.command == "stakeholders" else review_documentation
        rendered = json.dumps(review(payload), indent=2, ensure_ascii=True) + "\n"
        with args.output.open("x", encoding="utf-8") as output:
            output.write(rendered)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())