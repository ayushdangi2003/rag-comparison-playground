from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Qdrant
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo
from qdrant_client import QdrantClient

def run_selfquery_rag(query: str):
    try:
        qdrant = QdrantClient("http://localhost:6333")
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vectorstore = Qdrant(
            client=qdrant,
            collection_name="rag_collection",
            embeddings=embeddings
        )

        metadata_field_info = [
            AttributeInfo(name="source", description="The origin or type of document", type="string"),
            AttributeInfo(name="page", description="Page number of the document", type="integer")
        ]

        retriever = SelfQueryRetriever.from_llm(
            llm=ChatOpenAI(model="llama3-8b-8192"),
            vectorstore=vectorstore,
            document_contents="Information about a candidate's resume",
            metadata_field_info=metadata_field_info,
            metadata_key="metadata",  # ✅ THIS LINE FIXES THE ERROR
            verbose=True
        )

        qa = RetrievalQA.from_chain_type(
            llm=ChatOpenAI(model="llama3-8b-8192"),
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True
        )

        result = qa.invoke({"query": query})

        return {
            "query": query,
            "answer": result["result"],
            "sources": [doc.page_content for doc in result["source_documents"]]
}


    except Exception as e:
        return {"error": str(e)}
