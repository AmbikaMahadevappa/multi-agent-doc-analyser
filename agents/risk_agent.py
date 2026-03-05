"""
Risk Agent
===========
Scans a technical document for risk flags, warnings, safety concerns,
unresolved issues, or ambiguous requirements.
"""

import json
from typing import List
from agents.base_agent import BaseAgent


class RiskAgent(BaseAgent):

    def __init__(self, model, message_bus, verbose=False):
        super().__init__("RiskAgent", model, message_bus, verbose)

    @property
    def system_prompt(self) -> str:
        return """You are a technical risk analysis agent specialising in engineering documents.

Scan the document for:
- Safety warnings or hazard notices
- Unresolved issues, open questions, or TBDs
- Ambiguous or contradictory requirements
- Missing critical information
- Compliance or regulatory concerns
- Deprecated components or outdated references

Return a JSON array of short risk flag strings (max 15 words each).
Example: ["Safety critical: overvoltage protection not specified", "TBD: thermal limits undefined"]

If no risks found, return an empty array: []
Return ONLY the JSON array."""

    def run(self, document: str) -> List[str]:
        self.logger.info("Scanning for risk flags...")
        prompt = f"Scan this document for risk flags:\n\n---\n{document[:6000]}\n---"
        response = self.call_llm(prompt, temperature=0.1, max_tokens=400)

        try:
            cleaned = response.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("```")[1]
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:]
            flags = json.loads(cleaned.strip())
            if not isinstance(flags, list):
                flags = []
        except json.JSONDecodeError:
            flags = ["Warning: risk extraction encountered a parsing error"]

        self.publish("Orchestrator", "result", {"risk_flags": flags})
        return flags
