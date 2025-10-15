# app/schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum

class RoleEnum(str, Enum):
    etudiant = "etudiant"
    admin_local = "admin_local"
    admin_super = "admin_super"

class AccountStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: RoleEnum

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: RoleEnum
    status: AccountStatus

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserLoginSchema(BaseModel):
    email: EmailStr
    mot_de_passe: str

