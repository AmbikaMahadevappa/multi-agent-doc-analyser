"""
Orchestrator Agent
==================
The central controller of the multi-agent pipeline.
Coordinates task delegation to specialised sub-agents,
collects their results, and assembles the final report.

Pipeline flow:
    1. Receive document from user
    2. Dispatch to ExtractorAgent  → structured information
    3. Dispatch to SummaryAgent    → concise technical summary
    4. Dispatch to QAAgent         → answer user question (if provided)
    5. Dispatch to RiskAgent       → identify risk flags / warnings
    6. Dispatch to ReportAgent     → compile final structured report
"""

import json
from typing import Any, Dict, Optional

from agents.base_agent import BaseAgent
from agents.extractor_agent import ExtractorAgent
from agents.summary_agent import SummaryAgent
from agents.qa_agent import QAAgent
from agents.risk_agent import RiskAgent
from agents.report_agent import ReportAgent
from agents.message_bus import MessageBus


class OrchestratorAgent(BaseAgent):

    def __init__(self, model: str, message_bus: MessageBus, verbose: bool = False):
        super().__init__(
            name="Orchestrator",
            model=model,
            message_bus=message_bus,
            verbose=verbose
        )
        # Initialise all sub-agents
        self.extractor = ExtractorAgent(model, message_bus, verbose)
        self.summariser = SummaryAgent(model, message_bus, verbose)
        self.qa_agent   = QAAgent(model, message_bus, verbose)
        self.risk_agent = RiskAgent(model, message_bus, verbose)
        self.reporter   = ReportAgent(model, message_bus, verbose)

    @property
    def system_prompt(self) -> str:
        return (
            "You are an orchestrator agent managing a multi-agent pipeline "
            "for technical document analysis. Your role is to coordinate "
            "specialised sub-agents and ensure high-quality, structured output."
        )

    def run(
        self,
        document: str,
        document_name: str,
        user_question: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute the full multi-agent analysis pipeline.
        Returns a structured report dictionary.
        """
        self.logger.info("Pipeline started.")

        # ── Step 1: Extract structured information ──
        print("  [1/5] ExtractorAgent   — extracting structured information...")
        self.publish("Extractor", "task", {"document": document})
        extracted_info = self.extractor.run(document=document)
        self.publish("Orchestrator", "result", {"extracted_info": extracted_info})
        print(f"        ✓ Extracted {len(extracted_info)} fields\n")

        # ── Step 2: Generate summary ──
        print("  [2/5] SummaryAgent     — generating technical summary...")
        self.publish("Summariser", "task", {"document": document})
        summary = self.summariser.run(document=document)
        self.publish("Orchestrator", "result", {"summary": summary})
        print(f"        ✓ Summary generated ({len(summary)} chars)\n")

        # ── Step 3: Answer user question (if provided) ──
        qa_answer = None
        if user_question:
            print(f"  [3/5] QAAgent          — answering: '{user_question[:60]}...'")
            self.publish("QAAgent", "task", {
                "document": document,
                "question": user_question
            })
            qa_answer = self.qa_agent.run(
                document=document,
                question=user_question
            )
            self.publish("Orchestrator", "result", {"qa_answer": qa_answer})
            print(f"        ✓ Answer generated\n")
        else:
            print("  [3/5] QAAgent          — skipped (no question provided)\n")

        # ── Step 4: Risk flagging ──
        print("  [4/5] RiskAgent        — scanning for risk flags...")
        self.publish("RiskAgent", "task", {"document": document})
        risk_flags = self.risk_agent.run(document=document)
        self.publish("Orchestrator", "result", {"risk_flags": risk_flags})
        print(f"        ✓ {len(risk_flags)} risk flag(s) identified\n")

        # ── Step 5: Compile report ──
        print("  [5/5] ReportAgent      — compiling final report...")
        self.publish("ReportAgent", "task", {"compile": True})
        report = self.reporter.run(
            document_name=document_name,
            extracted_info=extracted_info,
            summary=summary,
            qa_answer=qa_answer,
            user_question=user_question,
            risk_flags=risk_flags,
            message_history=self.bus.get_history_summary()
        )
        print(f"        ✓ Report compiled\n")

        self.logger.info("Pipeline complete.")
        return report
