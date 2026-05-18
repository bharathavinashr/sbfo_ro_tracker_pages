from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from .database import Base

SCHEMA = "sbfo_ro"


class Entry(Base):
    __tablename__ = "entries"
    __table_args__ = {"schema": SCHEMA}

    id = Column(Integer, primary_key=True, autoincrement=True)
    original_entry_id = Column(Integer, nullable=True, index=True)
    version = Column(Integer, nullable=False, default=1)

    creation_date = Column(String(20), nullable=False)
    creation_date_period = Column(String(5), nullable=True)
    creation_date_year = Column(String(4), nullable=True)
    add_to_forecast_by_period = Column(String(5), nullable=True)
    add_to_forecast_by_year = Column(String(4), nullable=True)

    division = Column(String(255), nullable=False)
    ibp_step = Column(String(255), nullable=True)
    country = Column(JSONB, nullable=False)  # Map: {company_code: country_name}

    channel = Column(JSONB, nullable=False)  # Map: {channel_code: channel_name}
    sub_channel = Column(JSONB, nullable=False)  # Map: {subchannel_code: subchannel_name}
    account = Column(JSONB, nullable=False)  # Map: {account_code: account_name}

    brand = Column(JSONB, nullable=False)  # Map: {brand_code: brand_name}
    brand_family = Column(JSONB, nullable=True)  # Map: {brand_family_code: brand_family_name}

    r_and_o = Column(String(50), nullable=False)
    probability = Column(String(50), nullable=False)
    categorisation = Column(String(255), nullable=False)

    impact_period = Column(String(5), nullable=True)
    impact_year = Column(String(4), nullable=True)

    nsv_aud = Column(String(50), nullable=True)
    nsv_nzd = Column(String(50), nullable=True)
    volume_litres = Column(String(50), nullable=True)
    primary_impact = Column(String(20), nullable=True)  # "AUD", "NZD", "Volume"

    owner = Column(String(200), nullable=False)
    creator = Column(String(200), nullable=True)
    modified_user = Column(String(200), nullable=True)

    status = Column(String(50), nullable=True, default="Open")
    short_description = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    financial_impact_type = Column(String(10), nullable=True, default="NSV")
    volume_cases = Column(String(50), nullable=True)

    last_modified = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime, server_default=func.now())

    volume_impact_type = Column(String(20), nullable=True) # Stores "Cases" or "9LE"
    volume_impact_value = Column(String(50), nullable=True)


class ChildImpact(Base):
    __tablename__ = "child_impacts"
    __table_args__ = {"schema": SCHEMA}

    id = Column(Integer, primary_key=True, autoincrement=True)
    entry_id = Column(
        Integer,
        ForeignKey(f"{SCHEMA}.entries.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    impact_year = Column(String(4), nullable=False)
    impact_period = Column(String(5), nullable=False)
    nsv_aud = Column(String(50), nullable=True)
    nsv_nzd = Column(String(50), nullable=True)
    volume_litres = Column(String(50), nullable=True)
    volume_cases = Column(String(50), nullable=True)
    volume_impact_value = Column(String(50), nullable=True)
    volume_impact_value = Column(String(50), nullable=True)


class AppUser(Base):
    __tablename__ = "app_users"
    __table_args__ = {"schema": SCHEMA}

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(200), nullable=False, unique=True)
    display_name = Column(String(100), nullable=True)
    role = Column(Integer, nullable=False)  # 0=System Admin, 1=User, 2=IBP Step Approver, 3=Finance Approver, 4=Viewer
    ibp_steps = Column(JSONB, nullable=True) 
    is_active = Column(Boolean, default=True)
    role_name = Column(String(50), nullable=True) # 0=System Admin, 1=User, 2=IBP Step Approver, 3=Finance Approver, 4=Viewer
    country = Column(JSONB, nullable=True) # {"0014": "New Zealand", "0015": "Australia"}
    division = Column(JSONB, nullable=True) # ["Alcohol", "Non-Alcohol"]


class LookupOption(Base):
    __tablename__ = "lookup_options"
    __table_args__ = {"schema": SCHEMA}

    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(50), nullable=False, index=True)
    value = Column(String(200), nullable=False)
    parent_category = Column(String(50), nullable=True)
    parent_value = Column(String(200), nullable=True)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)


class ROProduct(Base):
    __tablename__ = "ro_products"
    __table_args__ = {"schema": SCHEMA}

    id = Column(Integer, primary_key=True, autoincrement=True)
    brand_family_code = Column(String(20), nullable=False, index=True)
    brand_family_name = Column(String(200), nullable=False)
    brand_code = Column(String(20), nullable=False, index=True)
    brand_name = Column(String(200), nullable=False)
    division = Column(String(255), nullable=False, index=True)
    company_code = Column(String(50), nullable=True)
    country = Column(String(255), nullable=True, index=True)


class ROCustomer(Base):
    __tablename__ = "ro_customers"
    __table_args__ = {"schema": SCHEMA}

    id = Column(Integer, primary_key=True, autoincrement=True)
    division = Column(String(255), nullable=False, index=True)
    company_code = Column(String(50), nullable=True)
    country = Column(String(255), nullable=True, index=True)
    channel_code = Column(String(50), nullable=False, index=True)
    channel_name = Column(String(200), nullable=False)
    subchannel_code = Column(String(50), nullable=False, index=True)
    subchannel_name = Column(String(200), nullable=False)
    account_code = Column(String(50), nullable=False, index=True)
    account_name = Column(String(200), nullable=False)


class Snapshot(Base):
    __tablename__ = "snapshots"
    __table_args__ = {"schema": SCHEMA}

    id = Column(Integer, primary_key=True, autoincrement=True)
    snapshot_id = Column(String(100), nullable=False, index=True)
    entry_id = Column(Integer, nullable=False)
    period = Column(String(10), nullable=False)
    year = Column(String(4), nullable=False)
    ibp_step = Column(String(255), nullable=False)
    entry_data = Column(JSONB, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
