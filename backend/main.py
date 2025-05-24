from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from utils.ingest import process_pdf
from rag.simple import run_simple_rag
from rag.selfquery import run_selfquery_rag
from rag.reranker import run_reranker_rag
import uvicorn

app = FastAPI()

# CORS for frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        return {"error": "Only PDF files are supported"}
    
    try:
        result = await process_pdf(file)
        return {"message": "PDF processed and stored", "chunks": result}
    except Exception as e:
        return {"error": str(e)}


@app.post("/query")
async def query_rag(payload: dict):
    query = payload.get("query")
    if not query:
        return {"error": "Query is required"}
    
    result = run_simple_rag(query)
    return result

if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)




@app.post("/selfquery")
async def query_selfquery(payload: dict):
    query = payload.get("query")
    if not query:
        return {"error": "Query is required"}

    result = run_selfquery_rag(query)
    return result

@app.post("/rerank")
async def rerank_query(payload: dict):
    query = payload.get("query")
    if not query:
        return {"error": "Query required"}
    return run_reranker_rag(query)
