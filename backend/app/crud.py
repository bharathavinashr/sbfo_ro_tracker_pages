from sqlalchemy.orm import Session
from sqlalchemy import func, cast, String, Text
from . import models, schemas


def get_latest_entries(db: Session, filters: dict = None, include_deleted: bool = False, ibp_step_in: list = None):
    """Return latest version of each entry (max version per original_entry_id)."""
    subq = (
        db.query(
            models.Entry.original_entry_id,
            func.max(models.Entry.version).label("max_ver"),
        )
        .group_by(models.Entry.original_entry_id)
        .subquery()
    )
    query = db.query(models.Entry).join(
        subq,
        (models.Entry.original_entry_id == subq.c.original_entry_id)
        & (models.Entry.version == subq.c.max_ver),
    )
    if not include_deleted:
        query = query.filter(models.Entry.status != "Deleted")
    if filters:
        for field, value in filters.items():
            if not value:
                continue
            
            column = getattr(models.Entry, field)
            # Handle JSON multi-select columns
            if field in ["channel", "sub_channel", "account", "brand", "brand_family"]:
                # For JSON storage, we check if any of the filter values match keys in the JSON object
                filter_list = [value] if isinstance(value, str) else value
                query = query.filter(func.jsonb_exists_any(cast(column, models.database.JSONB), filter_list))
            else:
                query = query.filter(column == value)

    # IBP Step Approver restriction: filter by allowed IBP Steps
    if ibp_step_in:
        query = query.filter(models.Entry.ibp_step.in_(ibp_step_in))
    return query.order_by(models.Entry.last_modified.desc()).all()


def get_entry_by_id(db: Session, entry_id: int):
    return db.query(models.Entry).filter(models.Entry.id == entry_id).first()


def get_entry_history(db: Session, original_entry_id: int):
    return (
        db.query(models.Entry)
        .filter(models.Entry.original_entry_id == original_entry_id)
        .order_by(models.Entry.version.desc())
        .all()
    )


def get_child_impacts(db: Session, entry_id: int):
    return db.query(models.ChildImpact).filter(models.ChildImpact.entry_id == entry_id).all()


def create_entry(db: Session, data: schemas.EntryCreate):
    child_impacts_data = data.child_impacts or []
    entry_data = data.model_dump(exclude={"child_impacts"})
    entry = models.Entry(**entry_data, version=1)
    db.add(entry)
    db.flush()
    entry.original_entry_id = entry.id
    for ci in child_impacts_data:
        child = models.ChildImpact(entry_id=entry.id, **ci.model_dump())
        db.add(child)
    db.commit()
    db.refresh(entry)
    return entry


def _get_max_version(db: Session, original_entry_id: int) -> int:
    return db.query(func.max(models.Entry.version)).filter(
        models.Entry.original_entry_id == original_entry_id
    ).scalar() or 0


def update_entry(db: Session, entry_id: int, data: schemas.EntryUpdate):
    current = db.query(models.Entry).filter(models.Entry.id == entry_id).first()
    if not current:
        return None

    max_version = _get_max_version(db, current.original_entry_id)

    child_impacts_data = data.child_impacts or []
    entry_data = data.model_dump(exclude={"child_impacts"})
    new_entry = models.Entry(
        original_entry_id=current.original_entry_id,
        version=max_version + 1,
        creator=current.creator,
        **entry_data,
    )
    db.add(new_entry)
    db.flush()
    for ci in child_impacts_data:
        child = models.ChildImpact(entry_id=new_entry.id, **ci.model_dump())
        db.add(child)
    db.commit()
    db.refresh(new_entry)
    return new_entry


def delete_entry(db: Session, entry_id: int, modified_user: str = None):
    """Soft delete: create a new version with status='Deleted'."""
    result = _new_version_with_status(db, entry_id, "Deleted", modified_user)
    return result is not None


def _new_version_with_status(db: Session, entry_id: int, new_status: str, modified_user: str = None):
    """Create a new version of an entry with only the status changed."""
    current = db.query(models.Entry).filter(models.Entry.id == entry_id).first()
    if not current:
        return None

    max_version = _get_max_version(db, current.original_entry_id)

    # Get all column names for the Entry model to copy values dynamically
    columns = models.Entry.__table__.columns.keys()
    # Exclude fields that should be new or modified
    exclude = {'id', 'version', 'last_modified', 'created_at', 'status', 'modified_user'}
    
    entry_dict = {col: getattr(current, col) for col in columns if col not in exclude}
    
    new_entry = models.Entry(
        version=max_version + 1,
        status=new_status,
        modified_user=modified_user,
        **entry_dict
    )
    db.add(new_entry)
    db.flush()

    for ci in db.query(models.ChildImpact).filter(models.ChildImpact.entry_id == current.id).all():
        db.add(models.ChildImpact(
            entry_id=new_entry.id,
            impact_year=ci.impact_year,
            impact_period=ci.impact_period,
            nsv_aud=ci.nsv_aud,
            nsv_nzd=ci.nsv_nzd,
            volume_litres=ci.volume_litres,
            volume_cases=ci.volume_cases,
        ))

    db.commit()
    db.refresh(new_entry)
    return new_entry


def update_entry_status(db: Session, entry_id: int, new_status: str, modified_user: str = None):
    return _new_version_with_status(db, entry_id, new_status, modified_user)


def approve_entry(db: Session, entry_id: int, modified_user: str = None):
    return _new_version_with_status(db, entry_id, "Approved", modified_user)


def get_lookup_options(db: Session, category: str, parent_value=None):
    q = db.query(models.LookupOption).filter(
        models.LookupOption.category == category,
        models.LookupOption.is_active == True,
    )
    if parent_value:
        # Handle both list and comma-separated string from query params
        if isinstance(parent_value, str):
            parent_list = [v.strip() for v in parent_value.split(",") if v.strip()]
        else:
            parent_list = parent_value
        
        if parent_list:
            q = q.filter(models.LookupOption.parent_value.in_(parent_list))
        else:
            q = q.filter(models.LookupOption.parent_value == None)
    else:
        q = q.filter(models.LookupOption.parent_value == None)
    return q.order_by(models.LookupOption.sort_order, models.LookupOption.value).all()


def get_divisions(db: Session):
    """Get distinct divisions from ro_products table."""
    return (
        db.query(models.ROProduct.division)
        .distinct()
        .order_by(models.ROProduct.division)
        .all()
    )


def get_brands_by_division(db: Session, division: str):
    """Get distinct brand names from ro_products table filtered by division."""
    rows = (
        db.query(models.ROProduct.brand_code, models.ROProduct.brand_name)
        .filter(models.ROProduct.division == division)
        .distinct()
        .order_by(models.ROProduct.brand_name)
        .all()
    )
    return [{"code": r[0], "name": r[1]} for r in rows]


def get_brand_families_by_brands(db: Session, brand_names: list):
    """Get distinct brand families from ro_products table filtered by list of brand names."""
    rows = (
        db.query(models.ROProduct.brand_family_code, models.ROProduct.brand_family)
        .filter(models.ROProduct.brand_name.in_(brand_names))
        .distinct()
        .order_by(models.ROProduct.brand_family)
        .all()
    )
    return [{"code": r[0], "name": r[1]} for r in rows]


def get_product_codes(db: Session, division: str, brand_name: str, brand_family):
    """Get brand_code and brand_family_code for a product.

    Handles both single brand_family (string) and multiple (list).
    Returns the unique brand_code and a list of unique brand_family_codes.
    """
    # Handle brand_family as either string or list
    brand_families = brand_family if isinstance(brand_family, list) else [brand_family]
    
    # Remove empty strings
    brand_families = [bf for bf in brand_families if bf]
    
    if not brand_families:
        return {
            "brand_code": None,
            "brand_family_code": None,
        }
    
    # Query for products matching division and brand_name
    products = (
        db.query(models.ROProduct)
        .filter(
            models.ROProduct.division == division,
            models.ROProduct.brand_name == brand_name,
            models.ROProduct.brand_family.in_(brand_families),
        )
        .all()
    )

    if products:
        # Brand code is typically the same for all families of the same brand
        brand_codes = list(dict.fromkeys(p.brand_code for p in products if p.brand_code))
        family_codes = list(dict.fromkeys(p.brand_family_code for p in products if p.brand_family_code))
        return {
            "brand_code": brand_codes[0] if brand_codes else None,
            "brand_family_code": family_codes,
        }

    return {
        "brand_code": None,
        "brand_family_code": None,
    }


def get_all_users(db: Session):
    return (
        db.query(models.AppUser)
        .filter(models.AppUser.is_active == True)
        .order_by(models.AppUser.email)
        .all()
    )


def get_channels_by_division(db: Session, division: str):
    """Get distinct channels (code and name) from ro_customers table filtered by division."""
    rows = (
        db.query(models.ROCustomer.channel_code, models.ROCustomer.channel_name)
        .filter(models.ROCustomer.division == division)
        .distinct()
        .order_by(models.ROCustomer.channel_name)
        .all()
    )
    return [{"code": r[0], "name": r[1]} for r in rows]


def get_subchannels_by_division_and_channel(db: Session, division: str, channel_code: str):
    """Get distinct subchannels (code and name) filtered by division and channel."""
    rows = (
        db.query(models.ROCustomer.subchannel_code, models.ROCustomer.subchannel_name)
        .filter(
            models.ROCustomer.division == division,
            models.ROCustomer.channel_code == channel_code
        )
        .distinct()
        .order_by(models.ROCustomer.subchannel_name)
        .all()
    )
    return [{"code": r[0], "name": r[1]} for r in rows]


def get_accounts_by_division_and_subchannel(db: Session, division: str, subchannel_code: str):
    """Get distinct accounts (code and name) filtered by division and subchannel."""
    rows = (
        db.query(models.ROCustomer.account_code, models.ROCustomer.account_name)
        .filter(
            models.ROCustomer.division == division,
            models.ROCustomer.subchannel_code == subchannel_code
        )
        .distinct()
        .order_by(models.ROCustomer.account_name)
        .all()
    )
    return [{"code": r[0], "name": r[1]} for r in rows]


def get_channel_and_subchannel_by_account(db: Session, division: str, account_code: str):
    """Get channel and subchannel for a specific account."""
    row = (
        db.query(
            models.ROCustomer.channel_code,
            models.ROCustomer.channel_name,
            models.ROCustomer.subchannel_code,
            models.ROCustomer.subchannel_name
        )
        .filter(
            models.ROCustomer.division == division,
            models.ROCustomer.account_code == account_code
        )
        .first()
    )
    if row:
        return {
            "channel_code": row[0],
            "channel_name": row[1],
            "subchannel_code": row[2],
            "subchannel_name": row[3]
        }
    return None
