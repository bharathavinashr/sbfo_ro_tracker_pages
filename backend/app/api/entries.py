from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from ..database import get_db
from .. import crud, schemas, models

router = APIRouter()


def _calculate_impact(entry, child_impacts) -> tuple:
    primary_impact = entry.primary_impact or ""
    impact_value = None
    impact_currency = primary_impact if primary_impact in ["AUD", "NZD"] else None
    vol_impact_value = None
    gp_value = None
    
    if child_impacts:
        total_fin = 0
        total_vol = 0
        total_gp = 0
        for ci in child_impacts:
            if primary_impact == "AUD" and ci.nsv_aud:
                try: total_fin += float(ci.nsv_aud)
                except (ValueError, TypeError): pass
            elif primary_impact == "NZD" and ci.nsv_nzd:
                try: total_fin += float(ci.nsv_nzd)
                except (ValueError, TypeError): pass

            if ci.volume_impact_value:
                try: total_vol += float(ci.volume_impact_value)
                except (ValueError, TypeError): pass

            gp_col = ci.gp_nzd if primary_impact == "NZD" else ci.gp_aud
            if gp_col:
                try: total_gp += float(gp_col)
                except (ValueError, TypeError): pass

        if total_fin != 0:
            impact_value = str(total_fin)
        if total_vol != 0:
            vol_impact_value = str(total_vol)
        if total_gp != 0:
            gp_value = str(total_gp)
    else:
        if primary_impact == "AUD" and entry.nsv_aud:
            impact_value = entry.nsv_aud
        elif primary_impact == "NZD" and entry.nsv_nzd:
            impact_value = entry.nsv_nzd
        vol_impact_value = entry.volume_impact_value
        gp_value = entry.net_financial_impact_value
    
    return impact_value, impact_currency, vol_impact_value, gp_value


def _entry_to_dict(entry, child_impacts) -> dict:
    impact_value, impact_currency, vol_impact_value, gp_value = _calculate_impact(entry, child_impacts)
    primary_impact = entry.primary_impact or ""
    
    division_value = entry.division
    if isinstance(division_value, (list, tuple)):
        division_display = list(division_value)
    elif isinstance(division_value, dict):
        division_display = list(division_value.values())
    elif isinstance(division_value, str):
        division_display = division_value
    else:
        division_display = division_value

    return {
        "id": entry.id,
        "originalEntryId": entry.original_entry_id,
        "version": entry.version,
        "creationDate": entry.creation_date,
        "creationDatePeriod": entry.creation_date_period,
        "creationDateYear": entry.creation_date_year,
        "addToForecastByPeriod": entry.add_to_forecast_by_period,
        "addToForecastByYear": entry.add_to_forecast_by_year,
        "division": division_display,
        "ibpStep": entry.ibp_step,
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
        "financialImpactType": entry.financial_impact_type,
        "volumeCases": entry.volume_cases,
        "volumeImpactType": entry.volume_impact_type,
        "volumeImpactValue": vol_impact_value,
        "impact": impact_value,
        "impactCurrency": impact_currency,
        "lastModified": entry.last_modified.isoformat() + "Z" if entry.last_modified else None,
        
        # NEW MAPPINGS
        "fixedNsvGpRatio": entry.fixed_nsv_gp_ratio,
        "fixedNsvVolRatio": entry.fixed_nsv_vol_ratio,
        "netFinancialImpactValue": gp_value,
        
        "childImpacts": [
            {
                "id": ci.id,
                "impactYear": ci.impact_year,
                "impactPeriod": ci.impact_period,
                "nsvAud": ci.nsv_aud,
                "nsvNzd": ci.nsv_nzd,
                "volumeLitres": ci.volume_litres,
                "volumeCases": ci.volume_cases,
                "volumeImpactType": entry.volume_impact_type, # Child impacts inherit parent's volume type
                "volumeImpactValue": ci.volume_impact_value,
                "impact": ci.nsv_aud if (primary_impact == "AUD" and ci.nsv_aud) else (ci.nsv_nzd if (primary_impact == "NZD" and ci.nsv_nzd) else None),
                "impactCurrency": primary_impact if primary_impact in ["AUD", "NZD"] else None,
                "gpAud": ci.gp_aud,
                "gpNzd": ci.gp_nzd,
            }
            for ci in child_impacts
        ],
    }


@router.get("")
def list_entries(
    db: Session = Depends(get_db),
    division: Optional[List[str]] = Query(None),
    ibp_step: Optional[List[str]] = Query(None),
    country: Optional[List[str]] = Query(None),
    channel: Optional[List[str]] = Query(None),
    sub_channel: Optional[List[str]] = Query(None),
    account: Optional[List[str]] = Query(None),
    brand: Optional[List[str]] = Query(None),
    brand_family: Optional[List[str]] = Query(None),
    categorisation: Optional[List[str]] = Query(None),
    r_and_o: Optional[List[str]] = Query(None),
    probability: Optional[List[str]] = Query(None),
    status: Optional[List[str]] = Query(None),
    owner: Optional[str] = Query(None),
    creation_date_period: Optional[List[str]] = Query(None),
    creation_date_year: Optional[List[str]] = Query(None),
    role: Optional[str] = Query(None),
    user_ibp_steps: Optional[str] = Query(None),  # comma-separated; None = all
):
    filters = {
        "division": division,
        "ibp_step": ibp_step,
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
    # IBP Step Approver: restrict to their allowed IBP Steps (None = all)
    ibp_step_in = None
    if role == "IBP Step Approver" and user_ibp_steps:
        ibp_step_in = [d.strip() for d in user_ibp_steps.split(",") if d.strip()]
    entries = crud.get_latest_entries(db, filters, include_deleted=include_deleted, ibp_step_in=ibp_step_in)
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