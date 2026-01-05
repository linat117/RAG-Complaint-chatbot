# Task 3 & Task 4 Implementation Guide

This guide explains how to use the new files created for Task 3 (RAG Pipeline) and Task 4 (Interactive UI) **without modifying your existing Task 1 and Task 2 code**.

## 📁 New Files Created

1. **`src/rag_pipeline.py`** - Core RAG logic (retrieval + generation)
2. **`src/evaluation.py`** - Evaluation script for Task 3
3. **`app.py`** - Gradio interface for Task 4
4. **`requirements.txt`** - Updated with Gradio dependency

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
pip install gradio
```

Or reinstall all requirements:
```bash
pip install -r requirements.txt
```

### Step 2: Run Task 3 Evaluation

Test your RAG pipeline with sample questions:

```bash
python -m src.evaluation
```

This will:
- Load your existing vector store from Task 2
- Test 10 default questions
- Generate answers and show retrieved sources
- Save results to `output/evaluation_results.md`

**Customize test questions:**
Edit `src/evaluation.py` and modify the `get_default_test_questions()` function or pass your own list.

### Step 3: Launch the Gradio UI (Task 4)

```bash
python app.py
```

Then open your browser to `http://localhost:7860`

## 📋 Task 3 Details

### What the RAG Pipeline Does

1. **Retrieval**: Takes your question → embeds it → searches ChromaDB → returns top 5 relevant chunks
2. **Generation**: Formats chunks as context → sends to LLM with prompt → returns answer

### Key Components

- **`RAGPipeline` class**: Main pipeline class
- **`retrieve()`**: Semantic search in ChromaDB
- **`generate()`**: LLM-based answer generation
- **`query()`**: Complete pipeline (retrieve + generate)

### Using the Pre-built Vector Store (Optional)

If you have the `complaint_embeddings.parquet` file from the challenge:

1. You can create a new ChromaDB collection from it
2. Or modify `rag_pipeline.py` to load from parquet directly
3. For now, it uses your existing `vector_store/` from Task 2

### Customizing the LLM

By default, it uses GPT-2 (small, works on CPU). To use a different model:

```python
from src.rag_pipeline import create_rag_pipeline

rag = create_rag_pipeline(
    llm_model="distilgpt2"  # or "microsoft/Phi-3-mini-4k-instruct", etc.
)
```

**Note**: Larger models require more memory. GPT-2 works well for testing.

### Evaluation Results Format

The evaluation script creates a markdown table with:
- Question
- Generated Answer
- Retrieved Sources (top 2 shown)
- Quality Score (1-5) - **You fill this in manually**
- Comments/Analysis - **You fill this in manually**

Open `output/evaluation_results.md` and add your quality scores and comments.

## 📋 Task 4 Details

### Gradio Interface Features

✅ Text input for questions  
✅ Chat history display  
✅ Source display (shows retrieved chunks)  
✅ Clear button  
✅ Copy buttons for easy sharing  

### Running the App

```bash
python app.py
```

The app will:
1. Load your vector store on startup
2. Initialize the RAG pipeline
3. Start a web server on port 7860

### Customization

**Change the port:**
```python
demo.launch(server_port=8080)
```

**Create a public link:**
```python
demo.launch(share=True)
```

**Modify the UI:**
Edit the `app.py` file - it uses Gradio's Blocks API for full customization.

## 🔧 Troubleshooting

### "Could not connect to collection"

**Problem**: Vector store not found or collection doesn't exist.

**Solution**: 
1. Make sure you've run Task 2: `python -m src.task2_pipeline`
2. Check that `vector_store/` directory exists
3. Verify collection name is "complaints"

### "Could not load any LLM"

**Problem**: LLM model download failed or incompatible.

**Solution**:
1. Check internet connection (models download from HuggingFace)
2. Try a smaller model: `llm_model="distilgpt2"`
3. For offline use, download model first: `python -c "from transformers import pipeline; pipeline('text-generation', model='gpt2')"`

### Slow Response Times

**Problem**: LLM generation is slow.

**Solutions**:
1. Use smaller models (GPT-2, DistilGPT-2)
2. Reduce `top_k` in `rag_pipeline.py` (default: 5)
3. Use GPU if available (set `use_cpu=False`)

### Gradio Not Installing

**Problem**: `pip install gradio` fails.

**Solution**:
```bash
pip install --upgrade pip
pip install gradio==4.44.0
```

## 📝 Next Steps

1. **Run Evaluation**: Test with your own questions
2. **Review Results**: Fill in quality scores in the markdown file
3. **Launch UI**: Test the Gradio interface
4. **Take Screenshots**: For your final report
5. **Write Report**: Document your findings

## 🎯 Key Points

- ✅ **No existing code modified** - All new files are separate
- ✅ **Uses your Task 2 vector store** - No need to rebuild
- ✅ **Simple LLM setup** - GPT-2 works out of the box
- ✅ **Full source display** - Shows retrieved chunks for transparency
- ✅ **Easy to customize** - Modify prompts, models, UI as needed

## 📚 Additional Resources

- [Gradio Documentation](https://www.gradio.app/docs)
- [HuggingFace Transformers](https://huggingface.co/docs/transformers)
- [ChromaDB Query API](https://docs.trychroma.com/reference/Collection#query)

---

**Note**: The RAG pipeline uses the same embedding model (`all-MiniLM-L6-v2`) as Task 2, ensuring compatibility with your existing vector store.

