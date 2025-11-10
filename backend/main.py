import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from bson import ObjectId
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import Paper

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Arsip Karya Ilmiah Backend"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
    }
    try:
        if db is not None:
            db.list_collection_names()
            response["database"] = "✅ Connected & Working"
    except Exception as e:
        response["database"] = f"⚠️ Error: {str(e)[:80]}"
    return response

# Create paper
@app.post("/papers", response_model=dict)
async def create_paper(paper: Paper):
    try:
        inserted_id = create_document("paper", paper)
        return {"_id": inserted_id, **paper.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# List papers
@app.get("/papers", response_model=List[dict])
async def list_papers(limit: Optional[int] = 100):
    try:
        docs = get_documents("paper", {}, limit=limit)
        # Convert ObjectId to string
        for d in docs:
            if isinstance(d.get("_id"), ObjectId):
                d["_id"] = str(d["_id"])
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
