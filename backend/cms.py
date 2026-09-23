"""CMS, dynamic site content, announcement scheduling/targeting, guided finder,
need-based landing pages, and product bundles. Does NOT touch checkout/stock model."""
import os
import base64
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from core import db, now_utc, clean, cleans
from auth import require_admin
from shop import public_product, log_audit
from storage import upload_image

cms_router = APIRouter(prefix="/api")


def _parse_dt(v):
    if not v:
        return None
    try:
        return datetime.fromisoformat(str(v).replace("Z", "+00:00"))
    except Exception:
        return None


async def _setting(key, default=None):
    s = await db.site_settings.find_one({"key": key})
    if not s:
        return default
    s = clean(s)
    s.pop("key", None)
    return s


# ---------------- Global editable site content (hero etc.) ----------------
DEFAULT_SITE_CONTENT = {
    "hero_eyebrow": "Award-winning not-for-profit CIC",
    "hero_title": "Affordable care equipment. Meaningful social impact.",
    "hero_highlight": "Let's Make Care Sustainable.",
    "hero_body": "We rescue, refurbish and resell used care and mobility equipment at half the RRP or less, and reinvest every penny into free community programmes.",
    "hero_image": "",
    "hero_cta_label": "Shop care equipment",
    "hero_cta_link": "/shop",
}


@cms_router.get("/content/site")
async def get_site_content():
    stored = await _setting("site_content", {})
    return {**DEFAULT_SITE_CONTENT, **(stored or {})}


class SiteContentBody(BaseModel):
    content: dict


@cms_router.put("/admin/content/site")
async def put_site_content(body: SiteContentBody, user=Depends(require_admin("content_admin"))):
    merged = {**DEFAULT_SITE_CONTENT, **(body.content or {})}
    await db.site_settings.update_one({"key": "site_content"}, {"$set": merged}, upsert=True)
    await log_audit(user, "update", "site_content")
    return {"ok": True, "content": merged}


# ---------------- Image upload for CMS ----------------
class UploadBody(BaseModel):
    data_url: str  # data:image/png;base64,....


@cms_router.post("/admin/upload")
async def admin_upload(body: UploadBody, user=Depends(require_admin("content_admin"))):
    try:
        header, b64 = body.data_url.split(",", 1)
        ext = "png"
        if "image/" in header:
            ext = header.split("image/")[1].split(";")[0] or "png"
        raw = base64.b64decode(b64)
        url = upload_image(raw, ext)
        return {"url": url}
    except Exception as e:
        raise HTTPException(400, f"Upload failed: {e}")


# ---------------- CMS pages ----------------
class CmsPageBody(BaseModel):
    slug: str
    title: str
    sections: List[dict] = []   # [{type: 'text'|'image'|'hero'|'html', ...}]
    seo_title: Optional[str] = ""
    seo_description: Optional[str] = ""
    status: str = "published"   # draft | published


@cms_router.get("/cms/pages")
async def list_public_pages():
    docs = await db.cms_pages.find({"status": "published"}).sort("title", 1).to_list(200)
    return [{"slug": d.get("slug"), "title": d.get("title")} for d in docs]


@cms_router.get("/cms/page/{slug}")
async def get_public_page(slug: str):
    d = await db.cms_pages.find_one({"slug": slug, "status": "published"})
    if not d:
        raise HTTPException(404, "Page not found")
    return clean(d)


@cms_router.get("/admin/cms/pages")
async def admin_list_pages(user=Depends(require_admin("content_admin"))):
    docs = await db.cms_pages.find().sort("updated_at", -1).to_list(500)
    return cleans(docs)


@cms_router.get("/admin/cms/page/{pid}")
async def admin_get_page(pid: str, user=Depends(require_admin("content_admin"))):
    d = await db.cms_pages.find_one({"_id": ObjectId(pid)})
    if not d:
        raise HTTPException(404, "Page not found")
    return clean(d)


@cms_router.post("/admin/cms/pages")
async def admin_create_page(body: CmsPageBody, user=Depends(require_admin("content_admin"))):
    if await db.cms_pages.find_one({"slug": body.slug}):
        raise HTTPException(409, "A page with that slug already exists")
    doc = body.model_dump()
    doc["created_at"] = now_utc()
    doc["updated_at"] = now_utc()
    res = await db.cms_pages.insert_one(doc)
    await log_audit(user, "create", "cms_page", str(res.inserted_id), after={"slug": body.slug})
    return clean(await db.cms_pages.find_one({"_id": res.inserted_id}))


@cms_router.put("/admin/cms/pages/{pid}")
async def admin_update_page(pid: str, body: CmsPageBody, user=Depends(require_admin("content_admin"))):
    upd = body.model_dump()
    upd["updated_at"] = now_utc()
    await db.cms_pages.update_one({"_id": ObjectId(pid)}, {"$set": upd})
    await log_audit(user, "update", "cms_page", pid)
    return clean(await db.cms_pages.find_one({"_id": ObjectId(pid)}))


@cms_router.delete("/admin/cms/pages/{pid}")
async def admin_delete_page(pid: str, user=Depends(require_admin("content_admin"))):
    await db.cms_pages.delete_one({"_id": ObjectId(pid)})
    await log_audit(user, "delete", "cms_page", pid)
    return {"ok": True}


# ---------------- Announcement bar (scheduling + targeting + dismissal) ----------------
DEFAULT_ANNOUNCEMENT = {
    "enabled": True,
    "text": "New stock added weekly \u2014 call 01543 730189 if you can't find what you need.",
    "link": "/shop",
    "version": 1,
    "dismissible": True,
    "start_at": "",
    "end_at": "",
    "paths": [],   # empty = all pages; otherwise list of path prefixes e.g. ['/shop','/product']
    "style": "lime",
}


@cms_router.get("/announcement")
async def get_announcement():
    a = {**DEFAULT_ANNOUNCEMENT, **((await _setting("announcement", {})) or {})}
    now = datetime.now(timezone.utc)
    active = bool(a.get("enabled")) and bool(a.get("text"))
    sd = _parse_dt(a.get("start_at"))
    ed = _parse_dt(a.get("end_at"))
    if sd and now < sd:
        active = False
    if ed and now > ed:
        active = False
    a["active"] = active
    return a


class AnnouncementBody(BaseModel):
    enabled: bool = True
    text: str = ""
    link: Optional[str] = ""
    version: int = 1
    dismissible: bool = True
    start_at: Optional[str] = ""
    end_at: Optional[str] = ""
    paths: List[str] = []
    style: Optional[str] = "lime"


@cms_router.get("/admin/announcement")
async def admin_get_announcement(user=Depends(require_admin("content_admin"))):
    return {**DEFAULT_ANNOUNCEMENT, **((await _setting("announcement", {})) or {})}


@cms_router.put("/admin/announcement")
async def admin_put_announcement(body: AnnouncementBody, user=Depends(require_admin("content_admin"))):
    data = body.model_dump()
    await db.site_settings.update_one({"key": "announcement"}, {"$set": data}, upsert=True)
    await log_audit(user, "update", "announcement")
    return {"ok": True, "announcement": data}


# ---------------- Guided finder ----------------
DEFAULT_FINDER = {
    "steps": [
        {"id": "who", "title": "Who is this for?", "options": [
            {"label": "Myself", "value": "self"},
            {"label": "Someone I care for", "value": "other"},
            {"label": "A patient / resident", "value": "professional"}]},
        {"id": "need", "title": "What do you need help with?", "options": [
            {"label": "Getting around", "category": "Mobility"},
            {"label": "Bathing & washing", "category": "Bathing"},
            {"label": "Sleeping & beds", "category": "Beds"},
            {"label": "Using the toilet", "category": "Toilet Aids"},
            {"label": "Preventing falls", "category": "Fall Prevention"},
            {"label": "Moving & handling", "category": "Moving and Handling"}]},
        {"id": "budget", "title": "Any budget in mind?", "options": [
            {"label": "Under \u00a350", "max_price": 50},
            {"label": "\u00a350\u2013\u00a3150", "min_price": 50, "max_price": 150},
            {"label": "\u00a3150+", "min_price": 150},
            {"label": "Show me everything"}]},
    ]
}


@cms_router.get("/finder/config")
async def finder_config():
    return {**DEFAULT_FINDER, **((await _setting("finder_config", {})) or {})}


class FinderResolveBody(BaseModel):
    category: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None


@cms_router.post("/finder/resolve")
async def finder_resolve(body: FinderResolveBody):
    query = {"status": {"$nin": ["hidden", "draft", "awaiting_approval"]}}
    params = {}
    if body.category:
        cat = await db.categories.find_one({"name": {"$regex": f"^{body.category}$", "$options": "i"}})
        if cat:
            query["category_id"] = str(cat["_id"])
            params["category_id"] = str(cat["_id"])
    if body.min_price is not None or body.max_price is not None:
        pr = {}
        if body.min_price is not None:
            pr["$gte"] = body.min_price
            params["min_price"] = body.min_price
        if body.max_price is not None:
            pr["$lte"] = body.max_price
            params["max_price"] = body.max_price
        query["price_ex_vat"] = pr
    count = await db.products.count_documents(query)
    qs = "&".join(f"{k}={v}" for k, v in params.items())
    return {"count": count, "shop_query": qs, "shop_url": f"/shop?{qs}" if qs else "/shop"}


# ---------------- Need-based landing pages ----------------
@cms_router.get("/landing")
async def list_landing():
    docs = await db.landing_pages.find({"published": {"$ne": False}}).to_list(100)
    return [{"slug": d.get("slug"), "title": d.get("title"), "intro": d.get("intro")} for d in docs]


async def _resolve_category_products(category_names, per_cat=6, limit=12):
    out = []
    seen = set()
    for name in category_names or []:
        cat = await db.categories.find_one({"name": {"$regex": f"^{name}$", "$options": "i"}})
        if not cat:
            continue
        docs = await db.products.find({
            "category_id": str(cat["_id"]),
            "status": {"$nin": ["hidden", "draft", "awaiting_approval"]},
        }).limit(per_cat).to_list(per_cat)
        for d in docs:
            p = public_product(d)
            if p["id"] in seen or p.get("available_qty", 0) <= 0:
                continue
            seen.add(p["id"])
            out.append(p)
    return out[:limit]


@cms_router.get("/landing/{slug}")
async def get_landing(slug: str):
    d = await db.landing_pages.find_one({"slug": slug})
    if not d:
        raise HTTPException(404, "Page not found")
    page = clean(d)
    page["products"] = await _resolve_category_products(d.get("categories", []))
    return page


# ---------------- Bundles ----------------
@cms_router.get("/bundles")
async def list_bundles():
    docs = await db.bundles.find({"published": {"$ne": False}}).to_list(50)
    out = []
    for d in docs:
        products = await _resolve_category_products(d.get("categories", []), per_cat=1, limit=6)
        total = round(sum(p.get("price_inc_vat", 0) for p in products), 2)
        rrp = round(sum((p.get("rrp") or 0) for p in products), 2)
        out.append({"slug": d.get("slug"), "title": d.get("title"),
                    "description": d.get("description"), "image": d.get("image"),
                    "item_count": len(products), "total": total,
                    "saving": round(rrp - total, 2) if rrp > total else 0})
    return out


@cms_router.get("/bundles/{slug}")
async def get_bundle(slug: str):
    d = await db.bundles.find_one({"slug": slug})
    if not d:
        raise HTTPException(404, "Bundle not found")
    bundle = clean(d)
    products = await _resolve_category_products(d.get("categories", []), per_cat=1, limit=6)
    bundle["products"] = products
    bundle["total"] = round(sum(p.get("price_inc_vat", 0) for p in products), 2)
    rrp = round(sum((p.get("rrp") or 0) for p in products), 2)
    bundle["rrp_total"] = rrp
    bundle["saving"] = round(rrp - bundle["total"], 2) if rrp > bundle["total"] else 0
    return bundle


# ---------------- Seeding ----------------
DEFAULT_LANDING = [
    {"slug": "help-after-a-fall", "title": "Help after a fall",
     "intro": "Practical, affordable equipment to help someone recover confidence and stay safe at home after a fall.",
     "categories": ["Fall Prevention", "Mobility", "Moving and Handling"],
     "body": "A fall can knock anyone's confidence. The right equipment \u2014 from grab rails to walking aids \u2014 helps people move safely again. Everything here is cleaned, safety-checked and priced fairly.",
     "faqs": [{"q": "Where do I start?", "a": "If you're unsure, call us on 01543 730189 \u2014 we're happy to talk it through, with no pressure to buy."}],
     "published": True},
    {"slug": "leaving-hospital", "title": "Coming home from hospital",
     "intro": "Everything you might need to make a discharge home safe and comfortable \u2014 often at short notice.",
     "categories": ["Beds", "Mobility", "Moving and Handling", "Toilet Aids"],
     "body": "Being discharged can happen quickly. We keep serviced profiling beds, wheelchairs and aids ready to go, at a fraction of new prices, with delivery available.",
     "faqs": [{"q": "Can you deliver quickly?", "a": "Often yes \u2014 call us and we'll do our best to help with short-notice needs."}],
     "published": True},
    {"slug": "living-with-arthritis", "title": "Living well with arthritis",
     "intro": "Small aids that make everyday tasks easier on painful joints \u2014 in the kitchen, bathroom and beyond.",
     "categories": ["Kitchen and Catering", "Bathing", "Toilet Aids"],
     "body": "The right aids take the strain off sore hands and joints, helping you stay independent and comfortable at home.",
     "faqs": [], "published": True},
]

DEFAULT_BUNDLES = [
    {"slug": "hospital-discharge", "title": "Hospital discharge bundle",
     "description": "The essentials for a safe, comfortable return home after a hospital stay.",
     "image": "", "categories": ["Beds", "Mobility"], "published": True},
    {"slug": "bedroom", "title": "Bedroom comfort bundle",
     "description": "Everything for a safer, more comfortable bedroom \u2014 rest and transfers made easier.",
     "image": "", "categories": ["Beds", "Moving and Handling"], "published": True},
    {"slug": "bathroom", "title": "Bathroom safety bundle",
     "description": "Stay safe and independent in the bathroom with these carefully chosen aids.",
     "image": "", "categories": ["Bathing", "Toilet Aids"], "published": True},
]

DEFAULT_CMS_PAGES = [
    {"slug": "our-story", "title": "Our story", "status": "published",
     "seo_title": "Our story | Grace Cares", "seo_description": "Why Grace Cares exists and the difference we make.",
     "sections": [
         {"type": "text", "heading": "Why we started", "body": "Grace Cares began with a simple belief: good care equipment should be affordable, and nothing usable should go to waste. We rescue, refurbish and resell equipment, reinvesting every penny into free community programmes."},
         {"type": "text", "heading": "Our mission", "body": "To make care sustainable \u2014 kinder on families' budgets and on the planet."},
     ]},
]


async def seed_cms():
    for lp in DEFAULT_LANDING:
        await db.landing_pages.update_one({"slug": lp["slug"]}, {"$setOnInsert": lp}, upsert=True)
    for b in DEFAULT_BUNDLES:
        await db.bundles.update_one({"slug": b["slug"]}, {"$setOnInsert": b}, upsert=True)
    for p in DEFAULT_CMS_PAGES:
        exists = await db.cms_pages.find_one({"slug": p["slug"]})
        if not exists:
            doc = dict(p)
            doc["created_at"] = now_utc()
            doc["updated_at"] = now_utc()
            await db.cms_pages.insert_one(doc)
