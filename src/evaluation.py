"""
RAG Pipeline Evaluation Script
Task 3: Qualitative and quantitative evaluation of the RAG system
"""
import sys
from pathlib import Path
from typing import List, Dict
import pandas as pd

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
    Computes mean retrieval distance (lower = more similar) and appends an Evaluation summary.
    """
    print("Initializing RAG pipeline...")
    rag = create_rag_pipeline(
        vector_store_path=vector_store_path,
        collection_name=collection_name
    )

    results = []
    all_distances = []

    print(f"\nEvaluating {len(test_questions)} questions...")
    print("=" * 80)

    for i, question in enumerate(test_questions, 1):
        print(f"\n[{i}/{len(test_questions)}] Question: {question}")
        print("-" * 80)

        answer, chunks = rag.query(question)

        distances = []
        if chunks:
            for ch in chunks:
                d = ch.get("distance")
                if d is not None:
                    distances.append(float(d))
        if distances:
            all_distances.extend(distances)

        print(f"Answer: {answer[:200]}..." if len(answer) > 200 else f"Answer: {answer}")
        print(f"\nRetrieved {len(chunks)} chunks")

        sources_text = []
        for j, chunk in enumerate(chunks[:2], 1):
            metadata = chunk.get('metadata', {})
            product = metadata.get('product', 'Unknown')
            issue = metadata.get('issue', 'Unknown')
            text_preview = chunk.get('text', '')[:150] + "..." if len(chunk.get('text', '')) > 150 else chunk.get('text', '')
            dist = chunk.get('distance')
            dist_str = f" (distance: {dist:.4f})" if dist is not None else ""
            sources_text.append(f"Source {j}: [{product}] {issue}{dist_str}\n{text_preview}")

        result = {
            'Question': question,
            'Generated Answer': answer,
            'Retrieved Sources': '\n\n'.join(sources_text),
            'Number of Sources': len(chunks),
            'Mean Distance': sum(distances) / len(distances) if distances else None,
            'Quality Score': None,
            'Comments': None
        }
        results.append(result)
        print("\n" + "=" * 80)

    df = pd.DataFrame(results)

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    markdown_content = "# RAG Pipeline Evaluation Results\n\n"
    markdown_content += "## Evaluation Table\n\n"
    markdown_content += "| Question | Generated Answer | Retrieved Sources | Mean Distance | Quality Score | Comments/Analysis |\n"
    markdown_content += "|----------|-------------------|-------------------|---------------|---------------|-------------------|\n"

    for _, row in df.iterrows():
        question = row['Question'].replace('|', '\\|')
        answer = row['Generated Answer'][:200].replace('|', '\\|') + "..." if len(row['Generated Answer']) > 200 else row['Generated Answer'].replace('|', '\\|')
        sources = row['Retrieved Sources'].replace('|', '\\|').replace('\n', '<br>')
        mean_d = row['Mean Distance']
        mean_d_str = f"{mean_d:.4f}" if pd.notna(mean_d) else "N/A"
        score = row['Quality Score'] if pd.notna(row['Quality Score']) else "TBD"
        comments = row['Comments'] if pd.notna(row['Comments']) else "TBD"
        markdown_content += f"| {question} | {answer} | {sources} | {mean_d_str} | {score} | {comments} |\n"

    mean_overall = sum(all_distances) / len(all_distances) if all_distances else None
    markdown_content += "\n## Evaluation Summary (Quantitative)\n\n"
    markdown_content += "- **Metric**: Mean retrieval distance (L2) over all retrieved chunks. Lower = more similar to the query.\n"
    markdown_content += f"- **Mean distance (all questions)**: {mean_overall:.4f}\n" if mean_overall is not None else "- **Mean distance (all questions)**: N/A (no retrievals)\n"
    markdown_content += "- **Number of test questions**: " + str(len(test_questions)) + "\n"

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    print(f"\n✓ Evaluation complete! Results saved to {output_file}")
    if mean_overall is not None:
        print(f"✓ Mean retrieval distance (all): {mean_overall:.4f}")
    print("✓ Please review the results and fill in Quality Scores (1-5) and Comments")

    return df


def get_default_test_questions() -> List[str]:
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
    try:
        from config.load_config import load_config, get_project_root
        cfg = load_config()
        root = get_project_root()
        paths = cfg.get("paths", {})
        vector_store_path = str(root / paths.get("vector_store", "vector_store"))
        output_file = str(root / paths.get("evaluation_output", "output/evaluation_results.md"))
        collection_name = cfg.get("rag", {}).get("collection_name", "complaints")
    except Exception:
        vector_store_path = "vector_store"
        output_file = "output/evaluation_results.md"
        collection_name = "complaints"

    test_questions = get_default_test_questions()
    results_df = evaluate_rag_pipeline(
        test_questions=test_questions,
        vector_store_path=vector_store_path,
        collection_name=collection_name,
        output_file=output_file
    )
    print("\nEvaluation DataFrame:")
    cols = [c for c in ['Question', 'Generated Answer', 'Number of Sources', 'Mean Distance'] if c in results_df.columns]
    print(results_df[cols].to_string())
