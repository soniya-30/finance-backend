from sqlalchemy import Column, Integer, String, Boolean
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

    role = Column(String, default="viewer")
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)


class FinancialRecord(Base):
    __tablename__ = "financial_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    amount = Column(Integer, nullable=False)
    description = Column(String)
    is_deleted = Column(Boolean, default=False)