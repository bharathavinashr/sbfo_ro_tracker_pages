from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
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
    """Get brands for a specific division from ro_products table."""
    rows = crud.get_brands_by_division(db, division)
    return {"options": [{"value": r[0], "label": r[0]} for r in rows]}


@router.get("/brand-families")
def get_brand_families(
    brand_name: str = Query(..., description="Brand name"),
    db: Session = Depends(get_db),
):
    """Get brand families for a specific brand from ro_products table."""
    rows = crud.get_brand_families_by_brand(db, brand_name)
    return {"options": [{"value": r[0], "label": r[0]} for r in rows]}
