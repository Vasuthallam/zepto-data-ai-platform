from fastapi import FastAPI
from .models import AskRequest, AskResponse
from .rag import build_graph


app = FastAPI(
    title="Zepto Support Assistant",
    description="RAG-based customer support assistant for Zepto policies",
    version="1.0.0",
)


rag_graph = build_graph()


@app.get("/")
def root():
    return {
        "message": "Zepto Support Assistant is running"
    }


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    result = rag_graph.invoke({
        "question": request.question
    })

    return AskResponse(
        answer=result.get("answer", ""),
        sources=result.get("sources", []),
        confidence=float(result.get("confidence", 0.0)),
    )