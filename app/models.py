# app/models.py
from sqlalchemy import Column, Integer, String, Enum, Boolean
from sqlalchemy.sql import func
from sqlalchemy import DateTime
from .db import Base
import enum

class RoleEnum(str, enum.Enum):
    etudiant = "etudiant"
    admin_local = "admin_local"
    admin_super = "admin_super"

class AccountStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(128), unique=True, index=True, nullable=False)
    email = Column(String(256), unique=True, index=True, nullable=False)
    hashed_password = Column(String(256), nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.etudiant, nullable=False)
    status = Column(Enum(AccountStatus), default=AccountStatus.pending, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
