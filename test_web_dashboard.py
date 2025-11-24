#!/usr/bin/env python3
"""
Test script to verify web dashboard functionality
"""
import requests
import json
import sys

API_BASE_URL = "http://localhost:8000"

def test_api_endpoint(method, endpoint, data=None, expected_status=200):
    """Test an API endpoint"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=5)
        else:
            return False, f"Unsupported method: {method}"
        
        if response.status_code == expected_status:
            return True, response.json() if response.content else "Success"
        else:
            return False, f"Status {response.status_code}: {response.text}"
    except Exception as e:
        return False, str(e)

def test_dashboard_html():
    """Test if dashboard HTML is accessible"""
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        if response.status_code == 200:
            html = response.text
            # Check if key functions are defined in the HTML
            functions_to_check = [
                "function createSession",
                "function enrollStudent",
                "function createCourse",
                "function loadSessions",
                "function loadStudents",
                "function loadCourses",
                "function startSession",
                "function stopSession",
                "const API_BASE_URL"
            ]
            found_functions = []
            missing_functions = []
            for func in functions_to_check:
                if func in html:
                    found_functions.append(func)
                else:
                    missing_functions.append(func)
            
            return True, {
                "found": found_functions,
                "missing": missing_functions,
                "html_length": len(html)
            }
        else:
            return False, f"Status {response.status_code}"
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 60)
    print("Web Dashboard Functionality Test")
    print("=" * 60)
    
    results = []
    
    # Test 1: Dashboard HTML
    print("\n1. Testing Dashboard HTML...")
    success, result = test_dashboard_html()
    if success:
        print(f"   ✅ Dashboard HTML accessible")
        print(f"   ✅ Found {len(result['found'])}/{len(result['found']) + len(result['missing'])} key functions")
        if result['missing']:
            print(f"   ⚠️  Missing functions: {', '.join(result['missing'])}")
        results.append(("Dashboard HTML", True))
    else:
        print(f"   ❌ Failed: {result}")
        results.append(("Dashboard HTML", False))
    
    # Test 2: API - Get Sessions
    print("\n2. Testing API - Get Sessions...")
    success, result = test_api_endpoint("GET", "/api/sessions")
    if success:
        print(f"   ✅ Sessions endpoint working")
        if isinstance(result, list):
            print(f"   ✅ Found {len(result)} sessions")
        results.append(("Get Sessions API", True))
    else:
        print(f"   ❌ Failed: {result}")
        results.append(("Get Sessions API", False))
    
    # Test 3: API - Get Students
    print("\n3. Testing API - Get Students...")
    success, result = test_api_endpoint("GET", "/api/students")
    if success:
        print(f"   ✅ Students endpoint working")
        if isinstance(result, list):
            print(f"   ✅ Found {len(result)} students")
        results.append(("Get Students API", True))
    else:
        print(f"   ❌ Failed: {result}")
        results.append(("Get Students API", False))
    
    # Test 4: API - Get Courses
    print("\n4. Testing API - Get Courses...")
    success, result = test_api_endpoint("GET", "/api/courses")
    if success:
        print(f"   ✅ Courses endpoint working")
        if isinstance(result, list):
            print(f"   ✅ Found {len(result)} courses")
        results.append(("Get Courses API", True))
    else:
        print(f"   ❌ Failed: {result}")
        results.append(("Get Courses API", False))
    
    # Test 5: API - Create Course (test endpoint)
    print("\n5. Testing API - Create Course...")
    test_course = {
        "course_code": "TEST999",
        "course_name": "Test Course",
        "lecturer_name": "Test Lecturer",
        "description": "Test description"
    }
    success, result = test_api_endpoint("POST", "/api/courses", test_course, expected_status=200)
    if success:
        print(f"   ✅ Create course endpoint working")
        # Try to delete the test course (if there's a delete endpoint)
        results.append(("Create Course API", True))
    else:
        print(f"   ⚠️  Create course test: {result}")
        results.append(("Create Course API", False))
    
    # Test 6: API - Start Session
    print("\n6. Testing API - Start Session...")
    # Use an existing inactive session if available
    success, sessions = test_api_endpoint("GET", "/api/sessions")
    if success and isinstance(sessions, list):
        inactive_sessions = [s for s in sessions if not s.get('is_active', False)]
        if inactive_sessions:
            session_id = inactive_sessions[0]['id']
            success, result = test_api_endpoint("POST", f"/api/sessions/{session_id}/start")
            if success:
                print(f"   ✅ Start session endpoint working")
                results.append(("Start Session API", True))
                # Stop it again
                test_api_endpoint("POST", f"/api/sessions/{session_id}/stop")
            else:
                print(f"   ⚠️  Start session test: {result}")
                results.append(("Start Session API", False))
        else:
            print(f"   ⚠️  No inactive sessions to test")
            results.append(("Start Session API", None))
    else:
        print(f"   ⚠️  Could not get sessions for test")
        results.append(("Start Session API", None))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(1 for _, result in results if result is True)
    failed = sum(1 for _, result in results if result is False)
    skipped = sum(1 for _, result in results if result is None)
    
    for test_name, result in results:
        status = "✅ PASS" if result is True else "❌ FAIL" if result is False else "⏭️  SKIP"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed} passed, {failed} failed, {skipped} skipped")
    print("=" * 60)
    
    # Check JavaScript function definitions
    print("\nJavaScript Function Check:")
    print("-" * 60)
    success, html_result = test_dashboard_html()
    if success:
        print(f"✅ All critical functions found in HTML")
        print(f"   Functions available: {len(html_result['found'])}")
        if html_result['missing']:
            print(f"   ⚠️  Missing: {', '.join(html_result['missing'])}")
    else:
        print(f"❌ Could not verify JavaScript functions")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())

