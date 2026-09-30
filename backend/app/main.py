from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import auth, categories, chat, checkout, menu, orders, users, webhooks
from app.core.config import settings

app = FastAPI(title="Brew & Bloom API", version="1.0.0", description="Local REST API for the Brew & Bloom cafe website")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url.rstrip("/")],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Stripe-Signature"],
)


@app.exception_handler(HTTPException)
async def http_error_handler(_: Request, exc: HTTPException):
    message = exc.detail if isinstance(exc.detail, str) else "Request failed"
    return JSONResponse(status_code=exc.status_code, content={"success": False, "error": message}, headers=exc.headers)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_: Request, exc: RequestValidationError):
    details = "; ".join(f"{'.'.join(map(str, err['loc'][1:]))}: {err['msg']}" for err in exc.errors())
    return JSONResponse(status_code=400, content={"success": False, "error": details or "Invalid request"})


@app.exception_handler(Exception)
async def unexpected_error_handler(_: Request, __: Exception):
    return JSONResponse(status_code=500, content={"success": False, "error": "Something went wrong"})


@app.get("/health", tags=["health"])
def health():
    return {"success": True, "data": {"status": "ok"}}


app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(users.router)
app.include_router(menu.router)
app.include_router(categories.router)
app.include_router(orders.router)
app.include_router(checkout.router)
app.include_router(webhooks.router)
