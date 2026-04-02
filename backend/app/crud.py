"""
crud.py

This module contains basic Create, Read, Update, Delete operations for the
ThrivePay backend. These functions abstract database interactions and can
be reused by our API endpoints.

The CRUD functions are synchronous because SQLAlchemy's ORM is synchronous
by default. If you need asynchronous support, consider using an async ORM
like SQLModel or the async extensions of SQLAlchemy.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from . import models, schemas
from .auth import get_password_hash


# User management
def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()


def create_owner(db: Session, user_in: schemas.UserCreate) -> models.User:
    """Create an owner account (role=owner)."""
    hashed_password = get_password_hash(user_in.password)
    db_user = models.User(email=user_in.email, hashed_password=hashed_password, role="owner")
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_trainer(db: Session, user_in: schemas.UserCreate) -> models.User:
    """Create a trainer account (role=trainer)."""
    hashed_password = get_password_hash(user_in.password)
    db_user = models.User(email=user_in.email, hashed_password=hashed_password, role="trainer")
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# Client CRUD
def create_client(db: Session, client_in: schemas.ClientCreate) -> models.Client:
    """Create a client record."""
    db_client = models.Client(
        name=client_in.name,
        email=client_in.email,
        phone=client_in.phone,
        sessions_remaining=client_in.sessions_remaining,
    )
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


def get_clients(db: Session, skip: int = 0, limit: int = 100) -> List[models.Client]:
    return db.query(models.Client).offset(skip).limit(limit).all()


def get_client(db: Session, client_id: int) -> Optional[models.Client]:
    return db.query(models.Client).filter(models.Client.id == client_id).first()


# Trainer CRUD
def get_trainer(db: Session, trainer_id: int) -> Optional[models.Trainer]:
    return db.query(models.Trainer).filter(models.Trainer.id == trainer_id).first()


def create_trainer_profile(db: Session, trainer_in: schemas.TrainerCreate) -> models.Trainer:
    """Create a trainer profile."""
    db_trainer = models.Trainer(name=trainer_in.name, email=trainer_in.email)
    db.add(db_trainer)
    db.commit()
    db.refresh(db_trainer)
    return db_trainer


# Session CRUD
def create_session(db: Session, session_in: schemas.SessionCreate) -> models.Session:
    """Create a session record."""
    db_session = models.Session(
        date=session_in.date,
        trainer_id=session_in.trainer_id,
        client_id=session_in.client_id,
        duration=session_in.duration,
        status=session_in.status,
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


def get_sessions_for_client(db: Session, client_id: int) -> List[models.Session]:
    return db.query(models.Session).filter(models.Session.client_id == client_id).all()


# Payment CRUD
def create_invoice(db: Session, invoice_in: schemas.InvoiceCreate) -> models.Invoice:
    """Create an invoice."""
    db_invoice = models.Invoice(
        client_id=invoice_in.client_id,
        trainer_id=invoice_in.trainer_id,
        amount=invoice_in.amount,
        due_date=invoice_in.due_date,
        status=invoice_in.status,
    )
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    return db_invoice


def create_payment(db: Session, payment_in: schemas.PaymentCreate) -> models.Payment:
    """Create a payment and optionally update the invoice status."""
    # Update invoice status to paid if payment status indicates success
    invoice = db.query(models.Invoice).filter(models.Invoice.id == payment_in.invoice_id).first()
    if invoice and payment_in.status in {"succeeded", "paid"}:
        invoice.status = "paid"
    db_payment = models.Payment(
        invoice_id=payment_in.invoice_id,
        amount=payment_in.amount,
        payment_date=payment_in.payment_date,
        method=payment_in.method,
        status=payment_in.status,
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment


# Payout CRUD
def create_trainer_payout(db: Session, payout_in: schemas.PayoutCreate) -> models.TrainerPayout:
    """Create a trainer payout record."""
    db_payout = models.TrainerPayout(
        trainer_id=payout_in.trainer_id,
        amount=payout_in.amount,
        payout_date=payout_in.payout_date,
        status=payout_in.status,
    )
    db.add(db_payout)
    db.commit()
    db.refresh(db_payout)
    return db_payout
