"""
A chat app which answers user's questions based on
the private knowledge base imported by ingest.py.
Exit the app when user explicitly type 'quit'.
"""

from app.utils.vectorstore import load_vector_store
from .llm import openai, moonshot
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import Runnable
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.language_models import LanguageModelLike
from langchain_core.messages import HumanMessage, AIMessage

RESPONSE_TEMPLATE = """You are an assistant for question-answering tasks. \
Use the following pieces of retrieved context to answer the question. \
If you don't know the answer, just say that you don't know. \
Use three sentences maximum and keep the answer concise.\

{context}"""

def get_retriever() -> BaseRetriever:
  vector_store = load_vector_store()
  return vector_store.as_retriever()

def create_chat_history_aware_retriever(llm: LanguageModelLike):
  """
  This is a chat history aware retriever.
  """
  # construct prompt
  system_prompt = """Given a chat history and the latest user question \
  which might reference context in the chat history, formulate a standalone question \
  which can be understood without the chat history. Do NOT answer the question, \
  just reformulate it if needed and otherwise return it as is."""
  
  history_aware_prompt = ChatPromptTemplate.from_messages([
     ("system", system_prompt),
     (MessagesPlaceholder("chat_history")),
     ("human", "{input}")
  ])
  return create_history_aware_retriever(
     llm=llm,
     prompt=history_aware_prompt,
     retriever=get_retriever()
  )

def create_chain() -> Runnable:
  llm = openai()
  retriever = create_chat_history_aware_retriever(llm)
  qa_prompt = ChatPromptTemplate.from_messages([
     ("system", RESPONSE_TEMPLATE),
     MessagesPlaceholder("chat_history"),
     ("human" "{input}")
  ])
  qa_chain = create_stuff_documents_chain(llm, qa_prompt)
  rag_chain = create_retrieval_chain(retriever=retriever, combine_docs_chain=qa_chain)
  return rag_chain

if __name__ == '__main__':
  rag_chain = create_chain()
  chat_history = []
  while True:
    user_input = input("Please input your question(type 'quit' to exit): \n")
    if user_input.lower() == 'quit':
        break
    response = rag_chain.invoke({"input": user_input, "chat_history": chat_history})
    answer = response["answer"]
    print(answer)
    chat_history.extend([HumanMessage(content=user_input), AIMessage(content=answer)])
    print("\n")