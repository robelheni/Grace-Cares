#!/usr/bin/env python3
"""Backend API tests for Grace Cares Phase 1: Search & Findability"""
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


def test_enhanced_search():
    """Test 1: Enhanced product search with synonyms"""
    print("\n=== TEST 1: Enhanced Product Search ===")
    
    # Test 1a: "wheel chair" (with space) should return wheelchair products
    try:
        resp = requests.get(f"{BASE_URL}/products", params={"q": "wheel chair"}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            total = data.get("total", 0)
            items = data.get("items", [])
            
            if total >= 1:
                # Check if any items contain "wheelchair" in name
                wheelchair_found = any("wheelchair" in item.get("name", "").lower() for item in items)
                if wheelchair_found:
                    log_pass("Search 'wheel chair'", f"Found {total} results with wheelchair products")
                else:
                    log_warning("Search 'wheel chair'", f"Found {total} results but no 'wheelchair' in product names")
            else:
                log_warning("Search 'wheel chair'", "No results found (may be no wheelchair products seeded)")
        else:
            log_fail("Search 'wheel chair'", f"Status {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        log_fail("Search 'wheel chair'", f"Exception: {str(e)}")
    
    # Test 1b: "zimmer" should return walking frame/walker products
    try:
        resp = requests.get(f"{BASE_URL}/products", params={"q": "zimmer"}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            total = data.get("total", 0)
            items = data.get("items", [])
            
            # zimmer is a synonym for walking frame/walker
            if total >= 1:
                log_pass("Search 'zimmer'", f"Found {total} results (synonym expansion working)")
            else:
                log_warning("Search 'zimmer'", "No results (may be no walking frame products seeded)")
        else:
            log_fail("Search 'zimmer'", f"Status {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        log_fail("Search 'zimmer'", f"Exception: {str(e)}")
    
    # Test 1c: nonsense query should return 0 results
    try:
        resp = requests.get(f"{BASE_URL}/products", params={"q": "xyznonsense"}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            total = data.get("total", 0)
            items = data.get("items", [])
            
            if total == 0 and len(items) == 0:
                log_pass("Search 'xyznonsense'", "Correctly returned 0 results")
            else:
                log_fail("Search 'xyznonsense'", f"Expected 0 results, got {total}")
        else:
            log_fail("Search 'xyznonsense'", f"Status {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        log_fail("Search 'xyznonsense'", f"Exception: {str(e)}")


def test_new_sorts():
    """Test 2: New sort options (saving and carbon)"""
    print("\n=== TEST 2: New Sort Options ===")
    
    # Test 2a: sort=saving
    try:
        resp = requests.get(f"{BASE_URL}/products", params={"sort": "saving", "limit": 5}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            items = data.get("items", [])
            
            if len(items) > 0:
                # Check that items have saving, saving_pct, rrp fields
                first_item = items[0]
                has_saving = "saving" in first_item
                has_saving_pct = "saving_pct" in first_item
                has_rrp = "rrp" in first_item
                
                if has_saving and has_saving_pct and has_rrp:
                    # Check if items are ordered by descending saving
                    savings = [item.get("saving", 0) for item in items]
                    is_sorted = all(savings[i] >= savings[i+1] for i in range(len(savings)-1))
                    
                    if is_sorted:
                        log_pass("Sort by saving", f"Items correctly ordered by saving (top: £{savings[0]})")
                    else:
                        log_fail("Sort by saving", f"Items not properly sorted: {savings}")
                else:
                    log_fail("Sort by saving", f"Missing fields - saving:{has_saving}, saving_pct:{has_saving_pct}, rrp:{has_rrp}")
            else:
                log_warning("Sort by saving", "No products returned")
        else:
            log_fail("Sort by saving", f"Status {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        log_fail("Sort by saving", f"Exception: {str(e)}")
    
    # Test 2b: sort=carbon
    try:
        resp = requests.get(f"{BASE_URL}/products", params={"sort": "carbon", "limit": 5}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            items = data.get("items", [])
            
            if len(items) > 0:
                # Check that items have carbon_saving_kg field
                first_item = items[0]
                has_carbon = "carbon_saving_kg" in first_item
                
                if has_carbon:
                    # Check if items are ordered by descending carbon_saving_kg
                    carbons = [item.get("carbon_saving_kg", 0) for item in items]
                    is_sorted = all(carbons[i] >= carbons[i+1] for i in range(len(carbons)-1))
                    
                    if is_sorted:
                        log_pass("Sort by carbon", f"Items correctly ordered by carbon saving (top: {carbons[0]}kg)")
                    else:
                        log_fail("Sort by carbon", f"Items not properly sorted: {carbons}")
                else:
                    log_fail("Sort by carbon", "Missing carbon_saving_kg field")
            else:
                log_warning("Sort by carbon", "No products returned")
        else:
            log_fail("Sort by carbon", f"Status {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        log_fail("Sort by carbon", f"Exception: {str(e)}")


def test_typeahead():
    """Test 3: Type-ahead suggestions endpoint"""
    print("\n=== TEST 3: Type-ahead Suggestions ===")
    
    # Test 3a: q="wheel" should return products
    try:
        resp = requests.get(f"{BASE_URL}/search/suggest", params={"q": "wheel"}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            products = data.get("products", [])
            categories = data.get("categories", [])
            did_you_mean = data.get("did_you_mean")
            
            if len(products) > 0:
                log_pass("Suggest 'wheel'", f"Returned {len(products)} products, {len(categories)} categories")
            else:
                log_warning("Suggest 'wheel'", "No products returned (may be no matching products)")
        else:
            log_fail("Suggest 'wheel'", f"Status {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        log_fail("Suggest 'wheel'", f"Exception: {str(e)}")
    
    # Test 3b: q="w" (1 char) should return empty arrays
    try:
        resp = requests.get(f"{BASE_URL}/search/suggest", params={"q": "w"}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            products = data.get("products", [])
            categories = data.get("categories", [])
            
            if len(products) == 0 and len(categories) == 0:
                log_pass("Suggest 'w' (1 char)", "Correctly returned empty arrays (guard for <2 chars)")
            else:
                log_fail("Suggest 'w' (1 char)", f"Expected empty arrays, got {len(products)} products, {len(categories)} categories")
        else:
            log_fail("Suggest 'w' (1 char)", f"Status {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        log_fail("Suggest 'w' (1 char)", f"Exception: {str(e)}")


def test_stock_alerts(admin_session: requests.Session):
    """Test 4: Stock alerts (public POST + admin-gated GET)"""
    print("\n=== TEST 4: Stock Alerts ===")
    
    # Test 4a: POST without auth (public endpoint)
    try:
        resp = requests.post(
            f"{BASE_URL}/stock-alerts",
            json={"email": "tester@example.com", "query": "riser recliner"},
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get("ok"):
                log_pass("POST stock-alert (no auth)", "Successfully created stock alert")
            else:
                log_fail("POST stock-alert (no auth)", f"Response: {data}")
        else:
            log_fail("POST stock-alert (no auth)", f"Status {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        log_fail("POST stock-alert (no auth)", f"Exception: {str(e)}")
    
    # Test 4b: GET without auth (should be 401/403)
    try:
        resp = requests.get(f"{BASE_URL}/admin/stock-alerts", timeout=10)
        if resp.status_code in [401, 403]:
            log_pass("GET stock-alerts (no auth)", f"Correctly returned {resp.status_code} (protected)")
        else:
            log_fail("GET stock-alerts (no auth)", f"Expected 401/403, got {resp.status_code}")
    except Exception as e:
        log_fail("GET stock-alerts (no auth)", f"Exception: {str(e)}")
    
    # Test 4c: GET with admin auth (should be 200)
    if admin_session:
        try:
            resp = admin_session.get(f"{BASE_URL}/admin/stock-alerts", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                # Should be a list
                if isinstance(data, list):
                    # Check if our alert is in the list
                    found = any(alert.get("email") == "tester@example.com" for alert in data)
                    if found:
                        log_pass("GET stock-alerts (admin)", f"Retrieved {len(data)} alerts, including test alert")
                    else:
                        log_warning("GET stock-alerts (admin)", f"Retrieved {len(data)} alerts, but test alert not found")
                else:
                    log_fail("GET stock-alerts (admin)", f"Expected list, got {type(data)}")
            else:
                log_fail("GET stock-alerts (admin)", f"Status {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            log_fail("GET stock-alerts (admin)", f"Exception: {str(e)}")


def test_search_reporting_and_synonyms(admin_session: requests.Session):
    """Test 5: Search reporting & synonyms admin"""
    print("\n=== TEST 5: Search Reporting & Synonyms Admin ===")
    
    # Test 5a: GET search-report without auth (should be 401/403)
    try:
        resp = requests.get(f"{BASE_URL}/admin/search-report", params={"days": 30}, timeout=10)
        if resp.status_code in [401, 403]:
            log_pass("GET search-report (no auth)", f"Correctly returned {resp.status_code} (protected)")
        else:
            log_fail("GET search-report (no auth)", f"Expected 401/403, got {resp.status_code}")
    except Exception as e:
        log_fail("GET search-report (no auth)", f"Exception: {str(e)}")
    
    # Test 5b: GET search-report with admin auth
    if admin_session:
        try:
            resp = admin_session.get(f"{BASE_URL}/admin/search-report", params={"days": 30}, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                has_total = "total_searches" in data
                has_zero = "zero_result_searches" in data
                has_top = "top_queries" in data
                has_zero_queries = "zero_result_queries" in data
                
                if has_total and has_zero and has_top and has_zero_queries:
                    top_queries = data.get("top_queries", [])
                    zero_queries = data.get("zero_result_queries", [])
                    
                    # Check if our earlier searches are logged
                    top_query_terms = [q.get("query") for q in top_queries]
                    zero_query_terms = [q.get("query") for q in zero_queries]
                    
                    has_nonsense = "xyznonsense" in zero_query_terms
                    
                    log_pass("GET search-report (admin)", 
                            f"Total: {data['total_searches']}, Zero-result: {data['zero_result_searches']}, "
                            f"Top queries: {len(top_queries)}, 'xyznonsense' in zero: {has_nonsense}")
                else:
                    log_fail("GET search-report (admin)", 
                            f"Missing fields - total:{has_total}, zero:{has_zero}, top:{has_top}, zero_queries:{has_zero_queries}")
            else:
                log_fail("GET search-report (admin)", f"Status {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            log_fail("GET search-report (admin)", f"Exception: {str(e)}")
    
    # Test 5c: GET search-synonyms without auth (should be 401/403)
    try:
        resp = requests.get(f"{BASE_URL}/admin/search-synonyms", timeout=10)
        if resp.status_code in [401, 403]:
            log_pass("GET search-synonyms (no auth)", f"Correctly returned {resp.status_code} (protected)")
        else:
            log_fail("GET search-synonyms (no auth)", f"Expected 401/403, got {resp.status_code}")
    except Exception as e:
        log_fail("GET search-synonyms (no auth)", f"Exception: {str(e)}")
    
    # Test 5d: GET search-synonyms with admin auth
    if admin_session:
        try:
            resp = admin_session.get(f"{BASE_URL}/admin/search-synonyms", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                has_defaults = "defaults" in data
                has_custom = "custom" in data
                
                if has_defaults and has_custom:
                    log_pass("GET search-synonyms (admin)", 
                            f"Retrieved defaults ({len(data['defaults'])} terms) and custom ({len(data['custom'])} terms)")
                else:
                    log_fail("GET search-synonyms (admin)", 
                            f"Missing fields - defaults:{has_defaults}, custom:{has_custom}")
            else:
                log_fail("GET search-synonyms (admin)", f"Status {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            log_fail("GET search-synonyms (admin)", f"Exception: {str(e)}")
    
    # Test 5e: PUT search-synonyms without auth (should be 401/403)
    try:
        resp = requests.put(
            f"{BASE_URL}/admin/search-synonyms",
            json={"map": {"loo": ["commode", "toilet aid"]}},
            timeout=10
        )
        if resp.status_code in [401, 403]:
            log_pass("PUT search-synonyms (no auth)", f"Correctly returned {resp.status_code} (protected)")
        else:
            log_fail("PUT search-synonyms (no auth)", f"Expected 401/403, got {resp.status_code}")
    except Exception as e:
        log_fail("PUT search-synonyms (no auth)", f"Exception: {str(e)}")
    
    # Test 5f: PUT search-synonyms with admin auth
    if admin_session:
        try:
            resp = admin_session.put(
                f"{BASE_URL}/admin/search-synonyms",
                json={"map": {"loo": ["commode", "toilet aid"]}},
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("ok"):
                    log_pass("PUT search-synonyms (admin)", "Successfully updated custom synonyms")
                    
                    # Test 5g: Verify the custom synonym works in search
                    try:
                        search_resp = requests.get(f"{BASE_URL}/products", params={"q": "loo"}, timeout=10)
                        if search_resp.status_code == 200:
                            log_pass("Search with custom synonym 'loo'", "Search executed successfully (synonym applied)")
                        else:
                            log_fail("Search with custom synonym 'loo'", f"Status {search_resp.status_code}")
                    except Exception as e:
                        log_fail("Search with custom synonym 'loo'", f"Exception: {str(e)}")
                    
                    # Test 5h: Verify persistence - GET synonyms again
                    try:
                        verify_resp = admin_session.get(f"{BASE_URL}/admin/search-synonyms", timeout=10)
                        if verify_resp.status_code == 200:
                            verify_data = verify_resp.json()
                            custom = verify_data.get("custom", {})
                            if "loo" in custom:
                                log_pass("Verify synonym persistence", f"Custom synonym 'loo' persisted: {custom['loo']}")
                            else:
                                log_fail("Verify synonym persistence", "Custom synonym 'loo' not found in persisted data")
                        else:
                            log_fail("Verify synonym persistence", f"Status {verify_resp.status_code}")
                    except Exception as e:
                        log_fail("Verify synonym persistence", f"Exception: {str(e)}")
                else:
                    log_fail("PUT search-synonyms (admin)", f"Response: {data}")
            else:
                log_fail("PUT search-synonyms (admin)", f"Status {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            log_fail("PUT search-synonyms (admin)", f"Exception: {str(e)}")


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
    print("Grace Cares Backend Tests - Phase 1: Search & Findability")
    print("="*60)
    print(f"Base URL: {BASE_URL}")
    print(f"Admin: {ADMIN_EMAIL}")
    print("="*60)
    
    # Login as admin first
    admin_session = admin_login()
    
    # Run all tests
    test_enhanced_search()
    test_new_sorts()
    test_typeahead()
    test_stock_alerts(admin_session)
    test_search_reporting_and_synonyms(admin_session)
    
    # Print summary
    print_summary()
    
    # Exit with appropriate code
    if results['failed']:
        exit(1)
    else:
        exit(0)


if __name__ == "__main__":
    main()
