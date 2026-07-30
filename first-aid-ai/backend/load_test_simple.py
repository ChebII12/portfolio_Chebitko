#!/usr/bin/env python
"""
Simple synchronous load test for API endpoints.
"""
import time
import requests
import uuid
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "http://127.0.0.1:8000/api"
NUM_THREADS = 5
NUM_REQUESTS = 30

results = {
    "health": {"success": 0, "failed": 0, "times": []},
    "register": {"success": 0, "failed": 0, "times": []},
    "questionnaire": {"success": 0, "failed": 0, "times": []},
}

def test_health():
    try:
        start = time.time()
        r = requests.get(f"{BASE_URL}/health", timeout=10)
        elapsed = time.time() - start
        if r.status_code == 200:
            results["health"]["success"] += 1
        else:
            results["health"]["failed"] += 1
        results["health"]["times"].append(elapsed)
    except Exception as e:
        results["health"]["failed"] += 1
        results["health"]["times"].append(0)

def test_register():
    try:
        start = time.time()
        payload = {
            "name": f"LoadTest{uuid.uuid4().hex[:8]}",
            "email": f"test{uuid.uuid4().hex[:8]}@example.com",
            "password": "LoadTest123!"
        }
        r = requests.post(f"{BASE_URL}/auth/register", json=payload, timeout=10)
        elapsed = time.time() - start
        if r.status_code == 200:
            results["register"]["success"] += 1
        else:
            results["register"]["failed"] += 1
        results["register"]["times"].append(elapsed)
    except Exception as e:
        results["register"]["failed"] += 1
        results["register"]["times"].append(0)

def test_questionnaire(user_id):
    try:
        start = time.time()
        payload = {
            "user_id": user_id,
            "answers": [
                "Weekly",
                "A few hours away",
                "Yes, advanced instructor/responder",
                "Yes, for critical emergencies",
                "Trained and comfortable using",
                "Designated group medic/leader"
            ]
        }
        r = requests.post(f"{BASE_URL}/questionnaire/analyze", json=payload, timeout=10)
        elapsed = time.time() - start
        if r.status_code == 200:
            results["questionnaire"]["success"] += 1
        else:
            results["questionnaire"]["failed"] += 1
        results["questionnaire"]["times"].append(elapsed)
    except Exception as e:
        results["questionnaire"]["failed"] += 1
        results["questionnaire"]["times"].append(0)

print(f"\n{'='*70}")
print("First Aid AI - API Load Test (Synchronous)")
print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Threads: {NUM_THREADS}, Requests per Endpoint: {NUM_REQUESTS}")
print(f"{'='*70}\n")

# Create a test user first
print("Creating test user...")
try:
    payload = {
        "name": "LoadTestUser",
        "email": f"loadtest{uuid.uuid4().hex[:8]}@example.com",
        "password": "LoadTest123!"
    }
    r = requests.post(f"{BASE_URL}/auth/register", json=payload, timeout=10)
    if r.status_code == 200:
        test_user_id = r.json().get("user_id")
        print(f"✅ Test user created: {test_user_id}")
    else:
        print("❌ Failed to create test user")
        test_user_id = str(uuid.uuid4())
except Exception as e:
    print(f"❌ Error creating test user: {e}")
    test_user_id = str(uuid.uuid4())

# Test health endpoint
print(f"\nTesting health endpoint ({NUM_REQUESTS} requests)...")
with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
    futures = [executor.submit(test_health) for _ in range(NUM_REQUESTS)]
    for future in as_completed(futures):
        pass

# Test registration
print(f"Testing registration ({NUM_REQUESTS} requests)...")
with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
    futures = [executor.submit(test_register) for _ in range(NUM_REQUESTS)]
    for future in as_completed(futures):
        pass

# Test questionnaire
print(f"Testing questionnaire ({NUM_REQUESTS} requests)...")
with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
    futures = [executor.submit(test_questionnaire, test_user_id) for _ in range(NUM_REQUESTS)]
    for future in as_completed(futures):
        pass

# Print results
print(f"\n{'='*70}")
print("LOAD TEST RESULTS")
print(f"{'='*70}\n")

total_requests = 0
total_success = 0

for endpoint, data in results.items():
    total = data["success"] + data["failed"]
    total_requests += total
    total_success += data["success"]
    
    if total > 0:
        success_rate = (data["success"] / total) * 100
        avg_time = sum(data["times"]) / len(data["times"])
        min_time = min(data["times"])
        max_time = max(data["times"])
        
        print(f"{endpoint.upper()}")
        print(f"  Total:          {total} requests")
        print(f"  Success:        {data['success']}")
        print(f"  Failed:         {data['failed']}")
        print(f"  Success Rate:   {success_rate:.1f}%")
        print(f"  Avg Time:       {avg_time*1000:.2f} ms")
        print(f"  Min Time:       {min_time*1000:.2f} ms")
        print(f"  Max Time:       {max_time*1000:.2f} ms")
        print()

print(f"{'='*70}")
print(f"OVERALL SUMMARY")
print(f"{'='*70}")
print(f"Total Requests:       {total_requests}")
print(f"Total Successful:     {total_success}")
print(f"Total Failed:         {total_requests - total_success}")
if total_requests > 0:
    print(f"Overall Success Rate: {(total_success / total_requests) * 100:.1f}%")
print(f"End Time:             {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"{'='*70}\n")

if total_success / total_requests >= 0.95:
    print("✅ LOAD TEST PASSED - API is stable under load")
else:
    print("⚠️  LOAD TEST WARNING - API showed some failures")

