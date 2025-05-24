from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Qdrant
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
import tempfile

async def process_pdf(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await uploaded_file.read())
        tmp_path = tmp.name

    # Load PDF and split into chunks
    loader = PyPDFLoader(tmp_path)
    pages = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    for page in pages:
        page.metadata["source"] = "resume"
        page.metadata["page"] = page.metadata.get("page", 0)

    chunks = splitter.split_documents(pages)


    # Create Qdrant collection if not exists
    qdrant = QdrantClient("http://localhost:6333")
    if "rag_collection" not in [col.name for col in qdrant.get_collections().collections]:
        qdrant.create_collection(
            collection_name="rag_collection",
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )

    # Embed and store chunks
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = Qdrant(client=qdrant, collection_name="rag_collection", embeddings=embeddings)
    vectorstore.add_documents(chunks)

    return [chunk.page_content[:100] for chunk in chunks]  # return preview of chunks
