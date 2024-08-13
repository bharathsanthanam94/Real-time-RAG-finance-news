import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Qdrant
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Bedrock
from qdrant_client import QdrantClient
import boto3
from langchain_community.vectorstores import Qdrant
from langchain_core.documents import Document
from typing import Optional, List
import constants
from custom_qdrant import CustomQdrant
# Load environment variables
load_dotenv()

# Constants
EMBEDDING_MODEL_ID = constants.EMBEDDING_MODEL_ID
EMBEDDING_MODEL_MAX_INPUT_LENGTH = constants.EMBEDDING_MODEL_MAX_INPUT_LENGTH
VECTOR_DB_OUTPUT_COLLECTION_NAME = constants.VECTOR_DB_OUTPUT_COLLECTION_NAME

# Initialize Bedrock client
bedrock_client = boto3.client(
    service_name="bedrock-runtime",
)

# Initialize Bedrock LLM
llm = Bedrock(
    model_id="mistral.mistral-7b-instruct-v0:2",
    client=bedrock_client,
    model_kwargs={"max_tokens": 384, "temperature": 0.7},
)


# Initialize HuggingFace Embeddings
embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL_ID,
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)

# Initialize Qdrant client
qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

# Initialize Qdrant vector store with CustomQdrant
vector_store = CustomQdrant(
    client=qdrant_client,
    collection_name=VECTOR_DB_OUTPUT_COLLECTION_NAME,
    embeddings=embeddings,
)

# Create a retriever
retriever = vector_store.as_retriever(search_kwargs={"k": 5})

# Create a custom prompt template
template = """Use the following pieces of context to answer the question at the end. 
If you don't know the answer, just say that you don't know, don't try to make up an answer.

{context}

Question: {question}
Answer:"""

prompt = PromptTemplate(
    template=template,
    input_variables=["context", "question"]
)

# Create the RetrievalQA chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True,
    chain_type_kwargs={"prompt": prompt}
)

def ask_question(question: str):
    """Function to ask a question and get an answer using the RAG system"""
    try:
        result = qa_chain.invoke({"query": question})
        return result["result"], result["source_documents"]
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return None, None

# Example usage
if __name__ == "__main__":
    question = "What is the latest news on Bitcoin?"
    answer, sources = ask_question(question)
    if answer is not None:
        print(f"Question: {question}")
        print(f"Answer: {answer}")
        print("\nSources:")
        for i, doc in enumerate(sources, 1):
            print(f"{i}. {doc.metadata.get('headline', 'Unknown headline')}")
            print(f"   URL: {doc.metadata.get('url', 'Unknown URL')}")
            print(f"   Created at: {doc.metadata.get('created_at', 'Unknown date')}")
            print(f"   Content: {doc.page_content[:100]}...")  # Print first 100 chars
            print()
    else:
        print("Failed to get an answer.")