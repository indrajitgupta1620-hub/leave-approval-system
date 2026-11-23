import unittest
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from ..config import config
from ..pages.login_page import LoginPage
from ..pages.employee_page import EmployeePage
from ..pages.manager_page import ManagerPage


class TestLeaveApprovalPOM(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = config.get_driver()
        cls.driver.implicitly_wait(config.IMPLICIT_WAIT)

    @classmethod
    def tearDownClass(cls):
        if cls.driver:
            cls.driver.quit()

    def setUp(self):
        self.driver.get(config.APP_URL)
        try:
            self.driver.execute_script("localStorage.clear();")
            self.driver.refresh()
        except Exception:
            pass
        self.login_page = LoginPage(self.driver)
        self.employee_page = EmployeePage(self.driver)
        self.manager_page = ManagerPage(self.driver)

    def test_pom_employee_demands_leave_and_manager_approves(self):
        emp1 = "Kavita Rao"
        reason1 = "Attending Technical Leadership Conference"
        self.assertTrue(self.login_page.is_loaded())
        self.login_page.login_as_employee(emp1)
        self.assertTrue(self.employee_page.is_loaded())
        self.employee_page.apply_leave("2026-12-05", "2026-12-09", reason1)
        self.employee_page.click_back_to_login()

        emp2 = "Rahul Sharma"
        reason2 = "Annual Medical Checkup"
        self.assertTrue(self.login_page.is_loaded())
        self.login_page.login_as_employee(emp2)
        self.assertTrue(self.employee_page.is_loaded())
        self.employee_page.apply_leave("2026-12-15", "2026-12-18", reason2)
        self.employee_page.click_back_to_login()

        self.assertTrue(self.login_page.is_loaded())
        self.login_page.login_as_manager("ManagerJohn")
        self.assertTrue(self.manager_page.is_loaded())

        mgr_pending = self.manager_page.get_pending_leaves_text()
        self.assertIn(emp1, mgr_pending)
        self.assertIn(reason1, mgr_pending)
        self.assertIn(emp2, mgr_pending)
        self.assertIn(reason2, mgr_pending)

        self.manager_page.approve_first_pending_leave()
        time.sleep(2)

        approved_text = self.manager_page.get_approved_leaves_text()
        self.assertIn(reason1, approved_text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
