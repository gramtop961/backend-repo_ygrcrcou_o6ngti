import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Medicine, Prescription, Staff, Supplier, SCHEMA_REGISTRY

app = FastAPI(title="Pharmacy Management API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Helpers
class ObjectIdStr(str):
    pass


def to_object_id(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid id format")


@app.get("/")
def read_root():
    return {"message": "Pharmacy Backend Running"}


@app.get("/schema")
def get_schema():
    return SCHEMA_REGISTRY


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set",
        "database_name": "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set",
        "connection_status": "Not Connected",
        "collections": [],
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["connection_status"] = "Connected"
            try:
                response["collections"] = db.list_collection_names()[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response


# ----------------------------- Medicines ----------------------------------
@app.post("/api/medicines", response_model=dict)
def create_medicine(payload: Medicine):
    new_id = create_document("medicine", payload)
    return {"id": new_id}


@app.get("/api/medicines", response_model=List[dict])
def list_medicines(q: Optional[str] = None, low_stock: Optional[bool] = False, limit: Optional[int] = 100):
    filt = {}
    if q:
        filt = {"$or": [
            {"name": {"$regex": q, "$options": "i"}},
            {"generic_name": {"$regex": q, "$options": "i"}},
            {"sku": {"$regex": q, "$options": "i"}},
        ]}
    if low_stock:
        filt.update({"$expr": {"$lte": ["$stock", "$reorder_level"]}})
    return get_documents("medicine", filt, limit)


# ----------------------------- Prescriptions -------------------------------
@app.post("/api/prescriptions", response_model=dict)
def create_prescription(payload: Prescription):
    new_id = create_document("prescription", payload)
    return {"id": new_id}


@app.get("/api/prescriptions", response_model=List[dict])
def list_prescriptions(status: Optional[str] = None, limit: Optional[int] = 100):
    filt = {"status": status} if status else {}
    return get_documents("prescription", filt, limit)


# ----------------------------- Staff --------------------------------------
@app.post("/api/staff", response_model=dict)
def create_staff(payload: Staff):
    new_id = create_document("staff", payload)
    return {"id": new_id}


@app.get("/api/staff", response_model=List[dict])
def list_staff(role: Optional[str] = None, active: Optional[bool] = None, limit: Optional[int] = 100):
    filt = {}
    if role:
        filt["role"] = role
    if active is not None:
        filt["is_active"] = active
    return get_documents("staff", filt, limit)


# ----------------------------- Suppliers ----------------------------------
@app.post("/api/suppliers", response_model=dict)
def create_supplier(payload: Supplier):
    new_id = create_document("supplier", payload)
    return {"id": new_id}


@app.get("/api/suppliers", response_model=List[dict])
def list_suppliers(q: Optional[str] = None, limit: Optional[int] = 100):
    filt = {}
    if q:
        filt = {"$or": [
            {"name": {"$regex": q, "$options": "i"}},
            {"contact_name": {"$regex": q, "$options": "i"}},
        ]}
    return get_documents("supplier", filt, limit)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
