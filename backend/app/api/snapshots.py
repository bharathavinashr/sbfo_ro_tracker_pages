from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime
import uuid

from ..database import get_db
from ..models import Snapshot, Entry, ChildImpact
from ..crud import get_latest_entries, get_child_impacts

# router = APIRouter(prefix="/api/snapshots", tags=["snapshots"])
router = APIRouter()

MONTH_NAMES = {
    "F01": "January", "F02": "February", "F03": "March", "F04": "April",
    "F05": "May", "F06": "June", "F07": "July", "F08": "August",
    "F09": "September", "F10": "October", "F11": "November", "F12": "December"
}


class SnapshotCreate(BaseModel):
    period: str
    year: str
    ibp_step: str
    is_final: Optional[bool] = False

class SnapshotFinalUpdate(BaseModel):
    is_final: bool = Field(validation_alias="isFinal")
    model_config = ConfigDict(populate_by_name=True)


@router.post("")
def create_snapshot(data: SnapshotCreate, db: Session = Depends(get_db)):
    # Check if a final version already exists for this period, year, and IBP step,
    # regardless of whether the current snapshot being created is marked as final.
    existing_final = (
        db.query(Snapshot)
        .filter(
            Snapshot.period == data.period,
            Snapshot.year == data.year,
            Snapshot.ibp_step == data.ibp_step,
            Snapshot.is_final == True
        )
        .first()
    )
    if existing_final:
        raise HTTPException(
            status_code=400,
            detail=f"A final version for {data.ibp_step} in {data.period} {data.year} already exists. No new snapshots can be created for this period."
        )

    # Determine the next version for this period, year, and IBP step
    max_version = (
        db.query(func.max(Snapshot.version))
        .filter(
            Snapshot.period == data.period,
            Snapshot.year == data.year,
            Snapshot.ibp_step == data.ibp_step
        )
        .scalar()
    )
    new_version = (max_version + 1) if max_version is not None else 0

    # Generate unique snapshot ID and name
    snapshot_id = f"SNAP-{data.year}-{data.period}-{data.ibp_step.replace(' ', '_')}-{uuid.uuid4().hex[:8]}".upper()
    month_name = MONTH_NAMES.get(data.period, data.period)
    snapshot_name = f"{data.ibp_step} - {month_name} {data.year}"
    
    # Get all entries matching the filter criteria
    filters = {"ibp_step": data.ibp_step}
    entries = get_latest_entries(db, filters=filters)
    
    if not entries:
        raise HTTPException(status_code=404, detail="No entries found for the specified filters")
    
    # Create snapshot records for each entry
    snapshots = []
    for entry in entries:
        child_impacts = get_child_impacts(db, entry.id)
        
        # Determine primary impact value for display
        impact_value = None
        vol_impact_value = None

        if child_impacts:
            total_fin = 0
            total_vol = 0
            for ci in child_impacts:
                if entry.primary_impact == "AUD" and ci.nsv_aud:
                    try: total_fin += float(ci.nsv_aud)
                    except: pass
                elif entry.primary_impact == "NZD" and ci.nsv_nzd:
                    try: total_fin += float(ci.nsv_nzd)
                    except: pass
                
                if ci.volume_impact_value:
                    try: total_vol += float(ci.volume_impact_value)
                    except: pass
            
            if total_fin != 0: impact_value = str(total_fin)
            if total_vol != 0: vol_impact_value = str(total_vol)
            if entry.primary_impact == "Volume" and total_vol != 0: impact_value = str(total_vol)
        else:
            if entry.primary_impact == "AUD": impact_value = entry.nsv_aud
            elif entry.primary_impact == "NZD": impact_value = entry.nsv_nzd
            elif entry.primary_impact == "Volume": impact_value = entry.volume_impact_value or entry.volume_litres
            
            vol_impact_value = entry.volume_impact_value

        entry_data = {
            "id": entry.id,
            "original_entry_id": entry.original_entry_id,
            "version": entry.version,
            "creation_date": entry.creation_date,
            "creation_date_period": entry.creation_date_period,
            "creation_date_year": entry.creation_date_year,
            "division": entry.division,
            "ibp_step": entry.ibp_step,
            "country": entry.country,
            "channel": entry.channel,
            "sub_channel": entry.sub_channel,
            "account": entry.account,
            "brand": entry.brand,
            "brand_family": entry.brand_family,
            "r_and_o": entry.r_and_o,
            "probability": entry.probability,
            "categorisation": entry.categorisation,
            "impact_period": entry.impact_period,
            "impact_year": entry.impact_year,
            "nsv_aud": entry.nsv_aud,
            "nsv_nzd": entry.nsv_nzd,
            "volume_litres": entry.volume_litres,
            "volume_cases": entry.volume_cases,
            "owner": entry.owner,
            "creator": entry.creator,
            "status": entry.status,
            "short_description": entry.short_description,
            "description": entry.description,
            "primary_impact": entry.primary_impact,
            "volume_impact_type": entry.volume_impact_type,
            "volume_impact_value": vol_impact_value,
            "impact": impact_value,
        }
        
        snapshot = Snapshot(
            snapshot_id=snapshot_id,
            entry_id=entry.id,
            period=data.period,
            year=data.year,
            ibp_step=data.ibp_step,
            entry_data=entry_data,
            is_final=data.is_final,
            version=new_version,
        )
        snapshots.append(snapshot)
    
    try:
        db.add_all(snapshots)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create snapshot: {str(e)}")
    
    return {
        "snapshot_id": snapshot_id,
        "name": snapshot_name,
        "version": new_version,
        "entries_count": len(snapshots),
        "created_at": datetime.now().isoformat(),
    }


@router.get("")
def get_all_snapshots(db: Session = Depends(get_db)):
    # Get unique snapshots grouped by snapshot_id
    snapshots = (
        db.query(
            Snapshot.snapshot_id,
            Snapshot.period,
            Snapshot.year,
            Snapshot.ibp_step,
            Snapshot.is_final,
            Snapshot.version,
            func.count(Snapshot.id).label("entries_count"),
            func.min(Snapshot.created_at).label("created_at"),
        )
        .group_by(Snapshot.snapshot_id, Snapshot.period, Snapshot.year, Snapshot.ibp_step, Snapshot.is_final, Snapshot.version)
        .order_by(func.min(Snapshot.created_at).desc())
        .all()
    )
    
    result = []
    for snap in snapshots:
        month_name = MONTH_NAMES.get(snap.period, snap.period)
        name = f"{snap.ibp_step} - {month_name} {snap.year}"
        result.append({
            "snapshot_id": snap.snapshot_id,
            "name": name,
            "period": snap.period,
            "year": snap.year,
            "ibp_step": snap.ibp_step,
            "is_final": snap.is_final,
            "entries_count": snap.entries_count,
            "version": snap.version,
            "created_at": snap.created_at.isoformat() if snap.created_at else None,
        })
    
    return {"snapshots": result}


@router.patch("/{snapshot_id}/final")
def toggle_snapshot_final(snapshot_id: str, data: SnapshotFinalUpdate, db: Session = Depends(get_db)):
    # Get the snapshot info from the first record
    first_record = db.query(Snapshot).filter(Snapshot.snapshot_id == snapshot_id).first()
    if not first_record:
        raise HTTPException(status_code=404, detail="Snapshot not found")

    if data.is_final:
        # Check if another snapshot for same period/year/step is already final
        existing_final = (
            db.query(Snapshot)
            .filter(
                Snapshot.period == first_record.period,
                Snapshot.year == first_record.year,
                Snapshot.ibp_step == first_record.ibp_step,
                Snapshot.is_final == True,
                Snapshot.snapshot_id != snapshot_id
            )
            .first()
        )
        if existing_final:
            raise HTTPException(
                status_code=400,
                detail=f"A final version for {first_record.ibp_step} in {first_record.period} {first_record.year} already exists."
            )

    db.query(Snapshot).filter(Snapshot.snapshot_id == snapshot_id).update({"is_final": data.is_final})
    db.commit()
    return {"success": True, "is_final": data.is_final}

@router.get("/{snapshot_id}")
def get_snapshot_by_id(snapshot_id: str, db: Session = Depends(get_db)):
    # Get all snapshot records for this snapshot_id
    snapshot_records = (
        db.query(Snapshot)
        .filter(Snapshot.snapshot_id == snapshot_id)
        .all()
    )
    
    if not snapshot_records:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    
    # Get snapshot metadata from first record
    first_record = snapshot_records[0]
    month_name = MONTH_NAMES.get(first_record.period, first_record.period)
    snapshot_name = f"{first_record.ibp_step} - {month_name} {first_record.year}"
    
    # Get entry IDs from snapshot records
    entry_ids = [snap.entry_id for snap in snapshot_records]
    
    # Fetch actual entries from entries table
    entries = db.query(Entry).filter(Entry.id.in_(entry_ids)).all()
    
    # Convert entries to dict format
    entries_data = []
    for entry in entries:
        # Get child impacts for this entry
        child_impacts = get_child_impacts(db, entry.id)
        child_impacts_data = []
        for ci in child_impacts:
            child_impacts_data.append({
                "id": ci.id,
                "impactYear": ci.impact_year,
                "impactPeriod": ci.impact_period,
                "nsvAud": ci.nsv_aud,
                "nsvNzd": ci.nsv_nzd,
                "volumeLitres": ci.volume_litres,
                "volumeCases": ci.volume_cases,
                "volumeImpactType": entry.volume_impact_type, # Child impacts inherit parent's volume type
                "volumeImpactValue": ci.volume_impact_value,
            })
        
        impact_value = None
        vol_impact_value = None

        if child_impacts:
            total_fin = 0
            total_vol = 0
            for ci in child_impacts:
                if entry.primary_impact == "AUD" and ci.nsv_aud:
                    try: total_fin += float(ci.nsv_aud)
                    except: pass
                elif entry.primary_impact == "NZD" and ci.nsv_nzd:
                    try: total_fin += float(ci.nsv_nzd)
                    except: pass
                if ci.volume_impact_value:
                    try: total_vol += float(ci.volume_impact_value)
                    except: pass
            if total_fin != 0: impact_value = str(total_fin)
            if total_vol != 0: vol_impact_value = str(total_vol)
            if entry.primary_impact == "Volume" and total_vol != 0: impact_value = str(total_vol)
        else:
            if entry.primary_impact == "AUD": impact_value = entry.nsv_aud
            elif entry.primary_impact == "NZD": impact_value = entry.nsv_nzd
            elif entry.primary_impact == "Volume": impact_value = entry.volume_impact_value or entry.volume_litres
            
            vol_impact_value = entry.volume_impact_value

        entries_data.append({
            "id": entry.id,
            "originalEntryId": entry.original_entry_id,
            "version": entry.version,
            "creationDate": entry.creation_date,
            "creationDatePeriod": entry.creation_date_period,
            "creationDateYear": entry.creation_date_year,
            "addToForecastByPeriod": entry.add_to_forecast_by_period,
            "addToForecastByYear": entry.add_to_forecast_by_year,
            "division": entry.division,
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
            "volumeCases": entry.volume_cases,
            "impact": impact_value,
            "primaryImpact": entry.primary_impact,
            "owner": entry.owner,
            "creator": entry.creator,
            "modifiedUser": entry.modified_user,
            "status": entry.status,
            "shortDescription": entry.short_description,
            "description": entry.description,
            "volumeImpactType": entry.volume_impact_type,
            "volumeImpactValue": vol_impact_value,
            "financialImpactType": entry.financial_impact_type,
            "lastModified": entry.last_modified.isoformat() if entry.last_modified else None,
            "childImpacts": child_impacts_data,
        })
    
    return {
        "snapshot": {
            "snapshot_id": snapshot_id,
            "name": snapshot_name,
            "period": first_record.period,
            "year": first_record.year,
            "ibp_step": first_record.ibp_step,
            "version": first_record.version,
            "created_at": first_record.created_at.isoformat() if first_record.created_at else None,
            "entries": entries_data,
        }
    }


@router.delete("/{snapshot_id}")
def delete_snapshot(snapshot_id: str, db: Session = Depends(get_db)):
    # Delete all entries with this snapshot_id
    deleted_count = db.query(Snapshot).filter(Snapshot.snapshot_id == snapshot_id).delete()
    
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    
    db.commit()
    
    return {
        "message": "Snapshot deleted successfully",
        "deleted_entries": deleted_count,
    }
