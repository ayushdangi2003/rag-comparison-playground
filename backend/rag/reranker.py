import os
import requests
from langchain.vectorstores import Qdrant
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from qdrant_client import QdrantClient
print("JINA_API_KEY:", os.getenv("JINA_API_KEY"))

def run_reranker_rag(query: str):
    try:
        # Embed + Retrieve
        qdrant = QdrantClient("http://localhost:6333")
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vectorstore = Qdrant(client=qdrant, collection_name="rag_collection", embeddings=embeddings)
        docs = vectorstore.similarity_search(query, k=6)

        docs_text = [doc.page_content for doc in docs]

        # REST call to Jina reranker
        url = "https://api.jina.ai/v1/rerank"
        headers = {
            "Authorization": f"Bearer {os.getenv('JINA_API_KEY')}",
            "Content-Type": "application/json"
        }
        payload = {
            "query": query,
            "documents": docs_text,
            "model": "jina-reranker-v1-base-en"
  # ✅ This works
        }


        print("Using JINA_API_KEY:", os.getenv("JINA_API_KEY"))

        response = requests.post(url, headers=headers, json=payload)

        try:
            result = response.json()
        except Exception:
            return {"error": "Failed to parse Jina response", "raw": response.text}

        if "results" not in result:
            return {"error": "Jina response missing 'results'", "raw": result}


        # Get top 3 from the response directly
        reranked_results = result["results"][:3]
        if not reranked_results:
            return {"error": "No reranked results found", "raw": result}


        # Map back to original docs by comparing content
        top_docs = []
        for item in reranked_results:
            reranked_text = item["document"]["text"].strip()
            for doc in docs:
                if doc.page_content.strip() == reranked_text:
                    top_docs.append(doc)
                    break

        # Prompt + Answer
        prompt = PromptTemplate.from_template(
            "Answer the question based on the context:\n\n{context}\n\nQuestion: {question}"
        )
        llm = ChatOpenAI(model="llama3-8b-8192")
        chain = LLMChain(llm=llm, prompt=prompt)
        answer = chain.run({
            "context": "\n".join([doc.page_content for doc in top_docs]),
            "question": query
        })

        return {
            "query": query,
            "answer": answer,
            "reranked_sources": [doc.page_content for doc in top_docs]
        }

    except Exception as e:
        return {"error": str(e)}
