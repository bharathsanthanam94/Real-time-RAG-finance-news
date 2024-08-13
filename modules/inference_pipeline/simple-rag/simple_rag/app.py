from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rag_financial_data import ask_question

app = FastAPI()

class Question(BaseModel):
    text: str

class Answer(BaseModel):
    answer: str
    sources: list

@app.post("/ask", response_model=Answer)
async def ask(question: Question):
    answer, sources = ask_question(question.text)
    if answer is None:
        raise HTTPException(status_code=500, detail="Failed to get an answer")
    
    formatted_sources = [
        {
            "headline": doc.metadata.get('headline', 'Unknown headline'),
            "url": doc.metadata.get('url', 'Unknown URL'),
            "created_at": doc.metadata.get('created_at', 'Unknown date'),
            "content_preview": doc.page_content[:100]  # First 100 chars of content
        } for doc in sources
    ]
    
    return Answer(answer=answer, sources=formatted_sources)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)