from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from ..database import get_db
from .. import crud

router = APIRouter()


@router.get("")
def get_lookup_options(
    category: str = Query(..., description="Lookup category, e.g. 'channel', 'sub_channel'"),
    parent_value: Optional[str] = Query(None, description="Parent value for cascade filtering"),
    db: Session = Depends(get_db),
):
    rows = crud.get_lookup_options(db, category, parent_value)
    return {"options": [{"value": r.value, "label": r.value} for r in rows]}


@router.get("/divisions")
def get_divisions(db: Session = Depends(get_db)):
    """Get all divisions from ro_products table."""
    rows = crud.get_divisions(db)
    return {"options": [{"value": r[0], "label": r[0]} for r in rows]}


@router.get("/brands")
def get_brands(
    division: str = Query(..., description="Division name"),
    db: Session = Depends(get_db),
):
    """Get brands (code and name) for a specific division."""
    brands = crud.get_brands_by_division(db, division)
    return {"options": [{"value": b["code"], "label": b["name"]} for b in brands]}


@router.get("/brand-families")
def get_brand_families(
    brand_names: List[str] = Query(..., description="List of brand names"),
    db: Session = Depends(get_db),
):
    """Get brand families (code and name) for a list of brands."""
    families = crud.get_brand_families_by_brands(db, brand_names)
    return {"options": [{"value": f["code"], "label": f["name"]} for f in families]}
