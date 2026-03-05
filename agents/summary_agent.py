"""
Summary Agent
=============
Generates a concise, plain-language technical summary of a document.
"""

from agents.base_agent import BaseAgent


class SummaryAgent(BaseAgent):

    def __init__(self, model, message_bus, verbose=False):
        super().__init__("Summariser", model, message_bus, verbose)

    @property
    def system_prompt(self) -> str:
        return """You are a technical summary agent specialising in engineering documentation.

Write a clear, concise summary (150–200 words) of the technical document provided.
Your summary must:
- State what the document is and what it covers
- Highlight the most important technical content
- Be written for a technically literate reader
- Use plain, direct language — no fluff or filler
- Not repeat the title or say "this document"

Write in flowing prose. No bullet points."""

    def run(self, document: str) -> str:
        self.logger.info("Generating summary...")
        prompt = f"Summarise this technical document:\n\n---\n{document[:6000]}\n---"
        summary = self.call_llm(prompt, temperature=0.3, max_tokens=400)
        self.publish("Orchestrator", "result", {"summary": summary})
        return summary
