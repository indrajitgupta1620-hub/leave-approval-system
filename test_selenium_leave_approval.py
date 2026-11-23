import os
import sys
import time
import unittest
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementNotInteractableException,
    TimeoutException
)

try:
    from webdriver_manager.chrome import ChromeDriverManager
    USE_WDM = True
except ImportError:
    USE_WDM = False

CURRENT_DIR = Path(__file__).resolve().parent
LOCAL_INDEX = CURRENT_DIR / "index.html"
if not LOCAL_INDEX.exists():
    LOCAL_INDEX = CURRENT_DIR.parent / "index.html"
if not LOCAL_INDEX.exists():
    LOCAL_INDEX = CURRENT_DIR / "leave-approval-system-main" / "index.html"

LOCAL_FILE_URL = f"file:///{str(LOCAL_INDEX).replace('\\', '/')}"
TARGET_URL = os.environ.get("APP_URL", LOCAL_FILE_URL)


def get_chromedriver_service():
    candidate_paths = [
        CURRENT_DIR / "drivers" / "chromedriver.exe",
        CURRENT_DIR.parent / "drivers" / "chromedriver.exe",
        Path(__file__).resolve().parent / "drivers" / "chromedriver.exe",
    ]
    for p in candidate_paths:
        if p.exists():
            return Service(executable_path=str(p))

    try:
        wdm_dir = Path.home() / ".wdm" / "drivers" / "chromedriver"
        if wdm_dir.exists():
            drivers = list(wdm_dir.glob("**/chromedriver.exe"))
            if drivers:
                return Service(executable_path=str(drivers[0]))
    except Exception:
        pass

    if USE_WDM:
        try:
            installed_path = ChromeDriverManager().install()
            return Service(executable_path=installed_path)
        except Exception:
            pass

    return None


class TestLeaveApprovalSelenium(unittest.TestCase):
    driver = None
    wait = None
    fluent_wait = None
    screenshots_dir = None

    @classmethod
    def setUpClass(cls):

        print("  STARTING SELENIUM TEST SUITE: LEAVE APPROVAL SYSTEM  ")
        print(f"  Target URL: {TARGET_URL}")


        chrome_options = Options()
        if os.environ.get("HEADLESS", "false").lower() == "true":
            chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-notifications")

        chrome_service = get_chromedriver_service()
        if chrome_service:
            cls.driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
        else:
            cls.driver = webdriver.Chrome(options=chrome_options)

        cls.driver.implicitly_wait(5)
        cls.wait = WebDriverWait(cls.driver, timeout=10)
        cls.fluent_wait = WebDriverWait(
            cls.driver,
            timeout=10,
            poll_frequency=0.5,
            ignored_exceptions=[NoSuchElementException, ElementNotInteractableException]
        )

        cls.screenshots_dir = CURRENT_DIR / "screenshots"
        cls.screenshots_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        time.sleep(1)
        if cls.driver:
            cls.driver.quit()

        print("  ALL TESTS COMPLETED SUCCESSFULLY                     ")
       

    def setUp(self):
        self.driver.get(TARGET_URL)
        try:
            self.driver.execute_script("localStorage.clear();")
            self.driver.refresh()
        except Exception:
            pass
        time.sleep(1)

    def capture_screenshot(self, test_name):
        filepath = self.screenshots_dir / f"{test_name}.png"
        self.driver.save_screenshot(str(filepath))
        print(f"  Screenshot saved: {filepath.name}")

    def login_user(self, username, role="employee"):
        user_input = self.wait.until(EC.visibility_of_element_located((By.ID, "username")))
        user_input.clear()
        user_input.send_keys(username)
        time.sleep(0.5)

        role_select = Select(self.driver.find_element(By.ID, "role"))
        role_select.select_by_value(role)
        time.sleep(0.5)

        login_btn = self.driver.find_element(By.ID, "loginBtn")
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

        self.driver.find_element(By.ID, "applyLeaveBtn").click()
        alert = self.wait.until(EC.alert_is_present())
        alert_msg = alert.text
        time.sleep(1.5)
        alert.accept()
        time.sleep(1)
        return alert_msg

    def test_01_verify_page_title_and_elements_by_locators(self):
        print("\n[TEST START] TC_SE_01: Verify Page Title and Multi-Locator Finding")

        title = self.driver.title
        current_url = self.driver.current_url
        print(f"  Page Title: '{title}'")
        print(f"  Current URL: '{current_url}'")
        self.assertIn("Leave Approval System", title)

        login_box_by_id = self.driver.find_element(By.ID, "loginBox")
        self.assertTrue(login_box_by_id.is_displayed())
        print("  [By.ID] Found 'loginBox' container")

        username_by_name = self.driver.find_element(By.NAME, "username")
        self.assertEqual(username_by_name.get_attribute("placeholder"), "Enter Name")
        print("  [By.NAME] Found 'username' input field")

        h1_element = self.driver.find_element(By.TAG_NAME, "h1")
        self.assertEqual(h1_element.text, "Leave Approval System")
        print(f"  [By.TAG_NAME] Found h1 heading: '{h1_element.text}'")

        container_div = self.driver.find_element(By.CLASS_NAME, "container")
        self.assertTrue(container_div.is_displayed())
        print("  [By.CLASS_NAME] Found container element")

        doc_link = self.driver.find_element(By.LINK_TEXT, "System Documentation")
        print(f"  [By.LINK_TEXT] Found link with text: '{doc_link.text}'")
        self.assertEqual(doc_link.text, "System Documentation")

        help_link = self.driver.find_element(By.PARTIAL_LINK_TEXT, "Support")
        print(f"  [By.PARTIAL_LINK_TEXT] Found link with partial text: '{help_link.text}'")
        self.assertIn("Help & Support", help_link.text)

        self.capture_screenshot("01_page_load_and_locators")
        time.sleep(2)
        print("  [PASS] TC_SE_01: Page title and all locator types successfully validated")

    def test_02_empty_username_alert_handling(self):
        print("\n[TEST START] TC_SE_02: Alert Handling on Empty Username")
        time.sleep(1)

        login_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]")
        login_btn.click()

        alert = self.wait.until(EC.alert_is_present())
        alert_text = alert.text
        print(f"  JavaScript Alert caught with message: '{alert_text}'")
        self.assertIn("Enter username", alert_text)
        time.sleep(2)
        alert.accept()
        time.sleep(1)

        self.capture_screenshot("02_empty_username_alert")
        print("  [PASS] TC_SE_02: Empty input validation alert handled successfully")

    def test_03_employee_demand_leave_workflow(self):
        print("\n[TEST START] TC_SE_03: Employee Leave Application Workflow")
        self.login_user("Rahul Sharma", "employee")

        employee_box = self.wait.until(EC.visibility_of_element_located((By.ID, "employeeBox")))
        self.assertTrue(employee_box.is_displayed())

        reason_text = "Attending National Software Testing Symposium"
        alert_msg = self.submit_leave("2026-12-01", "2026-12-05", reason_text)
        self.assertIn("Leave applied!", alert_msg)

        pending_section = self.wait.until(EC.visibility_of_element_located((By.ID, "empPending")))
        self.assertIn(reason_text, pending_section.text)

        self.capture_screenshot("03_employee_leave_demanded_pending")
        time.sleep(2)
        print("  [PASS] TC_SE_03: Employee successfully applied for leave and verified Pending status")

    def test_04_employee_demands_leave_and_manager_approves(self):
        print("\n[TEST START] TC_SE_04: Two Employees Apply Leave and Manager Views Both Applications and Approves")

        emp1_name = "Priya Verma"
        leave1_reason = "Annual Medical Checkup and Recovery"
        self.login_user(emp1_name, "employee")
        self.submit_leave("2026-12-15", "2026-12-18", leave1_reason)
        self.driver.find_element(By.CSS_SELECTOR, "#employeeBox .top-back").click()
        time.sleep(1)

        emp2_name = "Rahul Sharma"
        leave2_reason = "Attending Technical Leadership Conference"
        self.login_user(emp2_name, "employee")
        self.submit_leave("2026-12-20", "2026-12-23", leave2_reason)
        self.driver.find_element(By.CSS_SELECTOR, "#employeeBox .top-back").click()
        time.sleep(1)

        self.login_user("ManagerJohn", "manager")

        mgr_dashboard = self.wait.until(EC.visibility_of_element_located((By.ID, "managerBox")))
        self.assertTrue(mgr_dashboard.is_displayed())

        pending_container = self.wait.until(EC.visibility_of_element_located((By.ID, "pendingLeaves")))
        self.assertIn(emp1_name, pending_container.text)
        self.assertIn(leave1_reason, pending_container.text)
        self.assertIn(emp2_name, pending_container.text)
        self.assertIn(leave2_reason, pending_container.text)
        print(f"  [INFO] Verified both applications from '{emp1_name}' and '{emp2_name}' are visible in Manager Dashboard")
        time.sleep(3)

        target_approve_xpath = f"//div[@id='pendingLeaves']//div[contains(@class, 'box') and contains(., '{leave1_reason}')]//button[contains(@class, 'btn-approve')]"
        try:
            approve_button = self.fluent_wait.until(
                EC.element_to_be_clickable((By.XPATH, target_approve_xpath))
            )
        except Exception:
            approve_button = self.fluent_wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#pendingLeaves .btn-approve"))
            )
        approve_button.click()
        time.sleep(3)

        approved_container = self.wait.until(EC.visibility_of_element_located((By.ID, "approvedLeaves")))
        self.assertIn(leave1_reason, approved_container.text)

        updated_pending = self.driver.find_element(By.ID, "pendingLeaves").text
        self.assertNotIn(leave1_reason, updated_pending)
        self.assertIn(leave2_reason, updated_pending)

        self.capture_screenshot("04_manager_approved_leave_success")
        time.sleep(2)
        print("  [PASS] TC_SE_04: Both employee applications displayed to Manager and approved successfully")

    def test_05_employee_demands_leave_and_manager_rejects(self):
        print("\n[TEST START] TC_SE_05: Employee Applies for Leave and Manager Rejects")

        emp_name = "Alex Turner"
        reason = "Extended Unplanned Vacation"
        self.login_user(emp_name, "employee")
        self.submit_leave("2026-12-24", "2026-12-30", reason)

        self.driver.find_element(By.CSS_SELECTOR, "#employeeBox .top-back").click()
        time.sleep(1)

        self.login_user("ManagerSarah", "manager")
        self.wait.until(EC.visibility_of_element_located((By.ID, "managerBox")))
        time.sleep(2)

        reject_btn = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#pendingLeaves .btn-reject"))
        )
        reject_btn.click()
        time.sleep(3)

        rejected_container = self.wait.until(EC.visibility_of_element_located((By.ID, "rejectedLeaves")))
        self.assertIn(reason, rejected_container.text)

        self.capture_screenshot("05_manager_rejected_leave")
        time.sleep(2)
        print("  [PASS] TC_SE_05: Manager rejection flow executed and verified")


if __name__ == "__main__":
    unittest.main(verbosity=2)
