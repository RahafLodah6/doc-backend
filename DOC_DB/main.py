# main.py — FastAPI backend connected to PostgreSQL via Prisma
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from prisma import Prisma
import traceback

app = FastAPI(title="Documents Database Service")
db = Prisma()

# ===================================================
# 🌐 CORS settings
# ===================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===================================================
# 🧩 Pydantic model for validation
# ===================================================
class DocumentCreate(BaseModel):
    title: str
    content: str
    author: str = "Rahaf"  # default author

# ===================================================
# 🔌 Database connection events
# ===================================================
@app.on_event("startup")
async def startup():
    if not db.is_connected():
        await db.connect()
        print("✅ Connected to PostgreSQL database")

@app.on_event("shutdown")
async def shutdown():
    if db.is_connected():
        await db.disconnect()
        print("🛑 Database disconnected")

# ===================================================
# 🏠 Root route
# ===================================================
@app.get("/")
def home():
    return {"message": "Database service is running on PostgreSQL!"}

# ===================================================
# 📄 CRUD Endpoints for Documents
# ===================================================

# 🧾 Get all documents
@app.get("/documents")
async def get_documents():
    try:
        docs = await db.document.find_many(order={"updatedAt": "desc"})
        return docs
    except Exception as e:
        print("❌ ERROR GETTING DOCUMENTS:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
    


# 🔍 Get one document by ID
@app.get("/documents/{doc_id}")
async def get_document(doc_id: int):
    try:
        doc = await db.document.find_unique(where={"id": doc_id})
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        return doc
    except Exception as e:
        print("❌ ERROR FETCHING DOCUMENT:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
    


# ✏️ Create new document
@app.post("/documents")
async def create_document(data: DocumentCreate):
    try:
        result = await db.document.create(data=data.dict())
        print("✅ Document created:", result)
        return result
    except Exception as e:
        print("❌ ERROR CREATING DOCUMENT:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
    


# 🔄 Update existing document
@app.put("/documents/{doc_id}")
async def update_document(doc_id: int, data: DocumentCreate):
    try:
        updated = await db.document.update(where={"id": doc_id}, data=data.dict())
        return updated
    except Exception as e:
        print("❌ ERROR UPDATING DOCUMENT:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))



# 🗑️ Delete a document
@app.delete("/documents/{doc_id}")
async def delete_document(doc_id: int):
    try:
        await db.document.delete(where={"id": doc_id})
        return {"message": "Document deleted successfully"}
    except Exception as e:
        print("❌ ERROR DELETING DOCUMENT:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
