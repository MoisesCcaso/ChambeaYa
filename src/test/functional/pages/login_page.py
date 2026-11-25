"""Page Object for the login flows."""

from urllib.parse import urlparse

from selenium.webdriver.common.by import By

from .base_page import BasePage


class LoginPage(BasePage):
    """Actions and queries for the login view."""

    def open_login(self) -> None:
        """Opens the login form."""
        self.open("/ingresar")

    def login(self, email: str, password: str) -> None:
        """Fills in the credentials and submits the form."""
        self.wait_until_visible((By.NAME, "email")).send_keys(email)
        self.wait_until_visible((By.NAME, "password")).send_keys(password)
        self.wait_until_clickable(
            (By.CSS_SELECTOR, "#auth-form button[type='submit']")
        ).click()

    def wait_for_path(self, path: str) -> None:
        """Waits until the browser reaches the given path."""
        self.wait_for(lambda _driver: self.current_path == path)

    def logout(self) -> None:
        """Logs out from the dashboard and waits for the login form."""
        self.wait_until_clickable((By.ID, "logout-button")).click()
        self.wait_for_path("/ingresar")

    @property
    def current_path(self) -> str:
        """Current browser path, without domain or query string."""
        return urlparse(self.driver.current_url).path

    @property
    def role_label(self) -> str:
        """Waits for the role to load and returns its dashboard label."""
        locator = (By.ID, "sidebar-role")
        self.wait_for(
            lambda browser: (
                label
                if (label := browser.find_element(*locator).text.strip())
                and label != "Cuenta"
                else False
            )
        )
        return self.driver.find_element(*locator).text.strip()

    def company_menu_is_visible(self) -> bool:
        """Waits for the job postings option in the company menu."""
        return self.wait_until_visible(
            (By.CSS_SELECTOR, '[data-view="convocatorias"]')
        ).is_displayed()

    @property
    def error_message(self) -> str:
        """Waits for and returns the form error message."""
        return self.wait_until_visible((By.ID, "form-feedback")).text.strip()
