"""
Test script to query the Azure AI Search index with semantic/vector search.
"""
import os
from dotenv import load_dotenv
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI

# Load environment variables
load_dotenv("config/.env")

# Azure AI Search configuration
search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
search_key = os.getenv("AZURE_SEARCH_API_KEY")
index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")

# Azure OpenAI configuration
openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
openai_key = os.getenv("AZURE_OPENAI_API_KEY")
embedding_deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION")

# Initialize clients
search_client = SearchClient(
    endpoint=search_endpoint,
    index_name=index_name,
    credential=AzureKeyCredential(search_key)
)

openai_client = AzureOpenAI(
    api_key=openai_key,
    api_version=openai_api_version,
    azure_endpoint=openai_endpoint
)


def generate_query_embedding(query_text: str) -> list[float]:
    """Generate embedding for a search query."""
    response = openai_client.embeddings.create(
        input=query_text,
        model=embedding_deployment
    )
    return response.data[0].embedding


def vector_search(query: str, top_k: int = 5):
    """
    Perform vector search on the index.
    
    Args:
        query: Natural language query
        top_k: Number of results to return
    """
    print(f"\n{'='*80}")
    print(f"Query: {query}")
    print(f"{'='*80}\n")
    
    # Generate embedding for the query
    query_vector = generate_query_embedding(query)
    
    # Perform vector search
    results = search_client.search(
        search_text=None,  # Pure vector search
        vector_queries=[{
            "kind": "vector",
            "vector": query_vector,
            "fields": "embedding",
            "k": top_k
        }],
        select=["id", "content", "metadata"],
        top=top_k
    )
    
    # Display results
    for i, result in enumerate(results, 1):
        score = result.get('@search.score', 0)
        content = result.get('content', '')[:300]  # First 300 chars
        metadata = result.get('metadata', {})
        
        print(f"Result {i} (Score: {score:.4f}):")
        print(f"ID: {result.get('id', 'N/A')}")
        if metadata:
            print(f"Metadata: {metadata}")
        print(f"Content Preview: {content}...")
        print(f"-" * 80)


def hybrid_search(query: str, top_k: int = 5):
    """
    Perform hybrid search (text + vector) on the index.
    
    Args:
        query: Natural language query
        top_k: Number of results to return
    """
    print(f"\n{'='*80}")
    print(f"Hybrid Search Query: {query}")
    print(f"{'='*80}\n")
    
    # Generate embedding for the query
    query_vector = generate_query_embedding(query)
    
    # Perform hybrid search (combines keyword and vector search)
    results = search_client.search(
        search_text=query,  # Keyword search
        vector_queries=[{
            "kind": "vector",
            "vector": query_vector,
            "fields": "embedding",
            "k": top_k
        }],
        select=["id", "content", "metadata"],
        top=top_k
    )
    
    # Display results
    for i, result in enumerate(results, 1):
        score = result.get('@search.score', 0)
        content = result.get('content', '')[:300]  # First 300 chars
        metadata = result.get('metadata', {})
        
        print(f"Result {i} (Score: {score:.4f}):")
        print(f"ID: {result.get('id', 'N/A')}")
        if metadata:
            print(f"Metadata: {metadata}")
        print(f"Content Preview: {content}...")
        print(f"-" * 80)


def test_index_stats():
    """Display index statistics."""
    print("\n" + "="*80)
    print("Index Statistics")
    print("="*80)
    
    # Get total document count
    results = search_client.search(search_text="*", top=0, include_total_count=True)
    print(f"Total documents in index: {results.get_count()}")
    print(f"Index name: {index_name}")
    print(f"Endpoint: {search_endpoint}")
    print("="*80 + "\n")


if __name__ == "__main__":
    # Test 1: Show index stats
    test_index_stats()
    
    # Test 2: Example semantic/vector searches
    print("\n🔍 Testing Vector Search (Semantic Understanding):\n")
    
    # Example queries - these will find semantically similar clinical notes
    queries = [
        "patient with chest pain and breathing problems",
        "diabetes management and blood sugar control",
        "mental health anxiety and depression symptoms",
        "surgery recovery and post-operative care",
        "chronic pain and pain management"
    ]
    
    for query in queries:
        vector_search(query, top_k=3)
        input("\nPress Enter to continue to next query...")
    
    # Test 3: Hybrid search example
    print("\n\n🔍 Testing Hybrid Search (Text + Vector):\n")
    hybrid_search("patient experiencing headaches", top_k=3)
    
    print("\n" + "="*80)
    print("✅ Search testing complete!")
    print("="*80)
