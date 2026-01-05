"""
RAG Pipeline Evaluation Script
Task 3: Qualitative evaluation of the RAG system
"""
import sys
from pathlib import Path
from typing import List, Dict
import pandas as pd

# Project path
script_path = Path(__file__).resolve()
project_root = script_path.parent.parent
sys.path.append(str(project_root))

from src.rag_pipeline import create_rag_pipeline

def evaluate_rag_pipeline(
    test_questions: List[str],
    vector_store_path: str = "vector_store",
    collection_name: str = "complaints",
    output_file: str = "output/evaluation_results.md"
) -> pd.DataFrame:
    """
    Evaluate the RAG pipeline with a set of test questions.
    
    Args:
        test_questions: List of test questions to evaluate
        vector_store_path: Path to vector store
        collection_name: Collection name
        output_file: Path to save evaluation results
        
    Returns:
        DataFrame with evaluation results
    """
    print("Initializing RAG pipeline...")
    rag = create_rag_pipeline(
        vector_store_path=vector_store_path,
        collection_name=collection_name
    )
    
    results = []
    
    print(f"\nEvaluating {len(test_questions)} questions...")
    print("=" * 80)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n[{i}/{len(test_questions)}] Question: {question}")
        print("-" * 80)
        
        # Query the RAG pipeline
        answer, chunks = rag.query(question)
        
        # Display results
        print(f"Answer: {answer[:200]}..." if len(answer) > 200 else f"Answer: {answer}")
        print(f"\nRetrieved {len(chunks)} chunks")
        
        # Show top 2 sources
        sources_text = []
        for j, chunk in enumerate(chunks[:2], 1):
            metadata = chunk.get('metadata', {})
            product = metadata.get('product', 'Unknown')
            issue = metadata.get('issue', 'Unknown')
            text_preview = chunk.get('text', '')[:150] + "..." if len(chunk.get('text', '')) > 150 else chunk.get('text', '')
            sources_text.append(f"Source {j}: [{product}] {issue}\n{text_preview}")
        
        # Store result
        result = {
            'Question': question,
            'Generated Answer': answer,
            'Retrieved Sources': '\n\n'.join(sources_text),
            'Number of Sources': len(chunks),
            'Quality Score': None,  # You'll fill this manually
            'Comments': None  # You'll fill this manually
        }
        results.append(result)
        
        print("\n" + "=" * 80)
    
    # Create DataFrame
    df = pd.DataFrame(results)
    
    # Save to markdown file
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create markdown table
    markdown_content = "# RAG Pipeline Evaluation Results\n\n"
    markdown_content += "## Evaluation Table\n\n"
    markdown_content += "| Question | Generated Answer | Retrieved Sources | Quality Score | Comments/Analysis |\n"
    markdown_content += "|----------|-------------------|-------------------|---------------|-------------------|\n"
    
    for _, row in df.iterrows():
        question = row['Question'].replace('|', '\\|')
        answer = row['Generated Answer'][:200].replace('|', '\\|') + "..." if len(row['Generated Answer']) > 200 else row['Generated Answer'].replace('|', '\\|')
        sources = row['Retrieved Sources'].replace('|', '\\|').replace('\n', '<br>')
        score = row['Quality Score'] if pd.notna(row['Quality Score']) else "TBD"
        comments = row['Comments'] if pd.notna(row['Comments']) else "TBD"
        
        markdown_content += f"| {question} | {answer} | {sources} | {score} | {comments} |\n"
    
    # Save markdown
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"\n✓ Evaluation complete! Results saved to {output_file}")
    print(f"✓ Please review the results and fill in Quality Scores (1-5) and Comments")
    
    return df


def get_default_test_questions() -> List[str]:
    """
    Get default test questions for evaluation.
    You can modify these based on your needs.
    
    Returns:
        List of test questions
    """
    return [
        "Why are people unhappy with Credit Cards?",
        "What are the main issues with Personal Loans?",
        "What problems do customers face with Money Transfers?",
        "What are common complaints about Savings Accounts?",
        "Which product has the most billing disputes?",
        "What are the top customer service issues?",
        "What problems do customers report with account access?",
        "How do complaints differ between Credit Cards and Personal Loans?",
        "What are customers saying about transaction problems?",
        "What are the most frequent complaint types across all products?"
    ]


if __name__ == "__main__":
    # Get test questions
    test_questions = get_default_test_questions()
    
    # You can customize questions here:
    # test_questions = [
    #     "Your custom question 1",
    #     "Your custom question 2",
    #     ...
    # ]
    
    # Run evaluation
    results_df = evaluate_rag_pipeline(
        test_questions=test_questions,
        output_file="output/evaluation_results.md"
    )
    
    print("\nEvaluation DataFrame:")
    print(results_df[['Question', 'Generated Answer', 'Number of Sources']].to_string())

