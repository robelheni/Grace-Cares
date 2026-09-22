from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).parent / ".env")

import os
import logging
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from core import db
from auth import auth_router, seed_admin
from shop import shop_router
from content import content_router
from admin import admin_router
from extra import extra_router
from receipts import receipts_router
from seed_data import seed_all
from search import search_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("grace_cares")

app = FastAPI(title="Grace Cares API")

app.include_router(auth_router)
app.include_router(shop_router)
app.include_router(content_router)
app.include_router(admin_router)
app.include_router(extra_router)
app.include_router(receipts_router)
app.include_router(search_router)


@app.get("/api/")
async def root():
    return {"message": "Grace Cares API", "status": "ok"}


@app.get("/api/health")
async def health():
    return {"status": "healthy"}


@app.on_event("startup")
async def startup():
    await db.users.create_index("email", unique=True)
    await db.password_reset_tokens.create_index("expires_at", expireAfterSeconds=0)
    await db.login_attempts.create_index("identifier")
    await db.products.create_index("sku")
    await db.orders.create_index("reference")
    await db.search_logs.create_index("at")
    await db.search_logs.create_index("query")
    await seed_admin()
    await seed_all()
    # One-time backfill: give products a plausible RRP (~2x resale) so the
    # "biggest saving" sort/badges have data. Only touches docs missing rrp.
    try:
        async for p in db.products.find({"$or": [{"rrp": {"$exists": False}}, {"rrp": {"$in": [None, 0]}}]}):
            ex = p.get("price_ex_vat", 0) or 0
            inc = round(ex * (1 + p.get("vat_rate", 0.20)), 2)
            rrp = round(inc * 2, 2) if inc else 0
            await db.products.update_one({"_id": p["_id"]}, {"$set": {"rrp": rrp}})
    except Exception as e:
        logger.warning(f"rrp backfill skipped: {e}")
    logger.info("Startup complete")


app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origin_regex=".*",
    allow_methods=["*"],
    allow_headers=["*"],
)
