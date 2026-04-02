"""
Pydantic schemas for ThrivePay (simplified prototype).

These schemas define the shapes of data exchanged between the client and
server. They correspond to the simplified SQLAlchemy models defined in
models.py. Each schema has an associated `orm_mode = True` config to allow
automatic conversion from ORM objects to Pydantic models when returning
responses from FastAPI endpoints.
"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field
from enum import Enum


class UserRole(str, Enum):
    owner = "owner"
    trainer = "trainer"


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    role: UserRole


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: UserRole
    created_at: datetime

    class Config:
        orm_mode = True


# Token schema used for authentication responses
class Token(BaseModel):
    access_token: str
    token_type: str


# Client schemas
class ClientCreate(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    sessions_remaining: int = 0


class Client(BaseModel):
    id: int
    name: str
    email: Optional[EmailStr]
    phone: Optional[str]
    sessions_remaining: int
    status: str

    class Config:
        orm_mode = True


# Trainer schemas
class TrainerCreate(BaseModel):
    name: str
    email: Optional[EmailStr] = None


class Trainer(BaseModel):
    id: int
    name: str
    email: Optional[EmailStr]

    class Config:
        orm_mode = True


# Session schemas
class SessionCreate(BaseModel):
    date: datetime
    trainer_id: int
    client_id: int
    duration: float = 1.0
    status: Optional[str] = "scheduled"


class Session(BaseModel):
    id: int
    date: datetime
    trainer_id: int
    client_id: int
    duration: float
    status: str

    class Config:
        orm_mode = True


# Invoice schemas
class InvoiceCreate(BaseModel):
    client_id: int
    trainer_id: Optional[int] = None
    amount: float
    due_date: datetime
    status: Optional[str] = "pending"


class Invoice(BaseModel):
    id: int
    client_id: int
    trainer_id: Optional[int]
    amount: float
    due_date: datetime
    status: str
    created_at: datetime

    class Config:
        orm_mode = True


# Payment schemas
class PaymentCreate(BaseModel):
    invoice_id: int
    amount: float
    payment_date: datetime
    method: str
    status: Optional[str] = "created"


class Payment(BaseModel):
    id: int
    invoice_id: int
    amount: float
    payment_date: datetime
    method: str
    status: str

    class Config:
        orm_mode = True


# Payout schemas
class PayoutCreate(BaseModel):
    trainer_id: int
    amount: float
    payout_date: datetime
    status: Optional[str] = "pending"


class Payout(BaseModel):
    id: int
    trainer_id: int
    amount: float
    payout_date: datetime
    status: str

    class Config:
        orm_mode = True