from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas

router = APIRouter()

ROLE_NAMES = {0: "Admin", 1: "Creator/Owner", 2: "IBP-Step Approver", 3: "Finance Approver", 4: "Viewer"}


def _serialize(u):
    return {
        "id": u.id,
        "email": u.email,
        "display_name": u.display_name,
        "role": u.role,
        "role_name": u.role_name,
        "ibp_steps": u.ibp_steps,
        "is_active": u.is_active,
        "country": u.country,
        "division": u.division,
    }


@router.get("")
def list_users(db: Session = Depends(get_db)):
    return {"users": [_serialize(u) for u in crud.get_all_users(db)]}


@router.post("", status_code=201)
def create_user(body: schemas.UserCreate, db: Session = Depends(get_db)):
    if not body.role_name:
        body.role_name = ROLE_NAMES.get(body.role)
    user = crud.create_user(db, body)
    return _serialize(user)


@router.put("/{user_id}")
def update_user(user_id: int, body: schemas.UserUpdate, db: Session = Depends(get_db)):
    if body.role is not None and body.role_name is None:
        body.role_name = ROLE_NAMES.get(body.role)
    user = crud.update_user(db, user_id, body)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return _serialize(user)


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    if not crud.delete_user(db, user_id):
        raise HTTPException(status_code=404, detail="User not found")
