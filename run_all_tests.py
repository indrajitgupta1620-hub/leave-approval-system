import sys
import time
import subprocess
import unittest
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_DIR))

from test_selenium_leave_approval import TestLeaveApprovalSelenium
from test_api_leave_approval import TestLeaveApprovalAPI
from automation_framework.tests.test_leave_approval_pom import TestLeaveApprovalPOM


def is_api_server_running(url="http://localhost:3000/api/health"):
    import requests
    try:
        resp = requests.get(url, timeout=1)
        return resp.status_code == 200
    except Exception:
        return False


def run_full_suite():
    print("===========================================================================")
    print("       LEAVE APPROVAL SYSTEM: AUTOMATED TEST SUITE RUNNER                  ")
    print("===========================================================================")

    server_process = None
    if not is_api_server_running():
        server_script = PROJECT_DIR / "server.js"
        if not server_script.exists():
            server_script = PROJECT_DIR / "leave-approval-system-main" / "server.js"
        print("  Node API server not detected. Starting server.js...")
        server_process = subprocess.Popen(
            ["node", str(server_script)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(2)
        print("  API server started on http://localhost:3000")

    try:
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()

        suite.addTests(loader.loadTestsFromTestCase(TestLeaveApprovalSelenium))
        suite.addTests(loader.loadTestsFromTestCase(TestLeaveApprovalPOM))
        suite.addTests(loader.loadTestsFromTestCase(TestLeaveApprovalAPI))

        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)

        print("\n===========================================================================")
        print(f" TOTAL TESTS RUN : {result.testsRun}")
        print(f" SUCCESSFUL      : {result.testsRun - len(result.failures) - len(result.errors)}")
        print(f" FAILURES        : {len(result.failures)}")
        print(f" ERRORS          : {len(result.errors)}")
        print("===========================================================================")

        return len(result.failures) == 0 and len(result.errors) == 0

    finally:
        if server_process:
            print("  Stopping background API server...")
            server_process.terminate()
            server_process.wait()
            print("  API server stopped")


if __name__ == "__main__":
    success = run_full_suite()
    sys.exit(0 if success else 1)
