"""Common operations for the functional Page Objects."""

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BasePage:
    """Minimal base with navigation and explicit waits."""

    def __init__(self, driver, base_url: str, timeout: int = 10):
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.wait = WebDriverWait(driver, timeout)

    def open(self, path: str = "/") -> None:
        """Navigates to an absolute path or one relative to the app."""
        is_absolute_url = path.startswith(("http://", "https://"))
        url = path if is_absolute_url else f"{self.base_url}/{path.lstrip('/')}"
        self.driver.get(url)

    def wait_for(self, condition):
        """Waits for a Selenium condition and returns its result."""
        return self.wait.until(condition)

    def wait_until_visible(self, locator):
        """Waits for and returns a visible element."""
        return self.wait_for(EC.visibility_of_element_located(locator))

    def wait_until_clickable(self, locator):
        """Waits for and returns a clickable element."""
        return self.wait_for(EC.element_to_be_clickable(locator))
