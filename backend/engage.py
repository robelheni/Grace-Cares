"""Engagement & data: first-party reviews (AggregateRating), unified CRM Contact +
ConsentRecord model, no-account order tracking via signed link, save/share basket.
Does NOT modify checkout or the stock data model."""
import os
import hmac
import hashlib
import uuid
import io
import csv
from datetime import timedelta
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from bson import ObjectId

from core import db, now_utc, clean, cleans
from auth import require_admin
from shop import public_product

engage_router = APIRouter(prefix="/api")


def _secret():
    return os.environ.get("JWT_SECRET", "grace-cares-dev-secret")


def track_token(reference: str, email: str) -> str:
    msg = f"{reference.strip().upper()}:{email.strip().lower()}".encode()
    return hmac.new(_secret().encode(), msg, hashlib.sha256).hexdigest()[:32]


# ==================== First-party reviews ====================
class ReviewBody(BaseModel):
    product_id: str
    order_reference: str
    email: EmailStr
    author_name: str
    rating: int = Field(ge=1, le=5)
    title: Optional[str] = ""
    body: str


@engage_router.post("/reviews")
async def create_review(body: ReviewBody):
    order = await db.orders.find_one({"reference": body.order_reference.strip().upper()})
    if not order:
        raise HTTPException(404, "We couldn't find an order with that reference.")
    if (order.get("customer", {}).get("email", "").lower() != body.email.strip().lower()):
        raise HTTPException(403, "That email doesn't match the order.")
    item_ids = [str(it.get("product_id")) for it in order.get("items", [])]
    if body.product_id not in item_ids:
        raise HTTPException(400, "That product isn't part of this order.")
    existing = await db.reviews.find_one({"product_id": body.product_id,
                                          "order_reference": body.order_reference.strip().upper()})
    if existing:
        raise HTTPException(409, "You've already reviewed this item for this order.")
    doc = {
        "product_id": body.product_id, "order_reference": body.order_reference.strip().upper(),
        "email": body.email.strip().lower(), "author_name": body.author_name,
        "rating": body.rating, "title": body.title, "body": body.body,
        "verified": True, "status": "pending", "response": "", "created_at": now_utc(),
    }
    res = await db.reviews.insert_one(doc)
    return {"ok": True, "id": str(res.inserted_id),
            "message": "Thank you! Your review will appear once approved."}


async def _aggregate(product_id):
    docs = await db.reviews.find({"product_id": product_id, "status": "approved"}).to_list(1000)
    if not docs:
        return {"average": 0, "count": 0}
    avg = round(sum(d.get("rating", 0) for d in docs) / len(docs), 2)
    return {"average": avg, "count": len(docs)}


@engage_router.get("/products/{pid}/reviews")
async def product_reviews(pid: str):
    docs = await db.reviews.find({"product_id": pid, "status": "approved"}).sort("created_at", -1).to_list(200)
    items = []
    for d in docs:
        c = clean(d)
        c.pop("email", None)
        items.append(c)
    return {"items": items, "aggregate": await _aggregate(pid)}


@engage_router.get("/admin/reviews")
async def admin_list_reviews(status: Optional[str] = None, user=Depends(require_admin("content_admin"))):
    q = {"status": status} if status else {}
    docs = await db.reviews.find(q).sort("created_at", -1).to_list(1000)
    return cleans(docs)


class ModerateBody(BaseModel):
    status: str  # approved | rejected | pending
    response: Optional[str] = None


@engage_router.post("/admin/reviews/{rid}/moderate")
async def moderate_review(rid: str, body: ModerateBody, user=Depends(require_admin("content_admin"))):
    upd = {"status": body.status, "moderated_by": user["email"], "moderated_at": now_utc()}
    if body.response is not None:
        upd["response"] = body.response
    await db.reviews.update_one({"_id": ObjectId(rid)}, {"$set": upd})
    return {"ok": True}


# ==================== Unified CRM: Contact + ConsentRecord ====================
async def upsert_contact(email, name="", tags=None, source=""):
    if not email:
        return
    email = email.strip().lower()
    tags = tags or []
    set_fields = {"updated_at": now_utc()}
    if name:
        set_fields["name"] = name
    await db.contacts.update_one(
        {"email": email},
        {"$setOnInsert": {"email": email, "created_at": now_utc()},
         "$set": set_fields,
         "$addToSet": {"role_tags": {"$each": tags}, "sources": source} if source else {"role_tags": {"$each": tags}}},
        upsert=True)


async def record_consent(email, ctype, channel="email", action="granted", wording="", version=1, source=""):
    if not email:
        return
    await db.consent_records.insert_one({
        "contact_email": email.strip().lower(), "type": ctype, "channel": channel,
        "action": action, "wording": wording, "version": version, "source": source,
        "at": now_utc()})


@engage_router.get("/admin/contacts")
async def list_contacts(q: Optional[str] = None, tag: Optional[str] = None,
                        user=Depends(require_admin("content_admin"))):
    query = {}
    if q:
        query["$or"] = [{"email": {"$regex": q, "$options": "i"}},
                        {"name": {"$regex": q, "$options": "i"}}]
    if tag:
        query["role_tags"] = tag
    docs = await db.contacts.find(query).sort("updated_at", -1).to_list(2000)
    return cleans(docs)


@engage_router.get("/admin/contacts/{email}")
async def get_contact(email: str, user=Depends(require_admin("content_admin"))):
    c = await db.contacts.find_one({"email": email.strip().lower()})
    if not c:
        raise HTTPException(404, "Contact not found")
    consents = await db.consent_records.find({"contact_email": email.strip().lower()}).sort("at", -1).to_list(200)
    out = clean(c)
    out["consents"] = cleans(consents)
    return out


@engage_router.get("/admin/contacts-export.csv")
async def export_contacts(user=Depends(require_admin("content_admin"))):
    docs = await db.contacts.find().sort("updated_at", -1).to_list(5000)
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["email", "name", "role_tags", "sources", "created_at", "updated_at"])
    for d in docs:
        w.writerow([d.get("email", ""), d.get("name", ""),
                    ";".join(d.get("role_tags", []) or []), ";".join(d.get("sources", []) or []),
                    d.get("created_at", ""), d.get("updated_at", "")])
    buf.seek(0)
    return StreamingResponse(iter([buf.getvalue()]), media_type="text/csv",
                             headers={"Content-Disposition": "attachment; filename=contacts.csv"})


class ConsentWithdrawBody(BaseModel):
    email: EmailStr
    type: str = "marketing"


@engage_router.post("/consent/withdraw")
async def withdraw_consent(body: ConsentWithdrawBody):
    await record_consent(body.email, body.type, action="withdrawn", source="self_service")
    await db.contacts.update_one({"email": body.email.strip().lower()},
                                 {"$pull": {"role_tags": "newsletter"}})
    await db.subscribers.update_one({"email": body.email.strip().lower()},
                                    {"$set": {"unsubscribed": True, "unsubscribed_at": now_utc()}})
    return {"ok": True, "message": "Your preferences have been updated."}


async def backfill_contacts():
    """Build unified contacts from existing subscribers, enquiries, orders, donations."""
    try:
        async for s in db.subscribers.find():
            await upsert_contact(s.get("email"), s.get("name", ""),
                                 (s.get("tags") or []) + ["newsletter"], "subscriber")
        async for e in db.enquiries.find():
            await upsert_contact(e.get("email"), e.get("name", ""), ["enquiry"], "enquiry")
        async for o in db.orders.find():
            cust = o.get("customer", {})
            await upsert_contact(cust.get("email"), cust.get("name", ""), ["customer"], "order")
        async for d in db.donations.find():
            await upsert_contact(d.get("email"), d.get("name", ""), ["donor"], "donation")
    except Exception as ex:
        print(f"[CRM] backfill skipped: {ex}")


# ==================== No-account order tracking ====================
class TrackRequestBody(BaseModel):
    reference: str
    email: EmailStr


def _order_timeline(order):
    steps = [
        {"key": "placed", "label": "Order placed", "done": True, "at": order.get("created_at")},
        {"key": "paid", "label": "Payment received",
         "done": order.get("payment_status") == "paid", "at": order.get("paid_at")},
    ]
    status = order.get("status", "")
    steps.append({"key": "processing", "label": "Being prepared",
                  "done": status in ("processing", "ready", "dispatched", "completed")})
    steps.append({"key": "ready", "label": "Ready / dispatched",
                  "done": status in ("ready", "dispatched", "completed")})
    steps.append({"key": "completed", "label": "Completed", "done": status == "completed"})
    return steps


def _public_order(order):
    return {
        "reference": order.get("reference"),
        "status": order.get("status"),
        "payment_status": order.get("payment_status"),
        "fulfilment": order.get("fulfilment"),
        "created_at": order.get("created_at"),
        "items": [{"name": it.get("name"), "quantity": it.get("quantity")}
                  for it in order.get("items", [])],
        "total": (order.get("totals", {}) or {}).get("total_payable"),
        "timeline": _order_timeline(order),
        "tracking": order.get("tracking", {}),
    }


@engage_router.post("/track/request")
async def track_request(body: TrackRequestBody):
    order = await db.orders.find_one({"reference": body.reference.strip().upper()})
    if not order or order.get("customer", {}).get("email", "").lower() != body.email.strip().lower():
        raise HTTPException(404, "We couldn't find an order matching those details.")
    token = track_token(body.reference, body.email)
    path = f"/track?ref={order['reference']}&token={token}"
    # (Email delivery of this link can be wired to the email provider later.)
    return {"ok": True, "tracking_path": path, "order": _public_order(order)}


@engage_router.get("/track")
async def track(ref: str, token: str):
    order = await db.orders.find_one({"reference": ref.strip().upper()})
    if not order:
        raise HTTPException(404, "Order not found")
    email = order.get("customer", {}).get("email", "")
    if not hmac.compare_digest(token, track_token(ref, email)):
        raise HTTPException(403, "Invalid or expired tracking link")
    return _public_order(order)


# ==================== Save & share basket ====================
class SavedItem(BaseModel):
    product_id: str
    quantity: int = 1


class SaveBasketBody(BaseModel):
    items: List[SavedItem]


@engage_router.post("/baskets")
async def save_basket(body: SaveBasketBody):
    if not body.items:
        raise HTTPException(400, "Your basket is empty")
    token = uuid.uuid4().hex[:12]
    await db.saved_baskets.insert_one({
        "token": token,
        "items": [i.model_dump() for i in body.items],
        "created_at": now_utc(),
        "expires_at": now_utc() + timedelta(days=30),
    })
    return {"ok": True, "id": token, "share_path": f"/b/{token}"}


@engage_router.get("/baskets/{token}")
async def get_basket(token: str):
    b = await db.saved_baskets.find_one({"token": token})
    if not b:
        raise HTTPException(404, "This shared basket link is no longer available.")
    items = []
    for it in b.get("items", []):
        try:
            p = await db.products.find_one({"_id": ObjectId(it["product_id"])})
        except Exception:
            p = None
        if not p:
            continue
        pp = public_product(p)
        items.append({
            "product_id": pp["id"], "name": pp.get("name"), "sku": pp.get("sku"),
            "price_ex_vat": pp.get("price_ex_vat"), "vat_rate": pp.get("vat_rate"),
            "image": (pp.get("images") or [None])[0],
            "quantity": it.get("quantity", 1),
            "available_qty": pp.get("available_qty", 0),
        })
    return {"id": token, "items": items}
