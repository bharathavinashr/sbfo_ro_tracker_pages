from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from .. import crud, schemas, models

router = APIRouter()


def _calculate_impact(entry, child_impacts) -> tuple:
    """
    Calculate impact value and currency based on:
    1. If child_impacts exist: sum the corresponding nsv_aud or nsv_nzd
    2. Otherwise: use entry's own nsv_aud or nsv_nzd
    3. Based on primary_impact field (AUD/NZD)
    
    Returns: (impact_value, impact_currency)
    """
    primary_impact = entry.primary_impact or ""
    impact_value = None
    impact_currency = primary_impact if primary_impact in ["AUD", "NZD"] else None
    
    if child_impacts:
        # Sum child impacts based on primary_impact type
        total = 0
        for ci in child_impacts:
            if primary_impact == "AUD" and ci.nsv_aud:
                try:
                    total += float(ci.nsv_aud)
                except (ValueError, TypeError):
                    pass
            elif primary_impact == "NZD" and ci.nsv_nzd:
                try:
                    total += float(ci.nsv_nzd)
                except (ValueError, TypeError):
                    pass
        if total != 0:
            impact_value = str(total)
    else:
        # Use entry's own value
        if primary_impact == "AUD" and entry.nsv_aud:
            impact_value = entry.nsv_aud
        elif primary_impact == "NZD" and entry.nsv_nzd:
            impact_value = entry.nsv_nzd
    
    return impact_value, impact_currency


def _entry_to_dict(entry, child_impacts) -> dict:
    impact_value, impact_currency = _calculate_impact(entry, child_impacts)
    primary_impact = entry.primary_impact or ""
    
    return {
        "id": entry.id,
        "originalEntryId": entry.original_entry_id,
        "version": entry.version,
        "creationDate": entry.creation_date,
        "creationDatePeriod": entry.creation_date_period,
        "creationDateYear": entry.creation_date_year,
        "addToForecastByPeriod": entry.add_to_forecast_by_period,
        "addToForecastByYear": entry.add_to_forecast_by_year,
        "division": entry.division,
        "department": entry.department,
        "country": entry.country,
        "channel": entry.channel,
        "subChannel": entry.sub_channel,
        "account": entry.account,
        "brand": entry.brand,
        "brandFamily": entry.brand_family,
        "rAndO": entry.r_and_o,
        "probability": entry.probability,
        "categorisation": entry.categorisation,
        "impactPeriod": entry.impact_period,
        "impactYear": entry.impact_year,
        "nsvAud": entry.nsv_aud,
        "nsvNzd": entry.nsv_nzd,
        "volumeLitres": entry.volume_litres,
        "primaryImpact": entry.primary_impact,
        "owner": entry.owner,
        "creator": entry.creator,
        "modifiedUser": entry.modified_user,
        "status": entry.status,
        "shortDescription": entry.short_description,
        "description": entry.description,
        "impactType": entry.impact_type,
        "volumeCases": entry.volume_cases,
        "impact": impact_value,
        "impactCurrency": impact_currency,
        "lastModified": entry.last_modified.isoformat() + "Z" if entry.last_modified else None,
        "childImpacts": [
            {
                "id": ci.id,
                "impactYear": ci.impact_year,
                "impactPeriod": ci.impact_period,
                "nsvAud": ci.nsv_aud,
                "nsvNzd": ci.nsv_nzd,
                "volumeLitres": ci.volume_litres,
                "volumeCases": ci.volume_cases,
                "impact": ci.nsv_aud if (primary_impact == "AUD" and ci.nsv_aud) else (ci.nsv_nzd if (primary_impact == "NZD" and ci.nsv_nzd) else None),
                "impactCurrency": primary_impact if primary_impact in ["AUD", "NZD"] else None,
            }
            for ci in child_impacts
        ],
    }


@router.get("")
def list_entries(
    db: Session = Depends(get_db),
    division: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    channel: Optional[str] = Query(None),
    sub_channel: Optional[str] = Query(None),
    account: Optional[str] = Query(None),
    brand: Optional[str] = Query(None),
    brand_family: Optional[str] = Query(None),
    categorisation: Optional[str] = Query(None),
    r_and_o: Optional[str] = Query(None),
    probability: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    owner: Optional[str] = Query(None),
    creation_date_period: Optional[str] = Query(None),
    creation_date_year: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    user_departments: Optional[str] = Query(None),  # comma-separated; None = all
):
    filters = {
        "division": division,
        "department": department,
        "country": country,
        "channel": channel,
        "sub_channel": sub_channel,
        "account": account,
        "brand": brand,
        "brand_family": brand_family,
        "categorisation": categorisation,
        "r_and_o": r_and_o,
        "probability": probability,
        "status": status,
        "owner": owner,
        "creation_date_period": creation_date_period,
        "creation_date_year": creation_date_year,
    }
    include_deleted = (role == "System Admin")
    # Department Approver: restrict to their allowed departments (None = all)
    department_in = None
    if role == "Department Approver" and user_departments:
        department_in = [d.strip() for d in user_departments.split(",") if d.strip()]
    entries = crud.get_latest_entries(db, filters, include_deleted=include_deleted, department_in=department_in)
    result = []
    for entry in entries:
        child_impacts = crud.get_child_impacts(db, entry.id)
        result.append(_entry_to_dict(entry, child_impacts))
    return {"entries": result}


@router.post("")
def create_entry(data: schemas.EntryCreate, db: Session = Depends(get_db)):
    entry = crud.create_entry(db, data)
    return {"id": entry.id, "originalEntryId": entry.original_entry_id, "version": entry.version}


@router.put("/{entry_id}")
def update_entry(entry_id: int, data: schemas.EntryUpdate, db: Session = Depends(get_db)):
    entry = crud.update_entry(db, entry_id, data)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"id": entry.id, "originalEntryId": entry.original_entry_id, "version": entry.version}


@router.delete("/{entry_id}")
def delete_entry(entry_id: int, modified_user: Optional[str] = Query(None), db: Session = Depends(get_db)):
    success = crud.delete_entry(db, entry_id, modified_user)
    if not success:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"success": True}


@router.patch("/{entry_id}/status")
def update_status(entry_id: int, body: schemas.StatusUpdateBody, db: Session = Depends(get_db)):
    entry = crud.update_entry_status(db, entry_id, body.status, body.modified_user)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"id": entry.id, "status": entry.status}


@router.patch("/{entry_id}/approve")
def approve_entry(entry_id: int, body: schemas.StatusUpdateBody = None, db: Session = Depends(get_db)):
    modified_user = body.modified_user if body else None
    entry = crud.approve_entry(db, entry_id, modified_user)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"id": entry.id, "status": entry.status}


@router.get("/{entry_id}/status")
def get_entry_status(entry_id: int, db: Session = Depends(get_db)):
    entry = db.query(models.Entry).filter(models.Entry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    # Query the latest version by original_entry_id
    latest = (
        db.query(models.Entry)
        .filter(models.Entry.original_entry_id == entry.original_entry_id)
        .order_by(models.Entry.version.desc())
        .first()
    )
    return {"id": entry.id, "status": latest.status}


@router.get("/{original_entry_id}/history")
def get_history(original_entry_id: int, db: Session = Depends(get_db)):
    versions = crud.get_entry_history(db, original_entry_id)
    result = []
    for entry in versions:
        child_impacts = crud.get_child_impacts(db, entry.id)
        result.append(_entry_to_dict(entry, child_impacts))
    return {"versions": result}
