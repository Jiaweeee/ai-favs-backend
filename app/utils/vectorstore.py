import os
from langchain_community.vectorstores.faiss import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import VectorStore
from langchain_core.documents import Document

VECTOR_STORE_DIR = f'{os.curdir}/app/db/files/vector_store'

def _get_embeddings():
    return OpenAIEmbeddings()


def load_vector_store_by_index(index_name: str) -> VectorStore:
    index_file_path = f"{VECTOR_STORE_DIR}/{index_name}.faiss"
    if os.path.exists(index_file_path) == False:
        FAISS.from_texts(
            texts=["text"],
            embedding=_get_embeddings()
        ).save_local(folder_path=VECTOR_STORE_DIR, index_name=index_name)
    return FAISS.load_local(
        folder_path=VECTOR_STORE_DIR,
        index_name=index_name,
        embeddings=_get_embeddings(),
        allow_dangerous_deserialization=True
    )

def save_content_to_index(
    index_name: str,
    content: str,
    metadata: dict,
):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True
    )
    docs = [Document(page_content=content, metadata=metadata)]
    chunks = text_splitter.split_documents(docs)

    FAISS.from_documents(
        documents=chunks, embedding=_get_embeddings()
    ).save_local(folder_path=VECTOR_STORE_DIR, index_name=index_name)