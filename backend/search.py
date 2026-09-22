"""Search & findability: type-ahead suggestions, stock alerts, search reporting,
admin-editable synonyms. Complements the enhanced /api/products search in shop.py."""
import re
from datetime import timedelta
from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional

from core import db, now_utc, clean, cleans
from auth import require_admin, get_optional_user
from shop import public_product, expand_terms, build_search_or, DEFAULT_SYNONYMS, get_synonyms

search_router = APIRouter(prefix="/api")


@search_router.get("/search/suggest")
async def suggest(q: Optional[str] = None):
    """Predictive type-ahead: product name matches + matching categories +
    a synonym-corrected term hint. Cheap, capped, safe for keystroke calls."""
    q = (q or "").strip()
    if len(q) < 2:
        return {"query": q, "products": [], "categories": [], "did_you_mean": None}

    ors = await build_search_or(q)
    base = {"status": {"$nin": ["hidden", "draft", "awaiting_approval"]}, "$or": ors}
    docs = await db.products.find(base).limit(6).to_list(6)
    products = []
    for d in docs:
        p = public_product(d)
        products.append({"id": p["id"], "name": p.get("name"), "sku": p.get("sku"),
                         "price_inc_vat": p.get("price_inc_vat"),
                         "image": (p.get("images") or [None])[0]})

    cat_docs = await db.categories.find({
        "hidden": {"$ne": True},
        "name": {"$regex": re.escape(q), "$options": "i"},
    }).limit(4).to_list(4)
    categories = [{"id": clean(c)["id"], "name": c.get("name"), "slug": c.get("slug")} for c in cat_docs]

    # did-you-mean: if the query maps to a synonym, surface the canonical term
    variants = await expand_terms(q)
    did_you_mean = None
    if not products:
        syn = await get_synonyms()
        for canonical, words in syn.items():
            if q.lower() in [w.lower() for w in words] and canonical != q.lower():
                did_you_mean = canonical
                break

    return {"query": q, "products": products, "categories": categories,
            "did_you_mean": did_you_mean}


# ---------------- Stock alerts (zero-results / out-of-stock capture) ----------------
class StockAlertBody(BaseModel):
    email: EmailStr
    query: Optional[str] = ""
    product_id: Optional[str] = None
    note: Optional[str] = ""


@search_router.post("/stock-alerts")
async def create_stock_alert(body: StockAlertBody, user=Depends(get_optional_user)):
    doc = body.model_dump()
    doc["email"] = doc["email"].lower()
    doc["created_at"] = now_utc()
    doc["notified"] = False
    doc["user_email"] = (user or {}).get("email") if user else None
    await db.stock_alerts.insert_one(doc)
    return {"ok": True, "message": "We'll email you when something matching comes in."}


@search_router.get("/admin/stock-alerts")
async def list_stock_alerts(user=Depends(require_admin("shop_admin"))):
    docs = await db.stock_alerts.find().sort("created_at", -1).limit(500).to_list(500)
    return cleans(docs)


# ---------------- Search reporting (Prompt 2 / 16) ----------------
@search_router.get("/admin/search-report")
async def search_report(days: int = 30, user=Depends(require_admin("shop_admin"))):
    since = now_utc() - timedelta(days=days)
    pipeline_top = [
        {"$match": {"at": {"$gte": since}, "query": {"$ne": ""}}},
        {"$group": {"_id": "$query", "count": {"$sum": 1},
                    "avg_results": {"$avg": "$results"}}},
        {"$sort": {"count": -1}}, {"$limit": 50},
    ]
    top = await db.search_logs.aggregate(pipeline_top).to_list(50)
    top_queries = [{"query": t["_id"], "count": t["count"],
                    "avg_results": round(t.get("avg_results") or 0, 1)} for t in top]

    pipeline_zero = [
        {"$match": {"at": {"$gte": since}, "query": {"$ne": ""}, "results": 0}},
        {"$group": {"_id": "$query", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}, {"$limit": 50},
    ]
    zero = await db.search_logs.aggregate(pipeline_zero).to_list(50)
    zero_result_queries = [{"query": z["_id"], "count": z["count"]} for z in zero]

    total = await db.search_logs.count_documents({"at": {"$gte": since}, "query": {"$ne": ""}})
    zero_total = await db.search_logs.count_documents({"at": {"$gte": since}, "query": {"$ne": ""}, "results": 0})
    return {"days": days, "total_searches": total, "zero_result_searches": zero_total,
            "top_queries": top_queries, "zero_result_queries": zero_result_queries}


# ---------------- Synonyms admin ----------------
class SynonymsBody(BaseModel):
    map: dict  # { "term": ["variant1", "variant2"] }


@search_router.get("/admin/search-synonyms")
async def get_search_synonyms(user=Depends(require_admin("shop_admin"))):
    s = await db.site_settings.find_one({"key": "search_synonyms"})
    return {"defaults": DEFAULT_SYNONYMS, "custom": (s or {}).get("map") or {}}


@search_router.put("/admin/search-synonyms")
async def put_search_synonyms(body: SynonymsBody, user=Depends(require_admin("shop_admin"))):
    cleaned = {}
    for k, v in (body.map or {}).items():
        key = str(k).lower().strip()
        if not key:
            continue
        cleaned[key] = [str(x).strip() for x in v if str(x).strip()]
    await db.site_settings.update_one({"key": "search_synonyms"},
                                      {"$set": {"map": cleaned}}, upsert=True)
    return {"ok": True, "custom": cleaned}
