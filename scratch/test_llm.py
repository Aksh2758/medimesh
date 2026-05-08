from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

VLLM_BASE_URL = os.getenv("VLLM_BASE_URL")
VLLM_MODEL_NAME = os.getenv("VLLM_MODEL_NAME")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

print(f"Base URL: {VLLM_BASE_URL}")
print(f"Model: {VLLM_MODEL_NAME}")

llm = ChatOpenAI(
    base_url=VLLM_BASE_URL,
    api_key=OPENAI_API_KEY,
    model=VLLM_MODEL_NAME,
    temperature=0.1,
    max_tokens=400,
)

print("LLM initialized.")
try:
    response = llm.invoke("Hello")
    print(f"Response: {response.content}")
except Exception as e:
    print(f"Error: {e}")
