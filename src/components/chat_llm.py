from openai import OpenAI, AsyncOpenAI
import json
from uuid import uuid4
import os
import asyncio

CONFIG_PATH = os.path.join(os.getcwd(), "src/config","config.json")


def get_model():
    with open(CONFIG_PATH, "r", encoding = "utf-8") as file:
        model_info = json.load(file)
    if 'model' not in model_info:
        return "model missing"
    if 'name' not in model_info:
        return "model aliasing name missing"
    return model_info
    
key = get_model().get('key')
client = OpenAI(api_key = key)

def chat_stream_new(prompt:str, key:str, history: list[dict[str, str]] = [], model = "gpt-3.5-turbo", stream = True):
    messages = history.copy()
    messages.append({
         "role": "user", "content": prompt
    })
    #client = OpenAI(api_key = key)
    import time
    print("before create", time.time(), flush=True)
    responses = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=stream,
    )
    print("after create", time.time(), flush=True)
    for chunk in responses:
        part = chunk.choices[0].delta.content
        if part:
            for char in part: 
                yield char


async def chat_stream(prompt:str, key:str, history: list[dict[str, str]] = [], model = "gpt-3.5-turbo", stream = True):
    messages = history.copy()
    messages.append({
         "role": "user", "content": prompt
    })
    
    import time
    print("before create", time.time(), flush=True)
    async with client.responses.stream(
        model=model,
        input=prompt,
    ) as stream:
        print("after create", time.time(), flush=True)
        async for event in stream:
            if event.type == "response.output_text.delta":
                print("got delta:", event.delta, flush=True)
                yield event.delta
    # import time
    # print("before create", time.time(), flush=True)
    # responses = await client.responses.create(
    #     model=model,
    #     input = prompt,
    #     #messages=messages,
    #     stream=stream,
    # )
    
    # print("after create", time.time(), flush=True)
    # async for event in responses:
    #     if event.type == "response.output_text.delta":
    #         yield event.delta
    # Must use a synchronous 'for' loop for the synchronous Stream object
    # async for chunk in responses:
    #     part = chunk.choices[0].delta.content
    #     if part:
    #         # Yield single characters for best streaming effect
    #         for char in part: 
    #             print("got char", char, flush=True)
    #             await asyncio.sleep(0.01)
    #             yield char

def chat_stream_dummy(prompt:str, history: list[dict[str, str]] = [], model = "gpt-3.5-turbo", stream = True):
    """Generates and yields single characters from the OpenAI API stream."""
    messages = history.copy()
    messages.append({
         "role": "user", "content": prompt
    })
    responses = str(messages)
    for chunk in responses:
        for char in chunk: 
            yield char

def save_history(history: list[dict[str, str]], history_id:str, saved_path = "history.json"):
    if not history_id:
        history_id = str(uuid4())
    parsed_history = {
        "id":history_id,
        "history":history
    }
    with open(saved_path, 'w', encoding='utf-8') as f:
        json.dump(parsed_history, f, ensure_ascii=False, indent=4)
    #logging.info(f"save history into {saved_path}")

def clear_history(history_id:str, saved_path = "history.json"):
    with open(saved_path, 'r', encoding='utf-8') as f:
        current_history = json.load(f)
    if history_id in current_history:
        current_history.pop(history_id)
       # logging.info(f"clear historty: {history_id}")
   # else:
       # logging.info(f"history id: {history_id} not in database")