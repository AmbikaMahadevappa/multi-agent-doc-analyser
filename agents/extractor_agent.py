"""
Extractor Agent
===============
Specialised agent for extracting structured information from
unstructured technical documents. Returns a key-value dictionary
of the most important technical fields found in the document.
"""

import json
from typing import Dict
from agents.base_agent import BaseAgent


class ExtractorAgent(BaseAgent):

    def __init__(self, model, message_bus, verbose=False):
        super().__init__("Extractor", model, message_bus, verbose)

    @property
    def system_prompt(self) -> str:
        return """You are a specialised information extraction agent for technical engineering documents.

Your task is to extract structured key information from the document provided.

Always return a valid JSON object with these fields (use null if not found):
{
  "document_type": "type of document (e.g. technical specification, test report, user manual)",
  "title": "document title or name",
  "version": "version or revision number",
  "date": "document date",
  "author_or_organisation": "author or issuing organisation",
  "purpose": "one sentence stating the document's purpose",
  "key_components": "comma-separated list of main components, systems or topics covered",
  "technical_standards": "any standards referenced (e.g. ISO, DIN, IEC)",
  "performance_requirements": "key performance or technical requirements stated",
  "constraints": "any stated limitations, constraints or assumptions",
  "target_audience": "intended audience of the document"
}

Return ONLY the JSON object. No explanation, no markdown fences."""

    def run(self, document: str) -> Dict:
        self.logger.info("Extracting structured information...")

        prompt = f"""Extract structured information from this technical document:

---
{document[:6000]}
---

Return a JSON object with all fields listed in your instructions."""

        response = self.call_llm(prompt, temperature=0.1, max_tokens=1000)

        try:
            # Clean any accidental markdown fences
            cleaned = response.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("```")[1]
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:]
            extracted = json.loads(cleaned.strip())
        except json.JSONDecodeError:
            self.logger.warning("JSON parse failed — returning raw response")
            extracted = {"raw_extraction": response}

        self.publish("Orchestrator", "result", extracted)
        return extracted
