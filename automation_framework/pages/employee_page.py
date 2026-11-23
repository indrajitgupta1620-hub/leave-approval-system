from selenium.webdriver.common.by import By
from .base_page import BasePage


class EmployeePage(BasePage):
    EMPLOYEE_BOX = (By.ID, "employeeBox")
    START_DATE = (By.ID, "startDate")
    END_DATE = (By.ID, "endDate")
    REASON = (By.ID, "reason")
    APPLY_BUTTON = (By.ID, "applyLeaveBtn")
    PENDING_CONTAINER = (By.ID, "empPending")
    APPROVED_CONTAINER = (By.ID, "empApproved")
    REJECTED_CONTAINER = (By.ID, "empRejected")
    BACK_BUTTON = (By.ID, "empBackBtn")

    def __init__(self, driver):
        super().__init__(driver)

    def is_loaded(self):
        return self.is_visible(self.EMPLOYEE_BOX)

    def apply_leave(self, start_date, end_date, reason):
        s_elem = self.find(self.START_DATE)
        e_elem = self.find(self.END_DATE)
        self.driver.execute_script("arguments[0].value = arguments[1];", s_elem, start_date)
        self.driver.execute_script("arguments[0].value = arguments[1];", e_elem, end_date)
        self.type_text(self.REASON, reason)
        self.click(self.APPLY_BUTTON)
        alert_msg = self.handle_alert(accept=True)
        return alert_msg

    def get_pending_text(self):
        return self.get_text(self.PENDING_CONTAINER)

    def get_approved_text(self):
        return self.get_text(self.APPROVED_CONTAINER)

    def click_back_to_login(self):
        self.click(self.BACK_BUTTON)
