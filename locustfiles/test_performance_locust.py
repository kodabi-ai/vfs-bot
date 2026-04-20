"""
VFS Global Performance Testing with Locust
Phase 5 Innovation - RAG MCP Improved
Based on RAG MCP best practices for load testing
"""

from locust import HttpUser, task, between, events
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VFSGlobalUser(HttpUser):
    """
    VFS Global Load Test User
    - Simulates real user behavior
    - Tests login flow, OTP verification, dashboard access
    - Based on RAG MCP best practices for performance testing
    """
    
    # Simulate realistic user wait times (1-3 seconds between tasks)
    wait_time = between(1, 3)
    
    # Test credentials (from Phase 4 Quality)
    test_credentials = {
        "email": "mustafa.eke@live.com",
        "password": "Vfsglobal!5561!",
        "phone": "5468224662"
    }
    
    def on_start(self):
        """
        Setup before each user starts
        RAG MCP: Initialize session and connection pool
        """
        logger.info("🚀 Starting performance test session")
        # Establish connection pool
        self.session = self.client.session
        
    @task(5)
    def login_flow(self):
        """
        Test Login Flow with RAG MCP Best Practices
        - 50% weight in load test (most critical path)
        - Tests cookie collection + OTP trigger
        """
        payload = {
            "email": self.test_credentials["email"],
            "password": self.test_credentials["password"],
            "phone": self.test_credentials["phone"]
        }
        
        response = self.client.post(
            "/tur/tr/fra/login",
            json=payload,
            headers={"Content-Type": "application/json"},
            name="/login"
        )
        
        # RAG MCP: Track response time + status
        if response.status_code == 200:
            logger.info(f"✅ Login successful - {response.elapsed.total_seconds():.2f}s")
        elif response.status_code == 403:
            logger.warning(f"⚠️ Login failed (403) - {response.elapsed.total_seconds():.2f}s")
        else:
            logger.error(f"❌ Login error ({response.status_code})")
            
    @task(3)
    def verify_otp(self):
        """
        Test OTP Verification
        - 30% weight in load test
        - Tests OTP validation flow
        """
        response = self.client.post(
            "/api/otp/verify",
            json={"otp": "123456", "email": self.test_credentials["email"]},
            headers={"Content-Type": "application/json"},
            name="/otp/verify"
        )
        
        if response.status_code == 200:
            logger.info(f"✅ OTP verified - {response.elapsed.total_seconds():.2f}s")
        else:
            logger.error(f"❌ OTP verification failed")
            
    @task(2)
    def check_dashboard(self):
        """
        Test Dashboard Access
        - 20% weight in load test
        - Tests API endpoint availability
        """
        response = self.client.get(
            "/api/dashboard/status",
            headers={"Content-Type": "application/json"},
            name="/dashboard/status"
        )
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Dashboard accessible - {data.get('status', 'unknown')}")
        else:
            logger.error(f"❌ Dashboard check failed")


class VFSGlobalLoadUser(HttpUser):
    """
    Heavy Load User - Stress Testing
    - Simulates peak traffic conditions
    - Tests system under high load
    """
    
    wait_time = between(0.5, 1.5)  # Faster than regular users
    
    @task(3)
    def stress_login(self):
        """
        Stress Test - Login under high load
        """
        for _ in range(3):
            payload = {
                "email": f"test_{_}@example.com",
                "password": "TestPass123!"
            }
            
            response = self.client.post(
                "/tur/tr/fra/login",
                json=payload,
                headers={"Content-Type": "application/json"},
                name="/login/stress"
            )
            
    @task(2)
    def stress_api(self):
        """
        Stress Test - API endpoint under load
        """
        response = self.client.get(
            "/api/dashboard/status",
            name="/api/status/stress"
        )
        

# RAG MCP: Performance Test Event Hooks
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    logger.info("📊 Performance Testing Started - RAG MCP Enhanced")
    logger.info(f"Target Users: {environment.parsed_options.users}")
    logger.info(f"Spawn Rate: {environment.parsed_options.spawn_rate}")
    logger.info(f"Run Time: {environment.parsed_options.run_time}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """
    Generate Performance Report on Test Completion
    RAG MCP: Track metrics + generate insights
    """
    logger.info("📈 Performance Testing Complete")
    
    # RAG MCP: Extract metrics
    stats = environment.stats
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_requests": stats.num_requests,
        "total_failures": stats.num_failures,
        "avg_response_time": stats.avg_response_time,
        "max_response_time": stats.max_response_time,
        "min_response_time": stats.min_response_time,
        "requests_per_second": stats.total_rps,
        "failure_rate": (stats.num_failures / stats.num_requests * 100) if stats.num_requests > 0 else 0,
        "phase5_innovation": "RAG MCP Enhanced Performance Testing"
    }
    
    # Save report
    with open("locust_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"✅ Performance report saved to locust_report.json")
    logger.info(f"Total Requests: {report['total_requests']}")
    logger.info(f"Avg Response Time: {report['avg_response_time']:.2f}ms")
    logger.info(f"Failure Rate: {report['failure_rate']:.2f}%")
