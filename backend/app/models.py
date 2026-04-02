"""
SQLAlchemy ORM models for ThrivePay (simplified prototype).

These models define a basic schema to demonstrate the core entities needed for
the ThrivePay platform. They cover users, clients, trainers, sessions,
invoices, payments, payouts and audit logs. This simplified version omits
multi‑gym support, subscription plans and other advanced features for clarity
and ease of demonstration.

If you extend the system to support multiple gyms, subscription plans,
different billing cycles or more complex relationships, you can evolve this
schema accordingly.
"""

import datetime
from enum import Enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Float,
    Enum as SQLAlchemyEnum,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from .database import Base


class UserRole(str, Enum):
    owner = "owner"
    trainer = "trainer"


class User(Base):
    """Represents a user of the system.

    A user can be an owner or a trainer. Clients are represented separately
    (they are not system users with logins).
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLAlchemyEnum(UserRole), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    trainer_profile = relationship("Trainer", back_populates="user", uselist=False)


class ClientStatus(str, Enum):
    active = "active"
    paused = "paused"
    cancelled = "cancelled"


class Client(Base):
    """Represents a client who receives training sessions."""

    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    sessions_remaining = Column(Integer, default=0)
    status = Column(SQLAlchemyEnum(ClientStatus), default=ClientStatus.active)

    # Relationships
    sessions = relationship("Session", back_populates="client")
    invoices = relationship("Invoice", back_populates="client")


class Trainer(Base):
    """Represents a trainer who runs sessions."""

    __tablename__ = "trainers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    user = relationship("User", back_populates="trainer_profile")
    sessions = relationship("Session", back_populates="trainer")
    payouts = relationship("TrainerPayout", back_populates="trainer")


class SessionStatus(str, Enum):
    scheduled = "scheduled"
    completed = "completed"
    cancelled = "cancelled"


class Session(Base):
    """Represents a single training session between a client and a trainer."""

    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    trainer_id = Column(Integer, ForeignKey("trainers.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    duration = Column(Float, nullable=False, default=1.0)  # hours
    status = Column(SQLAlchemyEnum(SessionStatus), default=SessionStatus.scheduled)

    trainer = relationship("Trainer", back_populates="sessions")
    client = relationship("Client", back_populates="sessions")


class InvoiceStatus(str, Enum):
    draft = "draft"
    pending = "pending"
    paid = "paid"
    failed = "failed"


class Invoice(Base):
    """Represents an invoice issued to a client for a set of sessions."""

    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    trainer_id = Column(Integer, ForeignKey("trainers.id"), nullable=True)
    amount = Column(Float, nullable=False)
    due_date = Column(DateTime, nullable=False)
    status = Column(SQLAlchemyEnum(InvoiceStatus), default=InvoiceStatus.pending)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    client = relationship("Client", back_populates="invoices")
    payments = relationship("Payment", back_populates="invoice")


class PaymentMethod(str, Enum):
    card = "card"
    bank = "bank"


class PaymentStatus(str, Enum):
    created = "created"
    succeeded = "succeeded"
    failed = "failed"


class Payment(Base):
    """Represents a payment against an invoice."""

    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_date = Column(DateTime, default=datetime.datetime.utcnow)
    method = Column(SQLAlchemyEnum(PaymentMethod), nullable=False)
    status = Column(SQLAlchemyEnum(PaymentStatus), default=PaymentStatus.created)

    invoice = relationship("Invoice", back_populates="payments")


class PayoutStatus(str, Enum):
    pending = "pending"
    processed = "processed"


class TrainerPayout(Base):
    """Represents a payout to a trainer for sessions completed."""

    __tablename__ = "trainer_payouts"

    id = Column(Integer, primary_key=True, index=True)
    trainer_id = Column(Integer, ForeignKey("trainers.id"), nullable=False)
    amount = Column(Float, nullable=False)
    payout_date = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    status = Column(SQLAlchemyEnum(PayoutStatus), default=PayoutStatus.pending)

    trainer = relationship("Trainer", back_populates="payouts")


class AuditLog(Base):
    """Records actions taken in the system for auditing purposes."""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)
    data = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)