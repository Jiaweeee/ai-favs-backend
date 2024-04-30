import os
from langchain_community.document_loaders.text import TextLoader
from langchain_community.vectorstores.faiss import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import VectorStore
from langchain_core.documents import Document

KNOWLEDGE_BASE_DIR = f'{os.curdir}/app/example_data/txt'
INDEX_NAME = 'index'
VECTOR_STORE_DIR = f'{os.curdir}/app/db'

def _get_embeddings():
  return OpenAIEmbeddings()

def load_vector_store() -> VectorStore:
  index_file_path = f"{VECTOR_STORE_DIR}/{INDEX_NAME}.faiss"
  if os.path.exists(index_file_path) == False:
    raise Exception("vector store not found.")
  return FAISS.load_local(
    folder_path=VECTOR_STORE_DIR,
    index_name=INDEX_NAME,
    embeddings=_get_embeddings(),
    allow_dangerous_deserialization=True
  )

def save_content(content: str, metadata: dict):
  text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    add_start_index=True
  )
  docs = [Document(page_content=content, metadata=metadata)]
  chunks = text_splitter.split_documents(docs)

  FAISS.from_documents(
    documents=chunks, embedding=_get_embeddings()
  ).save_local(folder_path=VECTOR_STORE_DIR, index_name=INDEX_NAME)