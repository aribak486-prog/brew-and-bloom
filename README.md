# Brew & Bloom

A modern cafe website built with Next.js, React, TypeScript, Tailwind CSS, FastAPI, PostgreSQL, and a locally hosted Transformer-based cafe chatbot.

## Features

- Responsive cafe landing page with menu, categories, specials, gallery, reviews, and contact information
- Menu display and a demo cart counter in the frontend
- FastAPI endpoints for authentication, menu and category management, orders, checkout, and Stripe webhooks
- PostgreSQL persistence through SQLAlchemy and Alembic migrations
- Stripe Checkout configured for test mode only
- Cafe chatbot endpoint with database-backed menu context and a locally loaded Transformer model

The frontend currently presents the cafe and demo cart interactions. Ordering, authentication, and checkout are available as backend APIs; they are not all wired into the landing page UI.

## Tech stack

| Area | Technologies |
| --- | --- |
| Frontend | Next.js, React, TypeScript, Tailwind CSS |
| Backend | Python, FastAPI, SQLAlchemy, Alembic |
| Database | PostgreSQL |
| AI | Hugging Face Transformers and PyTorch, running locally |
| Payments | Stripe test mode |

## Requirements

- Node.js and npm
- Python 3.11 or newer
- PostgreSQL 14 or newer for the standard backend setup
- A Stripe test key only if you want to exercise checkout

## Local setup

### 1. Get the project

```powershell
git clone <your-repository-url>
Set-Location YOUR_REPOSITORY_FOLDER
```

### 2. Configure the frontend

From the project root:

```powershell
npm install
Copy-Item .env.local.example .env.local
```

The local frontend setting is `NEXT_PUBLIC_API_URL=http://localhost:8000`. `NEXT_PUBLIC_*` values are included in browser code, so do not put secrets in them.

### 3. Configure the backend

Create and activate a Python environment, then install the listed dependencies:

```powershell
Set-Location backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `backend/.env` with your own local settings:

- `DATABASE_URL`: your PostgreSQL connection string, using the `postgresql+psycopg://` scheme.
- `JWT_SECRET_KEY`: generate a private random value with `py -c "import secrets; print(secrets.token_urlsafe(48))"`.
- `STRIPE_SECRET_KEY`: optional for non-payment development; use your own `sk_test_...` key for checkout. Live keys are rejected.
- `STRIPE_WEBHOOK_SECRET`: optional until you configure Stripe CLI webhooks.
- `FRONTEND_URL`: normally `http://localhost:3000`.
- `ACCESS_TOKEN_EXPIRE_MINUTES`: token lifetime in minutes; defaults to `60`.
- `TRANSFORMER_MODEL`: Hugging Face model ID; defaults to `HuggingFaceTB/SmolLM2-360M-Instruct`.
- `DEMO_ADMIN_PASSWORD` and `DEMO_CUSTOMER_PASSWORD`: optional; set your own values if you want the seed script to create local demo accounts.

The backend reads its `.env` from the `backend` directory. Never commit `.env` or put credentials in frontend variables.

### 4. Create the PostgreSQL database and load sample data

Create a database named `brew_bloom` in PostgreSQL, then, from the `backend` directory with the virtual environment active, run:

```powershell
alembic upgrade head
py seed.py
```

`seed.py` adds sample menu categories and menu items. It is safe to rerun; it only inserts missing rows. Optional demo users are created only when you set `DEMO_ADMIN_PASSWORD` and/or `DEMO_CUSTOMER_PASSWORD` in `backend/.env`; choose your own values.

### 5. Start the backend

From the `backend` directory:

```powershell
py -m uvicorn app.main:app --reload
```

The API is at <http://localhost:8000>, Swagger docs at <http://localhost:8000/docs>, and the health endpoint at <http://localhost:8000/health>.

### 6. Start the frontend

In a second terminal, from the project root:

```powershell
npm run dev
```

Open <http://localhost:3000>.

### Optional local backend without PostgreSQL

For local UI/chat development where PostgreSQL is unavailable, the backend includes `backend/run-local.ps1`. From PowerShell, run it from the backend directory:

```powershell
Set-Location backend
.\run-local.ps1
```

This uses an ignored SQLite database file and the seeded sample catalog. It enables grounded offline chatbot answers and does not use the Transformer model. Use the standard PostgreSQL/uvicorn setup above for the Transformer-backed chatbot and the full database-backed application.

## Environment variables

The root `.env.example` lists the project's backend and frontend variable names with safe placeholders. Copy the backend values to `backend/.env` and the frontend API URL from `.env.local.example` to `.env.local`; replace placeholders with your own local credentials. The checked-in `backend/.env.example` is the backend-specific template. None of these files contain real credentials.

## API

All paths below are served by the FastAPI application:

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/api/auth/register` | Register a customer |
| `POST` | `/api/auth/login` | Log in and receive a bearer token |
| `GET` | `/api/auth/me` | Get the signed-in user |
| `GET` | `/api/users/me` | Get the current user profile |
| `GET`, `POST`, `PUT`, `DELETE` | `/api/menu` and `/api/menu/{item_id}` | Read and manage menu items |
| `PATCH` | `/api/menu/{item_id}/availability` | Update item availability |
| `GET`, `POST`, `PUT`, `DELETE` | `/api/categories` and `/api/categories/{category_id}` | Read and manage categories |
| `POST`, `GET` | `/api/orders` and `/api/orders/{order_id}` | Create and view orders |
| `PATCH` | `/api/orders/{order_id}/status` | Update order status |
| `POST` | `/api/checkout` | Create a Stripe test checkout session |
| `POST` | `/api/webhooks/stripe` | Receive signed Stripe events |
| `POST` | `/api/chat` | Ask the cafe chatbot a question |

Protected endpoints require `Authorization: Bearer <access_token>`. Successful API responses use `{ "success": true, "data": ... }`; failures use `{ "success": false, "error": "..." }`.

## Chatbot

The frontend sends chat messages to `POST /api/chat`. The backend retrieves cafe details from `backend/app/data/cafe_info.json` and current menu, prices, categories, and availability from the database. In the standard setup, it loads the model named by `TRANSFORMER_MODEL` on the first in-scope chat request and caches it locally. The first request may take time to download model files; model weights are not part of this repository. The model runs on the backend and no model credential is exposed to the browser.

## Project structure

```text
.
├── app/
│   ├── globals.css
│   ├── layout.tsx
│   └── page.tsx
├── components/
│   └── Chatbot.tsx
├── lib/
│   └── api.ts
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── data/
│   │   ├── database/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── services/
│   ├── alembic/
│   │   └── versions/
│   ├── run_local.py
│   ├── run-local.ps1
│   ├── seed.py
│   └── requirements.txt
├── .env.example
├── .env.local.example
├── package.json
└── package-lock.json
```

## GitHub safety

The root `.gitignore` excludes local environment files, Python virtual environments and caches, local databases, Node dependencies, Next.js build output, logs, and common OS/editor temporary files. Keep your real `.env`, `.env.local`, payment credentials, and database credentials out of Git.
