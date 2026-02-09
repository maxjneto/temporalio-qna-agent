"""MCP Server - Exposes semantic search tools via Model Context Protocol."""

import json
import os

import numpy as np
from dotenv import load_dotenv
from fastmcp import FastMCP
from openai import AzureOpenAI

load_dotenv()

SEARCH_FILENAME = os.getenv("SEARCH_FILENAME")

AZURE_EMBEDDINGS_ENDPOINT = os.getenv("AZURE_API_BASE")
AZURE_EMBEDDINGS_API_KEY = os.getenv("AZURE_API_KEY")
AZURE_EMBEDDINGS_DEPLOYMENT = os.getenv("AZURE_EMBEDDINGS_DEPLOYMENT")
AZURE_EMBEDDINGS_API_VERSION = os.getenv(
    "AZURE_EMBEDDINGS_API_VERSION", "2024-02-15-preview"
)

# Initialize Azure OpenAI client for embeddings
openai_client_async_max = AzureOpenAI(
    azure_endpoint=AZURE_EMBEDDINGS_ENDPOINT,
    api_key=AZURE_EMBEDDINGS_API_KEY,
    api_version=AZURE_EMBEDDINGS_API_VERSION,
)


def get_embedding(query: str) -> list[float]:
    """Generates embedding for a query using Azure OpenAI.
    
    Args:
        query: Text to generate embedding for
        
    Returns:
        List of floats representing the embedding
    """
    response = openai_client_async_max.embeddings.create(
        model=AZURE_EMBEDDINGS_DEPLOYMENT,
        input=query,
    )
    return response.data[0].embedding


def numpy_cosine_similarity(embedding1: list[float], embedding2: list[float]) -> float:
    """Calculates cosine similarity between two embeddings.
    
    Args:
        embedding1: First embedding
        embedding2: Second embedding
        
    Returns:
        Similarity value between -1 and 1
    """
    dot_product = np.dot(embedding1, embedding2)
    norm1 = np.linalg.norm(embedding1)
    norm2 = np.linalg.norm(embedding2)
    return dot_product / (norm1 * norm2)

mcp = FastMCP("AzureSearchMCP")

@mcp.tool()
def azure_ai_search(query: str, top_k: int = 3) -> list[dict]:
    """Searches documents in an index that simulates Azure AI Search.
    
    Args:
        query: Search text
        top_k: Number of results to return (default: 3)
        
    Returns:
        List of dictionaries with {id, score, chunk}
    """
    with open(SEARCH_FILENAME, "r", encoding="utf-8") as f:
        index = json.load(f)

    query_embedding = get_embedding(query)

    results = []
    for doc in index:
        similarity = numpy_cosine_similarity(
            query_embedding, doc.get("embedding")
        )
        results.append(
            {
                "id": doc.get("id"),
                "score": float(similarity),
                "chunk": doc.get("chunk"),
            }
        )

    results.sort(key=lambda x: x["score"], reverse=True)
    returning_results = results[:top_k]

    for result in returning_results:
        print(f"[{result['id']}] Score: {result['score']:.4f}")

    return returning_results

if __name__ == "__main__":
    # Runs via stdio (ideal for local MCP clients)
    mcp.run()