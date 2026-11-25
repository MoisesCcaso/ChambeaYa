"""Page Object for the registration view (/registro)."""

from urllib.parse import urlparse

from selenium.webdriver.common.by import By

from .base_page import BasePage


class RegisterPage(BasePage):
    """Wraps the registration form selectors and actions."""

    PATH = "/registro"

    FORM = (By.CSS_SELECTOR, '.auth-box[data-auth-mode="register"] #auth-form')
    EMAIL = (By.NAME, "email")
    PASSWORD = (By.NAME, "password")
    CONFIRMATION = (By.NAME, "password_confirmation")
    SUBMIT = (By.CSS_SELECTOR, '#auth-form button[type="submit"]')
    FEEDBACK = (By.ID, "form-feedback")

    PASSWORD_RULES = ("length", "lowercase", "uppercase", "number")

    FIELDS = {
        "email": EMAIL,
        "password": PASSWORD,
        "password_confirmation": CONFIRMATION,
    }

    def open(self, path: str = PATH) -> "RegisterPage":
        """Opens the registration view and waits for the form."""
        super().open(path)
        self.wait_until_visible(self.FORM)
        return self

    def select_type(self, role: str) -> "RegisterPage":
        """Selects the account type: 'practicante' or 'empresa'.

        The radio is hidden with opacity: 0, so its visible card is clicked instead.
        """
        card = (By.CSS_SELECTOR, f'input[name="tipo"][value="{role}"] + span')
        self.wait_until_clickable(card).click()
        return self

    def selected_type(self) -> str:
        """Returns the selected account type value."""
        radio = self.driver.find_element(By.CSS_SELECTOR, 'input[name="tipo"]:checked')
        return radio.get_attribute("value")

    def fill(self, email: str, password: str, confirmation: str | None = None) -> "RegisterPage":
        """Fills in the form; without a confirmation it repeats the password."""
        self._type(self.EMAIL, email)
        self._type(self.PASSWORD, password)
        self._type(self.CONFIRMATION, password if confirmation is None else confirmation)
        return self

    def submit(self) -> None:
        """Submits the form with the "Crear cuenta" button."""
        self.wait_until_clickable(self.SUBMIT).click()

    def register(
        self,
        email: str,
        password: str,
        confirmation: str | None = None,
        role: str = "practicante",
    ) -> None:
        """Shortcut: selects the type, fills in the form and submits it."""
        self.select_type(role)
        self.fill(email, password, confirmation)
        self.submit()

    def feedback_text(self) -> str:
        """Waits for the form message and returns its text."""
        return self.wait_until_visible(self.FEEDBACK).text

    def feedback_kind(self) -> str:
        """Returns the visible message type: 'error' or 'success'."""
        classes = self.wait_until_visible(self.FEEDBACK).get_attribute("class").split()
        return next((kind for kind in ("error", "success") if kind in classes), "")

    def is_feedback_visible(self) -> bool:
        """Whether a message is visible, without waiting."""
        return self.driver.find_element(*self.FEEDBACK).is_displayed()

    def rule_is_valid(self, rule: str) -> bool:
        """Whether a password rule shows as met ('valid' class)."""
        item = self.driver.find_element(
            By.CSS_SELECTOR, f'#password-requirements li[data-password-rule="{rule}"]'
        )
        return "valid" in item.get_attribute("class").split()

    def rules_status(self) -> dict[str, bool]:
        """Status of the four password rules."""
        return {rule: self.rule_is_valid(rule) for rule in self.PASSWORD_RULES}

    def field_validation_message(self, field: str) -> str:
        """Browser native validation message for a field ('' if valid)."""
        element = self.driver.find_element(*self.FIELDS[field])
        return self.driver.execute_script("return arguments[0].validationMessage;", element)

    def current_path(self) -> str:
        """Current browser path, without domain or query string."""
        return urlparse(self.driver.current_url).path

    def wait_for_path(self, path: str) -> None:
        """Waits until the browser reaches the given path."""
        self.wait_for(lambda driver: urlparse(driver.current_url).path == path)

    def _type(self, locator, value: str) -> None:
        element = self.wait_until_visible(locator)
        element.clear()
        element.send_keys(value)
