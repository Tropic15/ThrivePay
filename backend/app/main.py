"""
main.py

Entry point for the ThrivePay backend API.

This file defines the FastAPI application, sets up middleware, and includes
endpoints for authentication, user management, clients, sessions, invoices,
payments, and trainer payouts.

The API uses JSON Web Tokens (JWT) for authentication. Users must obtain
a token via the `/token` endpoint and include it in the `Authorization`
header as a Bearer token when calling protected routes.
"""

from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError
from sqlalchemy.orm import Session

from . import auth, crud, models, schemas
from .database import SessionLocal, engine, init_db


# Initialize database (create tables)
models.Base.metadata.create_all(bind=engine)


# Create FastAPI app
app = FastAPI(title="ThrivePay API", version="0.1.0")

# OAuth2 scheme for obtaining token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_db():
    """Dependency to get a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    """Dependency to get the currently authenticated user from a JWT token."""
    try:
        payload = auth.decode_access_token(token)
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def require_role(required_roles: List[str]):
    """Factory that returns a dependency function checking user roles."""
    def role_checker(current_user: models.User = Depends(get_current_user)):
        if current_user.role not in required_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return current_user
    return role_checker


# Authentication endpoints
@app.post("/users/owner", response_model=schemas.UserResponse)
def create_owner(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = crud.get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = crud.create_owner(db, user_in)
    return user


@app.post("/users/trainer", response_model=schemas.UserResponse)
def create_trainer_user(user_in: schemas.UserCreate, db: Session = Depends(get_db), current_user: models.User = Depends(require_role(["owner"]))):
    # Only owners can create trainers
    existing_user = crud.get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = crud.create_trainer(db, user_in)
    return user


@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    # Create token
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


# Client endpoints
@app.post("/clients", response_model=schemas.Client)
def create_client(client_in: schemas.ClientCreate, db: Session = Depends(get_db), current_user: models.User = Depends(require_role(["owner", "trainer"]))):
    return crud.create_client(db, client_in)


@app.get("/clients", response_model=List[schemas.Client])
def read_clients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(require_role(["owner", "trainer"]))):
    return crud.get_clients(db, skip=skip, limit=limit)


# Session endpoints
@app.post("/sessions", response_model=schemas.Session)
def create_session(session_in: schemas.SessionCreate, db: Session = Depends(get_db), current_user: models.User = Depends(require_role(["owner", "trainer"]))):
    # Additional validation like checking if trainer and client exist could be added
    return crud.create_session(db, session_in)


@app.get("/clients/{client_id}/sessions", response_model=List[schemas.Session])
def get_sessions_for_client(client_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_role(["owner", "trainer"]))):
    return crud.get_sessions_for_client(db, client_id)


# Invoice & payment endpoints
@app.post("/invoices", response_model=schemas.Invoice)
def create_invoice(invoice_in: schemas.InvoiceCreate, db: Session = Depends(get_db), current_user: models.User = Depends(require_role(["owner", "trainer"]))):
    return crud.create_invoice(db, invoice_in)


@app.post("/payments", response_model=schemas.Payment)
def create_payment(payment_in: schemas.PaymentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(require_role(["owner", "trainer"]))):
    return crud.create_payment(db, payment_in)


# Payout endpoint
@app.post("/payouts", response_model=schemas.Payout)
def create_payout(payout_in: schemas.PayoutCreate, db: Session = Depends(get_db), current_user: models.User = Depends(require_role(["owner"]))):
    return crud.create_trainer_payout(db, payout_in)


@app.get("/healthcheck")
def healthcheck():
    return {"status": "ok"}
