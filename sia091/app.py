
# Gradio web app for asking questions about a PDF or TXT document.

import gradio as gr

from src.answerer import Answerer
from src.chunker import chunk_pages, chunk_layout_items
from src.embedder import Embedder
from src.loader import load_document
from src.loader_layout import load_document_layout
from src.retriever import Retriever


# Load models once when the app starts.
embedder = Embedder()
answerer = Answerer()


def process_document(file_path, chunk_size, overlap, loader_mode):
    # Read the document, create chunks and build the search index.

    if file_path is None:
        return None, "Please upload a PDF or TXT file first."

    try:
        if loader_mode == "Layout-aware Loader":
            pages = load_document_layout(file_path)

            chunks = chunk_layout_items(
                pages,
                int(chunk_size),
                int(overlap)
            )

        else:
            pages = load_document(file_path)

            chunks = chunk_pages(
                pages,
                int(chunk_size),
                int(overlap)
            )

        retriever = Retriever(embedder)
        retriever.build(chunks)

    except (ValueError, FileNotFoundError) as error:
        return None, f"Error: {error}"

    return (
        retriever,
        f"Ready: {len(pages)} page/item(s) "
        f"split into {len(chunks)} chunks using {loader_mode}."
    )


def format_hits(hits):
    # Show each retrieved chunk with its page and similarity score.

    lines = []

    for number, hit in enumerate(hits, start=1):
        preview = hit["text"][:120].replace("\n", " ")

        lines.append(
            f"{number}. page {hit['page']} | "
            f"score {hit['score']:.2f} | {preview}..."
        )

    return "\n".join(lines)


def ask_question(question, retriever, top_k):
    # Retrieve relevant chunks and generate an answer.

    if retriever is None:
        return "Please process a document first.", "", "", ""

    try:
        hits = retriever.search(question, int(top_k))

        result = answerer.answer(question, hits)

    except (ValueError, RuntimeError) as error:
        return f"Error: {error}", "", "", ""

    retrieved = format_hits(hits)

    if result["page"] is None:
        return result["answer"], "", "", retrieved

    source = (
        f"Page {result['page']} | "
        f"confidence {result['score']:.2f}"
    )

    return (
        result["answer"],
        source,
        result["context"],
        retrieved
    )


with gr.Blocks(title="Document Q&A") as demo:

    gr.Markdown(
        "# Document Q&A\n"
        "Upload a PDF or TXT file and ask questions about it."
    )

    # Keep the retriever separately for each user session.
    retriever_state = gr.State(None)

    with gr.Row():

        with gr.Column():

            file_input = gr.File(
                label="Document",
                file_types=[".pdf", ".txt"],
                type="filepath"
            )

            loader_mode = gr.Radio(
                choices=[
                    "Standard Loader",
                    "Layout-aware Loader"
                ],
                value="Standard Loader",
                label="PDF Extraction Method"
            )

            chunk_size = gr.Slider(
                20,
                300,
                value=40,
                step=10,
                label="Chunk size (words)"
            )

            overlap = gr.Slider(
                0,
                100,
                value=10,
                step=5,
                label="Overlap (words)"
            )

            process_button = gr.Button("Process document")

            status = gr.Textbox(
                label="Status",
                interactive=False
            )

        with gr.Column():

            question = gr.Textbox(
                label="Your question",
                placeholder="Ask something about the document"
            )

            top_k = gr.Slider(
                1,
                10,
                value=10,
                step=1,
                label="Chunks to search"
            )

            ask_button = gr.Button(
                "Get answer",
                variant="primary"
            )

            answer = gr.Textbox(
                label="Answer",
                lines=6,
                interactive=False
            )

            source = gr.Textbox(
                label="Source",
                interactive=False
            )

            context = gr.Textbox(
                label="Source text",
                lines=8,
                interactive=False
            )

            retrieved = gr.Textbox(
                label="Retrieved chunks",
                lines=8,
                interactive=False
            )

    process_button.click(
        process_document,
        inputs=[
            file_input,
            chunk_size,
            overlap,
            loader_mode
        ],
        outputs=[
            retriever_state,
            status
        ]
    )

    ask_button.click(
        ask_question,
        inputs=[
            question,
            retriever_state,
            top_k
        ],
        outputs=[
            answer,
            source,
            context,
            retrieved
        ]
    )


if __name__ == "__main__":
    demo.launch()
