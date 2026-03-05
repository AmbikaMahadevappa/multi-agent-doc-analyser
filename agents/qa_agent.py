"""
QA Agent
=========
Answers specific user questions about a technical document.
Grounds answers strictly in the document content — no hallucination.
"""

from agents.base_agent import BaseAgent


class QAAgent(BaseAgent):

    def __init__(self, model, message_bus, verbose=False):
        super().__init__("QAAgent", model, message_bus, verbose)

    @property
    def system_prompt(self) -> str:
        return """You are a precise question-answering agent for technical documents.

Rules:
- Answer ONLY based on what is stated in the document
- If the document does not contain enough information to answer, say so clearly
- Be specific and cite relevant sections where possible
- Keep answers concise (under 150 words)
- Do not speculate or add external knowledge"""

    def run(self, document: str, question: str) -> str:
        self.logger.info(f"Answering question: {question[:80]}")
        prompt = (
            f"Document:\n---\n{document[:6000]}\n---\n\n"
            f"Question: {question}"
        )
        answer = self.call_llm(prompt, temperature=0.1, max_tokens=400)
        self.publish("Orchestrator", "result", {"qa_answer": answer})
        return answer
