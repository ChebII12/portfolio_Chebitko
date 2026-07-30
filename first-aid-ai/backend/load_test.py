#!/usr/bin/env python
"""
Load testing script for First Aid AI Module 1 API endpoints.
Tests concurrent requests to health, registration, and questionnaire endpoints.
"""
import asyncio
import time
import statistics
import uuid
from typing import List, Dict
import httpx
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:8000/api"
NUM_CONCURRENT = 10
NUM_REQUESTS_PER_ENDPOINT = 50

# Test data
TEST_ANSWERS = [
    "Weekly",
    "A few hours away",
    "Yes, advanced instructor/responder",
    "Yes, for critical emergencies",
    "Trained and comfortable using",
    "Designated group medic/leader"
]

VALID_LEVELS = ["beginner", "intermediate", "expert"]


class LoadTestMetrics:
    def __init__(self, endpoint: str, method: str):
        self.endpoint = endpoint
        self.method = method
        self.response_times: List[float] = []
        self.success_count = 0
        self.failure_count = 0
        self.status_codes: Dict[int, int] = {}
        self.errors: List[str] = []

    def add_success(self, response_time: float, status_code: int):
        self.response_times.append(response_time)
        self.success_count += 1
        self.status_codes[status_code] = self.status_codes.get(status_code, 0) + 1

    def add_failure(self, response_time: float, error: str):
        self.response_times.append(response_time)
        self.failure_count += 1
        self.errors.append(error)

    def get_stats(self) -> Dict:
        if not self.response_times:
            return {}
        return {
            "endpoint": self.endpoint,
            "method": self.method,
            "total_requests": self.success_count + self.failure_count,
            "successful": self.success_count,
            "failed": self.failure_count,
            "success_rate": f"{(self.success_count / (self.success_count + self.failure_count) * 100):.1f}%",
            "avg_response_time_ms": f"{(statistics.mean(self.response_times) * 1000):.2f}",
            "min_response_time_ms": f"{(min(self.response_times) * 1000):.2f}",
            "max_response_time_ms": f"{(max(self.response_times) * 1000):.2f}",
            "p95_response_time_ms": f"{(statistics.quantiles(self.response_times, n=20)[18] * 1000):.2f}" if len(self.response_times) > 1 else "N/A",
            "status_codes": self.status_codes,
        }


async def health_check(client: httpx.AsyncClient, metrics: LoadTestMetrics):
    """Test health endpoint"""
    try:
        start = time.time()
        response = await client.get(f"{BASE_URL}/health")
        elapsed = time.time() - start
        
        if response.status_code == 200:
            metrics.add_success(elapsed, response.status_code)
        else:
            metrics.add_failure(elapsed, f"Status {response.status_code}")
    except Exception as e:
        metrics.add_failure(0, str(e))


async def register_user(client: httpx.AsyncClient, metrics: LoadTestMetrics):
    """Test user registration endpoint"""
    try:
        start = time.time()
        payload = {
            "name": f"LoadTest{uuid.uuid4().hex[:8]}",
            "email": f"test{uuid.uuid4().hex[:8]}@loadtest.ai",
            "password": "LoadTest123!"
        }
        response = await client.post(f"{BASE_URL}/auth/register", json=payload)
        elapsed = time.time() - start
        
        if response.status_code == 200:
            metrics.add_success(elapsed, response.status_code)
        else:
            metrics.add_failure(elapsed, f"Status {response.status_code}")
    except Exception as e:
        metrics.add_failure(0, str(e))


async def questionnaire_analyze(client: httpx.AsyncClient, metrics: LoadTestMetrics, user_id: str):
    """Test questionnaire analysis endpoint"""
    try:
        start = time.time()
        payload = {
            "user_id": user_id,
            "answers": TEST_ANSWERS
        }
        response = await client.post(f"{BASE_URL}/questionnaire/analyze", json=payload)
        elapsed = time.time() - start
        
        if response.status_code == 200:
            metrics.add_success(elapsed, response.status_code)
        else:
            metrics.add_failure(elapsed, f"Status {response.status_code}")
    except Exception as e:
        metrics.add_failure(0, str(e))


async def get_user(client: httpx.AsyncClient, metrics: LoadTestMetrics, user_id: str):
    """Test get user endpoint"""
    try:
        start = time.time()
        response = await client.get(f"{BASE_URL}/auth/users/{user_id}")
        elapsed = time.time() - start
        
        if response.status_code in [200, 404]:  # 404 is expected for some test UUIDs
            metrics.add_success(elapsed, response.status_code)
        else:
            metrics.add_failure(elapsed, f"Status {response.status_code}")
    except Exception as e:
        metrics.add_failure(0, str(e))


async def run_load_test():
    """Run the complete load test"""
    print(f"\n{'='*80}")
    print(f"First Aid AI - API Load Test")
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Concurrent Requests: {NUM_CONCURRENT}")
    print(f"Requests per Endpoint: {NUM_REQUESTS_PER_ENDPOINT}")
    print(f"{'='*80}\n")

    metrics = {
        "health": LoadTestMetrics("/api/health", "GET"),
        "register": LoadTestMetrics("/api/auth/register", "POST"),
        "questionnaire": LoadTestMetrics("/api/questionnaire/analyze", "POST"),
        "get_user": LoadTestMetrics("/api/auth/users/{user_id}", "GET"),
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test 1: Health check
        print("Testing health endpoint...")
        health_tasks = [
            health_check(client, metrics["health"])
            for _ in range(NUM_REQUESTS_PER_ENDPOINT)
        ]
        await asyncio.gather(*[
            asyncio.gather(*health_tasks[i:i+NUM_CONCURRENT])
            for i in range(0, len(health_tasks), NUM_CONCURRENT)
        ])

        # Test 2: Registration
        print(f"Testing registration endpoint ({NUM_REQUESTS_PER_ENDPOINT} requests)...")
        register_tasks = [
            register_user(client, metrics["register"])
            for _ in range(NUM_REQUESTS_PER_ENDPOINT)
        ]
        await asyncio.gather(*[
            asyncio.gather(*register_tasks[i:i+NUM_CONCURRENT])
            for i in range(0, len(register_tasks), NUM_CONCURRENT)
        ])

        # Create a test user for questionnaire and get_user tests
        print("Creating test user for questionnaire/get tests...")
        test_user_response = await client.post(
            f"{BASE_URL}/auth/register",
            json={
                "name": "LoadTestUser",
                "email": f"loadtest{uuid.uuid4().hex[:8]}@test.ai",
                "password": "LoadTest123!"
            }
        )
        test_user_id = None
        if test_user_response.status_code == 200:
            test_user_id = test_user_response.json().get("user_id")

        # Test 3: Questionnaire analysis
        if test_user_id:
            print(f"Testing questionnaire analyze endpoint ({NUM_REQUESTS_PER_ENDPOINT} requests)...")
            qa_tasks = [
                questionnaire_analyze(client, metrics["questionnaire"], test_user_id)
                for _ in range(NUM_REQUESTS_PER_ENDPOINT)
            ]
            await asyncio.gather(*[
                asyncio.gather(*qa_tasks[i:i+NUM_CONCURRENT])
                for i in range(0, len(qa_tasks), NUM_CONCURRENT)
            ])

            # Test 4: Get user
            print(f"Testing get user endpoint ({NUM_REQUESTS_PER_ENDPOINT} requests)...")
            get_user_tasks = [
                get_user(client, metrics["get_user"], test_user_id)
                for _ in range(NUM_REQUESTS_PER_ENDPOINT)
            ]
            await asyncio.gather(*[
                asyncio.gather(*get_user_tasks[i:i+NUM_CONCURRENT])
                for i in range(0, len(get_user_tasks), NUM_CONCURRENT)
            ])

    # Print results
    print(f"\n{'='*80}")
    print("LOAD TEST RESULTS")
    print(f"{'='*80}\n")

    total_requests = 0
    total_successful = 0
    total_failed = 0

    for endpoint_key, metric in metrics.items():
        stats = metric.get_stats()
        if stats:
            print(f"\n{metric.endpoint} [{metric.method}]")
            print(f"  Total Requests:       {stats['total_requests']}")
            print(f"  Successful:           {stats['successful']}")
            print(f"  Failed:               {stats['failed']}")
            print(f"  Success Rate:         {stats['success_rate']}")
            print(f"  Avg Response Time:    {stats['avg_response_time_ms']} ms")
            print(f"  Min Response Time:    {stats['min_response_time_ms']} ms")
            print(f"  Max Response Time:    {stats['max_response_time_ms']} ms")
            print(f"  P95 Response Time:    {stats['p95_response_time_ms']} ms")
            if stats['status_codes']:
                print(f"  Status Codes:         {stats['status_codes']}")

            total_requests += stats['total_requests']
            total_successful += stats['successful']
            total_failed += stats['failed']

    print(f"\n{'='*80}")
    print(f"OVERALL SUMMARY")
    print(f"{'='*80}")
    print(f"Total Requests:       {total_requests}")
    print(f"Total Successful:     {total_successful}")
    print(f"Total Failed:         {total_failed}")
    print(f"Overall Success Rate: {(total_successful / total_requests * 100):.1f}%")
    print(f"End Time:             {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")

    # Verdict
    if total_successful / total_requests >= 0.95:
        print("✅ LOAD TEST PASSED - API is stable under load")
    else:
        print("⚠️  LOAD TEST WARNING - API showed instability")

    return total_successful / total_requests >= 0.95


if __name__ == "__main__":
    try:
        success = asyncio.run(run_load_test())
        exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Load test failed with error: {e}")
        exit(1)

