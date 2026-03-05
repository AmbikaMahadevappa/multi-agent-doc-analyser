"""
Report Agent
=============
Compiles all agent outputs into a single, structured final report.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from agents.base_agent import BaseAgent


class ReportAgent(BaseAgent):

    def __init__(self, model, message_bus, verbose=False):
        super().__init__("ReportAgent", model, message_bus, verbose)

    @property
    def system_prompt(self) -> str:
        return "You are a report compilation agent. You assemble structured analysis reports."

    def run(
        self,
        document_name: str,
        extracted_info: Dict,
        summary: str,
        risk_flags: List[str],
        qa_answer: Optional[str] = None,
        user_question: Optional[str] = None,
        message_history: Optional[List] = None,
    ) -> Dict[str, Any]:
        """Compile all agent outputs into the final report dictionary."""
        self.logger.info("Compiling final report...")

        report = {
            "document_name": document_name,
            "analysis_timestamp": datetime.now().isoformat(),
            "pipeline": {
                "agents_used": [
                    "OrchestratorAgent",
                    "ExtractorAgent",
                    "SummaryAgent",
                    "QAAgent",
                    "RiskAgent",
                    "ReportAgent"
                ],
                "model": self.model,
                "message_count": len(message_history) if message_history else 0,
            },
            "summary": summary,
            "extracted_info": extracted_info,
            "risk_flags": risk_flags,
            "user_question": user_question,
            "qa_answer": qa_answer,
            "agent_communication_log": message_history or [],
        }

        self.publish("Orchestrator", "result", {"report": "compiled"})
        return report
