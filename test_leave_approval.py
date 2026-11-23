import os
import sys
import time
import unittest
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

try:
    from webdriver_manager.chrome import ChromeDriverManager
    USE_WDM = True
except ImportError:
    USE_WDM = False

TARGET_URL = os.environ.get(
    "APP_URL",
    "https://alfiyazareen.github.io/leave-approval-system/"
)

class LeaveApprovalSystemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n=======================================================")
        print("  STARTING SELENIUM TEST SUITE: LEAVE APPROVAL SYSTEM  ")
        print(f"  Target URL: {TARGET_URL}")
        print("=======================================================\n")

        options = webdriver.ChromeOptions()
        if os.environ.get("HEADLESS", "false").lower() == "true":
            options.add_argument("--headless=new")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        local_driver = Path(__file__).resolve().parent / "drivers" / "chromedriver.exe"
        if local_driver.exists():
            cls.driver = webdriver.Chrome(service=Service(str(local_driver)), options=options)
        elif USE_WDM:
            cls.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        else:
            cls.driver = webdriver.Chrome(options=options)

        cls.wait = WebDriverWait(cls.driver, 10)
        cls.screenshots_dir = os.path.join(os.path.dirname(__file__), "screenshots")
        os.makedirs(cls.screenshots_dir, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        time.sleep(1)
        cls.driver.quit()
        print("\n=======================================================")
        print("  ALL TESTS COMPLETED SUCCESSFULLY                     ")
        print(f"  Screenshots saved in: {cls.screenshots_dir}")
        print("=======================================================\n")

    def setUp(self):
        self.driver.get(TARGET_URL)
        try:
            self.driver.execute_script("localStorage.clear();")
            self.driver.refresh()
        except Exception:
            pass
        time.sleep(1)

    def take_screenshot(self, name):
        filepath = os.path.join(self.screenshots_dir, f"{name}.png")
        self.driver.save_screenshot(filepath)
        print(f"  Screenshot saved: {name}.png")

    def login_user(self, username, role="employee"):
        user_input = self.wait.until(EC.visibility_of_element_located((By.ID, "username")))
        user_input.clear()
        user_input.send_keys(username)
        time.sleep(0.5)

        role_select = Select(self.driver.find_element(By.ID, "role"))
        role_select.select_by_value(role)
        time.sleep(0.5)

        login_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]")
        login_btn.click()
        time.sleep(1)

    def submit_leave(self, start, end, reason):
        start_date = self.wait.until(EC.visibility_of_element_located((By.ID, "startDate")))
        end_date = self.driver.find_element(By.ID, "endDate")
        reason_input = self.driver.find_element(By.ID, "reason")

        self.driver.execute_script("arguments[0].value = arguments[1];", start_date, start)
        self.driver.execute_script("arguments[0].value = arguments[1];", end_date, end)
        reason_input.clear()
        reason_input.send_keys(reason)
        time.sleep(1)

        self.driver.find_element(By.XPATH, "//button[contains(text(), 'Apply Leave')]").click()
        alert = self.wait.until(EC.alert_is_present())
        alert_msg = alert.text
        time.sleep(1.5)
        alert.accept()
        time.sleep(1)
        return alert_msg

    def test_01_verify_page_title(self):
        print("\n[RUNNING] TC01: Verify Page Title")
        self.assertIn("Leave Approval System", self.driver.title)
        login_box = self.driver.find_element(By.ID, "loginBox")
        self.assertTrue(login_box.is_displayed())
        print("  [PASS] TC01: Page title and login container verified")

    def test_02_login_empty_username_validation(self):
        print("\n[RUNNING] TC02: Validate Empty Username")
        time.sleep(1)
        login_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]")
        login_btn.click()

        alert = self.wait.until(EC.alert_is_present())
        alert_text = alert.text
        self.assertIn("Enter username", alert_text)
        time.sleep(2)
        alert.accept()
        time.sleep(1)
        print("  [PASS] TC02: Alert caught with message: " + alert_text)

    def test_03_employee_apply_leave_success(self):
        print("\n[RUNNING] TC03: Employee Apply Leave")
        self.login_user("Alfiya", "employee")

        employee_box = self.wait.until(EC.visibility_of_element_located((By.ID, "employeeBox")))
        self.assertTrue(employee_box.is_displayed())

        alert_msg = self.submit_leave("2026-12-01", "2026-12-05", "Medical leave for family emergency")
        self.assertIn("Leave applied!", alert_msg)

        pending_box = self.driver.find_element(By.ID, "empPending")
        self.assertIn("Medical leave for family emergency", pending_box.text)

        self.take_screenshot("01_employee_pending_leave")
        time.sleep(2)
        print("  [PASS] TC03: Leave applied and displayed under Pending list")

    def test_04_manager_view_and_approve_leave(self):
        print("\n[RUNNING] TC04: Two Employees Apply and Manager Views Both Applications and Approves")

        self.login_user("Alfiya", "employee")
        self.submit_leave("2026-12-01", "2026-12-05", "Medical leave for family emergency")
        self.driver.find_element(By.CSS_SELECTOR, "#employeeBox .top-back").click()
        time.sleep(1)

        self.login_user("StudentA", "employee")
        self.submit_leave("2026-12-10", "2026-12-12", "Attending Project Workshop")
        self.driver.find_element(By.CSS_SELECTOR, "#employeeBox .top-back").click()
        time.sleep(1)

        self.login_user("ManagerJane", "manager")

        manager_box = self.wait.until(EC.visibility_of_element_located((By.ID, "managerBox")))
        self.assertTrue(manager_box.is_displayed())

        pending_box = self.wait.until(EC.visibility_of_element_located((By.ID, "pendingLeaves")))
        self.assertIn("Alfiya", pending_box.text)
        self.assertIn("Medical leave for family emergency", pending_box.text)
        self.assertIn("StudentA", pending_box.text)
        self.assertIn("Attending Project Workshop", pending_box.text)
        print("  [INFO] Verified both employee applications are visible in Manager Dashboard")
        time.sleep(3)

        target_approve_xpath = "//div[@id='pendingLeaves']//div[contains(@class, 'box') and contains(., 'Attending Project Workshop')]//button[contains(@class, 'btn-approve')]"
        try:
            approve_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, target_approve_xpath)))
        except Exception:
            approve_btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#pendingLeaves .btn-approve")))
        approve_btn.click()
        time.sleep(3)

        approved_box = self.wait.until(EC.visibility_of_element_located((By.ID, "approvedLeaves")))
        self.assertIn("Attending Project Workshop", approved_box.text)

        updated_pending_box = self.driver.find_element(By.ID, "pendingLeaves")
        self.assertIn("Medical leave for family emergency", updated_pending_box.text)
        self.assertNotIn("Attending Project Workshop", updated_pending_box.text)

        self.take_screenshot("02_manager_approved_leave")
        time.sleep(2)
        print("  [PASS] TC04: Both employee applications displayed to Manager and approved successfully")


if __name__ == "__main__":
    unittest.main(verbosity=2)
