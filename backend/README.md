# Brew & Bloom API

A local FastAPI backend for the Brew & Bloom Next.js website. The app uses PostgreSQL, SQLAlchemy, Alembic, JWT bearer tokens and Stripe Checkout in test mode.

## Deploy on Render

Create a PostgreSQL database and a Python web service in Render. Set the web service's **Root Directory** to `backend`, **Build Command** to `pip install -r requirements.txt`, and **Start Command** to:

```sh
alembic upgrade head && python seed.py && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Set these environment variables on the web service:

| Variable | Value |
| --- | --- |
| `DATABASE_URL` | Render PostgreSQL **internal** connection URL. Generic `postgres://` and `postgresql://` URLs are normalized to the installed psycopg v3 driver. |
| `JWT_SECRET_KEY` | A randomly generated secret with at least 32 characters. |
| `FRONTEND_URL` | `https://brew-and-bloom-8gb0kpev2-aribak486-4754.vercel.app` |
| `TRANSFORMER_MODEL` | `HuggingFaceTB/SmolLM2-360M-Instruct` (or the selected Hugging Face model id). |
| `STRIPE_SECRET_KEY` | Your Stripe test secret key (`sk_test_...`). |
| `STRIPE_WEBHOOK_SECRET` | The signing secret (`whsec_...`) for the Stripe webhook pointing to `/api/webhooks/stripe`. |

The model downloads on the first in-scope chat request, so allow for a slower first response and sufficient service memory. After Render creates the API, set `NEXT_PUBLIC_API_URL` in the Vercel project's environment variables to the Render service's HTTPS origin, then redeploy the frontend. Set `BREW_BLOOM_FRONTEND_URL` in Streamlit secrets to the Vercel URL above.

## Requirements

- Python 3.11 or newer
- PostgreSQL 14 or newer, running locally
- A Stripe account and a **test mode** secret key only for checkout
- Optional: Stripe CLI to forward test webhooks locally

## 1. Create a local database

In `psql` (or pgAdmin), create a database:

```sql
CREATE DATABASE brew_bloom;
```

Make sure your PostgreSQL username and password in `DATABASE_URL` match your local setup. The example uses the local `postgres` user and a placeholder password that you must replace.

## 2. Configure the environment

From this `backend` directory, create a virtual environment and copy the example environment file:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
Copy-Item .env.example .env
```

Edit `.env` and set:

- `DATABASE_URL` to your PostgreSQL connection string, using the `postgresql+psycopg://` scheme.
- `JWT_SECRET_KEY` to a randomly generated secret of at least 32 characters. For example: `py -c "import secrets; print(secrets.token_urlsafe(48))"`
- `STRIPE_SECRET_KEY` to a Stripe **test** key beginning with `sk_test_`.
- `STRIPE_WEBHOOK_SECRET` to the webhook signing secret supplied by Stripe CLI.
- `FRONTEND_URL` to the frontend origin, normally `http://localhost:3000`.
- `TRANSFORMER_MODEL` to a Hugging Face conversational model id. The default is the lightweight `HuggingFaceTB/SmolLM2-360M-Instruct`.

The API deliberately refuses to start with a missing or example JWT secret and refuses to create payment sessions unless the configured Stripe key starts with `sk_test_`.

The first in-scope chat request downloads the configured Transformer and tokenizer once, then caches them in the API process. The default model is about 360 million parameters and runs locally on CPU; the first request can take longer while the model downloads and loads. The machine needs enough memory for PyTorch plus the model. No model/API secret is sent to the browser.

## 3. Install Python dependencies

```powershell
py -m pip install -r requirements.txt
```

## 4. Create the schema and sample data

```powershell
alembic upgrade head
py seed.py
```

Seed can be run again safely; it only adds missing sample rows.

## 5. Start the API

```powershell
uvicorn app.main:app --reload
```

- API: <http://localhost:8000>
- Swagger UI: <http://localhost:8000/docs>
- Health check: <http://localhost:8000/health>

### Quick local startup without PostgreSQL

If PostgreSQL is not installed or running, start the local development backend from PowerShell:

```powershell
Set-Location "C:\path\to\cafe noir\backend"
.\run-local.ps1
```

This starts the API on `http://localhost:8000`, creates a local SQLite database and sample cafe menu, and enables grounded offline chat answers so a first-time model download is not required. It does not use or modify the PostgreSQL database. Keep this terminal open while using the website.

## Optional demo users

The seed script creates demo users only when you set your own `DEMO_ADMIN_PASSWORD` and/or `DEMO_CUSTOMER_PASSWORD` in `backend/.env`. Do not reuse passwords from other accounts.

## Stripe test checkout and webhook

Use only Stripe test credentials. To receive webhooks locally, install and authenticate Stripe CLI, then run:

```powershell
stripe listen --forward-to localhost:8000/api/webhooks/stripe
```

Copy the CLI's `whsec_...` value into `STRIPE_WEBHOOK_SECRET` and restart the API. Use a Stripe test card such as `4242 4242 4242 4242` with any future expiry, any CVC, and any postal code. The browser return URL does not mark an order paid; only a signature-verified `checkout.session.completed` webhook does.

## Frontend connection

Run Next.js at `http://localhost:3000`. CORS allows the origin configured by `FRONTEND_URL`. The shared client in `lib/api.ts` uses `NEXT_PUBLIC_API_URL` when set and otherwise defaults to `http://localhost:8000`:

```ts
import { cafeApi } from '@/lib/api'

const result = await cafeApi.menu() // { success: true, data: [...] }
```

Send the login `access_token` on protected requests as `Authorization: Bearer <token>`. Order and checkout request bodies contain item IDs and quantities only; the API reads prices from PostgreSQL.

Copy the root `.env.local.example` to `.env.local` if you want to override the frontend API URL. The floating Brew & Bloom assistant is mounted once in `app/layout.tsx`, calls `POST /api/chat`, and remains fixed to the viewport.

## Cafe chatbot

`POST /api/chat` accepts `{ "message": "...", "history": [] }` and returns `{ "success": true, "data": { "message": "..." } }`. It retrieves menu records, prices, categories and availability from the configured database, and reads static cafe hours/contact/offer details from `app/data/cafe_info.json`. Conversation history is limited to the most recent 12 validated messages; each message is length-limited. The model is instructed to stay within the retrieved context, and unsupported prices are rejected.

Example:

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/chat `
  -ContentType 'application/json' `
  -Body '{"message":"How much is the Caramel Latte?"}'
```

## API overview

| Method | Path | Access |
| --- | --- | --- |
| POST | `/api/auth/register` | Public |
| POST | `/api/auth/login` | Public |
| GET | `/api/auth/me` | Signed in |
| GET | `/api/menu`, `/api/menu/{id}` | Public, available items |
| POST, PUT, DELETE | `/api/menu`, `/api/menu/{id}` | Admin |
| PATCH | `/api/menu/{id}/availability` | Admin |
| GET | `/api/categories`, `/api/categories/{id}` | Public |
| POST, PUT, DELETE | `/api/categories`, `/api/categories/{id}` | Admin |
| POST | `/api/orders` | Customer |
| GET | `/api/orders`, `/api/orders/{id}` | Owner; admin can see all |
| PATCH | `/api/orders/{id}/status` | Admin |
| POST | `/api/checkout` | Customer, Stripe test mode |
| POST | `/api/webhooks/stripe` | Stripe signature required |

Responses use `{ "success": true, "data": ... }` or `{ "success": false, "error": "..." }`.

## Project layout

`app/api` contains route handlers, `app/models` contains SQLAlchemy entities, `app/schemas` contains request and response validation, `app/services` contains authentication, order and payment logic, and `app/core` contains configuration and security. `alembic/versions` stores database migrations; `seed.py` adds local demo data.

The API is kept independent of the frontend, so another client such as a future Streamlit dashboard can use the same REST endpoints.
