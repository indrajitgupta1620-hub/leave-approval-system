import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent
INDEX_HTML = PROJECT_ROOT / "index.html"
if not INDEX_HTML.exists():
    INDEX_HTML = BASE_DIR / "index.html"

# Default URL: local index.html with fallback support
LOCAL_URL = f"file:///{str(INDEX_HTML).replace('\\', '/')}"
APP_URL = os.environ.get("APP_URL", LOCAL_URL)
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:3000")

# Driver Settings
BROWSER = os.environ.get("BROWSER", "chrome")
HEADLESS = os.environ.get("HEADLESS", "false").lower() == "true"
IMPLICIT_WAIT = 5
EXPLICIT_WAIT = 10
FLUENT_POLL = 0.5

# Test Users
DEFAULT_EMPLOYEE = "Rahul Sharma"
DEFAULT_MANAGER = "ManagerJohn"


def get_driver():
    """Builds and returns configured Chrome WebDriver with offline driver discovery."""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service

    chrome_options = Options()
    if HEADLESS:
        chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    # Search local drivers folder
    candidate_drivers = [
        PROJECT_ROOT / "drivers" / "chromedriver.exe",
        BASE_DIR / "drivers" / "chromedriver.exe",
    ]
    for d in candidate_drivers:
        if d.exists():
            return webdriver.Chrome(service=Service(str(d)), options=chrome_options)

    # Fallback to WDM
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    except Exception:
        return webdriver.Chrome(options=chrome_options)
