RAG Complaint Chatbot - Final Interim Report

Executive Summary

This report presents the implementation progress of a Retrieval-Augmented Generation (RAG) system for processing and querying consumer financial complaints from the CFPB (Consumer Financial Protection Bureau) dataset. The project implements a complete pipeline from raw complaint data to an interactive chatbot interface, focusing on four key product categories: Credit Cards, Personal Loans, Savings Accounts, and Money Transfers.

The system successfully processes large-scale complaint data, builds a semantic searchable vector database, implements a RAG pipeline for answer generation, and provides an interactive web interface for non-technical users. All four core tasks have been completed and integrated into a functional end-to-end system.

================================================================================

Task 1: Data Preprocessing Pipeline

Overview
The first task focused on building a robust data preprocessing pipeline to clean and filter raw consumer complaint data. The implementation prioritizes memory efficiency and data quality to handle large-scale datasets effectively.

Implementation Details

1.1 Memory-Efficient Data Loading
Approach: Implemented chunked CSV reading using pandas chunksize parameter
Benefits: Enables processing of datasets larger than available RAM
Implementation: The load_data() function processes data in configurable chunks, using iterator-based streaming to minimize memory footprint

1.2 Product Filtering
Scope: Focused on four key product categories:
  - Credit card
  - Personal loan
  - Savings account
  - Money transfers
Method: Filtered complaints based on exact product name matching to ensure data quality and relevance

1.3 Quality Control
Empty Narrative Removal: Eliminated complaints with missing or empty Consumer complaint narrative fields
Data Validation: Ensured only complaints with meaningful text content are processed

1.4 Text Cleaning Pipeline
The text cleaning module applies multiple preprocessing steps:
Lowercase Normalization: Standardizes text to lowercase for consistent processing
Boilerplate Removal: Removes common complaint filing phrases (e.g., "I am writing to file a complaint")
Special Character Handling: Removes special characters while preserving essential punctuation
Whitespace Normalization: Cleans up excessive whitespace and line breaks

Key Technical Choices
Chunked Processing: Essential for handling large datasets without memory constraints
Modular Design: Separate modules for loading, filtering, and cleaning enable maintainability and testing
Quality-First Approach: Prioritizes data quality over quantity by removing empty or low-quality entries

Output
File: data/processed/filtered_complaints.csv
Result: Cleaned and filtered dataset ready for further processing

Pipeline Script
The preprocessing pipeline (src/preprocess_pipeline.py) orchestrates all components:
1. Load data in chunks
2. Filter by product categories
3. Remove empty narratives
4. Apply text cleaning
5. Save processed data

================================================================================

Task 2: Vector Database Indexing

Overview
Task 2 builds a semantic searchable vector database by implementing stratified sampling, text chunking, embedding generation, and vector indexing using ChromaDB.

Implementation Details

2.1 Stratified Sampling
Purpose: Create a representative sample while maintaining original data distribution
Method: Proportional sampling based on product category frequency
Target Size: 12,000 complaints (configurable)
Reproducibility: Uses random seed (42) for consistent results
Benefit: Maintains statistical properties of the full dataset while reducing computational requirements

2.2 Text Chunking Strategy
Approach: Recursive Character Text Splitter from LangChain
Hierarchical Separators:
  - Primary: Paragraph breaks (\n\n)
  - Secondary: Line breaks (\n)
  - Tertiary: Word boundaries ( )
Chunk Size: 500 characters per chunk
Overlap: 50 characters between chunks to preserve context at boundaries
Rationale: Balances context preservation with retrieval granularity, optimized for RAG workflows

2.3 Semantic Embeddings
Model: all-MiniLM-L6-v2 from Sentence Transformers (HuggingFace)
Dimensions: 384-dimensional dense vector representations
Benefits: 
  - Fast inference suitable for batch processing
  - Good balance between quality and speed
  - Enables semantic similarity search (meaning-based rather than keyword-based)

2.4 Vector Database (ChromaDB)
Storage Type: Persistent local storage using ChromaDB's PersistentClient
API: Modern PersistentClient API (v1.4.0+), replacing deprecated Settings
Metadata Storage: Rich metadata stored alongside embeddings:
  - Complaint ID
  - Product category
  - Company name
  - Issue type
  - Chunk index and total chunks
Collection Management: Organized collection named "complaints" for easy retrieval

Key Technical Choices
Stratified Sampling: Ensures balanced representation across product categories
Recursive Text Splitting: Preserves document structure better than fixed-size splitting
50-Character Overlap: Prevents context loss at chunk boundaries
Metadata Preservation: Enables filtering and better context understanding
Persistent Storage: Allows reuse of vector store without regeneration

Output
Vector Store: vector_store/ directory (ChromaDB persistent storage)
Sample Data: data/processed/sample_complaints.csv (12,000 complaints)
Result: Fully indexed, searchable vector database ready for semantic retrieval

Pipeline Script
The Task 2 pipeline (src/task2_pipeline.py) executes:
1. Load cleaned dataset
2. Create stratified sample
3. Initialize ChromaDB collection
4. For each complaint:
   - Chunk text
   - Generate embeddings
   - Index with metadata
5. Persist vector store

================================================================================

Task 3: RAG Pipeline Implementation

Overview
Task 3 implements a complete Retrieval-Augmented Generation pipeline that combines semantic search with LLM-based answer generation to provide contextual answers about consumer complaints.

Implementation Details

3.1 RAG Architecture
The RAG pipeline follows a three-stage process:
1. Retrieval: Semantic search in the vector database
2. Context Formatting: Aggregation of retrieved chunks with metadata
3. Generation: LLM-based answer synthesis

3.2 Retrieval Component
Embedding Model: Uses the same all-MiniLM-L6-v2 model as Task 2 for consistency
Search Method: ChromaDB semantic similarity search
Retrieval Parameters: 
  - Default top_k = 5 chunks per query
  - Returns chunks with metadata and similarity scores
Process: Questions are embedded and matched against indexed complaint chunks

3.3 Context Formatting
Metadata Integration: Formats retrieved chunks with complaint context:
  - Complaint ID
  - Product category
  - Issue type
  - Original complaint text
Structured Format: Presents context in a readable format for the LLM

3.4 Answer Generation
LLM Model: GPT-2 (default, lightweight and CPU-friendly)
Framework: HuggingFace Transformers pipeline
Prompt Engineering: Custom prompt template designed for financial analysis:

You are a financial analyst assistant for CrediTrust. 
Your task is to answer questions about customer complaints. 
Use the following retrieved complaint excerpts to formulate your answer. 
If the context doesn't contain the answer, state that you don't have enough information.

Context: {context}
Question: {question}
Answer:

Generation Parameters:
  - Temperature: 0.7 (balanced creativity/consistency)
  - Max length: Dynamic based on prompt length
  - Sampling: Enabled for diverse responses

3.5 Evaluation Framework
Evaluation Script: src/evaluation.py provides systematic testing
Test Questions: 10 predefined questions covering:
  - Product-specific queries
  - Cross-product comparisons
  - Issue type analysis
  - General complaint patterns
Output Format: Markdown table with:
  - Questions
  - Generated answers
  - Retrieved sources
  - Quality scores (for manual assessment)
  - Comments/analysis

Key Technical Choices
RAG Architecture: Combines semantic search with LLM generation for grounded, context-aware answers
Same Embedding Model: Ensures consistency between indexing and retrieval
GPT-2 Default: Lightweight model suitable for CPU-only environments
Flexible Model Support: Architecture allows swapping to other HuggingFace models
Source Transparency: Returns retrieved chunks for verification and trust

Output
RAG Pipeline Class: RAGPipeline in src/rag_pipeline.py
Evaluation Results: output/evaluation_results.md
Factory Function: create_rag_pipeline() for easy instantiation
Result: Functional RAG system capable of answering questions about complaints

Pipeline Workflow
1. Initialize RAG pipeline (load models, connect to vector store)
2. User asks question
3. Embed question using embedding model
4. Retrieve top_k relevant chunks from ChromaDB
5. Format chunks with metadata into context
6. Generate answer using LLM with context
7. Return answer and source chunks

================================================================================

Task 4: Interactive Web Interface

Overview
Task 4 provides a user-friendly Gradio web interface that enables non-technical users to interact with the RAG system through an intuitive chat interface.

Implementation Details

4.1 User Interface Design
Framework: Gradio (modern, easy-to-deploy web framework)
Layout: Two-column design:
  - Left Column: Chat interface with conversation history
  - Right Column: Source citation display
Components:
  - Chatbot display with conversation history
  - Text input for questions
  - Submit button
  - Clear chat functionality
  - Source display panel

4.2 Interface Features
Real-Time Interaction: Instant question-answering with visual feedback
Conversation History: Maintains context across multiple questions
Source Citation: Displays retrieved complaint chunks with metadata:
  - Complaint ID
  - Product category
  - Issue type
  - Company name
  - Text preview (300 characters)
User-Friendly Design: 
  - Clear instructions and example questions
  - Intuitive layout
  - Professional styling (Gradio Soft theme)

4.3 Technical Implementation
Initialization: RAG pipeline loaded once at startup (efficient resource usage)
Event Handlers: 
  - Submit button click
  - Enter key press
  - Clear chat button
Error Handling: Graceful handling of empty inputs and errors
Input Clearing: Automatic clearing of question input after submission

4.4 Deployment Configuration
Server: Localhost (127.0.0.1) for security
Port: 7860 (configurable)
Share Option: Disabled by default (can be enabled for public links)
Theme: Soft theme for professional appearance

Key Technical Choices
Gradio Framework: Rapid prototyping and deployment without complex web development
Source Transparency: Displays retrieved sources to build user trust
Persistent Pipeline: Loads RAG pipeline once for efficiency
Local Deployment: Secure local deployment suitable for internal use

Output
Application: app.py (standalone Gradio application)
Result: Fully functional web interface accessible at http://localhost:7860

Usage Workflow
1. Launch application: python app.py
2. Open browser to http://localhost:7860
3. User enters question in text input
4. System retrieves relevant complaints and generates answer
5. Answer displayed in chat, sources shown in side panel
6. User can continue conversation or clear chat

================================================================================

System Integration and Workflow

End-to-End Pipeline
The complete system integrates all four tasks into a cohesive workflow:

Raw Data → Task 1 (Preprocessing) → Cleaned Data
                                ↓
                       Task 2 (Indexing) → Vector Store
                                ↓
                       Task 3 (RAG Pipeline) → Answer Generation
                                ↓
                       Task 4 (Web Interface) → User Interaction

Data Flow
1. Input: Raw CFPB complaint data (data/raw/complaints.csv)
2. Task 1 Output: Cleaned, filtered complaints (data/processed/filtered_complaints.csv)
3. Task 2 Output: Vector database (vector_store/) and sample data
4. Task 3 Output: RAG pipeline module and evaluation results
5. Task 4 Output: Interactive web interface

Dependencies
Python 3.x: Core language
Pandas: Data manipulation
Sentence Transformers: Embedding generation
ChromaDB: Vector database
LangChain: Text splitting utilities
Transformers: LLM framework
Gradio: Web interface
Torch: Deep learning backend

================================================================================

Key Design Decisions and Rationale

1. Memory Efficiency (Task 1)
Decision: Chunked data loading instead of loading entire dataset
Rationale: Enables processing of large datasets on machines with limited RAM

2. Stratified Sampling (Task 2)
Decision: Proportional sampling maintaining product distribution
Rationale: Preserves dataset characteristics while reducing computational cost

3. Recursive Text Splitting (Task 2)
Decision: Hierarchical separators with overlap
Rationale: Better preserves document structure and context compared to fixed-size splitting

4. Lightweight Embedding Model (Task 2)
Decision: all-MiniLM-L6-v2 instead of larger models
Rationale: Good balance between quality and speed, suitable for CPU environments

5. RAG Architecture (Task 3)
Decision: Retrieval-Augmented Generation over pure LLM
Rationale: Provides grounded answers with source citations, reducing hallucination

6. GPT-2 Default (Task 3)
Decision: GPT-2 as default LLM
Rationale: Lightweight, CPU-friendly, sufficient for proof-of-concept

7. Source Transparency (Tasks 3 & 4)
Decision: Display retrieved sources to users
Rationale: Builds trust, enables verification, and improves interpretability

8. Gradio Interface (Task 4)
Decision: Gradio over custom web framework
Rationale: Rapid development, easy deployment, sufficient for interactive prototype

================================================================================

Challenges and Solutions

Challenge 1: Memory Constraints
Problem: Large complaint dataset cannot fit in memory
Solution: Implemented chunked processing with pandas iterator

Challenge 2: Data Quality
Problem: Many complaints have empty narratives or poor formatting
Solution: Multi-stage filtering and cleaning pipeline

Challenge 3: Balanced Sampling
Problem: Maintaining product distribution in sample
Solution: Stratified sampling with proportional allocation

Challenge 4: Context Preservation
Problem: Text chunking can lose context at boundaries
Solution: 50-character overlap between chunks

Challenge 5: LLM Resource Requirements
Problem: Large LLMs require GPU and significant resources
Solution: Use lightweight GPT-2 with CPU support, architecture allows model swapping

Challenge 6: User Experience
Problem: Making technical system accessible to non-technical users
Solution: Gradio interface with clear UI and source citations

================================================================================

Evaluation and Testing

Task 3 Evaluation
The RAG pipeline has been evaluated with 10 test questions covering:
- Product-specific queries (Credit Cards, Personal Loans, Money Transfers, Savings Accounts)
- Cross-product comparisons
- Issue type analysis
- General complaint patterns

Evaluation results are stored in output/evaluation_results.md and include:
- Generated answers for each question
- Retrieved source complaints
- Quality assessment framework (for manual scoring)
- Analysis comments

System Testing
Task 1: Verified data quality and filtering effectiveness
Task 2: Validated vector store indexing and retrieval accuracy
Task 3: Tested RAG pipeline with diverse questions
Task 4: User interface tested for usability and functionality

================================================================================

Future Improvements and Extensions

Potential Enhancements
1. Advanced LLM Models: Integration with larger models (GPT-3.5, GPT-4, Llama) for improved answer quality
2. Re-ranking: Implement re-ranking of retrieved chunks for better relevance
3. Hybrid Search: Combine semantic and keyword-based search
4. Multi-turn Conversations: Enhanced context management for follow-up questions
5. Fine-tuning: Fine-tune embedding model on complaint domain data
6. Analytics: Add usage analytics and performance metrics
7. Deployment: Containerization and cloud deployment options
8. Authentication: User authentication and access control
9. Export Features: Export conversations and analysis results
10. Multi-language Support: Extend to handle complaints in multiple languages

================================================================================

Conclusion

This project successfully implements a complete RAG-based complaint analysis system covering all four core tasks:

1. Task 1: Robust data preprocessing pipeline with memory-efficient processing
2. Task 2: Semantic vector database with stratified sampling and intelligent chunking
3. Task 3: Functional RAG pipeline with retrieval and generation capabilities
4. Task 4: User-friendly web interface for interactive complaint analysis

The system demonstrates effective integration of modern NLP techniques (embeddings, vector databases, RAG) to create a practical tool for analyzing consumer financial complaints. All components work together seamlessly, providing an end-to-end solution from raw data to interactive querying.

The modular architecture enables easy maintenance, testing, and future enhancements. The system is production-ready for internal use and can be extended with additional features as needed.

================================================================================

Appendix: File Structure

rag-complaint-chatbot/
  data/
    raw/
      complaints.csv
    processed/
      filtered_complaints.csv
      sample_complaints.csv
  src/
    load_data.py              (Task 1: Data loading)
    filtering.py              (Task 1: Product filtering)
    text_cleaning.py          (Task 1: Text preprocessing)
    sampling.py               (Task 2: Stratified sampling)
    chunking.py               (Task 2: Text chunking)
    embedding.py              (Task 2: Embedding model)
    index_builder.py          (Task 2: ChromaDB utilities)
    preprocess_pipeline.py    (Task 1: Main pipeline)
    task2_pipeline.py         (Task 2: Main pipeline)
    rag_pipeline.py           (Task 3: RAG implementation)
    evaluation.py             (Task 3: Evaluation script)
  app.py                      (Task 4: Gradio interface)
  vector_store/               (Task 2: ChromaDB storage)
  output/
    evaluation_results.md     (Task 3: Evaluation results)
  report.md                   (This document)
  README.md                   (Project documentation)

================================================================================

Report generated: Final Interim Report
Project: RAG Complaint Chatbot
Status: All four tasks completed and integrated
