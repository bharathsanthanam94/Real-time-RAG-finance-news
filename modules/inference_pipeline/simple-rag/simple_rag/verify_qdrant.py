import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient

# Load environment variables
load_dotenv()

def get_sample_data_from_qdrant(limit=500):
    # Initialize Qdrant client
    client = QdrantClient(
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY")
    )

    # Retrieve sample data
    samples = client.scroll(
        collection_name="alpaca_financial_news",
        limit=limit,
        with_payload=True,
        with_vectors=True
    )

    return samples[0]  # samples[0] contains the actual records

def print_sample_data(samples):
    for i, sample in enumerate(samples, 1):
        print(f"\nSample {i}:")
        print(f"ID: {sample.id}")
        print("Payload:")
        for key, value in sample.payload.items():
            if key == 'text':
                print(f"  {key}: {value[:100]}...")  # Print first 100 characters of text
            else:
                print(f"  {key}: {value}")
        print(f"Vector (first 5 dimensions): {sample.vector[:5]}...")

if __name__ == "__main__":
    samples = get_sample_data_from_qdrant()
    print_sample_data(samples)