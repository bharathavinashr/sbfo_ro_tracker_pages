from pydantic import BaseModel
from typing import Optional, List, Any, Dict
from datetime import datetime


class ChildImpactBase(BaseModel):
    impact_year: str
    impact_period: str
    nsv_aud: Optional[str] = None
    nsv_nzd: Optional[str] = None
    volume_litres: Optional[str] = None
    volume_cases: Optional[str] = None
    volume_impact_value: Optional[str] = None


class ChildImpactOut(ChildImpactBase):
    id: int
    model_config = {"from_attributes": True}


class EntryBase(BaseModel):
    creation_date: Optional[str] = None
    creation_date_period: Optional[str] = None
    creation_date_year: Optional[str] = None
    add_to_forecast_by_period: Optional[str] = None
    add_to_forecast_by_year: Optional[str] = None
    division: str
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
