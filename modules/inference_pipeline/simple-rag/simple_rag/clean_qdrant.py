import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models
from tqdm import tqdm
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

# Constants
VECTOR_DB_OUTPUT_COLLECTION_NAME = "alpaca_financial_news"
BATCH_SIZE = 100  # Number of points to process in each batch

# Initialize Qdrant client
qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

def clean_qdrant_collection():
    # Get the total number of points in the collection
    collection_info = qdrant_client.get_collection(VECTOR_DB_OUTPUT_COLLECTION_NAME)
    total_points = collection_info.vectors_count

    logging.info(f"Total points in collection: {total_points}")

    # Process points in batches
    for offset in tqdm(range(0, total_points, BATCH_SIZE), desc="Processing batches"):
        # Scroll through the collection
        response = qdrant_client.scroll(
            collection_name=VECTOR_DB_OUTPUT_COLLECTION_NAME,
            limit=BATCH_SIZE,
            offset=offset,
            with_payload=True,
            with_vectors=False  # We don't need vectors for this operation
        )

        points_to_delete = []

        for point in response[0]:
            if 'page_content' not in point.payload or point.payload['page_content'] is None:
                points_to_delete.append(point.id)

        if points_to_delete:
            logging.info(f"Deleting {len(points_to_delete)} points with None content")
            qdrant_client.delete(
                collection_name=VECTOR_DB_OUTPUT_COLLECTION_NAME,
                points_selector=models.PointIdsList(
                    points=points_to_delete
                )
            )

    logging.info("Cleanup completed")

if __name__ == "__main__":
    clean_qdrant_collection()