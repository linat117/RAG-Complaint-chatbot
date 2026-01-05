"""
RAG Pipeline for Complaint Analysis
Task 3: Core retrieval and generation logic

This module provides a simple RAG pipeline that:
1. Retrieves relevant complaint chunks using semantic search
2. Generates answers using an LLM with the retrieved context
"""
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional

# Project path
script_path = Path(__file__).resolve()
project_root = script_path.parent.parent
sys.path.append(str(project_root))

import chromadb
from src.embedding import load_embedding_model
from transformers import pipeline
import torch

class RAGPipeline:
    """
    Retrieval-Augmented Generation pipeline for answering questions about complaints.
    """
    
    def __init__(
        self,
        vector_store_path: str = "vector_store",
        collection_name: str = "complaints",
        embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        llm_model_name: Optional[str] = None,
        top_k: int = 5,
        use_cpu: bool = True
    ):
        """
        Initialize the RAG pipeline.
        
        Args:
            vector_store_path: Path to ChromaDB vector store
            collection_name: Name of the ChromaDB collection
            embedding_model_name: Name of the embedding model (must match Task 2)
            llm_model_name: Name of the LLM for generation. If None, uses GPT-2 as default
            top_k: Number of chunks to retrieve (default: 5)
            use_cpu: Force CPU usage (set False to use GPU if available)
        """
        self.top_k = top_k
        
        # Load embedding model (same as Task 2)
        print("Loading embedding model...")
        self.embedding_model = load_embedding_model()
        
        # Connect to ChromaDB
        print("Connecting to vector store...")
        self.client = chromadb.PersistentClient(path=vector_store_path)
        try:
            self.collection = self.client.get_collection(collection_name)
            print(f"✓ Connected to collection: {collection_name}")
        except Exception as e:
            raise Exception(f"Could not connect to collection '{collection_name}'. Make sure Task 2 has been completed. Error: {e}")
        
        # Load LLM
        if llm_model_name is None:
            # Default to GPT-2 (small, works on CPU)
            llm_model_name = "gpt2"
        
        print(f"Loading LLM: {llm_model_name}...")
        device = -1 if use_cpu else (0 if torch.cuda.is_available() else -1)
        
        try:
            self.llm_pipeline = pipeline(
                "text-generation",
                model=llm_model_name,
                device=device,
                model_kwargs={"dtype": torch.float32 if use_cpu else torch.float16}
            )
            print(f"✓ LLM loaded successfully")
        except Exception as e:
            print(f"Error loading model {llm_model_name}: {e}")
            print("Trying with GPT-2 as fallback...")
            try:
                self.llm_pipeline = pipeline(
                    "text-generation",
                    model="gpt2",
                    device=device
                )
                print("✓ Fallback model (GPT-2) loaded")
            except Exception as e2:
                raise Exception(f"Could not load any LLM. Error: {e2}")
        
        # Prompt template (as specified in the challenge)
        self.prompt_template = """You are a financial analyst assistant for CrediTrust. Your task is to answer questions about customer complaints. Use the following retrieved complaint excerpts to formulate your answer. If the context doesn't contain the answer, state that you don't have enough information.

Context: {context}

Question: {question}

Answer:"""
    
    def retrieve(self, question: str) -> List[Dict]:
        """
        Retrieve relevant complaint chunks for a given question.
        
        Args:
            question: User's question as a string
            
        Returns:
            List of dictionaries containing retrieved chunks with metadata
        """
        # Embed the question using the same model as Task 2
        question_embedding = self.embedding_model.encode(question).tolist()
        
        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[question_embedding],
            n_results=self.top_k
        )
        
        # Format results
        retrieved_chunks = []
        if results['documents'] and len(results['documents'][0]) > 0:
            for i in range(len(results['documents'][0])):
                chunk = {
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {},
                    'id': results['ids'][0][i] if results['ids'] and results['ids'][0] else None,
                    'distance': results['distances'][0][i] if results['distances'] and results['distances'][0] else None
                }
                retrieved_chunks.append(chunk)
        
        return retrieved_chunks
    
    def format_context(self, chunks: List[Dict]) -> str:
        """
        Format retrieved chunks into a context string for the LLM.
        
        Args:
            chunks: List of retrieved chunk dictionaries
            
        Returns:
            Formatted context string
        """
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            metadata = chunk.get('metadata', {})
            product = metadata.get('product', 'Unknown')
            issue = metadata.get('issue', 'Unknown')
            complaint_id = metadata.get('complaint_id', 'Unknown')
            text = chunk.get('text', '')
            
            context_parts.append(
                f"[Complaint {complaint_id}] Product: {product}, Issue: {issue}\n{text}\n"
            )
        
        return "\n".join(context_parts)
    
    def generate(self, question: str, context: str) -> str:
        """
        Generate an answer using the LLM.
        
        Args:
            question: User's question
            context: Formatted context from retrieved chunks
            
        Returns:
            Generated answer
        """
        prompt = self.prompt_template.format(context=context, question=question)
        
        # Generate response
        result = self.llm_pipeline(
            prompt,
            max_length=min(len(prompt.split()) + 150, 1024),  # Limit total length
            num_return_sequences=1,
            temperature=0.7,
            do_sample=True,
            pad_token_id=self.llm_pipeline.tokenizer.eos_token_id
        )
        
        # Extract only the generated part (remove the prompt)
        generated_text = result[0]['generated_text']
        answer = generated_text[len(prompt):].strip()
        
        # Clean up the answer (remove any trailing incomplete sentences)
        if answer:
            # Take first complete sentence or first 200 characters
            sentences = answer.split('.')
            if len(sentences) > 1:
                answer = '. '.join(sentences[:-1]) + '.' if len(sentences[-1].strip()) < 10 else answer
            answer = answer[:500]  # Limit length
        
        return answer if answer else "I couldn't generate a response. Please try rephrasing your question."
    
    def query(self, question: str) -> Tuple[str, List[Dict]]:
        """
        Complete RAG pipeline: retrieve and generate.
        
        Args:
            question: User's question
            
        Returns:
            Tuple of (answer, retrieved_chunks) where:
            - answer: Generated answer string
            - retrieved_chunks: List of retrieved chunk dictionaries with metadata
        """
        # Step 1: Retrieve relevant chunks
        chunks = self.retrieve(question)
        
        if not chunks:
            return "I couldn't find any relevant complaints in the database. Please try rephrasing your question.", []
        
        # Step 2: Format context
        context = self.format_context(chunks)
        
        # Step 3: Generate answer
        answer = self.generate(question, context)
        
        return answer, chunks


def create_rag_pipeline(
    vector_store_path: str = "vector_store",
    collection_name: str = "complaints",
    llm_model: Optional[str] = None
) -> RAGPipeline:
    """
    Factory function to create a RAG pipeline with sensible defaults.
    
    Args:
        vector_store_path: Path to vector store (default: "vector_store")
        collection_name: Collection name (default: "complaints")
        llm_model: LLM model name. If None, uses GPT-2. 
                   Options: "gpt2", "distilgpt2", or any HuggingFace model
        
    Returns:
        Configured RAGPipeline instance
    """
    return RAGPipeline(
        vector_store_path=vector_store_path,
        collection_name=collection_name,
        llm_model_name=llm_model,
        use_cpu=True  # Set to False if you have GPU
    )

