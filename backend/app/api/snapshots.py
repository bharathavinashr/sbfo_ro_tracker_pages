from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime
import uuid

from ..database import get_db
from ..models import Snapshot, Entry
from ..crud import get_latest_entries, get_child_impacts, get_final_snapshots_for_period_year, get_all_entries_for_period_year, get_snapshot_by_params, update_snapshot_is_final

# router = APIRouter(prefix="/api/snapshots", tags=["snapshots"])
router = APIRouter()

# Define known IBP steps and the special "All IBP Steps" name
ALL_IBP_STEP_NAME = "All"
KNOWN_IBP_STEPS = ["Portfolio Review", "Supply Review", "Demand Review", "A&P (Pre-Exec)", "Overheads (Pre-Exec)"]


class SnapshotCreate(BaseModel):
    period: str
    year: str
    ibp_step: str
    is_final: Optional[bool] = False

class SnapshotFinalUpdate(BaseModel):
    is_final: bool = Field(validation_alias="isFinal")
    model_config = ConfigDict(populate_by_name=True)

# Helper function to calculate impact values (can be moved to crud or utils if needed elsewhere)
def _calculate_entry_impacts(entry, child_impacts):
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
    return impact_value, vol_impact_value

def _generate_entry_data_for_snapshot(entry, child_impacts, impact_value, vol_impact_value):
    # Serialize child impacts into a list of dictionaries
    child_impacts_serialized = []
    if child_impacts:
        for ci in child_impacts:
            child_impacts_serialized.append({
                "id": ci.id,
                "impact_year": ci.impact_year,
                "impact_period": ci.impact_period,
                "nsv_aud": ci.nsv_aud,
                "nsv_nzd": ci.nsv_nzd,
                "volume_litres": ci.volume_litres,
                "volume_cases": ci.volume_cases,
                "volume_impact_value": ci.volume_impact_value,
            })

    return {
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
        "child_impacts": child_impacts_serialized,  # Added this line to capture child impacts
    }


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
    new_version = (max_version + 1) if max_version is not None else 1

    # Generate unique snapshot ID and name
    snapshot_id = f"SNAP-{data.year}-{data.period}-{data.ibp_step.replace(' ', '_')}-{uuid.uuid4().hex[:8]}".upper()
    snapshot_name = f"{data.ibp_step} - {data.period} {data.year}"
    
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
        impact_value, vol_impact_value = _calculate_entry_impacts(entry, child_impacts)
        entry_data = _generate_entry_data_for_snapshot(entry, child_impacts, impact_value, vol_impact_value)
        
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
        db.refresh(snapshots[0]) # Refresh one to get created_at for the response
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create snapshot: {e}")
    
    # After creating an individual snapshot, check if an "All IBP Steps" snapshot needs to be created/updated
    if data.is_final and data.ibp_step in KNOWN_IBP_STEPS:
        _reconcile_all_ibp_snapshot(db, data.period, data.year)
    
    return {
        "snapshot_id": snapshot_id,
        "name": snapshot_name,
        "version": new_version,
        "entries_count": len(snapshots),
        "created_at": snapshots[0].created_at.isoformat(), # Use created_at from the actual snapshot
    }

def _reconcile_all_ibp_snapshot(db: Session, period: str, year: str):
    """
    Reconciles the "All IBP Steps" snapshot for a given period/year.
    If all KNOWN_IBP_STEPS have a final snapshot, it creates/updates the "All IBP Steps" snapshot as final.
    Otherwise, it ensures any existing "All IBP Steps" snapshot for that period/year is not final.
    """
    final_snapshots_for_period = get_final_snapshots_for_period_year(db, period, year)
    final_ibp_steps = {s.ibp_step for s in final_snapshots_for_period if s.ibp_step != ALL_IBP_STEP_NAME}
    
    if not all(step in final_ibp_steps for step in KNOWN_IBP_STEPS):
        # If not all IBP steps are final, ensure the "All IBP Steps" snapshot is not final
        existing_all_snapshot = get_snapshot_by_params(db, period, year, ALL_IBP_STEP_NAME, is_final=True)
        if existing_all_snapshot:
            update_snapshot_is_final(db, existing_all_snapshot.snapshot_id, False)
            print(f"Un-finalized '{ALL_IBP_STEP_NAME}' snapshot for {period} {year} because not all individual steps are final.")
        return

    # If all IBP steps are final, proceed to create/update the "All IBP Steps" snapshot as final
    print(f"All IBP steps are final for {period} {year}. Creating/updating '{ALL_IBP_STEP_NAME}' snapshot.")
    
    # Use the entries from the final snapshots already identified
    individual_final_snapshots = [s for s in final_snapshots_for_period if s.ibp_step != ALL_IBP_STEP_NAME]

    if not individual_final_snapshots:
        print(f"No entries found in final individual snapshots for {period} {year}.")
        return

    # Determine the next version for the "All IBP Steps" snapshot
    max_version = (
        db.query(func.max(Snapshot.version))
        .filter(
            Snapshot.period == period,
            Snapshot.year == year,
            Snapshot.ibp_step == ALL_IBP_STEP_NAME
        )
        .scalar()
    )
    new_version = (max_version + 1) if max_version is not None else 1

    # Generate unique snapshot ID and name for the "All IBP Steps" snapshot
    snapshot_id = f"SNAP-{year}-{period}-{ALL_IBP_STEP_NAME.replace(' ', '_')}-{uuid.uuid4().hex[:8]}".upper()
    snapshot_name = f"{ALL_IBP_STEP_NAME} - {period} {year}"

    snapshots_to_add = []
    for snap_record in individual_final_snapshots:
        # Reuse the entry data from the individual snapshot to ensure consistency
        snapshot = Snapshot(
            snapshot_id=snapshot_id,
            entry_id=snap_record.entry_id,
            period=period,
            year=year,
            ibp_step=ALL_IBP_STEP_NAME,
            entry_data=snap_record.entry_data,
            is_final=True, # The "All" snapshot is always final if created this way
            version=new_version,
        )
        snapshots_to_add.append(snapshot)
    
    try:
        # Delete any existing "All IBP Steps" snapshots for this period/year before adding new ones
        db.query(Snapshot).filter(
            Snapshot.period == period,
            Snapshot.year == year,
            Snapshot.ibp_step == ALL_IBP_STEP_NAME
        ).delete(synchronize_session=False)
        
        db.add_all(snapshots_to_add)
        db.commit()
        print(f"Successfully created/updated '{ALL_IBP_STEP_NAME}' snapshot: {snapshot_name} (version {new_version})")
    except Exception as e:
        db.rollback()
        print(f"Failed to create/update '{ALL_IBP_STEP_NAME}' snapshot: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create/update '{ALL_IBP_STEP_NAME}' snapshot: {str(e)}")


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
        name = f"{snap.ibp_step} - {snap.period} {snap.year}"
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
    
    _reconcile_all_ibp_snapshot(db, first_record.period, first_record.year)
    
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
    snapshot_name = f"{first_record.ibp_step} - {first_record.period} {first_record.year}"
    
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
                "impact": ci.nsv_aud if (entry.primary_impact == "AUD" and ci.nsv_aud) else (ci.nsv_nzd if (entry.primary_impact == "NZD" and ci.nsv_nzd) else None),
                "impactCurrency": entry.primary_impact if entry.primary_impact in ["AUD", "NZD"] else None,
            })
        
        impact_value, vol_impact_value = _calculate_entry_impacts(entry, child_impacts)

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
            "impactCurrency": entry.primary_impact if entry.primary_impact in ["AUD", "NZD"] else None,
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
    # Get the snapshot info from the first record before deleting
    first_record = db.query(Snapshot).filter(Snapshot.snapshot_id == snapshot_id).first()
    
    # Delete all entries with this snapshot_id
    deleted_count = db.query(Snapshot).filter(Snapshot.snapshot_id == snapshot_id).delete()
    
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    db.commit()
    
    # Reconcile the "All IBP Steps" snapshot if an individual IBP step snapshot was deleted
    if first_record and first_record.ibp_step in KNOWN_IBP_STEPS and first_record.ibp_step != ALL_IBP_STEP_NAME:
        _reconcile_all_ibp_snapshot(db, first_record.period, first_record.year)
    
    return {
        "message": "Snapshot deleted successfully",
        "deleted_entries": deleted_count,
    }
