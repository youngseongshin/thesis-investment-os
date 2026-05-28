from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from thesis_os.adapters.sample import SampleQualitativeProvider, SampleQuantProvider
from thesis_os.alpha.collectors import load_evidence_csv
from thesis_os.alpha.discovery import run_daily_discovery
from thesis_os.alpha.evidence_builder import event_to_evidence, ingest_csv_to_workspace, ingest_evidence_to_workspace
from thesis_os.alpha.intraday_monitor import run_intraday_monitor
from thesis_os.alpha.local_db import connect, init_db, insert_evidence, list_evidence, list_screener_candidates
from thesis_os.alpha.market_db import run_market_db_refresh
from thesis_os.alpha.quant_screener import run_quant_screener
from thesis_os.alpha.screener import run_sample_screener
from thesis_os.alpha.trade_proxy import run_trade_proxy
from thesis_os.arki.dashboard import build_dashboard
from thesis_os.arki.harness_contracts import validate_harness_contracts
from thesis_os.arki.health_check import check_demo_outputs, check_workspace
from thesis_os.arki.job_manifest import write_default_job_manifest
from thesis_os.arki.schema_lint import lint_schemas
from thesis_os.arki.vault_writer import VaultWriter
from thesis_os.arki.wiki_index import build_wiki_index
from thesis_os.lattice.action_queue import write_action_queue
from thesis_os.lattice.decision_card import decision_card_markdown
from thesis_os.lattice.feedback_interpreter import feedback_report_markdown
from thesis_os.lattice.judgment_feedback import evaluate_judgment
from thesis_os.lattice.prediction_ledger import append_prediction, read_predictions
from thesis_os.lattice.roundtable import run_sample_roundtable
from thesis_os.lattice.screener_feedback import evaluate_screener_candidate
from thesis_os.lattice.thesis_registry import build_sample_thesis, thesis_markdown
from thesis_os.models import Action, Prediction, utc_now
from thesis_os.runtime.workspace import init_workspace, load_workspace_evidence


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="thesis-os")
    sub = parser.add_subparsers(dest="command", required=True)

    demo_parser = sub.add_parser("demo", help="Generate a runnable sample Thesis OS loop.")
    demo_parser.add_argument("--out", default="./demo_run", help="Output directory.")

    init_parser = sub.add_parser("init", help="Initialize a local Thesis OS workspace.")
    init_parser.add_argument("--out", default="./thesis_os_workspace", help="Output directory.")

    lint_parser = sub.add_parser("lint", help="Lint public schemas.")
    lint_parser.add_argument("--root", default=".", help="Repository root.")

    alpha_parser = sub.add_parser("alpha", help="Alpha evidence collection commands.")
    alpha_sub = alpha_parser.add_subparsers(dest="alpha_command", required=True)
    alpha_ingest = alpha_sub.add_parser("ingest-csv", help="Ingest evidence CSV into a workspace.")
    alpha_ingest.add_argument("--csv", required=True, help="Evidence CSV path.")
    alpha_ingest.add_argument("--workspace", default="./thesis_os_workspace", help="Workspace directory.")
    alpha_sample = alpha_sub.add_parser("sample-collect", help="Run public sample quant and qualitative providers.")
    alpha_sample.add_argument("--workspace", default="./thesis_os_workspace", help="Workspace directory.")
    alpha_list = alpha_sub.add_parser("list-evidence", help="List workspace evidence records.")
    alpha_list.add_argument("--workspace", default="./thesis_os_workspace", help="Workspace directory.")
    alpha_screen = alpha_sub.add_parser("run-screener", help="Run the public sample screener and write candidates.")
    alpha_screen.add_argument("--workspace", default="./thesis_os_workspace", help="Workspace directory.")
    alpha_quant = alpha_sub.add_parser("run-quant-screener", help="Run an executable CSV-backed Alpha-style quantitative screener.")
    alpha_quant.add_argument("--workspace", default="./thesis_os_workspace", help="Workspace directory.")
    alpha_quant.add_argument("--input-csv", required=True, help="Quant screener feature CSV.")
    alpha_quant.add_argument("--top-n", type=int, default=20)
    alpha_discovery = alpha_sub.add_parser("discover", help="Run daily multi-channel discovery and compress to a Top 5 portfolio-review queue.")
    alpha_discovery.add_argument("--workspace", default="./thesis_os_workspace", help="Workspace directory.")
    alpha_discovery.add_argument("--top-n", type=int, default=5)
    alpha_market = alpha_sub.add_parser("refresh-market-db", help="Refresh local KR/US listed-equity DB snapshots from a CSV adapter.")
    alpha_market.add_argument("--workspace", default="./thesis_os_workspace", help="Workspace directory.")
    alpha_market.add_argument("--input-csv", required=True, help="Market snapshot CSV.")
    alpha_alerts = alpha_sub.add_parser("intraday-monitor", help="Monitor holdings/watchlist intraday price and flow events from a CSV adapter.")
    alpha_alerts.add_argument("--workspace", default="./thesis_os_workspace", help="Workspace directory.")
    alpha_alerts.add_argument("--input-csv", required=True, help="Intraday event CSV.")
    alpha_trade = alpha_sub.add_parser("trade-proxy", help="Build customs/export-import style trade proxy evidence from a CSV adapter.")
    alpha_trade.add_argument("--workspace", default="./thesis_os_workspace", help="Workspace directory.")
    alpha_trade.add_argument("--input-csv", required=True, help="Trade proxy CSV.")
    alpha_trade.add_argument("--proxy-name", default="trade_proxy", help="Proxy name, e.g. semiconductor-memory.")
    alpha_list_screen = alpha_sub.add_parser("list-screeners", help="List workspace screener candidates.")
    alpha_list_screen.add_argument("--workspace", default="./thesis_os_workspace", help="Workspace directory.")

    lattice_parser = sub.add_parser("lattice", help="Lattice judgment commands. Korean: 격자.")
    lattice_sub = lattice_parser.add_subparsers(dest="lattice_command", required=True)
    lattice_thesis = lattice_sub.add_parser("build-thesis", help="Build a sample thesis from workspace evidence.")
    lattice_thesis.add_argument("--workspace", default="./thesis_os_workspace", help="Workspace directory.")
    lattice_thesis.add_argument("--entity", default="", help="Optional entity filter.")
    lattice_decision = lattice_sub.add_parser("decision-card", help="Create a decision card from workspace evidence.")
    lattice_decision.add_argument("--workspace", default="./thesis_os_workspace", help="Workspace directory.")
    lattice_decision.add_argument("--action", default="watch", help="Action enum value.")
    lattice_decision.add_argument("--reason", default="Evidence supports monitoring, but market reflection and base-rate checks remain required.")
    lattice_predict = lattice_sub.add_parser("predict", help="Append a prediction to the workspace ledger.")
    lattice_predict.add_argument("--workspace", default="./thesis_os_workspace", help="Workspace directory.")
    lattice_predict.add_argument("--prediction", required=True, help="Prediction statement.")
    lattice_predict.add_argument("--direction", default="relative_outperform")
    lattice_predict.add_argument("--horizon", default="1m")
    lattice_predict.add_argument("--confidence", type=float, default=0.55)
    lattice_predict.add_argument("--evaluation-due", default="manual")
    lattice_eval = lattice_sub.add_parser("evaluate", help="Evaluate a prediction with measured returns.")
    lattice_eval.add_argument("--workspace", default="./thesis_os_workspace", help="Workspace directory.")
    lattice_eval.add_argument("--prediction-id", required=True)
    lattice_eval.add_argument("--absolute-return", required=True, type=float, help="Example: 0.04 for 4%.")
    lattice_eval.add_argument("--benchmark-return", default=0.0, type=float)
    lattice_screen_eval = lattice_sub.add_parser("evaluate-screener", help="Evaluate a screener candidate with measured forward returns.")
    lattice_screen_eval.add_argument("--workspace", default="./thesis_os_workspace", help="Workspace directory.")
    lattice_screen_eval.add_argument("--candidate-id", required=True)
    lattice_screen_eval.add_argument("--horizon", default="1m")
    lattice_screen_eval.add_argument("--absolute-return", required=True, type=float, help="Example: 0.04 for 4%.")
    lattice_screen_eval.add_argument("--benchmark-return", default=0.0, type=float)
    lattice_judgment_eval = lattice_sub.add_parser("evaluate-judgment", help="Evaluate a Lattice decision/action over a fixed horizon.")
    lattice_judgment_eval.add_argument("--workspace", default="./thesis_os_workspace", help="Workspace directory.")
    lattice_judgment_eval.add_argument("--action-id", required=True)
    lattice_judgment_eval.add_argument("--horizon", default="1m")
    lattice_judgment_eval.add_argument("--absolute-return", required=True, type=float, help="Example: 0.04 for 4%.")
    lattice_judgment_eval.add_argument("--benchmark-return", default=0.0, type=float)
    lattice_roundtable = lattice_sub.add_parser("roundtable", help="Run a sample holdings/watchlist judgment roundtable.")
    lattice_roundtable.add_argument("--workspace", default="./thesis_os_workspace", help="Workspace directory.")

    arki_parser = sub.add_parser("arki", help="Arki system governance commands.")
    arki_sub = arki_parser.add_subparsers(dest="arki_command", required=True)
    arki_init = arki_sub.add_parser("init", help="Initialize a Thesis OS workspace.")
    arki_init.add_argument("--workspace", default="./thesis_os_workspace", help="Workspace directory.")
    arki_health = arki_sub.add_parser("health", help="Check workspace health.")
    arki_health.add_argument("--workspace", default="./thesis_os_workspace", help="Workspace directory.")
    arki_wiki = arki_sub.add_parser("build-wiki-index", help="Build vault wiki index and SSOT notes.")
    arki_wiki.add_argument("--workspace", default="./thesis_os_workspace", help="Workspace directory.")
    arki_harness = arki_sub.add_parser("validate-harness", help="Validate a public harness contract JSON manifest.")
    arki_harness.add_argument("--workspace", default="./thesis_os_workspace", help="Workspace directory.")
    arki_harness.add_argument("--input-json", required=True, help="Harness contract JSON manifest.")
    arki_dashboard = arki_sub.add_parser("build-dashboard", help="Build a static HTML Thesis OS cockpit from workspace state.")
    arki_dashboard.add_argument("--workspace", default="./thesis_os_workspace", help="Workspace directory.")

    args = parser.parse_args(argv)
    if args.command == "demo":
        return run_demo(Path(args.out))
    if args.command == "init":
        return run_init(Path(args.out))
    if args.command == "lint":
        return run_lint(Path(args.root))
    if args.command == "alpha":
        return run_alpha(args)
    if args.command == "lattice":
        return run_lattice(args)
    if args.command == "arki":
        return run_arki(args)
    parser.error("unknown command")
    return 2


def run_init(out: Path) -> int:
    init_workspace(out)
    print(f"initialized Thesis OS workspace: {out}")
    return 0


def run_lint(root: Path) -> int:
    errors = lint_schemas(root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("schema lint ok")
    return 0


def run_alpha(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace)
    init_workspace(workspace)
    if args.alpha_command == "ingest-csv":
        result = ingest_csv_to_workspace(args.csv, workspace)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    if args.alpha_command == "sample-collect":
        quant = SampleQuantProvider().collect()
        qualitative_events = SampleQualitativeProvider().collect_events()
        qualitative = [event_to_evidence(event) for event in qualitative_events]
        result = ingest_evidence_to_workspace(workspace, quant + qualitative)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    if args.alpha_command == "list-evidence":
        evidence = load_workspace_evidence(workspace)
        print(json.dumps([item.to_dict() for item in evidence], indent=2, ensure_ascii=False))
        return 0
    if args.alpha_command == "run-screener":
        result = run_sample_screener(workspace)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    if args.alpha_command == "run-quant-screener":
        result = run_quant_screener(workspace, args.input_csv, top_n=args.top_n)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    if args.alpha_command == "discover":
        result = run_daily_discovery(workspace, limit=args.top_n)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    if args.alpha_command == "refresh-market-db":
        result = run_market_db_refresh(workspace, args.input_csv)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    if args.alpha_command == "intraday-monitor":
        result = run_intraday_monitor(workspace, args.input_csv)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    if args.alpha_command == "trade-proxy":
        result = run_trade_proxy(workspace, args.input_csv, proxy_name=args.proxy_name)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    if args.alpha_command == "list-screeners":
        conn = connect(workspace / "local" / "thesis_os.db")
        init_db(conn)
        candidates = list_screener_candidates(conn)
        conn.close()
        print(json.dumps(candidates, indent=2, ensure_ascii=False))
        return 0
    raise ValueError(f"unknown alpha command: {args.alpha_command}")


def run_lattice(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace)
    init_workspace(workspace)
    evidence = load_workspace_evidence(workspace)
    if args.lattice_command in {"build-thesis", "decision-card", "predict"}:
        if args.lattice_command == "build-thesis" and args.entity:
            evidence = [item for item in evidence if item.entity == args.entity]
        if not evidence:
            print("ERROR: no evidence available. Run `thesis-os alpha sample-collect` or ingest CSV first.")
            return 1

    if args.lattice_command == "build-thesis":
        thesis = build_sample_thesis(evidence)
        path = _write_thesis(workspace, thesis)
        print(json.dumps({"thesis_id": thesis.id, "path": str(path)}, indent=2, ensure_ascii=False))
        return 0

    if args.lattice_command == "decision-card":
        thesis = build_sample_thesis(evidence)
        _write_thesis(workspace, thesis)
        action = Action(
            id="ACTION-SAMPLE-001",
            entity=thesis.entity,
            action=args.action,
            reason=args.reason,
            evidence_ids=thesis.evidence_ids,
            created_at=utc_now(),
            thesis_id=thesis.id,
            confidence="medium",
            next_check="Next scheduled review",
        )
        path = _write_decision(workspace, thesis, action)
        write_action_queue(workspace / "action_queue.json", [action])
        print(json.dumps({"action_id": action.id, "path": str(path)}, indent=2, ensure_ascii=False))
        return 0

    if args.lattice_command == "predict":
        thesis = build_sample_thesis(evidence)
        _write_thesis(workspace, thesis)
        prediction = Prediction(
            id=f"PRED-{utc_now().replace(':', '').replace('-', '')}",
            entity=thesis.entity,
            thesis_id=thesis.id,
            prediction=args.prediction,
            direction=args.direction,
            horizon=args.horizon,
            confidence=args.confidence,
            created_at=utc_now(),
            evaluation_due=args.evaluation_due,
            evidence_ids=thesis.evidence_ids,
            invalidation=thesis.invalidation,
        )
        append_prediction(workspace / "prediction_ledger.jsonl", prediction)
        print(json.dumps(prediction.to_dict(), indent=2, ensure_ascii=False))
        return 0

    if args.lattice_command == "evaluate":
        predictions = read_predictions(workspace / "prediction_ledger.jsonl")
        prediction = next((item for item in predictions if item.get("id") == args.prediction_id), None)
        if prediction is None:
            print(f"ERROR: prediction not found: {args.prediction_id}")
            return 1
        feedback_md = feedback_report_markdown(prediction, args.absolute_return, args.benchmark_return)
        path = VaultWriter(workspace / "vault").write_note(
            f"feedback/{args.prediction_id}_feedback.md",
            title=f"Feedback: {args.prediction_id}",
            body=feedback_md,
            frontmatter={
                "prediction_id": args.prediction_id,
                "entity": prediction.get("entity", ""),
                "generated_at": utc_now(),
            },
        )
        print(json.dumps({"prediction_id": args.prediction_id, "path": str(path)}, indent=2, ensure_ascii=False))
        return 0

    if args.lattice_command == "evaluate-screener":
        try:
            result = evaluate_screener_candidate(
                workspace=workspace,
                candidate_id=args.candidate_id,
                horizon=args.horizon,
                absolute_return=args.absolute_return,
                benchmark_return=args.benchmark_return,
            )
        except KeyError:
            print(f"ERROR: screener candidate not found: {args.candidate_id}")
            return 1
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    if args.lattice_command == "evaluate-judgment":
        try:
            result = evaluate_judgment(
                workspace=workspace,
                action_id=args.action_id,
                horizon=args.horizon,
                absolute_return=args.absolute_return,
                benchmark_return=args.benchmark_return,
            )
        except KeyError:
            print(f"ERROR: action not found: {args.action_id}")
            return 1
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    if args.lattice_command == "roundtable":
        result = run_sample_roundtable(workspace)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    raise ValueError(f"unknown lattice command: {args.lattice_command}")


def run_arki(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace)
    if args.arki_command == "init":
        init_workspace(workspace)
        print(json.dumps({"workspace": str(workspace), "initialized": True}, indent=2))
        return 0
    if args.arki_command == "health":
        health = check_workspace(workspace)
        print(json.dumps({"workspace": str(workspace), "health": health}, indent=2, ensure_ascii=False))
        return 0 if health["ok"] else 1
    if args.arki_command == "build-wiki-index":
        result = build_wiki_index(workspace)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    if args.arki_command == "validate-harness":
        init_workspace(workspace)
        result = validate_harness_contracts(args.input_json, workspace=workspace)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result.get("error_count") == 0 else 1
    if args.arki_command == "build-dashboard":
        init_workspace(workspace)
        result = build_dashboard(workspace)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    raise ValueError(f"unknown arki command: {args.arki_command}")


def _write_thesis(workspace: Path, thesis) -> Path:
    return VaultWriter(workspace / "vault").write_note(
        f"theses/{thesis.id}.md",
        title="Sample AI Infrastructure Thesis",
        body=thesis_markdown(thesis),
        frontmatter=thesis.to_dict(),
    )


def _write_decision(workspace: Path, thesis, action: Action) -> Path:
    return VaultWriter(workspace / "vault").write_note(
        f"decisions/{action.id}.md",
        title="Sample Decision Card",
        body=decision_card_markdown(thesis, action),
        frontmatter=action.to_dict(),
    )


def run_demo(out: Path) -> int:
    out.mkdir(parents=True, exist_ok=True)
    sample_csv = out / "sample_evidence.csv"
    _write_sample_evidence_csv(sample_csv)

    vault = VaultWriter(out / "vault")
    vault.ensure_layout()
    write_default_job_manifest(out / "jobs.yaml")

    evidence = load_evidence_csv(sample_csv)
    db_path = out / "local" / "thesis_os.db"
    conn = connect(db_path)
    init_db(conn)
    insert_evidence(conn, evidence)

    for item in evidence:
        vault.write_note(
            f"evidence/{item.id}.md",
            title=f"Evidence: {item.entity}",
            body="\n".join(
                [
                    f"**Claim:** {item.claim}",
                    "",
                    f"**Interpretation:** {item.interpretation or 'No interpretation provided.'}",
                    "",
                    f"**Source:** {item.source}",
                ]
            ),
            frontmatter=item.to_dict(),
        )

    thesis = build_sample_thesis(evidence)
    _write_thesis(out, thesis)

    action = Action(
        id="ACTION-SAMPLE-001",
        entity=thesis.entity,
        action="watch",
        reason="Evidence supports active monitoring, but market reflection and base-rate checks are still required.",
        evidence_ids=thesis.evidence_ids,
        created_at=utc_now(),
        thesis_id=thesis.id,
        confidence="medium",
        next_check="Next weekly refresh",
    )
    _write_decision(out, thesis, action)
    write_action_queue(out / "action_queue.json", [action])
    run_sample_screener(out)
    sample_quant_csv = out / "sample_quant_features.csv"
    _write_sample_quant_csv(sample_quant_csv)
    run_quant_screener(out, sample_quant_csv, top_n=5)
    run_daily_discovery(out, limit=5)
    sample_market_csv = out / "sample_market_snapshots.csv"
    _write_sample_market_csv(sample_market_csv)
    run_market_db_refresh(out, sample_market_csv)
    sample_intraday_csv = out / "sample_intraday_events.csv"
    _write_sample_intraday_csv(sample_intraday_csv)
    run_intraday_monitor(out, sample_intraday_csv)
    sample_trade_csv = out / "sample_trade_proxy.csv"
    _write_sample_trade_proxy_csv(sample_trade_csv)
    run_trade_proxy(out, sample_trade_csv, proxy_name="semiconductor-memory")
    sample_harness_json = out / "sample_harness_contracts.json"
    _write_sample_harness_contracts_json(sample_harness_json)
    validate_harness_contracts(sample_harness_json, workspace=out)
    evidence = load_workspace_evidence(out)
    thesis = build_sample_thesis(evidence)
    _write_thesis(out, thesis)
    action = Action(
        id="ACTION-SAMPLE-001",
        entity=thesis.entity,
        action="watch",
        reason="Evidence supports active monitoring, but market reflection and base-rate checks are still required.",
        evidence_ids=thesis.evidence_ids,
        created_at=utc_now(),
        thesis_id=thesis.id,
        confidence="medium",
        next_check="Next weekly refresh",
    )
    _write_decision(out, thesis, action)
    write_action_queue(out / "action_queue.json", [action])
    build_wiki_index(out)

    prediction = Prediction(
        id="PRED-SAMPLE-001",
        entity=thesis.entity,
        thesis_id=thesis.id,
        prediction="The sample basket should outperform its benchmark if evidence remains positive and market reflection is incomplete.",
        direction="relative_outperform",
        horizon="1m",
        confidence=0.55,
        created_at=utc_now(),
        evaluation_due="sample+1m",
        evidence_ids=thesis.evidence_ids,
        invalidation=thesis.invalidation,
    )
    ledger_path = out / "prediction_ledger.jsonl"
    append_prediction(ledger_path, prediction)
    latest_prediction = read_predictions(ledger_path)[-1]
    feedback_md = feedback_report_markdown(latest_prediction, absolute_return=0.04, benchmark_return=0.015)
    vault.write_note(
        "feedback/PRED-SAMPLE-001_feedback.md",
        title="Sample Feedback Report",
        body=feedback_md,
        frontmatter={
            "prediction_id": prediction.id,
            "entity": prediction.entity,
            "generated_at": utc_now(),
            "sample": True,
        },
    )
    evaluate_judgment(out, action.id, horizon="1m", absolute_return=0.04, benchmark_return=0.015)
    build_dashboard(out)

    manifest = {
        "db": str(db_path),
        "vault": str(out / "vault"),
        "evidence_count": len(list_evidence(conn)),
        "health": check_demo_outputs(out),
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    conn.close()

    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    return 0


def _write_sample_evidence_csv(path: Path) -> None:
    rows = [
        {
            "id": "EVID-SAMPLE-001",
            "entity": "AI Infrastructure Basket",
            "source_type": "market_data",
            "source": "sample_quant_provider",
            "source_date": "2026-01-31",
            "claim": "Relative strength improved while volume expanded.",
            "interpretation": "Potential evidence of renewed institutional interest, not sufficient alone.",
            "confidence": "medium",
            "source_url": "",
            "tags": "sample|quant|relative-strength",
        },
        {
            "id": "EVID-SAMPLE-002",
            "entity": "AI Infrastructure Basket",
            "source_type": "youtube",
            "source": "sample_transcript_digest",
            "source_date": "2026-01-31",
            "claim": "Industry commentary points to sustained AI infrastructure capex.",
            "interpretation": "Qualitative support; must be cross-checked against official and market data.",
            "confidence": "low",
            "source_url": "https://example.com/sample",
            "tags": "sample|qualitative|youtube",
        },
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _write_sample_quant_csv(path: Path) -> None:
    rows = [
        {
            "ticker": "AI-INFRA",
            "entity": "AI Infrastructure Basket",
            "as_of_date": "2026-01-31",
            "source_signals": "quality|smart_money_quality|rs80_notlate|consensus_up",
            "quality_rank": "2",
            "smart_money_quality_rank": "4",
            "rs80_notlate_rank": "8",
            "consensus_up_rank": "5",
            "source_count": "40",
            "relative_strength": "88",
            "rs_score_norm": "0.88",
            "trend_quality_score_norm": "0.74",
            "turnover_score_norm": "0.70",
            "smart_money_candidate_score": "0.72",
            "supply_demand_score": "0.68",
            "quality_score_basic": "0.76",
            "compounder_score_basic": "0.78",
            "value_score_basic": "0.58",
            "value_quality_score_basic": "0.64",
            "earnings_improvement_score_basic": "0.62",
            "cycle_rerating_score_basic": "0.55",
            "smart_flow_score": "0.72",
            "quality_score": "0.76",
            "extension_risk": "0.30",
            "avg_turnover_20d": "42000000000",
            "foreign_quality_institution_5d_krw": "36000000000",
            "individual_5d_krw": "-18000000000",
            "action_bucket": "Focus Candidate",
            "entry_gap_pct": "0.05",
            "box_risk_pct": "-0.11",
            "kiwoom_surface_score": "0.62",
            "consensus_revision_score": "0.58",
            "dart_catalyst_score": "0.45",
            "short_loan_risk_score": "0.20",
            "thesis_id": "THESIS-SAMPLE-AI-INFRA-001",
        },
        {
            "ticker": "SUBSTRATE",
            "entity": "AI Server Substrate Basket",
            "as_of_date": "2026-01-31",
            "source_signals": "cycle|earnings|rs80_notlate",
            "cycle_rank": "6",
            "earnings_rank": "11",
            "rs80_notlate_rank": "15",
            "source_count": "40",
            "relative_strength": "82",
            "rs_score_norm": "0.82",
            "trend_quality_score_norm": "0.68",
            "turnover_score_norm": "0.60",
            "smart_money_candidate_score": "0.61",
            "supply_demand_score": "0.59",
            "quality_score_basic": "0.64",
            "compounder_score_basic": "0.62",
            "value_score_basic": "0.66",
            "value_quality_score_basic": "0.67",
            "earnings_improvement_score_basic": "0.68",
            "cycle_rerating_score_basic": "0.72",
            "smart_flow_score": "0.61",
            "quality_score": "0.64",
            "extension_risk": "0.22",
            "avg_turnover_20d": "28000000000",
            "foreign_quality_institution_5d_krw": "21000000000",
            "individual_5d_krw": "-9000000000",
            "action_bucket": "Watch - flow",
            "entry_gap_pct": "0.08",
            "box_risk_pct": "-0.14",
            "kiwoom_surface_score": "0.56",
            "consensus_revision_score": "0.44",
            "dart_catalyst_score": "0.30",
            "short_loan_risk_score": "0.18",
        },
        {
            "ticker": "HUMANOID",
            "entity": "Humanoid Robotics Basket",
            "as_of_date": "2026-01-31",
            "source_signals": "rs80_notlate",
            "rs80_notlate_rank": "5",
            "source_count": "40",
            "relative_strength": "91",
            "rs_score_norm": "0.91",
            "trend_quality_score_norm": "0.66",
            "turnover_score_norm": "0.48",
            "smart_money_candidate_score": "0.44",
            "supply_demand_score": "0.42",
            "quality_score_basic": "0.38",
            "compounder_score_basic": "0.34",
            "value_score_basic": "0.30",
            "value_quality_score_basic": "0.32",
            "earnings_improvement_score_basic": "0.40",
            "cycle_rerating_score_basic": "0.36",
            "smart_flow_score": "0.44",
            "quality_score": "0.38",
            "extension_risk": "0.46",
            "industry": "robot software",
            "avg_turnover_20d": "18000000000",
            "foreign_quality_institution_5d_krw": "6000000000",
            "individual_5d_krw": "8000000000",
            "action_bucket": "Watch - wide box",
            "entry_gap_pct": "0.15",
            "box_risk_pct": "-0.21",
            "kiwoom_surface_score": "0.50",
            "consensus_revision_score": "0.20",
            "dart_catalyst_score": "0.10",
            "short_loan_risk_score": "0.35",
        },
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_csv_fieldnames(rows))
        writer.writeheader()
        writer.writerows(rows)


def _write_sample_market_csv(path: Path) -> None:
    rows = [
        {"market": "KR", "ticker": "AI-INFRA", "entity": "AI Infrastructure Basket", "as_of_date": "2026-01-31", "close": "104.0", "volume": "1500000", "foreign_flow": "1200000", "institution_flow": "900000", "retail_flow": "-500000", "source": "sample_kr_close"},
        {"market": "US", "ticker": "US-AI", "entity": "US AI Infrastructure Basket", "as_of_date": "2026-01-31", "close": "212.0", "volume": "2500000", "foreign_flow": "0", "institution_flow": "700000", "retail_flow": "100000", "source": "sample_us_close"},
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_csv_fieldnames(rows))
        writer.writeheader()
        writer.writerows(rows)


def _write_sample_intraday_csv(path: Path) -> None:
    rows = [
        {"ticker": "AI-INFRA", "entity": "AI Infrastructure Basket", "watch_type": "holding", "observed_at": "2026-01-31T10:30:00+09:00", "price": "108.0", "reference_price": "104.0", "foreign_flow": "1000000", "institution_flow": "800000"},
        {"ticker": "CROWD-MOMO", "entity": "Crowded Momentum Basket", "watch_type": "watchlist", "observed_at": "2026-01-31T10:35:00+09:00", "price": "93.0", "reference_price": "100.0", "foreign_flow": "-600000", "institution_flow": "-500000"},
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_csv_fieldnames(rows))
        writer.writeheader()
        writer.writerows(rows)


def _write_sample_trade_proxy_csv(path: Path) -> None:
    rows = [
        {
            "period": "2026-01",
            "entity": "AI Memory Export Proxy",
            "origin": "Korea",
            "destination": "Taiwan",
            "hs_code": "854232",
            "description": "memory IC export proxy",
            "value_usd": "133400000",
            "baseline_usd": "105200000",
            "yoy_value_usd": "47500000",
            "quantity": "0",
            "unit": "",
            "confidence": "medium",
            "source": "sample_customs_adapter",
            "source_url": "https://example.com/customs-sample",
        },
        {
            "period": "2026-01",
            "entity": "AI Server Substrate Proxy",
            "origin": "Korea",
            "destination": "Global",
            "hs_code": "853400",
            "description": "printed circuit substrate proxy",
            "value_usd": "62000000",
            "baseline_usd": "54000000",
            "yoy_value_usd": "51000000",
            "quantity": "0",
            "unit": "",
            "confidence": "low",
            "source": "sample_customs_adapter",
            "source_url": "https://example.com/customs-sample",
        },
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_csv_fieldnames(rows))
        writer.writeheader()
        writer.writerows(rows)


def _write_sample_harness_contracts_json(path: Path) -> None:
    data = {
        "contracts": [
            {
                "id": "alpha.trade-proxy.semiconductor.v1",
                "owner_agent": "alpha",
                "purpose": "Convert customs/export-import adapter output into thesis evidence.",
                "trigger": "after_monthly_trade_data_refresh",
                "command": "thesis-os alpha trade-proxy --workspace ./workspace --input-csv ./trade.csv --proxy-name semiconductor-memory",
                "inputs": ["trade_proxy_csv"],
                "outputs": ["local_db.evidence", "vault/evidence/{proxy_name}-trade-proxy.md"],
                "delivery": ["vault"],
                "failure_policy": "write deterministic error note and keep previous evidence",
                "model_policy": {"llm_required": False},
            },
            {
                "id": "lattice.concentrated-strategy.v1",
                "owner_agent": "lattice",
                "purpose": "Review Top 5 candidates and holdings for portfolio inclusion and concentration decisions.",
                "trigger": "after_market_close_evidence_refresh",
                "command": "thesis-os lattice roundtable --workspace ./workspace",
                "inputs": ["local_db.evidence", "vault/theses", "screeners.top5"],
                "outputs": ["vault/decisions/daily-roundtable-sample.md"],
                "delivery": ["vault", "telegram-summary-placeholder"],
                "failure_policy": "preserve previous decision and flag stale output",
                "model_policy": {"high_capability_model_for_judgment": True},
            },
        ]
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _csv_fieldnames(rows: list[dict[str, str]]) -> list[str]:
    names: list[str] = []
    for row in rows:
        for key in row:
            if key not in names:
                names.append(key)
    return names


if __name__ == "__main__":
    raise SystemExit(main())
