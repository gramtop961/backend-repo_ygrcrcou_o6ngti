"""
Database Schemas for Pharmacy Management

Each Pydantic model below represents a MongoDB collection. The collection name
is the lowercase of the class name (e.g., Medicine -> "medicine").
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from datetime import date


class Medicine(BaseModel):
    name: str = Field(..., description="Medicine name")
    generic_name: Optional[str] = Field(None, description="Generic/chemical name")
    category: Optional[str] = Field(None, description="Therapeutic category")
    manufacturer: Optional[str] = Field(None, description="Manufacturer name")
    sku: Optional[str] = Field(None, description="Internal SKU / barcode")
    batch_number: Optional[str] = Field(None, description="Batch/Lot number")
    expiry_date: Optional[date] = Field(None, description="Expiry date (YYYY-MM-DD)")
    price: float = Field(..., ge=0, description="Selling price")
    cost_price: Optional[float] = Field(None, ge=0, description="Cost price")
    stock: int = Field(0, ge=0, description="Units in stock")
    reorder_level: int = Field(10, ge=0, description="Reorder threshold")
    unit: Literal["tablet", "capsule", "bottle", "syrup", "ml", "mg", "g", "pack", "unit"] = Field(
        "unit", description="Unit of measure"
    )
    taxable: bool = Field(True, description="Whether item is taxable")
    tax_rate: float = Field(0.0, ge=0, le=100, description="Tax rate percentage")
    notes: Optional[str] = Field(None, description="Additional notes")


class PrescriptionItem(BaseModel):
    medicine_id: str = Field(..., description="Reference to medicine _id")
    name: Optional[str] = Field(None, description="Snapshot of medicine name")
    quantity: int = Field(..., ge=1)
    unit_price: float = Field(..., ge=0)


class Prescription(BaseModel):
    number: Optional[str] = Field(None, description="Prescription number / receipt")
    patient_name: str = Field(...)
    patient_phone: Optional[str] = Field(None)
    doctor_name: Optional[str] = Field(None)
    items: List[PrescriptionItem] = Field(default_factory=list)
    subtotal: float = Field(0, ge=0)
    tax: float = Field(0, ge=0)
    total: float = Field(0, ge=0)
    status: Literal["pending", "dispensed", "cancelled"] = Field("pending")
    payment_method: Optional[Literal["cash", "card", "upi", "insurance"]] = None


class Staff(BaseModel):
    name: str
    email: str
    role: Literal["Admin", "Pharmacist", "Sales", "Accountant"] = "Sales"
    phone: Optional[str] = None
    is_active: bool = True


class Supplier(BaseModel):
    name: str
    contact_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    gst_number: Optional[str] = None


# Map all schemas for easy discovery by tools/clients
SCHEMA_REGISTRY = {
    "medicine": Medicine.model_json_schema(),
    "prescription": Prescription.model_json_schema(),
    "staff": Staff.model_json_schema(),
    "supplier": Supplier.model_json_schema(),
}
