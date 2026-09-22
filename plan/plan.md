# Grace Cares — Brief vs. Current Build: Gap Analysis

This compares the *Emergent AI Build Brief v3 (21 Aug 2026)* against the website currently in the codebase. It is a status assessment, not yet a build plan. It ends with the decisions needed before any building starts.

---

## The one thing that changes everything (read first)

The brief opens with three **non‑negotiable** technical requirements:

1. **Server‑rendered HTML (Next.js SSR/SSG)** — every page's main content must be in the initial HTML and readable with JavaScript disabled.
2. Unique stock that can never be sold twice, enforced at the database level.
3. Works properly on every screen from 320px up, including the admin.

**The current site is a client‑rendered React single‑page application (Create React App), not Next.js.** With JavaScript disabled, pages are effectively blank until scripts run. This fails requirement 1 as written, and it undermines much of the SEO/structured‑data intent (Prompts 14, 16) and the "AI systems can read the HTML" principle.

This is the pivotal decision (see end of document): **rebuild the front end on Next.js with server rendering, or continue enhancing the current SPA and accept the SSR/SEO limitation.** Everything else is downstream of that choice.

Two further foundational deviations from the brief's data model:
- **Money is stored as decimals**, not whole pence integers (the brief calls integer pence out specifically for VAT accuracy).
- **Stock is a quantity field on the product**, not a separate physical‑item table. Unique items are handled with a reserved‑quantity counter and a 30‑minute reservation, not the atomic "one physical item, one record, serial number" model the brief requires. Overselling is *mostly* prevented but not by the atomic conditional update the brief insists on, and there is no per‑item serial/asset number for recall traceability.

---

## 1) Built and working today

**Shop & catalogue**
- Categories (CRUD) and products with a `stock_model` field (unique / repeat).
- Product listing with filters (search text, category, condition, fulfilment route, VAT‑relief, price range, in‑stock, featured) and sorts (recent, price, name).
- Product detail page with related items, condition grade, dimensions, max user weight, carbon saving, and a two‑price display (standard vs. VAT‑relief).
- 30‑minute stock reservation with automatic release of expired reservations.

**Checkout & payments (Stripe test mode)**
- Guest checkout; server‑computed totals; Stripe Checkout session.
- VAT‑relief step: a gate question plus a declaration form, applied per‑line to eligible items only, with an editable declaration statement.
- Donation step (a single free amount) held as a separate line, kept out of product revenue.
- Three fulfilment routes (postable / hub collection / bulky delivery); postage by weight bands; a bulky‑delivery questionnaire captured at checkout; admin can issue a separate delivery quote as a Stripe payment link.
- Orders, order status updates with customer emails, refunds (with optional stock return), order notes.

**Admin area** (nine granular roles; editable per‑section permission matrix)
- Product contributor → approver → publish workflow (contributors cannot publish).
- Guided product entry form, image upload to object storage, bulk CSV/XLSX import (with dry‑run) and photo‑zip import, CSV/XLSX/PDF stock reports and exports, SKU suggestion.
- Editable postage bands; editable transactional email templates (with preview/test‑send); redirect manager with CSV import; audit logging.
- Reporting dashboard (sales, VAT, zero‑rated, donations, refunds, items reused, carbon, bookings, downloads, sign‑ups) with period comparison; orders CSV.
- **Xero sync is mocked** (queue, retry, reconciliation view — no live Xero connection).
- VAT declarations list/detail/export, restricted to finance role, with relief totals.
- Users & roles management.

**Content & engagement**
- News/Impact articles; resources (with gated download capturing email); newsletter sign‑up; enquiry form with routing by topic and a "sensitive enquiries" access restriction.
- Events with bookings, capacity, **waiting list**, paid‑event payments, check‑in, and a booking‑reminder cron with per‑event lead time.
- Financial donations one‑off **and monthly (Stripe subscription)** with thank‑you email.
- Equipment donation form with acceptance fields and an admin pipeline.
- **Grace AI**: a rule‑based stub assistant that refuses clinical advice and VAT‑eligibility decisions and points to a human — matching the brief's "stub only" intent.
- `sitemap.xml` and `robots.txt` generated; homepage announcement bar (basic).

---

## 2) Partially built / incomplete (exists, but not to the brief)

- **Search (Prompt 2).** Only a basic case‑insensitive match on name/description/SKU. Missing: predictive/type‑ahead suggestions, a **synonyms/misspelling** field and tolerance, searching across categories/needs/content, sort by "biggest saving / biggest carbon", and the guided finder.
- **VAT declaration (Prompt 5).** Works, but is not a field‑for‑field replica of the live Grace Cares form: no **medical‑condition dropdown list**, no charity fields, mailing‑list/Google‑review opt‑ins not split out as separate consents, and no **staff route to raise a declaration on a tablet** for phone/counter sales. Wording versioning is only partially present.
- **Checkout donation step (Prompt 4).** Only a free amount. Missing **round‑up to nearest pound** and **cover‑the‑card‑fee** options, and the recalculation rules.
- **Equipment donation (Prompt 8).** A single fixed form exists but is **not adaptive by donor type**, has **no acceptance‑checker gate** before the long form, and omits POPs labelling, ownership/right‑to‑donate questions, and "never end with a flat no" routing.
- **Events (Prompt 9/10).** No separate **occurrences** model (a monthly tea party can't be one event with many dates), and accessibility/dietary/**referral‑with‑consent** capture is not structured.
- **Announcement bar (Prompt 6).** Present but lacks per‑page targeting rules, scheduled start/stop, and sticky per‑person dismissal keyed to message version.
- **Assisted/phone orders (Prompt 6/Part F).** Delivery quotes use a payment link, but there is no full "staff raises an order, applies VAT relief, takes payment or records cash, stock decrements identically" flow.
- **Site structure & navigation (Prompt 7).** Only a subset of pages exists. Category set does not match the brief's new eight categories, and old→new **301 redirect mapping** is not in place.
- **Roles (Prompt 6).** Current nine roles are more granular than the brief's four; functional, but a mapping/decision is needed.
- **Accessibility & responsive (Part B/B2).** Not yet audited against WCAG 2.2 AA, 18px minimum, 320px floor, 400% reflow, 13″ short‑viewport, and admin‑on‑tablet requirements.

---

## 3) Missing entirely (not built)

**Architecture & data model**
- Next.js server‑side rendering; integer‑pence money; separate physical **StockItem** table with serial/asset numbers and atomic anti‑oversell; a **Location** dimension on product/stock/order/event.

**Findability (Prompts 2, 14, 16)**
- Guided finder wizard; **need‑based landing pages**; **term‑triggered landing pages** and an admin to manage trigger terms; a proper **Stair Lifts** service page (referral + removal + alternatives); a helpful **zero‑results page** (category buttons + fallback products + stock‑alert form); **search logging, monthly search report**, and Google Search Console / Analytics integration; product JSON‑LD and other structured data (Organization, LocalBusiness, BreadcrumbList, Article, VideoObject, Review/AggregateRating); location pages for towns in the delivery radius.

**Shopping & conversion (Prompts 3, 4, 21)**
- **Postcode address lookup**; save/share a basket and email it; deliver to a different address; **"answer delivery before the basket"** postcode estimate on product pages; genuine "goes with this" suggestions; **bundles** (hospital discharge, bedroom, bathroom); **product video** support with lazy‑load + captions + VideoObject.

**Trust & reviews (Prompt 18)**
- First‑party reviews tied to orders with AggregateRating; a **Google reviews + Facebook recommendations** wall on the homepage; the post‑purchase review‑request loop and QR codes.

**Selling channels (Prompt 19)**
- Google Merchant Center feed; Meta catalogue feed; a fast **"mark sold everywhere"** control covering eBay/counter to prevent double‑selling; Google Business Profile alignment.

**Content management (Prompt 15)**
- A real **page builder / CMS**: templates, constrained blocks, drafts, scheduling, private preview links, version history/restore, reusable blocks, media library, gated assets behind **signed expiring links** with ungated summary pages, and the in‑editor SEO/readability/accessibility assistant. Today's pages are hard‑coded, not editable by the marketing team.

**Partnerships & portals (Prompts 10, 13)**
- Corporate partnership tiers page (entry price shown, others "book a conversation") and gated partnership pack; **Friends of Grace Cares** as its own recurring product; **NHS and care‑provider logged‑in portals** with strict per‑organisation data segregation, PO/bulk pricing, document access, and an **impact dashboard**.

**CRM, consent & automation (Prompt 12)**
- A single **Contact record per person** with role tags, a proper **ConsentRecord** history (wording, version, channel, date, withdrawal), operational‑vs‑marketing separation, and CSV/JSON export shaped for TheCarePro. Current storage is ad‑hoc (subscribers, enquiries) with no unified contact or consent model.

**Order comms & operations (Prompt 16)**
- Full transactional email set (ready‑for‑collection, delivery‑quote‑issued, dispatched‑with‑tracking, etc.); **order tracking without an account** via a signed link; performance budget/monitoring; documented recall process; staging + tested backups.

**Security & data protection (Prompt 17)**
- The data‑protection package: a written **data map**, **encryption of the medical‑condition field** and signed/expiring access to declarations, MFA on admin, security headers/HSTS/CSP, server‑side authorisation checks proven against ID‑swapping, cookie consent that gates loading, DPIA, and UK/EU hosting confirmation. (Note: card data is already kept off‑site via Stripe Checkout, which is good.)

**Email deliverability (Prompt 20)**
- Separate transactional vs. marketing sending subdomains; SPF/DKIM/DMARC; SMS delivery‑day option; consented single abandoned‑basket reminder.

**Pages/sections still absent (Prompt 7 selection)**
- Merch shop (separate from equipment), Special Offers page, Sustainability/Zero‑to‑Landfill, FAQs, Visit Us, the Accessible Shop van service, Meet the Team / Start With a WHY / Our Partners, funder/governance pages, Returns / Accessibility statement / Cookie policy, and the NHS & Care Providers and Other Support sub‑sections.

---

## Decisions needed before any build

1. **Architecture (pivotal).** Rebuild the front end on **Next.js with server rendering** to meet the brief's non‑negotiable requirement (and unlock the SEO/structured‑data/AI‑readability goals), **or** keep enhancing the current React SPA and accept that "readable with JavaScript disabled" and much of the search‑engine intent will not be met. This decision determines whether subsequent work is enhancement or rebuild.

2. **Data‑model corrections.** Whether to adopt the brief's foundations now — integer pence, a separate physical StockItem table with serial numbers and atomic anti‑oversell, and a Location dimension — before more screens are built on top of the current model. Retrofitting these later is expensive.

3. **First build phase.** The brief itself flags Prompts 1–6 as the ones that must be right (data model, search/finder, product page, checkout, VAT declaration, volunteer listing/admin). A sensible first phase is to bring those fully up to brief on the chosen architecture, then tackle content/CMS, partnerships/portals, CRM/consent, and the security/deliverability package in later phases.

4. **Scope confirmations already stated in the brief** (assumed, flag if wrong): equipment **hire is out of scope**; guest checkout stays the default; the medical‑condition field must **not** flow into any marketing CRM; live integrations (Stripe live, Xero, TheCarePro, real email/DNS) stay off until sign‑off.

*No building has started. This document is for review; on approval, a phased build plan will be produced against the decisions above.*
