from selenium.webdriver.common.by import By
from .base_page import BasePage


class ManagerPage(BasePage):
    MANAGER_BOX = (By.ID, "managerBox")
    PENDING_CONTAINER = (By.ID, "pendingLeaves")
    APPROVED_CONTAINER = (By.ID, "approvedLeaves")
    REJECTED_CONTAINER = (By.ID, "rejectedLeaves")
    APPROVE_BUTTON = (By.CSS_SELECTOR, "#pendingLeaves .btn-approve")
    REJECT_BUTTON = (By.CSS_SELECTOR, "#pendingLeaves .btn-reject")
    BACK_BUTTON = (By.ID, "mgrBackBtn")

    def __init__(self, driver):
        super().__init__(driver)

    def is_loaded(self):
        return self.is_visible(self.MANAGER_BOX)

    def get_pending_leaves_text(self):
        return self.get_text(self.PENDING_CONTAINER)

    def get_approved_leaves_text(self):
        return self.get_text(self.APPROVED_CONTAINER)

    def get_rejected_leaves_text(self):
        return self.get_text(self.REJECTED_CONTAINER)

    def approve_first_pending_leave(self):
        self.click(self.APPROVE_BUTTON)

    def reject_first_pending_leave(self):
        self.click(self.REJECT_BUTTON)

    def click_back_to_login(self):
        self.click(self.BACK_BUTTON)
