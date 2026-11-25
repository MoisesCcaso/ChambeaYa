"""Page Object for account activation and password recovery."""

from urllib.parse import parse_qs, urlparse

from selenium.webdriver.common.by import By

from .base_page import BasePage

SUBMIT = (By.CSS_SELECTOR, "#auth-form button[type='submit']")
FEEDBACK = (By.ID, "form-feedback")


class RecoveryPage(BasePage):
    """Actions and queries for `/activar`, `/recuperar` and `/restablecer`."""

    # --- Activation ---------------------------------------------------
    def open_activation(self, token: str) -> None:
        """Opens the activation link with the given token."""
        self.open(f"/activar?token={token}")

    def submit_activation(self) -> None:
        """Confirms the account activation."""
        self.wait_until_clickable(SUBMIT).click()

    # --- Recovery -----------------------------------------------------
    def open_recovery(self) -> None:
        """Opens the recovery request form."""
        self.open("/recuperar")

    def request_recovery(self, email: str) -> None:
        """Requests recovery access for an email."""
        self.wait_until_visible((By.NAME, "email")).send_keys(email)
        self.wait_until_clickable(SUBMIT).click()

    # --- Restablecimiento ---------------------------------------------
    def open_reset(self, token: str = "") -> None:
        """Opens the reset form (with or without token)."""
        self.open(f"/restablecer?token={token}" if token else "/restablecer")

    def reset_password(self, new_password: str) -> None:
        """Types the new password and submits the form."""
        self.wait_until_visible((By.NAME, "new_password")).send_keys(new_password)
        self.wait_until_clickable(SUBMIT).click()

    def reset_password_skipping_browser_validation(
        self, new_password: str
    ) -> None:
        """Submits the new password with HTML5 validation disabled.

        Lets the server rule be checked, since the browser's `minlength`
        blocks submitting the form with short values.
        """
        field = self.wait_until_visible((By.NAME, "new_password"))
        field.send_keys(new_password)
        self.driver.execute_script(
            "document.getElementById('auth-form').noValidate = true;"
        )
        self.wait_until_clickable(SUBMIT).click()

    def password_field_is_too_short(self) -> bool:
        """Whether the browser flags the password as too short."""
        field = self.driver.find_element(By.NAME, "new_password")
        return bool(
            self.driver.execute_script(
                "return arguments[0].validity.tooShort;", field
            )
        )

    # --- Consultas comunes ----------------------------------------------
    @property
    def current_path(self) -> str:
        """Current browser path, without domain or query string."""
        return urlparse(self.driver.current_url).path

    @property
    def current_token(self) -> str:
        """Token in the current query string (empty string if none)."""
        query = parse_qs(urlparse(self.driver.current_url).query)
        return query.get("token", [""])[0]

    def wait_for_path(self, path: str) -> None:
        """Waits until the browser reaches the given path."""
        self.wait_for(lambda browser: urlparse(browser.current_url).path == path)

    @property
    def feedback(self) -> str:
        """Waits for and returns the visible form message."""
        return self.wait_until_visible(FEEDBACK).text.strip()

    def feedback_is_visible(self) -> bool:
        """Whether a message is visible, without waiting."""
        return self.driver.find_element(*FEEDBACK).is_displayed()
