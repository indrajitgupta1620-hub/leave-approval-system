from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from .base_page import BasePage


class LoginPage(BasePage):
    LOGIN_BOX = (By.ID, "loginBox")
    USERNAME_INPUT = (By.ID, "username")
    USERNAME_BY_NAME = (By.NAME, "username")
    ROLE_SELECT = (By.ID, "role")
    LOGIN_BUTTON = (By.ID, "loginBtn")
    LOGIN_BUTTON_XPATH = (By.XPATH, "//button[contains(text(), 'Login')]")
    PAGE_HEADING = (By.TAG_NAME, "h1")
    DOC_LINK = (By.LINK_TEXT, "System Documentation")

    def __init__(self, driver):
        super().__init__(driver)

    def is_loaded(self):
        return self.is_visible(self.LOGIN_BOX)

    def enter_username(self, username):
        self.type_text(self.USERNAME_INPUT, username)

    def select_role(self, role):
        select_elem = Select(self.find(self.ROLE_SELECT))
        select_elem.select_by_value(role.lower())

    def click_login(self):
        self.click(self.LOGIN_BUTTON)

    def login_as_employee(self, username="Alfiya"):
        self.enter_username(username)
        self.select_role("employee")
        self.click_login()

    def login_as_manager(self, username="ManagerJane"):
        self.enter_username(username)
        self.select_role("manager")
        self.click_login()
