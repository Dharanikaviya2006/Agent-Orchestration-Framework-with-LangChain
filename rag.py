from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

embeddings = OpenAIEmbeddings()

def build_vector_store(texts: list[str]):
    docs = [Document(page_content=t) for t in texts]
    return FAISS.from_documents(docs, embeddings)

def retrieve_context(vector_store, query: str):
    docs = vector_store.similarity_search(query, k=3)
    return "\n".join([d.page_content for d in docs])
