Copy everything below and paste into Google Docs.

This submission includes (1) work completed during this interim period with evidence (tests added, where to find them, how to run and capture output) and (2) a planned vs actual comparison for the interim period, plus the forward-looking plan (priorities and day-by-day schedule).


Week 12 Interim Submission — 10 Academy

1. Selected Project Name

RAG Complaint Chatbot — Retrieval-Augmented Generation pipeline for consumer financial complaint analysis (CFPB dataset).

2. Business Problem Summary

Financial institutions and regulators need reliable, auditable access to patterns in consumer complaint data. Manual review does not scale; ungrounded generative AI introduces regulatory and reputational risk. This RAG pipeline addresses that by:

• Risk reduction: Answers are grounded in retrieved complaint excerpts, reducing hallucination and inappropriate generalisation.
• Reliability: Semantic search over a curated vector index ensures that responses reflect actual CFPB complaint content (Credit Cards, Personal Loans, Savings Accounts, Money Transfers).
• Auditability: Every answer can be traced to specific complaint IDs, products, issues, and companies, supporting internal review and regulatory scrutiny.
• Regulatory sensitivity: The design favours traceability and source citation, which aligns with expectations for explainable, evidence-based use of AI in finance.
• Knowledge retrieval accuracy: Embedding-based retrieval targets meaning rather than keywords, improving relevance for analytical questions.
• Operational efficiency: A single pipeline from raw data to an interactive interface reduces time to insight for compliance and product teams.

The system is positioned for internal and regulatory-adjacent use where verifiability and control over data sources matter more than maximum model scale.

3. What Was Accomplished in the Original Project

3.1 What Was Originally Implemented

• Task 1 — Data preprocessing
  Modules: src/load_data.py (chunked CSV reading), src/filtering.py (product filter, empty-narrative removal), src/text_cleaning.py (lowercase, boilerplate removal, punctuation preserved).
  Orchestration: src/preprocess_pipeline.py — load, filter, clean, save to data/processed/filtered_complaints.csv.
  Scope: Four products (Credit card, Personal loan, Savings account, Money transfers); memory-efficient chunked processing.

• Task 2 — Vector indexing
  Modules: src/sampling.py (stratified sampling, seed 42), src/chunking.py (LangChain RecursiveCharacterTextSplitter, 500 chars, 50 overlap), src/embedding.py (sentence-transformers/all-MiniLM-L6-v2), src/index_builder.py (ChromaDB PersistentClient).
  Orchestration: src/task2_pipeline.py — load filtered data, stratified sample (e.g. 12k rows), chunk, embed, index into ChromaDB at vector_store/ with metadata (complaint_id, product, company, issue, chunk_index).

• Task 3 — RAG pipeline
  Module: src/rag_pipeline.py — RAGPipeline with retrieve(), format_context(), generate() (HuggingFace text-generation pipeline, default GPT-2, CPU).
  Prompt: Fixed template for a CrediTrust financial analyst assistant with context and question; instructs to say when context is insufficient.
  Evaluation: src/evaluation.py — 10 fixed questions, runs pipeline, writes output/evaluation_results.md with question, answer, retrieved sources; Quality Score and Comments left as TBD for manual fill.

• Task 4 — Interactive UI
  Entrypoint: app.py — Gradio app (chat + source panel), loads RAG once at startup, displays answer and formatted sources (complaint ID, product, issue, company, text preview).
  Run: python app.py → http://localhost:7860.

• Supporting assets
  report.md: narrative report of design and implementation.
  src/load_prebuilt_store.py: optional loader from a pre-built parquet into ChromaDB.
  src/eda.py: EDA helpers; notebook notebooks/0_EDA_and_preprocessing.ipynb for analysis and preprocessing.

3.2 What Works Well

• End-to-end flow: Raw data to filtered/cleaned CSV to vector store to RAG to Gradio works as a single pipeline; README and report describe it clearly.
• Modular design: Clear separation (load, filter, clean, sample, chunk, embed, index, retrieve, generate) aids maintenance and future changes.
• Source transparency: UI and evaluation output both show which complaint chunks were used, supporting basic auditability.
• Stable choices: Stratified sampling with seed, single embedding model for index and query, and persistent ChromaDB give reproducible indexing.
• Lightweight default: GPT-2 and CPU-friendly embedding allow running without GPU; pipeline accepts other HuggingFace models.

3.3 What Is Missing From a Production-Grade System

• Automated tests: No test files or pytest/unittest; only manual runs and the evaluation script.
• CI/CD: No .github/workflows or other automation for lint, test, or build.
• Quantified evaluation: No faithfulness, relevance, or retrieval metrics; evaluation table has Quality Score/Comments as TBD.
• Config and reproducibility: Paths, seeds, and model names are hardcoded; no single config file or env schema.
• Preprocessing default: preprocess_pipeline.py runs with sample_for_eda=True in __main__, so it stops after a few chunks unless changed.
• Explainability beyond citations: No similarity scores or confidence in the UI; no structured why this chunk explanation.
• Error and edge handling: Limited handling for missing vector store, empty retrieval, or API failures in one place.
• Dependency and env spec: requirements.txt exists but no environment.yml or Dockerfile for full reproducibility.

Interim period: Completed improvements and evidence

This section documents work completed during this interim period (Week 12), with evidence in the repo.

Command to reproduce test evidence (from project root):
  python -m pytest tests/ -v --tb=short
Optionally save output: python -m pytest tests/ -v --tb=short 2>&1 | Out-File -FilePath output\pytest_results.txt (PowerShell) or ... > output/pytest_results.txt (bash).

Improvement 1: Minimal unit test suite (tests/)

What was done: Added a tests/ directory with unit tests for the preprocessing pipeline so that filtering and text-cleaning behaviour can be verified automatically and regressions caught.

Where in repo:
• tests/conftest.py — Adds project root to Python path so tests can import src.
• tests/test_filtering.py — Tests for filter_products and remove_empty_narratives (src/filtering.py).
• tests/test_text_cleaning.py — Tests for clean_text and apply_text_cleaning (src/text_cleaning.py).

Evidence (code snippet): tests/test_filtering.py

  def test_filter_products_keeps_only_allowed():
      df = pd.DataFrame({
          "Product": ["Credit card", "Mortgage", "Personal loan", "Credit card"],
          "Consumer complaint narrative": ["a", "b", "c", "d"],
      })
      out = filter_products(df)
      assert len(out) == 3
      assert set(out["Product"].tolist()) == {"Credit card", "Personal loan"}

Evidence (test run): Run the following command from the project root to run all unit tests and capture output.

Command (Windows PowerShell, from project root):
  cd d:\KAIM\rag-complaint-chatbot
  python -m pytest tests/ -v --tb=short

Command (Linux/Mac, from project root):
  cd /path/to/rag-complaint-chatbot
  python -m pytest tests/ -v --tb=short

To save the output to a file for evidence: run the same pytest command and redirect output to output/pytest_results.txt (e.g. in PowerShell: python -m pytest tests/ -v --tb=short 2>&1 | Out-File -FilePath output\pytest_results.txt). The repo includes a placeholder at output/pytest_results.txt; replace it with your actual run output.

Screenshot (optional): Add a screenshot of the pytest run (terminal or IDE test panel) and save as output/pytest_screenshot.png or paste into this document.

Planned vs actual (this interim period)

Comparison of what was planned for this interim period versus what was completed. Use this to report progress in future submissions.

• Unit tests for preprocessing (filtering, text cleaning) — Planned: Yes. Actual: Done. Evidence: tests/test_filtering.py, tests/test_text_cleaning.py. Reproduce: from project root run python -m pytest tests/ -v --tb=short; optionally save output to output/pytest_results.txt.
• CI workflow (e.g. GitHub Actions) — Planned: Yes (next). Actual: Not yet. Evidence: N/A.
• Config externalisation — Planned: Yes. Actual: Not yet. Evidence: N/A.
• Quantitative evaluation metric — Planned: Yes. Actual: Not yet. Evidence: N/A.
• Retrieval scores in UI — Planned: Yes. Actual: Not yet. Evidence: N/A.
• Environment and runbook documentation — Planned: Yes. Actual: Not yet. Evidence: N/A.

4. Gap Analysis

• Code quality — Is there a consistent style (e.g. formatter/linter)? Status: No. Evidence: No pyproject.toml, .flake8, ruff, or pre-commit config.
• Code quality — Are paths and config externalised? Status: No. Evidence: Paths like data/raw/complaints.csv, vector_store and seeds hardcoded in preprocess_pipeline.py, task2_pipeline.py, rag_pipeline.py.
• Testing — Are there unit tests? Status: Partial. Evidence: tests/test_filtering.py and tests/test_text_cleaning.py added (7 tests). Run: python -m pytest tests/ -v --tb=short from project root.
• Testing — Are there integration tests (e.g. RAG query)? Status: No. Evidence: Only src/evaluation.py as a manual evaluation script, not an automated test.
• Documentation — Is the pipeline documented for a new developer? Status: Partial. Evidence: README and report.md describe flow; README has UTF-16 BOM; no API/docs for src modules.
• Documentation — Is there a runbook or ops guide? Status: No. Evidence: No runbook, env vars, or deployment notes.
• Reproducibility — Can the environment be recreated from a single spec? Status: Partial. Evidence: requirements.txt present; no version pinning strategy doc, no Docker/conda.
• Reproducibility — Is preprocessing fully reproducible (no EDA shortcut)? Status: Partial. Evidence: preprocess_pipeline.py line 57: run_pipeline(sample_for_eda=True) stops early by default.
• Visualization — Is there a user-facing interface? Status: Yes. Evidence: app.py — Gradio chat UI with source panel.
• Visualization — Are retrieval or evaluation results visualised? Status: Partial. Evidence: EDA notebook and eda.py; evaluation is markdown table only, no charts.
• Business impact — Are outputs traceable to source data? Status: Yes. Evidence: Sources shown in UI and in evaluation_results.md with complaint ID, product, issue.
• Business impact — Is there quantified quality (e.g. metrics)? Status: No. Evidence: evaluation_results.md has Quality Score and Comments as TBD; no automated metrics.
• Explainability — Are retrieval scores or confidence shown? Status: Partial. Evidence: rag_pipeline.py returns distance in chunks but UI does not show it; no confidence for the answer.

5. Improvement Priorities (3–5) with Time Estimates

Priority 1: Add a Minimal Test Suite and Run It in CI

• Why (finance): Tests reduce regression risk and support safe changes when adapting the pipeline for new products or regulators. CI gives a clear green/red signal for every change.
• What: (1) Add tests/ with pytest: unit tests for filter_products, apply_text_cleaning, chunk_text, and format_context (and optionally a small integration test that mocks ChromaDB and checks RAGPipeline.query returns answer and chunks). (2) Add a GitHub Actions workflow that runs pip install -r requirements.txt and pytest tests/ on push/PR.
• Time: 4–6 hours.
• Portfolio impact: Demonstrates engineering discipline and aligns with production-ready expectations.

Priority 2: Externalise Config and Fix Preprocessing Default

• Why (finance): Reproducibility and auditability require a single place for data paths, seeds, and model names. Correct default behaviour avoids accidental partial runs in production-like use.
• What: (1) Introduce a small config (e.g. config.yaml or config.py) for paths (raw_data, processed_data, vector_store), seed, sample_size, embedding_model, collection_name, and optionally llm_model. (2) Load this in preprocess_pipeline.py, task2_pipeline.py, and rag_pipeline.py. (3) Change preprocess_pipeline.py __main__ to run_pipeline(sample_for_eda=False) and document the EDA flag.
• Time: 2–3 hours.
• Portfolio impact: Clear single source of truth for reproducibility and future compliance documentation.

Priority 3: Add One Quantitative Evaluation Metric and Report It

• Why (finance): A single repeatable metric (e.g. retrieval relevance or answer faithfulness) gives a baseline for no regression and supports credibility with stakeholders.
• What: (1) In evaluation.py, add a simple metric: e.g. for each test question, compute mean similarity score (or reciprocal rank) of the top-k retrieved chunks from ChromaDB (scores already returned in results distances). (2) Append a short Evaluation summary to evaluation_results.md (e.g. average distance or MRR). (3) Optionally add a second metric (e.g. keyword overlap between question and retrieved text) and document what each measures.
• Time: 3–4 hours.
• Portfolio impact: Moves from qualitative only to measured quality, which is expected in serious ML projects.

Priority 4: Expose Retrieval Scores in the UI and Add a Short How to Read This Note

• Why (finance): Showing why an answer is trusted (e.g. high vs low similarity) supports interpretability and aligns with explainability expectations in regulated contexts.
• What: (1) In app.py, when formatting sources, include the distance/similarity from each chunk (e.g. Score: 0.82). (2) Add one or two sentences in the UI: Lower distance = more similar to your question. Use this to gauge how strongly the answer is supported.
• Time: 1–2 hours.
• Portfolio impact: Strengthens the auditable and explainable story without large refactors.

Priority 5: Document Environment and One-Click Run

• Why (finance): Reproducibility and handover to compliance or other teams require a clear, repeatable setup.
• What: (1) Add a short Environment section to README: Python version, optional venv, pip install -r requirements.txt, and any env vars (if introduced in Priority 2). (2) Add a single Full pipeline section: commands to run Task 1 (with sample_for_eda=False), Task 2, then python app.py, in order, with expected outputs. (3) Optionally add a scripts/run_all.sh (or .bat) that runs these in sequence.
• Time: 1–2 hours.
• Portfolio impact: Makes the project easy to run and judge for reviewers and assessors.

6. Detailed Day-by-Day Plan (7 Days)

• Day 1 — Focus: Tests and CI. Tasks: Add tests/ directory and pytest; unit tests for filter_products, apply_text_cleaning, chunk_text, format_context. Run pytest locally and fix failures. Hours: 3–4. Deliverables: tests/test_*.py, all tests passing locally.
• Day 2 — Focus: Tests and CI. Tasks: Add one integration test (mock or in-memory ChromaDB) for RAGPipeline.query. Create .github/workflows/ci.yml to run pytest tests/ on push/PR. Fix CI (deps, paths) until green. Hours: 3–4. Deliverables: Green CI; integration test in repo.
• Day 3 — Focus: Config and preprocessing. Tasks: Introduce config.yaml or config.py with paths, seed, sample_size, model names. Refactor preprocess_pipeline.py, task2_pipeline.py, and rag_pipeline.py to use it. Set sample_for_eda=False by default and document. Hours: 3–4. Deliverables: Single config used across pipeline; README note on EDA flag.
• Day 4 — Focus: Evaluation metric. Tasks: In evaluation.py, compute mean retrieval distance (or MRR) over the 10 questions; write Evaluation summary (e.g. average score) to evaluation_results.md. Document metric in README or report. Hours: 2–3. Deliverables: Updated evaluation_results.md with numeric summary; short doc of the metric.
• Day 5 — Focus: Explainability in UI. Tasks: Pass distance/similarity from rag_pipeline to Gradio; show per-source score in the sources panel. Add brief How to read this text in the UI. Hours: 1–2. Deliverables: UI shows retrieval scores and short explanation.
• Day 6 — Focus: Documentation and runbook. Tasks: Update README: Environment (Python, venv, install), Full pipeline (Task 1 to Task 2 to app.py) with exact commands and expected outputs. Add scripts/run_all.sh or .bat if time allows. Hours: 2–3. Deliverables: README sections; optional scripts/run_all.
• Day 7 — Focus: Buffer and polish. Tasks: Re-run full pipeline with config; re-run evaluation and confirm metric in report; fix any CI or test flakiness; proofread README and this submission. Hours: 2–3. Deliverables: Clean run; stable CI; submission ready.

Total estimated effort: approximately 18–23 hours over 7 days (realistic for a week with other commitments).

Document generated for 10 Academy Week 12 Interim Submission. It describes the original project, gaps, work completed this interim period (with evidence and planned vs actual), and the plan for the coming week. File references and evidence paths are from the current state of the repo.
