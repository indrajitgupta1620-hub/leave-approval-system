import os
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By

STEP_DELAY = float(os.environ.get("STEP_DELAY", "1.5"))


class BasePage:
    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def pause(self, seconds=STEP_DELAY):
        if seconds > 0:
            time.sleep(seconds)

    def find(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    def find_visible(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def click(self, locator):
        element = self.wait.until(EC.element_to_be_clickable(locator))
        element.click()
        self.pause(STEP_DELAY)

    def type_text(self, locator, text):
        element = self.find_visible(locator)
        element.clear()
        element.send_keys(text)
        self.pause(0.5)

    def get_text(self, locator):
        return self.find(locator).text

    def is_visible(self, locator):
        try:
            return self.find_visible(locator).is_displayed()
        except TimeoutException:
            return False

    def handle_alert(self, accept=True):
        alert = self.wait.until(EC.alert_is_present())
        alert_text = alert.text
        time.sleep(1.5)
        if accept:
            alert.accept()
        else:
            alert.dismiss()
        time.sleep(1)
        return alert_text
