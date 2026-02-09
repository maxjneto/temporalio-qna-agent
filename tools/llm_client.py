import os
from openai import AsyncAzureOpenAI
from dotenv import load_dotenv

load_dotenv()

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

if not (AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY and AZURE_OPENAI_DEPLOYMENT):
    raise RuntimeError("Azure OpenAI variables not configured.")

client = AsyncAzureOpenAI(
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY
)

async def chat_complete(messages: list[dict], temperature: float = 0.3) -> str:
    """
    messages = [
      {"role":"system","content":"..."},
      {"role":"user","content":"..."},
      ...
    ]
    """
    resp = await client.chat.completions.create(
        model=AZURE_OPENAI_DEPLOYMENT,           # In Azure, 'model' = deployment name
        messages=messages,
    )
    return resp.choices[0].message.content