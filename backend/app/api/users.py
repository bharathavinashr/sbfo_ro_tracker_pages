from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud

router = APIRouter()


@router.get("")
def list_users(db: Session = Depends(get_db)):
    users = crud.get_all_users(db)
    return {
        "users": [
            {"id": u.id, "email": u.email, "display_name": u.display_name, "role": u.role, "ibp_steps": u.ibp_steps, "role_name": u.role_name, "country": u.country, "division": u.division}
            for u in users
        ]
    }
