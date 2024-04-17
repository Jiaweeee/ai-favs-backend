# A chat app which answers user's questions based on
# the private knowledge base imported by ingest.py.
# Exit the app when user explicitly type 'quit'.

from ingest import load_vector_store
from langchain_core.retrievers import BaseRetriever
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, Runnable
from langchain_core.prompts import ChatPromptTemplate

RESPONSE_TEMPLATE = """\
You are an assistant for question-answering tasks. \
Use the following pieces of retrieved context to answer the question. \
If you don't know the answer, just say that you don't know. \
Try to keep the answer concise. \
Question: {question} \
Context: {context} \
Answer:
"""

def get_retriever() -> BaseRetriever:
  vector_store = load_vector_store()
  return vector_store.as_retriever()

def create_chain() -> Runnable:
  llm = ChatOpenAI()
  retriever = get_retriever()
  prompt = ChatPromptTemplate.from_template(RESPONSE_TEMPLATE)
  return (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
  )

if __name__ == '__main__':
  rag_chain = create_chain()
  #TODO: add chat history to the context.
  #TODO: decide whether it is necessary to retrieve context from db automatically based on user input.
  while True:
    user_input = input("Please input your question(type 'quit' to exit): \n")
    if user_input.lower() == 'quit':
        break
    for chunk in rag_chain.stream(user_input):
        print(chunk, end="")
    print("\n")