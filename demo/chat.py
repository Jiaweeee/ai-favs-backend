import requests

BASE_URL = 'http://localhost:8000'

apis = {
  "chat": f'{BASE_URL}/chat',
  "chat_stream": f'{BASE_URL}/chat/stream',
  "followups_get": f'{BASE_URL}/chat/followups/get'
}

def get_answer(input: str, chat_history: list) -> dict:
  response = requests.post(
    url=apis["chat"],
    json={
      "input": input,
      "chat_history": chat_history
    }
  ).json().get("data")
  if response:
    answer = response.get("content")
    sources = response.get("sources")
  return {
    "answer": answer,
    "sources": sources
  }

def get_follow_ups(input: str, chat_history: list) -> list:
  response = requests.get(
    url=apis["followups_get"],
    json={
      "input": input,
      "chat_history": chat_history
    }
  ).json().get("data")
  if response:
    followups = response.get("follow_ups")
  return {
    "follow_ups": followups
  }

def get_answers_stream(input: str, chat_history: list):
  response = requests.post(
    url=apis["chat_stream"],
    json={
      "input": input,
      "chat_history": chat_history
    }
  ).json()
  for part in response:
    answer = part.get("answer", None)
    if answer:
      print(answer, end="")

def ai_message(content: str):
  return {
    "type": "ai",
    "content": content
  }

def human_message(content: str):
  return {
    "type": "human",
    "content": content
  }

if __name__ == '__main__':
  chat_history = []
  while True:
    user_input = input("Please input your question(type 'quit' to exit): \n")
    if user_input.lower() == 'quit':
        break
    answer_dict = get_answer(user_input, chat_history)
    answer = answer_dict.get("answer")
    sources = answer_dict.get("sources")
    print(f'\nAnswer:\n{answer}')
    print(f'\nSources:\n{sources}')

    chat_history.extend([human_message(user_input), ai_message(answer)])
    follow_ups = get_follow_ups(user_input, chat_history).get("follow_ups")
    if follow_ups and len(follow_ups) > 0:
      print(f'\nFollow up questions:')      
      for index, value in enumerate(follow_ups, start=1):
        print(f'{index}. {value}')
    print('\n')
  