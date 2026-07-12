import json
from pydantic import BaseModel, field_validator
from typing import Optional, List, Any, Dict, Union
from datetime import datetime


def normalize_division_value(value: Any) -> Any:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, tuple):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return value.strip() or []
    if isinstance(value, dict):
        return [str(item).strip() for item in value.values() if str(item).strip()]
    return [str(value).strip()] if str(value).strip() else []


def serialize_division_value(value: Any) -> Any:
    normalized = normalize_division_value(value)
    if isinstance(normalized, list):
        return json.dumps(normalized, separators=(",", ":")) if len(normalized) > 1 else (normalized[0] if normalized else [])
    return normalized


class ChildImpactBase(BaseModel):
    impact_year: str
    impact_period: str
    nsv_aud: Optional[str] = None
    nsv_nzd: Optional[str] = None
    volume_litres: Optional[str] = None
    volume_cases: Optional[str] = None
    volume_impact_value: Optional[str] = None
    gp_aud: Optional[str] = None
    gp_nzd: Optional[str] = None


class ChildImpactOut(ChildImpactBase):
    id: int
    model_config = {"from_attributes": True}


class EntryBase(BaseModel):
    creation_date: Optional[str] = None
    creation_date_period: Optional[str] = None
    creation_date_year: Optional[str] = None
    add_to_forecast_by_period: Optional[str] = None
    add_to_forecast_by_year: Optional[str] = None
    division: Union[str, List[str], Dict[str, str]]
    ibp_step: Optional[str] = None
    country: Dict[str, str]  # Map: {company_code: country_name}
    channel: Dict[str, str]  # Map: {channel_code: channel_name}
    sub_channel: Dict[str, str]  # Map: {subchannel_code: subchannel_name}
    account: Dict[str, str]  # Map: {account_code: account_name}
    brand: Dict[str, str]
    brand_family: Optional[Dict[str, str]] = None
    r_and_o: str
    probability: str
    categorisation: str
    impact_period: Optional[str] = None
    impact_year: Optional[str] = None
    nsv_aud: Optional[str] = None
    nsv_nzd: Optional[str] = None
    volume_litres: Optional[str] = None
    primary_impact: Optional[str] = None
    owner: str
    modified_user: Optional[str] = None
    status: Optional[str] = "Open"
    short_description: Optional[str] = None
    description: Optional[str] = None
    financial_impact_type: Optional[str] = "NSV"
    volume_cases: Optional[str] = None
    volume_impact_type: Optional[str] = None
    volume_impact_value: Optional[str] = None

    # NEW FIELDS
    fixed_nsv_gp_ratio: Optional[str] = None
    fixed_nsv_vol_ratio: Optional[str] = None
    net_financial_impact_value: Optional[str] = None

    @field_validator("division", mode="before")
    @classmethod
    def validate_division(cls, value: Any) -> Any:
        return normalize_division_value(value)


class EntryCreate(EntryBase):
    creator: Optional[str] = None
    child_impacts: Optional[List[ChildImpactBase]] = []


class EntryUpdate(EntryBase):
    child_impacts: Optional[List[ChildImpactBase]] = []


class StatusUpdateBody(BaseModel):
    status: str
    modified_user: Optional[str] = None


class EntryOut(EntryBase):
    id: int
    original_entry_id: Optional[int] = None
    version: int
    creator: Optional[str] = None
    last_modified: Optional[datetime] = None
    child_impacts: List[ChildImpactOut] = []
    model_config = {"from_attributes": True}


class UserOut(BaseModel):
    id: int
    email: str
    display_name: Optional[str] = None
    role: int
    role_name: Optional[str] = None
    ibp_steps: Optional[List[str]] = None
    is_active: bool = True
    country: Optional[Any] = None
    division: Optional[Any] = None
    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    email: str
    display_name: Optional[str] = None
    role: int
    role_name: Optional[str] = None
    ibp_steps: Optional[List[str]] = None
    is_active: bool = True
    country: Optional[Any] = None
    division: Optional[Any] = None


class UserUpdate(BaseModel):
    email: Optional[str] = None
    display_name: Optional[str] = None
    role: Optional[int] = None
    role_name: Optional[str] = None
    ibp_steps: Optional[List[str]] = None
    is_active: Optional[bool] = None
    country: Optional[Any] = None
    division: Optional[Any] = None


class LookupOptionOut(BaseModel):
    value: str
    label: str
    model_config = {"from_attributes": True}