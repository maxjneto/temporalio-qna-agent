import json
import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

AZURE_EMBEDDINGS_ENDPOINT = os.getenv("AZURE_EMBEDDINGS_ENDPOINT")
AZURE_EMBEDDINGS_API_KEY = os.getenv("AZURE_EMBEDDINGS_API_KEY")
AZURE_EMBEDDINGS_DEPLOYMENT = os.getenv("AZURE_EMBEDDINGS_DEPLOYMENT")
AZURE_EMBEDDINGS_API_VERSION = os.getenv("AZURE_EMBEDDINGS_API_VERSION", "2024-02-15-preview")

openai_client_async_max = AzureOpenAI(
        azure_endpoint=AZURE_EMBEDDINGS_ENDPOINT,
        api_key=AZURE_EMBEDDINGS_API_KEY,
        api_version=AZURE_EMBEDDINGS_API_VERSION
)

def get_embedding(query: str):
    response = openai_client_async_max.embeddings.create(
        model=AZURE_EMBEDDINGS_DEPLOYMENT, 
        input=query,
    )
    return response.data[0].embedding

def generate_embeddings():
    with open("database/index.json", "r",encoding='utf-8') as f:
        documents = json.load(f)
    for doc in documents:
        embedding = get_embedding(doc["chunk"])
        doc["embedding"] = embedding

    with open("database/search_index.json", "w") as f:
        json.dump(documents, f)

if __name__ == "__main__":
    print("Generating embeddings...")
    generate_embeddings()
    print("Embeddings generated successfully!")