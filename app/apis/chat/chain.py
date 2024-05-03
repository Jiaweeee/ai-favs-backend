"""
A chat app which answers user's questions based on
the private knowledge base imported by ingest.py.
Exit the app when user explicitly type 'quit'.
"""

from app.utils.vectorstore import load_vector_store
from app.utils.llm import get_llm
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import Runnable, RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.language_models import LanguageModelLike
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import JsonOutputParser

RESPONSE_TEMPLATE = """
You are an assistant for question-answering tasks. \
Use the following pieces of retrieved context to answer the question. \
If you don't know the answer, just say that you don't know. \
{context}
"""

REPHRASE_PROMPT = """
Given a chat history and the latest user question \
which might reference context in the chat history, formulate a standalone question \
which can be understood without the chat history. Do NOT answer the question, \
just reformulate it if needed and otherwise return it as is.
"""

def get_retriever() -> BaseRetriever:
  vector_store = load_vector_store()
  print("Load vectore store: DONE")
  return vector_store.as_retriever()

def create_chat_history_aware_retriever(llm: LanguageModelLike):
  """
  This is a chat history aware retriever.
  """
  history_aware_prompt = ChatPromptTemplate.from_messages([
     ("system", REPHRASE_PROMPT),
     (MessagesPlaceholder("chat_history")),
     ("human", "{input}")
  ])
  return create_history_aware_retriever(
     llm=llm,
     prompt=history_aware_prompt,
     retriever=get_retriever()
  )

def create_rag_chain() -> Runnable:
  llm = get_llm()
  retriever = create_chat_history_aware_retriever(llm)
  qa_prompt = ChatPromptTemplate.from_messages([
    ("system", RESPONSE_TEMPLATE),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}")
  ])
  
  qa_chain = create_stuff_documents_chain(
    llm=llm,
    prompt=qa_prompt
  )
  rag_chain = RunnablePassthrough.assign(
    context=retriever
  ).assign(answer=qa_chain)

  return rag_chain

def create_follow_ups_chain() -> Runnable:
  system_prompt = """
  Given a chat history and the latest user question, \
  please generate a list of no more than 5 potential follow-up questions that could continue the conversation.\
  The aim is to create questions that are relevant, \
  encourage further dialogue, and directly address the user's inquiry. \
  Format the questions in an open-ended manner to allow for more in-depth exploration of the topics.\
  
  chat history: {chat_history} \
  question: {input} \

  Return the information in simplified Chinese. \
  The output should be in the format of a json list with the key 'follow_ups' \
  """
  output_parser = JsonOutputParser()
  prompt = PromptTemplate(
    template=system_prompt,
    input_variables=["chat_history", "input"]
  )
  llm = get_llm()
  return prompt | llm | output_parser

if __name__ == '__main__':
  rag_chain = create_rag_chain()
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