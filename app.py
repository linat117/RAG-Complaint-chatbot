"""
Gradio Interface for RAG Complaint Chatbot
Task 4: Interactive chat interface for non-technical users
"""
import sys
from pathlib import Path

# Project path
script_path = Path(__file__).resolve()
project_root = script_path.parent
sys.path.append(str(project_root))

import gradio as gr
from src.rag_pipeline import create_rag_pipeline

# Initialize RAG pipeline (loads once at startup)
print("Initializing RAG pipeline...")
rag_pipeline = create_rag_pipeline(
    vector_store_path="vector_store",
    collection_name="complaints"
)
print("✓ RAG pipeline ready!")


def format_sources(chunks):
    """Format retrieved chunks for display."""
    if not chunks:
        return "No sources retrieved."
    
    formatted = []
    for i, chunk in enumerate(chunks, 1):
        metadata = chunk.get('metadata', {})
        product = metadata.get('product', 'Unknown')
        issue = metadata.get('issue', 'Unknown')
        complaint_id = metadata.get('complaint_id', 'Unknown')
        company = metadata.get('company', 'Unknown')
        text = chunk.get('text', '')
        
        formatted.append(
            f"**Source {i}:**\n"
            f"- Complaint ID: {complaint_id}\n"
            f"- Product: {product}\n"
            f"- Issue: {issue}\n"
            f"- Company: {company}\n"
            f"- Text: {text[:300]}{'...' if len(text) > 300 else ''}\n"
        )
    
    return "\n---\n".join(formatted)


def chat_with_rag(question, history):
    """
    Process a question through the RAG pipeline and return the answer.
    
    Args:
        question: User's question
        history: Chat history (list of [user_message, bot_message] pairs)
        
    Returns:
        Updated history, sources, and empty question (to clear input)
    """
    if not question or question.strip() == "":
        return history, "Please enter a question.", ""
    
    # Query the RAG pipeline
    answer, chunks = rag_pipeline.query(question)
    
    # Format sources
    sources_text = format_sources(chunks)
    
    # Update history
    history.append([question, answer])
    
    return history, sources_text, ""  # Clear the question input


def clear_chat():
    """Clear the chat history."""
    return [], ""


# Create Gradio interface
with gr.Blocks(title="CrediTrust Complaint Analysis Chatbot") as demo:
    gr.Markdown(
        """
        # 🏦 CrediTrust Complaint Analysis Chatbot
        
        Ask questions about customer complaints across Credit Cards, Personal Loans, Savings Accounts, and Money Transfers.
        
        **Example questions:**
        - "Why are people unhappy with Credit Cards?"
        - "What are the main issues with Personal Loans?"
        - "What problems do customers face with Money Transfers?"
        """
    )
    
    with gr.Row():
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(
                label="Conversation",
                height=400
            )
            
            with gr.Row():
                question_input = gr.Textbox(
                    label="Ask a question",
                    placeholder="e.g., Why are people unhappy with Credit Cards?",
                    scale=4
                )
                submit_btn = gr.Button("Ask", variant="primary", scale=1)
            
            with gr.Row():
                clear_btn = gr.Button("Clear Chat", variant="secondary")
        
        with gr.Column(scale=1):
            gr.Markdown("### 📚 Retrieved Sources")
            sources_display = gr.Textbox(
                label="Sources used for the answer",
                lines=15,
                max_lines=20,
                interactive=False
            )
    
    # Event handlers
    submit_btn.click(
        fn=chat_with_rag,
        inputs=[question_input, chatbot],
        outputs=[chatbot, sources_display, question_input]
    )
    
    question_input.submit(
        fn=chat_with_rag,
        inputs=[question_input, chatbot],
        outputs=[chatbot, sources_display, question_input]
    )
    
    clear_btn.click(
        fn=clear_chat,
        outputs=[chatbot, sources_display]
    )
    
    gr.Markdown(
        """
        ---
        **Note:** This chatbot uses Retrieval-Augmented Generation (RAG) to answer questions based on real customer complaint data.
        The sources shown below each answer are the actual complaint excerpts used to generate the response.
        """
    )


if __name__ == "__main__":
    # Launch the interface
    # Change the port here if 7860 doesn't work (e.g., 8080, 5000, 3000)
    PORT = 7860
    
    print(f"\n🚀 Launching Gradio interface...")
    print(f"📱 Open your browser to: http://localhost:{PORT}")
    print(f"   (If port {PORT} is busy, change PORT in app.py)\n")
    
    try:
        demo.launch(
            server_name="127.0.0.1",  # Use localhost (safer than 0.0.0.0)
            server_port=PORT,
            share=False,  # Set to True to create a public link
            theme=gr.themes.Soft()  # Theme moved here for Gradio 6.0+
        )
    except OSError as e:
        if "Address already in use" in str(e) or "port" in str(e).lower():
            print(f"\n❌ Error: Port {PORT} is already in use!")
            print(f"💡 Solution: Change PORT = {PORT} to a different number (e.g., 8080) in app.py")
            print(f"   Or close the program using port {PORT}\n")
        else:
            raise

