# Technical Document Analyser — Multi-Agent System

A production-style **multi-agent AI pipeline** for analysing technical engineering documents. Built with Python and the OpenAI API (GPT-4o), using a message-bus architecture for agent-to-agent (A2A) communication.

Each agent in the pipeline has a specialised role. They communicate asynchronously through a shared message bus — no agent holds a direct reference to another. The orchestrator coordinates the pipeline, routes tasks, collects results, and compiles the final report.

---

## Architecture

```
User Input (document + optional question)
        │
        ▼
┌─────────────────────┐
│  OrchestratorAgent  │  ← coordinates the full pipeline
└──────────┬──────────┘
           │ dispatches tasks via MessageBus
    ┌──────┼──────────────────────────┐
    ▼      ▼          ▼              ▼
ExtractorAgent  SummaryAgent   QAAgent    RiskAgent
(structured     (150-200 word  (grounded  (safety flags,
 key-value       technical      Q&A)       TBDs, open
 extraction)     summary)                  issues)
    │      │          │              │
    └──────┴──────────┴──────────────┘
                      │ all results via MessageBus
                      ▼
               ReportAgent
          (compiles final JSON report)
```

### Agents

| Agent | Role |
|---|---|
| `OrchestratorAgent` | Controls the pipeline, routes tasks between agents |
| `ExtractorAgent` | Extracts structured key-value information from the document |
| `SummaryAgent` | Generates a concise technical summary (150–200 words) |
| `QAAgent` | Answers specific user questions grounded in the document |
| `RiskAgent` | Flags safety concerns, TBDs, open issues, and ambiguities |
| `ReportAgent` | Compiles all outputs into a final structured JSON report |
| `MessageBus` | Decoupled A2A communication layer — agents publish and subscribe |

---

## Quickstart

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/multi-agent-doc-analyser.git
cd multi-agent-doc-analyser
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add your OpenAI API key

```bash
cp .env.example .env
# Edit .env and add your key:
# OPENAI_API_KEY=sk-...
```

### 4. Run with the included sample document

```bash
python main.py
```

### 5. Run with your own document

```bash
python main.py --doc path/to/your/document.txt
```

### 6. Ask a specific question about the document

```bash
python main.py --doc sample_docs/example_spec.txt \
               --question "What are the safety requirements and open issues?"
```

### 7. Enable verbose agent communication logs

```bash
python main.py --verbose
```

---

## Example Output

```
════════════════════════════════════════════════════════════
  TECHNICAL DOCUMENT ANALYSER — MULTI-AGENT PIPELINE
════════════════════════════════════════════════════════════
  Document : example_spec.txt
  Model    : gpt-4o
  Question : Default analysis suite
════════════════════════════════════════════════════════════

  [1/5] ExtractorAgent   — extracting structured information...
        ✓ Extracted 11 fields

  [2/5] SummaryAgent     — generating technical summary...
        ✓ Summary generated (743 chars)

  [3/5] QAAgent          — skipped (no question provided)

  [4/5] RiskAgent        — scanning for risk flags...
        ✓ 5 risk flag(s) identified

  [5/5] ReportAgent      — compiling final report...
        ✓ Report compiled

════════════════════════════════════════════════════════════
  FINAL REPORT
════════════════════════════════════════════════════════════

📄 DOCUMENT: example_spec.txt

📋 SUMMARY:
This specification defines the design, performance, and interface requirements
for an Ultrasonic Proximity Sensor Array (UPSA) used in low-speed vehicle
manoeuvring assistance systems...

🔍 EXTRACTED INFORMATION:
  • document_type: Technical Specification
  • title: Vehicle Proximity Sensor System — Ultrasonic Array Module
  • version: 2.1
  • technical_standards: ISO 26262:2018, ISO 17386:2010, IEC 61000-4-3
  • performance_requirements: 0.15–2.50m range, ±30mm accuracy, 20Hz update rate
  ...

📊 RISK FLAGS:
  • Safety critical: blind zone below 0.15m must be communicated to driver
  • ASIL decomposition analysis not yet finalised (OI-031)
  • LIN interface spec pending revision — timing parameters may change
  • Cross-talk multiplexing schedule undefined (OI-047)
  • Thermal derating data above 70°C not yet available (OI-061)

✅ Report saved to: outputs/report.json
```

---

## Project Structure

```
multi-agent-doc-analyser/
├── main.py                        # Entry point — CLI + pipeline runner
├── requirements.txt
├── .env.example                   # API key template
├── .gitignore
│
├── agents/
│   ├── __init__.py
│   ├── message_bus.py             # A2A communication layer
│   ├── base_agent.py              # Abstract base — all agents inherit this
│   ├── orchestrator.py            # Pipeline controller
│   ├── extractor_agent.py         # Structured information extraction
│   ├── summary_agent.py           # Technical summarisation
│   ├── qa_agent.py                # Grounded question answering
│   ├── risk_agent.py              # Risk and safety flag detection
│   └── report_agent.py            # Final report compilation
│
├── utils/
│   ├── document_loader.py         # File loading utilities
│   └── logger.py                  # Consistent logging across agents
│
├── sample_docs/
│   └── example_spec.txt           # Automotive sensor system specification
│
└── outputs/
    └── report.json                # Generated analysis report (git-ignored)
```

---

## Design Decisions

**Why a message bus?**
Direct agent-to-agent calls create tight coupling — if one agent changes, others break. A message bus decouples agents completely. Each agent only knows its own task and publishes results to the bus. The orchestrator handles routing. This mirrors production multi-agent architectures (A2A protocol design).

**Why specialised agents instead of one large prompt?**
Each agent has a single, focused responsibility and a tailored system prompt. This produces significantly higher quality outputs than asking one model to do everything at once. It also makes the system easy to extend — adding a new capability means adding a new agent, not modifying existing ones.

**Why JSON-structured outputs?**
Structured outputs from the ExtractorAgent and RiskAgent make the system composable — the report can be consumed by downstream systems, stored in a database, or fed into another pipeline.

---

## Extending the System

Adding a new agent takes three steps:

1. Create `agents/your_agent.py` inheriting from `BaseAgent`
2. Define `system_prompt` and `run()` method
3. Add it to `OrchestratorAgent.__init__()` and call it in `run()`

---

## Technologies

- **Python 3.10+**
- **OpenAI API** (GPT-4o) — LLM backbone for all agents
- **Custom MessageBus** — decoupled A2A communication
- **dataclasses** — typed message objects
- **argparse** — CLI interface

---

## Author

**Ambika Sugganahalli Mahadevappa**
M.Sc. Information and Electrical Engineering — Hochschule Wismar
[LinkedIn](https://linkedin.com/in/ambika-sugganahalli-mahadevappa-b49261188)
