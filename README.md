ThrivePay
=========

This repository contains a prototype implementation of **ThrivePay**, a payment and session management platform designed for gyms like L&M Thrive Fitness.

**What this is:**

* A **code skeleton** for a backend service written with FastAPI (Python) that models gyms, users, clients, trainers, sessions, invoices and payments.
* A starting point for extending the system into a full‑featured product.  It includes basic authentication, CRUD operations and simulated payment processing.
* Documentation to help you understand how to run and develop the project.

**What this is not:**

* A finished, production‑ready system.  Payment processing is mocked; there is no real bank or card integration yet.
* A polished frontend.  Frontend code is not included in this prototype but can be added in a `frontend/` directory following the design document in `thrivepay_design.md`.

## Running the backend locally

1. Ensure you have Python 3.9+ installed.
2. Create and activate a virtual environment (optional but recommended).
3. Install dependencies:

   ```bash
   pip install -r backend/requirements.txt
   ```

4. Start the server from the `backend/` directory:

   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000`.  You can explore it using the automatically generated docs at `http://localhost:8000/docs`.

5. The database uses SQLite by default (`thrivepay.db` in the repository root).  To use PostgreSQL or another database, edit `app/database.py` and set `SQLALCHEMY_DATABASE_URL` accordingly.

## Project structure

```
thrivepay_project/
├─ backend/
│  ├─ app/
│  │  ├─ main.py        # FastAPI application entry point
│  │  ├─ database.py    # Database connection and session management
│  │  ├─ models.py      # SQLAlchemy ORM models
│  │  ├─ schemas.py     # Pydantic models (request/response)
│  │  ├─ crud.py        # Database CRUD helpers
│  │  └─ auth.py        # Authentication helpers (password hashing, tokens)
│  ├─ thrivepay.db      # SQLite database (created after first run)
│  └─ requirements.txt   # Python dependencies
├─ thrivepay_design.md   # High‑level system design (copied from specification)
└─ README.md             # This file
```

## Next steps

This prototype lays the groundwork for the full ThrivePay system described in `thrivepay_design.md`.  To build out the complete product you will need to:

* Implement real payment processing via a bank API (FedNow or RTP) or a card processor (Stripe, Adyen).  Currently payments are simply marked as paid.
* Build the React and React Native frontends and connect them to the backend.
* Enhance authentication and authorization (e.g. JWT with role‑based access control).
* Add error handling, logging and tests.

Feel free to fork and extend this code to meet your specific needs.

## Running the frontend

The `frontend/` directory contains a very simple React application scaffolded
with Webpack and Babel.  It does not yet communicate with the backend but
provides a starting point for building your web interface.

To run the frontend:

1. Ensure you have Node.js and npm installed.
2. Navigate to the `frontend` directory:

   ```bash
   cd frontend
   ```

3. Install dependencies:

   ```bash
   npm install
   ```

4. Start the development server:

   ```bash
   npm start
   ```

The frontend will be served at `http://localhost:3000` and will hot‑reload
as you make changes.

## Running the mobile app

The `mobile/` directory contains a minimal React Native (Expo) project.  You
will need Expo CLI installed globally (`npm install -g expo-cli`) to run it.

1. Navigate to the `mobile` directory:

   ```bash
   cd mobile
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

3. Start the Expo development server:

   ```bash
   npm start
   ```

Expo will launch a development server and provide a QR code you can scan
with the Expo app on your device or run in an emulator.
