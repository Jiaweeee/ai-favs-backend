import os
from dotenv import load_dotenv
from langchain_community.document_loaders.text import TextLoader
from langchain_community.vectorstores.faiss import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import VectorStore

KNOWLEDGE_BASE_DIR = f'{os.curdir}/app/knowledge_base_jiawei/txt'
INDEX_NAME = 'jiawei'
VECTOR_STORE_DIR = f'{os.curdir}/app/db'

def get_embeddings():
  return OpenAIEmbeddings()

def load_vector_store() -> VectorStore:
  if os.path.exists(f'{VECTOR_STORE_DIR}/{INDEX_NAME}') == False:
    ingest_docs()
  return FAISS.load_local(
    folder_path=VECTOR_STORE_DIR,
    index_name=INDEX_NAME,
    embeddings=get_embeddings(),
    allow_dangerous_deserialization=True
  )

def ingest_docs():
  docs = []
  text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    add_start_index=True
  )

  for root, _, files in os.walk(KNOWLEDGE_BASE_DIR):
    for file in files:
      path = os.path.join(root, file)
      loader = TextLoader(file_path=path)
      temp_docs = loader.load()
      chunks = text_splitter.split_documents(temp_docs)
      docs += chunks

  FAISS.from_documents(
    documents=docs, embedding=get_embeddings()
  ).save_local(folder_path=VECTOR_STORE_DIR, index_name=INDEX_NAME)

def check_env_vars():
  if os.environ['OPENAI_API_KEY'] == None:
    return False
  return True

if __name__ == "__main__":
  if check_env_vars() == False:
    load_dotenv()
  ingest_docs()
  