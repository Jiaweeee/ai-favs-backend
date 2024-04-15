from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from langserve import add_routes
from dotenv import load_dotenv
from langchain.chat_models.openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World!"}

@app.post("/save_link")
async def save_link():
    pass #TODO

@app.post("/save_file")
async def save_file():
    pass #TODO

llm = ChatOpenAI()
prompt = ChatPromptTemplate.from_template("{question}")
llm_chain = prompt | llm

add_routes(
    app,
    llm_chain,
    path="/chat",
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
