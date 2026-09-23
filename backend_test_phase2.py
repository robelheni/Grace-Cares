#!/usr/bin/env python3
"""Backend API tests for Grace Cares Phase 2: CMS, Engagement & Data features"""
import requests
import json
from typing import Dict, Any

# Configuration
BASE_URL = "https://show-site-4.preview.emergentagent.com/api"
ADMIN_EMAIL = "paul@cass-online.co.uk"
ADMIN_PASSWORD = "GraceCares2026!"

# Test results tracking
results = {
    "passed": [],
    "failed": [],
    "warnings": []
}


def log_pass(test_name: str, details: str = ""):
    """Log a passing test"""
    msg = f"✅ {test_name}"
    if details:
        msg += f": {details}"
    results["passed"].append(msg)
    print(msg)


def log_fail(test_name: str, details: str):
    """Log a failing test"""
    msg = f"❌ {test_name}: {details}"
    results["failed"].append(msg)
    print(msg)


def log_warning(test_name: str, details: str):
    """Log a warning"""
    msg = f"⚠️  {test_name}: {details}"
    results["warnings"].append(msg)
    print(msg)


def admin_login() -> requests.Session:
    """Login as admin and return session with cookies"""
    session = requests.Session()
    try:
        resp = session.post(
            f"{BASE_URL}/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            timeout=10
        )
        if resp.status_code == 200:
            log_pass("Admin login", f"Logged in as {ADMIN_EMAIL}")
            return session
        else:
            log_fail("Admin login", f"Status {resp.status_code}: {resp.text[:200]}")
            return None
    except Exception as e:
        log_fail("Admin login", f"Exception: {str(e)}")
        return None


def test_cms_dynamic_content(admin_session: requests.Session):
    """Test 1: CMS & dynamic site content"""
    print("\n=== TEST 1: CMS & Dynamic Content ===")
    
    # Test 1a: GET /api/content/site (public)
    try:
        resp = requests.get(f"{BASE_URL}/content/site", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            has_hero_title = "hero_title" in data
            if has_hero_title:
                log_pass("GET /api/content/site", f"Retrieved site content with hero_title: '{data.get('hero_title')}'")
            else:
                log_fail("GET /api/content/site", "Missing hero_title field")
        else:
            log_fail("GET /api/content/site", f"Status {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        log_fail("GET /api/content/site", f"Exception: {str(e)}")
    
    # Test 1b: PUT /api/admin/content/site without auth (should be 401/403)
    try:
        resp = requests.put(
            f"{BASE_URL}/admin/content/site",
            json={"content": {"hero_title": "TEST HERO"}},
            timeout=10
        )
        if resp.status_code in [401, 403]:
            log_pass("PUT /api/admin/content/site (no auth)", f"Correctly returned {resp.status_code} (protected)")
        else:
            log_fail("PUT /api/admin/content/site (no auth)", f"Expected 401/403, got {resp.status_code}")
    except Exception as e:
        log_fail("PUT /api/admin/content/site (no auth)", f"Exception: {str(e)}")
    
    # Test 1c: PUT /api/admin/content/site with admin auth
    if admin_session:
        try:
            resp = admin_session.put(
                f"{BASE_URL}/admin/content/site",
                json={"content": {"hero_title": "TEST HERO"}},
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("ok"):
                    log_pass("PUT /api/admin/content/site (admin)", "Successfully updated site content")
                    
                    # Test 1d: Verify the change persisted
                    verify_resp = requests.get(f"{BASE_URL}/content/site", timeout=10)
                    if verify_resp.status_code == 200:
                        verify_data = verify_resp.json()
                        if verify_data.get("hero_title") == "TEST HERO":
                            log_pass("Verify site content persistence", "hero_title correctly updated to 'TEST HERO'")
                        else:
                            log_fail("Verify site content persistence", f"Expected 'TEST HERO', got '{verify_data.get('hero_title')}'")
                    else:
                        log_fail("Verify site content persistence", f"Status {verify_resp.status_code}")
                else:
                    log_fail("PUT /api/admin/content/site (admin)", f"Response: {data}")
            else:
                log_fail("PUT /api/admin/content/site (admin)", f"Status {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            log_fail("PUT /api/admin/content/site (admin)", f"Exception: {str(e)}")


def test_cms_pages(admin_session: requests.Session):
    """Test 2: CMS pages CRUD"""
    print("\n=== TEST 2: CMS Pages ===")
    
    # Test 2a: GET /api/cms/pages (public list)
    try:
        resp = requests.get(f"{BASE_URL}/cms/pages", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list):
                # Should have seeded 'our-story' page
                has_our_story = any(p.get("slug") == "our-story" for p in data)
                log_pass("GET /api/cms/pages", f"Retrieved {len(data)} pages, 'our-story' seeded: {has_our_story}")
            else:
                log_fail("GET /api/cms/pages", f"Expected list, got {type(data)}")
        else:
            log_fail("GET /api/cms/pages", f"Status {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        log_fail("GET /api/cms/pages", f"Exception: {str(e)}")
    
    # Test 2b: GET /api/cms/page/our-story (public page)
    try:
        resp = requests.get(f"{BASE_URL}/cms/page/our-story", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            has_title = "title" in data
            has_sections = "sections" in data
            if has_title and has_sections:
                log_pass("GET /api/cms/page/our-story", f"Retrieved page: '{data.get('title')}'")
            else:
                log_fail("GET /api/cms/page/our-story", "Missing title or sections")
        else:
            log_fail("GET /api/cms/page/our-story", f"Status {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        log_fail("GET /api/cms/page/our-story", f"Exception: {str(e)}")
    
    # Test 2c: GET /api/admin/cms/pages without auth (should be 401/403)
    try:
        resp = requests.get(f"{BASE_URL}/admin/cms/pages", timeout=10)
        if resp.status_code in [401, 403]:
            log_pass("GET /api/admin/cms/pages (no auth)", f"Correctly returned {resp.status_code} (protected)")
        else:
            log_fail("GET /api/admin/cms/pages (no auth)", f"Expected 401/403, got {resp.status_code}")
    except Exception as e:
        log_fail("GET /api/admin/cms/pages (no auth)", f"Exception: {str(e)}")
    
    # Test 2d: Admin CMS CRUD
    if admin_session:
        created_page_id = None
        
        # GET admin pages list
        try:
            resp = admin_session.get(f"{BASE_URL}/admin/cms/pages", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                log_pass("GET /api/admin/cms/pages (admin)", f"Retrieved {len(data)} pages")
            else:
                log_fail("GET /api/admin/cms/pages (admin)", f"Status {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            log_fail("GET /api/admin/cms/pages (admin)", f"Exception: {str(e)}")
        
        # POST create new page
        try:
            resp = admin_session.post(
                f"{BASE_URL}/admin/cms/pages",
                json={
                    "slug": "test-x",
                    "title": "Test X",
                    "sections": [{"type": "text", "heading": "H", "body": "B"}],
                    "status": "published"
                },
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                created_page_id = data.get("id")
                log_pass("POST /api/admin/cms/pages", f"Created page 'test-x' with id: {created_page_id}")
            else:
                log_fail("POST /api/admin/cms/pages", f"Status {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            log_fail("POST /api/admin/cms/pages", f"Exception: {str(e)}")
        
        # GET the created page publicly
        try:
            resp = requests.get(f"{BASE_URL}/cms/page/test-x", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("title") == "Test X":
                    log_pass("GET /api/cms/page/test-x", "Created page is publicly accessible")
                else:
                    log_fail("GET /api/cms/page/test-x", f"Title mismatch: {data.get('title')}")
            else:
                log_fail("GET /api/cms/page/test-x", f"Status {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            log_fail("GET /api/cms/page/test-x", f"Exception: {str(e)}")
        
        # PUT update the page
        if created_page_id:
            try:
                resp = admin_session.put(
                    f"{BASE_URL}/admin/cms/pages/{created_page_id}",
                    json={
                        "slug": "test-x",
                        "title": "Test X Updated",
                        "sections": [{"type": "text", "heading": "H", "body": "B"}],
                        "status": "published"
                    },
                    timeout=10
                )
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("title") == "Test X Updated":
                        log_pass("PUT /api/admin/cms/pages/{id}", "Successfully updated page title")
                    else:
                        log_fail("PUT /api/admin/cms/pages/{id}", f"Title not updated: {data.get('title')}")
                else:
                    log_fail("PUT /api/admin/cms/pages/{id}", f"Status {resp.status_code}: {resp.text[:200]}")
            except Exception as e:
                log_fail("PUT /api/admin/cms/pages/{id}", f"Exception: {str(e)}")
            
            # DELETE the page
            try:
                resp = admin_session.delete(f"{BASE_URL}/admin/cms/pages/{created_page_id}", timeout=10)
                if resp.status_code == 200:
                    log_pass("DELETE /api/admin/cms/pages/{id}", "Successfully deleted page")
                else:
                    log_fail("DELETE /api/admin/cms/pages/{id}", f"Status {resp.status_code}: {resp.text[:200]}")
            except Exception as e:
                log_fail("DELETE /api/admin/cms/pages/{id}", f"Exception: {str(e)}")


def test_announcement(admin_session: requests.Session):
    """Test 3: Announcement bar"""
    print("\n=== TEST 3: Announcement Bar ===")
    
    # Test 3a: GET /api/announcement (public)
    try:
        resp = requests.get(f"{BASE_URL}/announcement", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            has_active = "active" in data
            if has_active:
                log_pass("GET /api/announcement", f"Retrieved announcement, active: {data.get('active')}")
            else:
                log_fail("GET /api/announcement", "Missing 'active' field")
        else:
            log_fail("GET /api/announcement", f"Status {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        log_fail("GET /api/announcement", f"Exception: {str(e)}")
    
    # Test 3b: GET /api/admin/announcement without auth (should be 401/403)
    try:
        resp = requests.get(f"{BASE_URL}/admin/announcement", timeout=10)
        if resp.status_code in [401, 403]:
            log_pass("GET /api/admin/announcement (no auth)", f"Correctly returned {resp.status_code} (protected)")
        else:
            log_fail("GET /api/admin/announcement (no auth)", f"Expected 401/403, got {resp.status_code}")
    except Exception as e:
        log_fail("GET /api/admin/announcement (no auth)", f"Exception: {str(e)}")
    
    # Test 3c: PUT /api/admin/announcement without auth (should be 401/403)
    try:
        resp = requests.put(
            f"{BASE_URL}/admin/announcement",
            json={"enabled": True, "text": "Hi", "version": 2, "paths": ["/shop"], "dismissible": True},
            timeout=10
        )
        if resp.status_code in [401, 403]:
            log_pass("PUT /api/admin/announcement (no auth)", f"Correctly returned {resp.status_code} (protected)")
        else:
            log_fail("PUT /api/admin/announcement (no auth)", f"Expected 401/403, got {resp.status_code}")
    except Exception as e:
        log_fail("PUT /api/admin/announcement (no auth)", f"Exception: {str(e)}")
    
    # Test 3d: Admin announcement GET/PUT
    if admin_session:
        # GET admin announcement
        try:
            resp = admin_session.get(f"{BASE_URL}/admin/announcement", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                log_pass("GET /api/admin/announcement (admin)", f"Retrieved announcement config")
            else:
                log_fail("GET /api/admin/announcement (admin)", f"Status {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            log_fail("GET /api/admin/announcement (admin)", f"Exception: {str(e)}")
        
        # PUT update announcement
        try:
            resp = admin_session.put(
                f"{BASE_URL}/admin/announcement",
                json={
                    "enabled": True,
                    "text": "Hi",
                    "version": 2,
                    "paths": ["/shop"],
                    "dismissible": True
                },
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("ok"):
                    log_pass("PUT /api/admin/announcement (admin)", "Successfully updated announcement")
                    
                    # Verify persistence
                    verify_resp = requests.get(f"{BASE_URL}/announcement", timeout=10)
                    if verify_resp.status_code == 200:
                        verify_data = verify_resp.json()
                        if verify_data.get("text") == "Hi" and verify_data.get("version") == 2:
                            log_pass("Verify announcement persistence", "Announcement correctly updated")
                        else:
                            log_fail("Verify announcement persistence", f"Data mismatch: {verify_data}")
                    else:
                        log_fail("Verify announcement persistence", f"Status {verify_resp.status_code}")
                else:
                    log_fail("PUT /api/admin/announcement (admin)", f"Response: {data}")
            else:
                log_fail("PUT /api/admin/announcement (admin)", f"Status {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            log_fail("PUT /api/admin/announcement (admin)", f"Exception: {str(e)}")


def test_guided_finder():
    """Test 4: Guided finder"""
    print("\n=== TEST 4: Guided Finder ===")
    
    # Test 4a: GET /api/finder/config
    try:
        resp = requests.get(f"{BASE_URL}/finder/config", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            has_steps = "steps" in data
            if has_steps:
                steps = data.get("steps", [])
                log_pass("GET /api/finder/config", f"Retrieved finder config with {len(steps)} steps")
            else:
                log_fail("GET /api/finder/config", "Missing 'steps' field")
        else:
            log_fail("GET /api/finder/config", f"Status {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        log_fail("GET /api/finder/config", f"Exception: {str(e)}")
    
    # Test 4b: POST /api/finder/resolve
    try:
        resp = requests.post(
            f"{BASE_URL}/finder/resolve",
            json={"category": "Mobility", "max_price": 200},
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            has_count = "count" in data
            has_shop_url = "shop_url" in data
            if has_count and has_shop_url:
                count = data.get("count")
                shop_url = data.get("shop_url")
                if isinstance(count, int):
                    log_pass("POST /api/finder/resolve", f"Resolved to {count} products, shop_url: {shop_url}")
                else:
                    log_fail("POST /api/finder/resolve", f"count is not int: {type(count)}")
            else:
                log_fail("POST /api/finder/resolve", f"Missing fields - count:{has_count}, shop_url:{has_shop_url}")
        else:
            log_fail("POST /api/finder/resolve", f"Status {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        log_fail("POST /api/finder/resolve", f"Exception: {str(e)}")


def test_landing_pages():
    """Test 5: Need-based landing pages"""
    print("\n=== TEST 5: Need-based Landing Pages ===")
    
    # Test 5a: GET /api/landing (list)
    try:
        resp = requests.get(f"{BASE_URL}/landing", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list):
                # Should have 3 seeded pages
                has_leaving_hospital = any(p.get("slug") == "leaving-hospital" for p in data)
                log_pass("GET /api/landing", f"Retrieved {len(data)} landing pages, 'leaving-hospital' seeded: {has_leaving_hospital}")
            else:
                log_fail("GET /api/landing", f"Expected list, got {type(data)}")
        else:
            log_fail("GET /api/landing", f"Status {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        log_fail("GET /api/landing", f"Exception: {str(e)}")
    
    # Test 5b: GET /api/landing/leaving-hospital
    try:
        resp = requests.get(f"{BASE_URL}/landing/leaving-hospital", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            has_products = "products" in data
            if has_products:
                products = data.get("products", [])
                log_pass("GET /api/landing/leaving-hospital", f"Retrieved landing page with {len(products)} products")
            else:
                log_fail("GET /api/landing/leaving-hospital", "Missing 'products' array")
        else:
            log_fail("GET /api/landing/leaving-hospital", f"Status {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        log_fail("GET /api/landing/leaving-hospital", f"Exception: {str(e)}")
    
    # Test 5c: GET /api/landing/nonexistent (should be 404)
    try:
        resp = requests.get(f"{BASE_URL}/landing/nonexistent", timeout=10)
        if resp.status_code == 404:
            log_pass("GET /api/landing/nonexistent", "Correctly returned 404")
        else:
            log_fail("GET /api/landing/nonexistent", f"Expected 404, got {resp.status_code}")
    except Exception as e:
        log_fail("GET /api/landing/nonexistent", f"Exception: {str(e)}")


def test_bundles():
    """Test 6: Product bundles"""
    print("\n=== TEST 6: Product Bundles ===")
    
    # Test 6a: GET /api/bundles (list)
    try:
        resp = requests.get(f"{BASE_URL}/bundles", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list):
                # Should have 3 seeded bundles
                if len(data) >= 3:
                    # Check structure of first bundle
                    first = data[0]
                    has_total = "total" in first
                    has_item_count = "item_count" in first
                    if has_total and has_item_count:
                        log_pass("GET /api/bundles", f"Retrieved {len(data)} bundles with total & item_count")
                    else:
                        log_fail("GET /api/bundles", f"Missing fields - total:{has_total}, item_count:{has_item_count}")
                else:
                    log_warning("GET /api/bundles", f"Expected 3 seeded bundles, got {len(data)}")
            else:
                log_fail("GET /api/bundles", f"Expected list, got {type(data)}")
        else:
            log_fail("GET /api/bundles", f"Status {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        log_fail("GET /api/bundles", f"Exception: {str(e)}")
    
    # Test 6b: GET /api/bundles/bathroom
    try:
        resp = requests.get(f"{BASE_URL}/bundles/bathroom", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            has_products = "products" in data
            has_total = "total" in data
            has_saving = "saving" in data
            if has_products and has_total and has_saving:
                products = data.get("products", [])
                log_pass("GET /api/bundles/bathroom", f"Retrieved bundle with {len(products)} products, total: £{data.get('total')}, saving: £{data.get('saving')}")
            else:
                log_fail("GET /api/bundles/bathroom", f"Missing fields - products:{has_products}, total:{has_total}, saving:{has_saving}")
        else:
            log_fail("GET /api/bundles/bathroom", f"Status {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        log_fail("GET /api/bundles/bathroom", f"Exception: {str(e)}")
    
    # Test 6c: GET /api/bundles/nope (should be 404)
    try:
        resp = requests.get(f"{BASE_URL}/bundles/nope", timeout=10)
        if resp.status_code == 404:
            log_pass("GET /api/bundles/nope", "Correctly returned 404")
        else:
            log_fail("GET /api/bundles/nope", f"Expected 404, got {resp.status_code}")
    except Exception as e:
        log_fail("GET /api/bundles/nope", f"Exception: {str(e)}")


def test_reviews(admin_session: requests.Session):
    """Test 7: First-party reviews tied to orders"""
    print("\n=== TEST 7: First-party Reviews ===")
    
    # Get a product ID first
    product_id = None
    try:
        resp = requests.get(f"{BASE_URL}/products", params={"limit": 1}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            items = data.get("items", [])
            if items:
                product_id = items[0].get("id")
                log_pass("Get product ID", f"Retrieved product ID: {product_id}")
            else:
                log_warning("Get product ID", "No products found")
        else:
            log_fail("Get product ID", f"Status {resp.status_code}")
    except Exception as e:
        log_fail("Get product ID", f"Exception: {str(e)}")
    
    # Test 7a: POST /api/reviews with fake order (should be 404)
    if product_id:
        try:
            resp = requests.post(
                f"{BASE_URL}/reviews",
                json={
                    "product_id": product_id,
                    "order_reference": "GC-00000000",
                    "email": "test@example.com",
                    "author_name": "Test User",
                    "rating": 5,
                    "title": "Great product",
                    "body": "Very satisfied"
                },
                timeout=10
            )
            if resp.status_code == 404:
                log_pass("POST /api/reviews (fake order)", "Correctly returned 404 (order not found)")
            else:
                log_fail("POST /api/reviews (fake order)", f"Expected 404, got {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            log_fail("POST /api/reviews (fake order)", f"Exception: {str(e)}")
    
    # Test 7b: GET /api/products/{pid}/reviews
    if product_id:
        try:
            resp = requests.get(f"{BASE_URL}/products/{product_id}/reviews", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                has_items = "items" in data
                has_aggregate = "aggregate" in data
                if has_items and has_aggregate:
                    items = data.get("items", [])
                    aggregate = data.get("aggregate", {})
                    has_average = "average" in aggregate
                    has_count = "count" in aggregate
                    if has_average and has_count:
                        log_pass("GET /api/products/{pid}/reviews", f"Retrieved {len(items)} reviews, aggregate: {aggregate}")
                    else:
                        log_fail("GET /api/products/{pid}/reviews", f"Missing aggregate fields - average:{has_average}, count:{has_count}")
                else:
                    log_fail("GET /api/products/{pid}/reviews", f"Missing fields - items:{has_items}, aggregate:{has_aggregate}")
            else:
                log_fail("GET /api/products/{pid}/reviews", f"Status {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            log_fail("GET /api/products/{pid}/reviews", f"Exception: {str(e)}")
    
    # Test 7c: GET /api/admin/reviews without auth (should be 401/403)
    try:
        resp = requests.get(f"{BASE_URL}/admin/reviews", timeout=10)
        if resp.status_code in [401, 403]:
            log_pass("GET /api/admin/reviews (no auth)", f"Correctly returned {resp.status_code} (protected)")
        else:
            log_fail("GET /api/admin/reviews (no auth)", f"Expected 401/403, got {resp.status_code}")
    except Exception as e:
        log_fail("GET /api/admin/reviews (no auth)", f"Exception: {str(e)}")
    
    # Test 7d: GET /api/admin/reviews with admin auth
    if admin_session:
        try:
            resp = admin_session.get(f"{BASE_URL}/admin/reviews", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list):
                    log_pass("GET /api/admin/reviews (admin)", f"Retrieved {len(data)} reviews")
                else:
                    log_fail("GET /api/admin/reviews (admin)", f"Expected list, got {type(data)}")
            else:
                log_fail("GET /api/admin/reviews (admin)", f"Status {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            log_fail("GET /api/admin/reviews (admin)", f"Exception: {str(e)}")


def test_crm_contacts(admin_session: requests.Session):
    """Test 8: CRM Contact + ConsentRecord"""
    print("\n=== TEST 8: CRM Contact + ConsentRecord ===")
    
    # Test 8a: Trigger contact capture via POST /api/newsletter
    try:
        resp = requests.post(
            f"{BASE_URL}/newsletter",
            json={"email": "crmtest@example.com", "name": "CRM Test", "consent": True},
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get("ok"):
                log_pass("POST /api/newsletter", "Successfully captured contact via newsletter signup")
            else:
                log_fail("POST /api/newsletter", f"Response: {data}")
        else:
            log_fail("POST /api/newsletter", f"Status {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        log_fail("POST /api/newsletter", f"Exception: {str(e)}")
    
    # Test 8b: GET /api/admin/contacts without auth (should be 401/403)
    try:
        resp = requests.get(f"{BASE_URL}/admin/contacts", params={"q": "crmtest"}, timeout=10)
        if resp.status_code in [401, 403]:
            log_pass("GET /api/admin/contacts (no auth)", f"Correctly returned {resp.status_code} (protected)")
        else:
            log_fail("GET /api/admin/contacts (no auth)", f"Expected 401/403, got {resp.status_code}")
    except Exception as e:
        log_fail("GET /api/admin/contacts (no auth)", f"Exception: {str(e)}")
    
    # Test 8c: GET /api/admin/contacts?q=crmtest with admin auth
    if admin_session:
        try:
            resp = admin_session.get(f"{BASE_URL}/admin/contacts", params={"q": "crmtest"}, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list):
                    # Find our test contact
                    found = None
                    for contact in data:
                        if contact.get("email") == "crmtest@example.com":
                            found = contact
                            break
                    
                    if found:
                        role_tags = found.get("role_tags", [])
                        has_newsletter = "newsletter" in role_tags
                        if has_newsletter:
                            log_pass("GET /api/admin/contacts?q=crmtest", f"Found contact with role_tags: {role_tags}")
                        else:
                            log_fail("GET /api/admin/contacts?q=crmtest", f"Contact found but missing 'newsletter' tag: {role_tags}")
                    else:
                        log_fail("GET /api/admin/contacts?q=crmtest", "Contact not found")
                else:
                    log_fail("GET /api/admin/contacts?q=crmtest", f"Expected list, got {type(data)}")
            else:
                log_fail("GET /api/admin/contacts?q=crmtest", f"Status {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            log_fail("GET /api/admin/contacts?q=crmtest", f"Exception: {str(e)}")
        
        # Test 8d: GET /api/admin/contacts/{email} with admin auth
        try:
            resp = admin_session.get(f"{BASE_URL}/admin/contacts/crmtest@example.com", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                has_consents = "consents" in data
                if has_consents:
                    consents = data.get("consents", [])
                    # Should have a granted marketing consent
                    has_marketing = any(c.get("type") == "marketing" and c.get("action") == "granted" for c in consents)
                    if has_marketing:
                        log_pass("GET /api/admin/contacts/{email}", f"Retrieved contact with {len(consents)} consent records, including granted marketing consent")
                    else:
                        log_warning("GET /api/admin/contacts/{email}", f"Retrieved contact but no granted marketing consent found in {len(consents)} records")
                else:
                    log_fail("GET /api/admin/contacts/{email}", "Missing 'consents' array")
            else:
                log_fail("GET /api/admin/contacts/{email}", f"Status {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            log_fail("GET /api/admin/contacts/{email}", f"Exception: {str(e)}")
    
    # Test 8e: POST /api/consent/withdraw
    try:
        resp = requests.post(
            f"{BASE_URL}/consent/withdraw",
            json={"email": "crmtest@example.com", "type": "marketing"},
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get("ok"):
                log_pass("POST /api/consent/withdraw", "Successfully withdrew consent")
            else:
                log_fail("POST /api/consent/withdraw", f"Response: {data}")
        else:
            log_fail("POST /api/consent/withdraw", f"Status {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        log_fail("POST /api/consent/withdraw", f"Exception: {str(e)}")
    
    # Test 8f: GET /api/admin/contacts-export.csv without auth (should be 401/403)
    try:
        resp = requests.get(f"{BASE_URL}/admin/contacts-export.csv", timeout=10)
        if resp.status_code in [401, 403]:
            log_pass("GET /api/admin/contacts-export.csv (no auth)", f"Correctly returned {resp.status_code} (protected)")
        else:
            log_fail("GET /api/admin/contacts-export.csv (no auth)", f"Expected 401/403, got {resp.status_code}")
    except Exception as e:
        log_fail("GET /api/admin/contacts-export.csv (no auth)", f"Exception: {str(e)}")
    
    # Test 8g: GET /api/admin/contacts-export.csv with admin auth
    if admin_session:
        try:
            resp = admin_session.get(f"{BASE_URL}/admin/contacts-export.csv", timeout=10)
            if resp.status_code == 200:
                content_type = resp.headers.get("content-type", "")
                if "text/csv" in content_type:
                    log_pass("GET /api/admin/contacts-export.csv (admin)", f"Retrieved CSV export ({len(resp.text)} bytes)")
                else:
                    log_fail("GET /api/admin/contacts-export.csv (admin)", f"Expected text/csv, got {content_type}")
            else:
                log_fail("GET /api/admin/contacts-export.csv (admin)", f"Status {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            log_fail("GET /api/admin/contacts-export.csv (admin)", f"Exception: {str(e)}")


def test_order_tracking():
    """Test 9: Order tracking (no account)"""
    print("\n=== TEST 9: Order Tracking (No Account) ===")
    
    # Test 9a: POST /api/track/request with invalid order (should be 404)
    try:
        resp = requests.post(
            f"{BASE_URL}/track/request",
            json={"reference": "GC-00000000", "email": "nobody@example.com"},
            timeout=10
        )
        if resp.status_code == 404:
            log_pass("POST /api/track/request (invalid order)", "Correctly returned 404 (order not found)")
        else:
            log_fail("POST /api/track/request (invalid order)", f"Expected 404, got {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        log_fail("POST /api/track/request (invalid order)", f"Exception: {str(e)}")
    
    # Test 9b: GET /api/track with invalid token (should be 404 or 403)
    try:
        resp = requests.get(f"{BASE_URL}/track", params={"ref": "GC-00000000", "token": "bad"}, timeout=10)
        if resp.status_code in [404, 403]:
            log_pass("GET /api/track (invalid token)", f"Correctly returned {resp.status_code} (invalid/expired link)")
        else:
            log_fail("GET /api/track (invalid token)", f"Expected 404/403, got {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        log_fail("GET /api/track (invalid token)", f"Exception: {str(e)}")


def test_saved_baskets():
    """Test 10: Save & share basket"""
    print("\n=== TEST 10: Save & Share Basket ===")
    
    # Get a product ID first
    product_id = None
    try:
        resp = requests.get(f"{BASE_URL}/products", params={"limit": 1}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            items = data.get("items", [])
            if items:
                product_id = items[0].get("id")
                log_pass("Get product ID for basket", f"Retrieved product ID: {product_id}")
            else:
                log_warning("Get product ID for basket", "No products found")
        else:
            log_fail("Get product ID for basket", f"Status {resp.status_code}")
    except Exception as e:
        log_fail("Get product ID for basket", f"Exception: {str(e)}")
    
    # Test 10a: POST /api/baskets with empty items (should be 400)
    try:
        resp = requests.post(
            f"{BASE_URL}/baskets",
            json={"items": []},
            timeout=10
        )
        if resp.status_code == 400:
            log_pass("POST /api/baskets (empty items)", "Correctly returned 400 (basket is empty)")
        else:
            log_fail("POST /api/baskets (empty items)", f"Expected 400, got {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        log_fail("POST /api/baskets (empty items)", f"Exception: {str(e)}")
    
    # Test 10b: POST /api/baskets with valid item
    basket_id = None
    if product_id:
        try:
            resp = requests.post(
                f"{BASE_URL}/baskets",
                json={"items": [{"product_id": product_id, "quantity": 1}]},
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                has_id = "id" in data
                has_share_path = "share_path" in data
                if has_id and has_share_path:
                    basket_id = data.get("id")
                    share_path = data.get("share_path")
                    log_pass("POST /api/baskets", f"Created basket with id: {basket_id}, share_path: {share_path}")
                else:
                    log_fail("POST /api/baskets", f"Missing fields - id:{has_id}, share_path:{has_share_path}")
            else:
                log_fail("POST /api/baskets", f"Status {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            log_fail("POST /api/baskets", f"Exception: {str(e)}")
    
    # Test 10c: GET /api/baskets/{id}
    if basket_id:
        try:
            resp = requests.get(f"{BASE_URL}/baskets/{basket_id}", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                has_items = "items" in data
                if has_items:
                    items = data.get("items", [])
                    if len(items) > 0:
                        first_item = items[0]
                        has_name = "name" in first_item
                        has_price = "price_ex_vat" in first_item
                        if has_name and has_price:
                            log_pass("GET /api/baskets/{id}", f"Retrieved basket with {len(items)} items, resolved product: {first_item.get('name')}")
                        else:
                            log_fail("GET /api/baskets/{id}", f"Item missing fields - name:{has_name}, price:{has_price}")
                    else:
                        log_fail("GET /api/baskets/{id}", "Items array is empty")
                else:
                    log_fail("GET /api/baskets/{id}", "Missing 'items' array")
            else:
                log_fail("GET /api/baskets/{id}", f"Status {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            log_fail("GET /api/baskets/{id}", f"Exception: {str(e)}")
    
    # Test 10d: GET /api/baskets/badtoken (should be 404)
    try:
        resp = requests.get(f"{BASE_URL}/baskets/badtoken", timeout=10)
        if resp.status_code == 404:
            log_pass("GET /api/baskets/badtoken", "Correctly returned 404 (basket not found)")
        else:
            log_fail("GET /api/baskets/badtoken", f"Expected 404, got {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        log_fail("GET /api/baskets/badtoken", f"Exception: {str(e)}")


def print_summary():
    """Print test summary"""
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    print(f"\n✅ PASSED: {len(results['passed'])}")
    for msg in results['passed']:
        print(f"  {msg}")
    
    if results['warnings']:
        print(f"\n⚠️  WARNINGS: {len(results['warnings'])}")
        for msg in results['warnings']:
            print(f"  {msg}")
    
    if results['failed']:
        print(f"\n❌ FAILED: {len(results['failed'])}")
        for msg in results['failed']:
            print(f"  {msg}")
    
    print("\n" + "="*60)
    total = len(results['passed']) + len(results['failed'])
    pass_rate = (len(results['passed']) / total * 100) if total > 0 else 0
    print(f"PASS RATE: {pass_rate:.1f}% ({len(results['passed'])}/{total})")
    print("="*60 + "\n")


def main():
    """Run all tests"""
    print("="*60)
    print("Grace Cares Backend Tests - Phase 2: CMS, Engagement & Data")
    print("="*60)
    print(f"Base URL: {BASE_URL}")
    print(f"Admin: {ADMIN_EMAIL}")
    print("="*60)
    
    # Login as admin first
    admin_session = admin_login()
    
    # Run all tests
    test_cms_dynamic_content(admin_session)
    test_cms_pages(admin_session)
    test_announcement(admin_session)
    test_guided_finder()
    test_landing_pages()
    test_bundles()
    test_reviews(admin_session)
    test_crm_contacts(admin_session)
    test_order_tracking()
    test_saved_baskets()
    
    # Print summary
    print_summary()
    
    # Exit with appropriate code
    if results['failed']:
        exit(1)
    else:
        exit(0)


if __name__ == "__main__":
    main()
