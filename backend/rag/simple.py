from langchain.vectorstores import Qdrant
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from qdrant_client import QdrantClient

def run_simple_rag(query: str):
    try:
        # Connect to Qdrant
        qdrant = QdrantClient("http://localhost:6333")

        # Load vector store and retriever
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vectorstore = Qdrant(client=qdrant, collection_name="rag_collection", embeddings=embeddings)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

        # Initialize LLM
        import os
        from langchain.llms import OpenAI
        if not os.getenv("OPENAI_API_KEY"):
            raise EnvironmentError("OPENAI_API_KEY not found in environment variables")

        llm = ChatOpenAI(
        model="llama3-8b-8192",
        temperature=0.3
        )


        # RAG Chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True
        )

        result = qa_chain(query)
        return {
            "query": query,
            "answer": result["result"],
            "sources": [doc.page_content for doc in result["source_documents"]]
        }

    except Exception as e:
        return {"error": str(e)}
