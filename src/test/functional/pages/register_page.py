"""Page Object de la vista de registro (/registro)."""

from urllib.parse import urlparse

from selenium.webdriver.common.by import By

from .base_page import BasePage


class RegisterPage(BasePage):
    """Encapsula los selectores y acciones del formulario de registro."""

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
        """Abre la vista de registro y espera a que el formulario esté visible."""
        super().open(path)
        self.wait_until_visible(self.FORM)
        return self

    def select_type(self, tipo: str) -> "RegisterPage":
        """Selecciona el tipo de cuenta: 'practicante' o 'empresa'.

        El radio está oculto con opacity: 0, por eso se hace clic en su tarjeta visible.
        """
        card = (By.CSS_SELECTOR, f'input[name="tipo"][value="{tipo}"] + span')
        self.wait_until_clickable(card).click()
        return self

    def selected_type(self) -> str:
        """Devuelve el valor del tipo de cuenta seleccionado."""
        radio = self.driver.find_element(By.CSS_SELECTOR, 'input[name="tipo"]:checked')
        return radio.get_attribute("value")

    def fill(self, email: str, password: str, confirmation: str | None = None) -> "RegisterPage":
        """Completa el formulario; si no se indica confirmación, repite la contraseña."""
        self._type(self.EMAIL, email)
        self._type(self.PASSWORD, password)
        self._type(self.CONFIRMATION, password if confirmation is None else confirmation)
        return self

    def submit(self) -> None:
        """Envía el formulario con el botón "Crear cuenta"."""
        self.wait_until_clickable(self.SUBMIT).click()

    def register(
        self,
        email: str,
        password: str,
        confirmation: str | None = None,
        tipo: str = "practicante",
    ) -> None:
        """Atajo: selecciona el tipo, completa el formulario y lo envía."""
        self.select_type(tipo)
        self.fill(email, password, confirmation)
        self.submit()

    def feedback_text(self) -> str:
        """Espera a que aparezca el mensaje del formulario y devuelve su texto."""
        return self.wait_until_visible(self.FEEDBACK).text

    def feedback_kind(self) -> str:
        """Devuelve el tipo del mensaje visible: 'error' o 'success'."""
        classes = self.wait_until_visible(self.FEEDBACK).get_attribute("class").split()
        return next((kind for kind in ("error", "success") if kind in classes), "")

    def is_feedback_visible(self) -> bool:
        """Indica si hay un mensaje visible, sin esperar."""
        return self.driver.find_element(*self.FEEDBACK).is_displayed()

    def rule_is_valid(self, rule: str) -> bool:
        """Indica si una regla de contraseña aparece como cumplida (clase 'valid')."""
        item = self.driver.find_element(
            By.CSS_SELECTOR, f'#password-requirements li[data-password-rule="{rule}"]'
        )
        return "valid" in item.get_attribute("class").split()

    def rules_status(self) -> dict[str, bool]:
        """Estado de las cuatro reglas de contraseña."""
        return {rule: self.rule_is_valid(rule) for rule in self.PASSWORD_RULES}

    def field_validation_message(self, field: str) -> str:
        """Mensaje de validación nativa del navegador para un campo ('' si es válido)."""
        element = self.driver.find_element(*self.FIELDS[field])
        return self.driver.execute_script("return arguments[0].validationMessage;", element)

    def current_path(self) -> str:
        """Ruta actual del navegador, sin dominio ni query string."""
        return urlparse(self.driver.current_url).path

    def wait_for_path(self, path: str) -> None:
        """Espera hasta que el navegador llegue a la ruta indicada."""
        self.wait_for(lambda driver: urlparse(driver.current_url).path == path)

    def _type(self, locator, value: str) -> None:
        element = self.wait_until_visible(locator)
        element.clear()
        element.send_keys(value)
