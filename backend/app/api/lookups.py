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


@router.get("/countries")
def get_countries(
    division: str = Query(..., description="Division name"),
    db: Session = Depends(get_db)
):
    """Get all countries from ro_customers table for a specific division.
    Returns countries with company_code as key and country_name as value."""
    countries = crud.get_countries_by_division(db, division)
    return {"options": [{"value": c["code"], "label": c["country"]} for c in countries]}


@router.get("/brands")
def get_brands(
    division: str = Query(..., description="Division name"),
    country: Optional[str] = Query(None, description="Country name"),
    db: Session = Depends(get_db),
):
    """Get brands (code and name) for a specific division."""
    brands = crud.get_brands_by_division(db, division, country)
    return {"options": [{"value": b["code"], "label": b["name"]} for b in brands]}


@router.get("/brand-families")
def get_brand_families(
    brand_names: List[str] = Query(..., description="List of brand names"),
    country: Optional[str] = Query(None, description="Country name"),
    division: Optional[str] = Query(None, description="Division name"),
    db: Session = Depends(get_db),
):
    """Get brand families (code and name) for a list of brands."""
    families = crud.get_brand_families_by_brands(db, brand_names, country, division)
    return {"options": [{"value": f["code"], "label": f["name"]} for f in families]}


@router.get("/channels")
def get_channels(
    division: str = Query(..., description="Division name"),
    country: Optional[str] = Query(None, description="Country name"),
    db: Session = Depends(get_db),
):
    """Get channels (code and name) for a specific division from ro_customers table."""
    channels = crud.get_channels_by_division(db, division, country)
    return {"options": [{"value": c["code"], "label": c["name"]} for c in channels]}


@router.get("/subchannels")
def get_subchannels(
    division: str = Query(..., description="Division name"),
    channel_code: Optional[str] = Query(None, description="Channel code"),
    country: Optional[str] = Query(None, description="Country name"),
    db: Session = Depends(get_db),
):
    """Get subchannels (code and name) for a specific division and channel."""
    subchannels = crud.get_subchannels_by_division_and_channel(db, division, channel_code, country)
    return {"options": [{"value": s["code"], "label": s["name"]} for s in subchannels]}


@router.get("/accounts")
def get_accounts(
    division: str = Query(..., description="Division name"),
    subchannel_code: Optional[str] = Query(None, description="Subchannel code"),
    country: Optional[str] = Query(None, description="Country name"),
    db: Session = Depends(get_db),
):
    """Get accounts (code and name) for a specific division and subchannel."""
    accounts = crud.get_accounts_by_division_and_subchannel(db, division, subchannel_code, country)
    return {"options": [{"value": a["code"], "label": a["name"]} for a in accounts]}


@router.get("/subchannel-details")
def get_subchannel_details(
    division: str = Query(..., description="Division name"),
    subchannel_code: str = Query(..., description="Subchannel code"),
    country: Optional[str] = Query(None, description="Country name"),
    db: Session = Depends(get_db),
):
    """Get channel details for a specific subchannel (for auto-population)."""
    details = crud.get_channel_by_subchannel(db, division, subchannel_code, country)
    if details:
        return {"channel": details}
    return {"channel": None}


@router.get("/account-details")
def get_account_details(
    division: str = Query(..., description="Division name"),
    account_code: str = Query(..., description="Account code"),
    country: Optional[str] = Query(None, description="Country name"),
    db: Session = Depends(get_db),
):
    """Get channel and subchannel details for a specific account (for auto-population)."""
    details = crud.get_channel_and_subchannel_by_account(db, division, account_code, country)
    if details:
        return {
            "channel": {"code": details["channel_code"], "name": details["channel_name"]},
            "subchannel": {"code": details["subchannel_code"], "name": details["subchannel_name"]}
        }
    return {"channel": None, "subchannel": None}
