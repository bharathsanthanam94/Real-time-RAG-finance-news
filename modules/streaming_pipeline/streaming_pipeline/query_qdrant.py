import os
from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Qdrant client
client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

# Define the collection name
COLLECTION_NAME = "alpaca_financial_news"  # or whatever your collection name is

def print_collection_info():
    # Get collection info
    collection_info = client.get_collection(COLLECTION_NAME)
    print(f"Collection Info: {collection_info}")

def search_by_keyword(keyword, limit=5):
    # Search for points containing the keyword
    search_result = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=[0] * 384,  # Replace with actual vector if you want semantic search
        query_filter=Filter(
            must=[
                FieldCondition(
                    key="text",
                    match=MatchValue(value=keyword)
                )
            ]
        ),
        limit=limit
    )
    
    print(f"Search results for keyword '{keyword}':")
    for scored_point in search_result:
        print(f"Score: {scored_point.score}, Payload: {scored_point.payload}")

def get_random_points(limit=5):
    # Get random points from the collection
    points = client.scroll(
        collection_name=COLLECTION_NAME,
        limit=limit,
    )[0]
    
    print(f"Random {limit} points from the collection:")
    for point in points:
        print(f"ID: {point.id}, Payload: {point.payload}")

if __name__ == "__main__":
    print_collection_info()
    search_by_keyword("Madison")  # Replace with any keyword you want to search for
    get_random_points()