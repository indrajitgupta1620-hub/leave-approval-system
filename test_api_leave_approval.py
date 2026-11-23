import os
import sys
import time
import json
import unittest
import subprocess
from pathlib import Path
import requests

BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:3000")


class TestLeaveApprovalAPI(unittest.TestCase):
    server_process = None

    @classmethod
    def setUpClass(cls):
        print("\n===========================================================================")
        print(" [SETUP] REST API TEST SUITE: LEAVE APPROVAL SYSTEM")
        print(f" Target Base URL: {BASE_URL}")
        print("===========================================================================")

        is_running = False
        try:
            resp = requests.get(f"{BASE_URL}/api/health", timeout=2)
            if resp.status_code == 200:
                is_running = True
                print("  Existing API server detected and responding at " + BASE_URL)
        except Exception:
            is_running = False

        if not is_running and "localhost" in BASE_URL:
            project_dir = Path(__file__).resolve().parent
            server_script = project_dir / "server.js"
            if not server_script.exists():
                server_script = project_dir.parent / "server.js"
            if not server_script.exists():
                server_script = project_dir / "leave-approval-system-main" / "server.js"

            if server_script.exists():
                print("  Auto-starting local API server (node server.js)...")
                cls.server_process = subprocess.Popen(
                    ["node", str(server_script)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                time.sleep(1.5)
                for _ in range(10):
                    try:
                        r = requests.get(f"{BASE_URL}/api/health", timeout=1)
                        if r.status_code == 200:
                            print("  Local API server started and verified at " + BASE_URL)
                            break
                    except Exception:
                        time.sleep(0.5)

    @classmethod
    def tearDownClass(cls):
        if cls.server_process:
            print("\n  Stopping auto-started API server...")
            cls.server_process.terminate()
            try:
                cls.server_process.wait(timeout=3)
            except Exception:
                cls.server_process.kill()
            print("  API server stopped cleanly")

    def test_01_api_health_check(self):
        print("\n[RUNNING] TC_API_01: Health Check (GET /api/health)")
        endpoint = f"{BASE_URL}/api/health"

        start_time = time.time()
        response = requests.get(endpoint, timeout=5)
        duration_ms = (time.time() - start_time) * 1000

        print(f"  HTTP Status Code: {response.status_code}")
        print(f"  Response Time   : {duration_ms:.2f} ms")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(duration_ms < 1000)

        data = response.json()
        self.assertEqual(data.get("status"), "UP")
        self.assertIn("timestamp", data)
        print("  [PASS] TC_API_01: Health Check verified")

    def test_02_user_login_success_and_validation(self):
        print("\n[RUNNING] TC_API_02: User Login (POST /api/login)")
        endpoint = f"{BASE_URL}/api/login"

        payload = {"username": "Alfiya", "role": "employee"}
        resp = requests.post(endpoint, json=payload, timeout=5)
        self.assertEqual(resp.status_code, 200)

        json_data = resp.json()
        self.assertEqual(json_data.get("message"), "Login successful")
        self.assertEqual(json_data.get("user", {}).get("username"), "Alfiya")
        self.assertEqual(json_data.get("user", {}).get("role"), "employee")

        bad_payload = {"role": "employee"}
        bad_resp = requests.post(endpoint, json=bad_payload, timeout=5)
        self.assertEqual(bad_resp.status_code, 400)
        self.assertIn("error", bad_resp.json())
        print("  [PASS] TC_API_02: User login positive and negative scenarios verified")

    def test_03_request_chaining_apply_and_approve_leave(self):
        print("\n[RUNNING] TC_API_03: Request Chaining (Apply Leave -> Extract ID -> Approve)")

        create_payload = {
            "user": "Rahul Verma",
            "reason": "Attending International Testing Conference",
            "start": "2026-12-05",
            "end": "2026-12-08"
        }
        create_resp = requests.post(f"{BASE_URL}/api/leaves", json=create_payload, timeout=5)
        self.assertEqual(create_resp.status_code, 201)

        created_data = create_resp.json()
        chained_leave_id = created_data["leave"]["id"]
        print(f"  [CHAINING] Extracted Leave ID: '{chained_leave_id}' | Status: '{created_data['leave']['status']}'")
        self.assertEqual(created_data["leave"]["status"], "Pending")

        approve_payload = {"status": "Approved"}
        approve_resp = requests.put(f"{BASE_URL}/api/leaves/{chained_leave_id}", json=approve_payload, timeout=5)
        self.assertEqual(approve_resp.status_code, 200)
        approve_data = approve_resp.json()
        self.assertEqual(approve_data["leave"]["status"], "Approved")

        get_resp = requests.get(f"{BASE_URL}/api/leaves", timeout=5)
        self.assertEqual(get_resp.status_code, 200)

        all_leaves = get_resp.json().get("leaves", [])
        matched_leave = next((l for l in all_leaves if l["id"] == str(chained_leave_id)), None)
        self.assertIsNotNone(matched_leave)
        self.assertEqual(matched_leave["status"], "Approved")
        print("  [PASS] TC_API_03: Request Chaining executed and verified")

    def test_04_manager_reject_leave(self):
        print("\n[RUNNING] TC_API_04: Manager Reject Leave (PUT /api/leaves/{id})")

        create_resp = requests.post(f"{BASE_URL}/api/leaves", json={
            "user": "Sneha Patel",
            "reason": "Personal Leave",
            "start": "2026-12-20",
            "end": "2026-12-22"
        }, timeout=5)
        leave_id = create_resp.json()["leave"]["id"]

        reject_resp = requests.put(f"{BASE_URL}/api/leaves/{leave_id}", json={"status": "Rejected"}, timeout=5)
        self.assertEqual(reject_resp.status_code, 200)
        self.assertEqual(reject_resp.json()["leave"]["status"], "Rejected")
        print("  [PASS] TC_API_04: Leave rejection verified")

    def test_05_negative_scenarios(self):
        print("\n[RUNNING] TC_API_05: Negative and Validation Scenarios")

        invalid_dates_payload = {
            "user": "Alfiya",
            "reason": "Vacation",
            "start": "2026-12-10",
            "end": "2026-12-05"
        }
        resp1 = requests.post(f"{BASE_URL}/api/leaves", json=invalid_dates_payload, timeout=5)
        self.assertEqual(resp1.status_code, 400)

        missing_payload = {"user": "Alfiya"}
        resp2 = requests.post(f"{BASE_URL}/api/leaves", json=missing_payload, timeout=5)
        self.assertEqual(resp2.status_code, 400)

        resp3 = requests.put(f"{BASE_URL}/api/leaves/1", json={"status": "Maybe"}, timeout=5)
        self.assertEqual(resp3.status_code, 400)

        resp4 = requests.put(f"{BASE_URL}/api/leaves/999999", json={"status": "Approved"}, timeout=5)
        self.assertEqual(resp4.status_code, 404)
        print("  [PASS] TC_API_05: All negative and boundary scenarios handled correctly")

    def test_06_delete_leave_endpoint(self):
        print("\n[RUNNING] TC_API_06: Delete Leave (DELETE /api/leaves/{id})")

        temp_resp = requests.post(f"{BASE_URL}/api/leaves", json={
            "user": "TempUser",
            "reason": "To be deleted",
            "start": "2026-12-10",
            "end": "2026-12-11"
        }, timeout=5)
        temp_id = temp_resp.json()["leave"]["id"]

        del_resp = requests.delete(f"{BASE_URL}/api/leaves/{temp_id}", timeout=5)
        self.assertEqual(del_resp.status_code, 200)

        del_again_resp = requests.delete(f"{BASE_URL}/api/leaves/{temp_id}", timeout=5)
        self.assertEqual(del_again_resp.status_code, 404)
        print("  [PASS] TC_API_06: Delete endpoint verified")


if __name__ == "__main__":
    unittest.main(verbosity=2)
