from fastapi import FastAPI, HTTPException, Request
from openai import OpenAI
import redis
import uuid
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Modify OpenAI's API key and API base to use vLLM's API server.
openai_api_key = "EMPTY"
openai_api_base = "http://213.181.110.225:30998/v1"  # Each time after running the server, remember to modify this port number
client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base
)

base_prompt = f"""system
You are Jackie.
|<im_start|>assistant
Nice to meet you! I'm Jackie.

"""

# Connect to Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)  # Local Redis

app = FastAPI()

@app.post("/generate/")
async def generate_response(request: Request):
    try:
        payload = await request.json()
        logging.info(f"Received payload: {payload}")

        user_prompt = payload.get("prompt")
        session_id = payload.get("session_id") or str(uuid.uuid4())

        logging.info(f"Using session_id: {session_id}")

        # Retrieve conversation history from Redis
        conversation_history = redis_client.get(session_id)
        if conversation_history is None:
            conversation_history = base_prompt
        else:
            conversation_history = conversation_history.decode('utf-8')

        # Append user input to the conversation history
        full_prompt = conversation_history + "|<im_start|>user" + "\n" + user_prompt + "\n" + "|<im_start|>assistant"
        response = client.completions.create(model="satpalsr/jackie-2.1", prompt=full_prompt, max_tokens=200)

        # Update conversation history
        conversation_history += f"{full_prompt}\n{response.choices[0].text}\n"
        redis_client.set(session_id, conversation_history)

        return {"response": response.choices[0].text, "session_id": session_id}
    except Exception as e:
        logging.error(f"Error in generate_response: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test-ai-server/")
async def test_ai_server():
    try:
        static_prompt = base_prompt + "Hi Jackie!" + "\n" + "|<im_start|>assistant"
        response = client.completions.create(model="satpalsr/jackie-2.1", prompt=static_prompt, max_tokens=200)
        return {"response": response.choices[0].text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
