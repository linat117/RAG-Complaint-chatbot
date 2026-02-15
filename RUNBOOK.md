# Runbook: Environment and Full Pipeline

## Environment

- **Python**: 3.10 or 3.11 recommended.
- **Optional**: Create a virtual environment before installing:
  - Windows: `python -m venv venv` then `venv\Scripts\activate`
  - Linux/Mac: `python3 -m venv venv` then `source venv/bin/activate`
- **Install dependencies** (from project root):
  ```bash
  pip install -r requirements.txt
  pip install pytest
  ```
- **Config**: Paths and settings are in `config/config.yaml`. You can change `paths`, `data.seed`, `data.sample_size`, and `rag.collection_name` there.
- **No required env vars** for default runs.

## Full Pipeline (one-time setup and run)

Run from the **project root** in order. Ensure `data/raw/complaints.csv` exists (CFPB complaint data).

### Step 1: Preprocess data (Task 1)

```bash
python -m src.preprocess_pipeline
```

- **Expected**: Logs per chunk, then "Task 1 preprocessing completed successfully."
- **Output**: `data/processed/filtered_complaints.csv`

### Step 2: Build vector index (Task 2)

```bash
python -m src.task2_pipeline
```

- **Expected**: Progress bar over complaints, then "Task 2 completed. Vector store saved in 'vector_store/'."
- **Output**: `vector_store/` (ChromaDB), `data/processed/sample_complaints.csv`

### Step 3: Run evaluation (optional)

```bash
python -m src.evaluation
```

- **Expected**: 10 questions evaluated, mean retrieval distance printed, "Evaluation complete!"
- **Output**: `output/evaluation_results.md` (includes Evaluation Summary with mean distance)

### Step 4: Launch the chatbot UI

```bash
python app.py
```

- **Expected**: "RAG pipeline ready!" then "Launching Gradio interface..."
- **Browser**: Open http://localhost:7860

## Run tests

From project root:

```bash
python -m pytest tests/ -v --tb=short
```

- **Expected**: All tests in `tests/test_filtering.py` and `tests/test_text_cleaning.py` pass.

## CI

GitHub Actions runs tests on push/PR to `main` or `master` (see `.github/workflows/ci.yml`).
