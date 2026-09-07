import os
from pathlib import Path
from typing import TypedDict, List

from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langgraph.graph import StateGraph, END


BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "docs"
CHROMA_DIR = BASE_DIR / "chroma_db"

MOCK_LLM = os.getenv("MOCK_LLM", "0") == "1"


class GraphState(TypedDict, total=False):
    question: str
    intent: str
    context: str
    sources: List[str]
    answer: str
    confidence: float


def load_documents() -> List[Document]:
    documents = []

    for path in sorted(DOCS_DIR.glob("*.txt")):
        text = path.read_text(encoding="utf-8").strip()

        if text:
            documents.append(
                Document(
                    page_content=text,
                    metadata={"source": path.name}
                )
            )

    return documents


def get_vector_store() -> Chroma:
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    documents = load_documents()

    vector_store = Chroma(
        collection_name="zepto_support",
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR),
    )

    existing = vector_store.get()

    if not existing["ids"]:
        vector_store.add_documents(documents)

    return vector_store


VECTOR_STORE = get_vector_store()


def classify_intent(state: GraphState) -> GraphState:
    question = state["question"].lower()

    policy_keywords = [
        "delivery",
        "return",
        "refund",
        "membership",
        "tracking",
        "cancel",
        "cancellation",
        "gift card",
        "support",
        "delivery fee",
        "payment",
    ]

    if any(keyword in question for keyword in policy_keywords):
        intent = "policy_question"
    else:
        intent = "general_question"

    return {
        **state,
        "intent": intent,
    }


def retrieve_and_answer(state: GraphState) -> GraphState:
    question = state["question"]

    results = VECTOR_STORE.similarity_search_with_score(
        question,
        k=3
    )

    context_parts = []
    sources = []

    for document, score in results:
        context_parts.append(document.page_content)
        source = document.metadata.get("source", "unknown")

        if source not in sources:
            sources.append(source)

    context = "\n\n".join(context_parts)

    if MOCK_LLM:
        if results:
            answer = (
                "Based on the retrieved context: "
                + results[0][0].page_content
            )
        else:
            answer = "No relevant information was found in the support documents."

        confidence = 0.90 if results else 0.20

    else:
        # Real-LLM integration point.
        # The required pipeline remains functional in mock mode.
        answer = (
            "Retrieved support information:\n\n"
            + context
        )
        confidence = 0.75 if results else 0.20

    return {
        **state,
        "context": context,
        "sources": sources,
        "answer": answer,
        "confidence": confidence,
    }


def direct_answer(state: GraphState) -> GraphState:
    if MOCK_LLM:
        answer = (
            "I can help with Zepto support questions. "
            "Please ask about delivery, returns, refunds, membership, "
            "tracking, cancellation, payment, or another supported topic."
        )
        confidence = 0.85
    else:
        answer = (
            "I can help answer your question, but it does not match "
            "the available Zepto support policy topics."
        )
        confidence = 0.60

    return {
        **state,
        "sources": [],
        "answer": answer,
        "confidence": confidence,
    }


def route_after_classification(state: GraphState) -> str:
    if state.get("intent") == "policy_question":
        return "retrieve_and_answer"

    return "direct_answer"


def build_graph():
    graph = StateGraph(GraphState)

    graph.add_node("classify_intent", classify_intent)
    graph.add_node("retrieve_and_answer", retrieve_and_answer)
    graph.add_node("direct_answer", direct_answer)

    graph.set_entry_point("classify_intent")

    graph.add_conditional_edges(
        "classify_intent",
        route_after_classification,
        {
            "retrieve_and_answer": "retrieve_and_answer",
            "direct_answer": "direct_answer",
        },
    )

    graph.add_edge("retrieve_and_answer", END)
    graph.add_edge("direct_answer", END)

    return graph.compile()


rag_graph = build_graph()


def ask_question(question: str) -> dict:
    result = rag_graph.invoke({
        "question": question
    })

    return {
        "answer": result.get("answer", ""),
        "sources": result.get("sources", []),
        "confidence": float(result.get("confidence", 0.0)),
    }
