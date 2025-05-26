from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from utils.ingest import process_pdf
from rag.simple import run_simple_rag
from rag.selfquery import run_selfquery_rag
from rag.reranker import run_reranker_rag
import uvicorn

import logging

app = FastAPI()

# CORS for frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or better: ["https://rag-comparison-playground.vercel.app"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "RAG backend is live"}


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    logging.info(f"Received file: {file.filename}")
    contents = await file.read()
    logging.info(f"File size: {len(contents)} bytes")
    return {"message": f"PDF processed: {file.filename}"}


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
