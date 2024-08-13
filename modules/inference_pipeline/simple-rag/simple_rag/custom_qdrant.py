from langchain_community.vectorstores import Qdrant
from langchain_core.documents import Document
from typing import Optional, List
class CustomQdrant(Qdrant):
    def _document_from_scored_point(
        self,
        scored_point,
        metadata_fields: Optional[List[str]] = None,
        content_payload_key: Optional[str] = None,
        metadata_payload_key: Optional[str] = None,
    ):
        payload = scored_point.payload or {}
        
        # Extract the content from the 'text' field, which is a list in your streaming pipeline
        content = " ".join(payload.get("text", []))
        
        # Extract metadata fields
        metadata = {
            "headline": payload.get("headline", ""),
            "summary": payload.get("summary", ""),
            "url": payload.get("url", ""),
            "symbols": payload.get("symbols", []),
            "author": payload.get("author", ""),
            "created_at": payload.get("created_at", "")
        }
        
        # Return only the Document object, not a tuple
        return Document(page_content=content, metadata=metadata)