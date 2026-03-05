"""
Technical Document Analyser — Multi-Agent System
==================================================
A production-style multi-agent pipeline that analyses technical engineering
documents using specialised AI agents communicating via a shared message bus.

Architecture:
    OrchestratorAgent  — coordinates the pipeline, routes tasks between agents
    ExtractorAgent     — extracts structured information from raw document text
    SummaryAgent       — generates concise technical summaries
    QAAgent            — answers specific questions about the document
    ReportAgent        — compiles all agent outputs into a final structured report

Usage:
    python main.py --doc sample_docs/example_spec.txt --question "What are the safety requirements?"
    python main.py --doc sample_docs/example_spec.txt  (uses default questions)

Author: Ambika Sugganahalli Mahadevappa
"""

import argparse
import json
import os
import sys
from pathlib import Path

from agents.orchestrator import OrchestratorAgent
from agents.message_bus import MessageBus
from utils.document_loader import load_document
from utils.logger import get_logger

logger = get_logger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Technical Document Analyser — Multi-Agent System"
    )
    parser.add_argument(
        "--doc",
        type=str,
        default="sample_docs/example_spec.txt",
        help="Path to the technical document to analyse"
    )
    parser.add_argument(
        "--question",
        type=str,
        default=None,
        help="Optional: specific question to answer about the document"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="outputs/report.json",
        help="Path to save the final report (JSON)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o",
        help="OpenAI model to use (default: gpt-4o)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed agent communication logs"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # ── Load document ──
    doc_path = Path(args.doc)
    if not doc_path.exists():
        logger.error(f"Document not found: {doc_path}")
        sys.exit(1)

    document_text = load_document(doc_path)
    logger.info(f"Loaded document: {doc_path.name} ({len(document_text)} characters)")

    # ── Initialise message bus (agent communication layer) ──
    bus = MessageBus(verbose=args.verbose)

    # ── Initialise orchestrator (it creates and manages all sub-agents) ──
    orchestrator = OrchestratorAgent(
        model=args.model,
        message_bus=bus,
        verbose=args.verbose
    )

    # ── Run the pipeline ──
    print("\n" + "═" * 60)
    print("  TECHNICAL DOCUMENT ANALYSER — MULTI-AGENT PIPELINE")
    print("═" * 60)
    print(f"  Document : {doc_path.name}")
    print(f"  Model    : {args.model}")
    print(f"  Question : {args.question or 'Default analysis suite'}")
    print("═" * 60 + "\n")

    report = orchestrator.run(
        document=document_text,
        document_name=doc_path.name,
        user_question=args.question
    )

    # ── Save report ──
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # ── Print final report to console ──
    print("\n" + "═" * 60)
    print("  FINAL REPORT")
    print("═" * 60)
    print(f"\n📄 DOCUMENT: {report['document_name']}\n")
    print(f"📋 SUMMARY:\n{report['summary']}\n")
    print(f"🔍 EXTRACTED INFORMATION:")
    for key, value in report['extracted_info'].items():
        print(f"  • {key}: {value}")
    if report.get('qa_answer'):
        print(f"\n❓ Q: {report['user_question']}")
        print(f"💡 A: {report['qa_answer']}")
    print(f"\n📊 RISK FLAGS: {', '.join(report['risk_flags']) if report['risk_flags'] else 'None identified'}")
    print(f"\n✅ Report saved to: {output_path}")
    print("═" * 60 + "\n")

    return report


if __name__ == "__main__":
    main()
