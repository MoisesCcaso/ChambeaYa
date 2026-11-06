"""Page Object para activación y recuperación de contraseña."""

from urllib.parse import parse_qs, urlparse

from selenium.webdriver.common.by import By

from .base_page import BasePage

SUBMIT = (By.CSS_SELECTOR, "#auth-form button[type='submit']")
FEEDBACK = (By.ID, "form-feedback")


class RecoveryPage(BasePage):
    """Acciones y consultas de `/activar`, `/recuperar` y `/restablecer`."""

    # --- Activación ---------------------------------------------------
    def open_activation(self, token: str) -> None:
        """Abre el enlace de activación con el token indicado."""
        self.open(f"/activar?token={token}")

    def submit_activation(self) -> None:
        """Confirma la activación de la cuenta."""
        self.wait_until_clickable(SUBMIT).click()

    # --- Recuperación -------------------------------------------------
    def open_recovery(self) -> None:
        """Abre el formulario de solicitud de recuperación."""
        self.open("/recuperar")

    def request_recovery(self, email: str) -> None:
        """Solicita el acceso de recuperación para un correo."""
        self.wait_until_visible((By.NAME, "email")).send_keys(email)
        self.wait_until_clickable(SUBMIT).click()

    # --- Restablecimiento ---------------------------------------------
    def open_reset(self, token: str = "") -> None:
        """Abre el formulario de restablecimiento (con o sin token)."""
        self.open(f"/restablecer?token={token}" if token else "/restablecer")

    def reset_password(self, new_password: str) -> None:
        """Escribe la nueva contraseña y envía el formulario."""
        self.wait_until_visible((By.NAME, "new_password")).send_keys(new_password)
        self.wait_until_clickable(SUBMIT).click()

    def reset_password_skipping_browser_validation(
        self, new_password: str
    ) -> None:
        """Envía la nueva contraseña desactivando la validación HTML5.

        Permite comprobar la regla del servidor, ya que `minlength` del
        navegador impide enviar el formulario con valores cortos.
        """
        field = self.wait_until_visible((By.NAME, "new_password"))
        field.send_keys(new_password)
        self.driver.execute_script(
            "document.getElementById('auth-form').noValidate = true;"
        )
        self.wait_until_clickable(SUBMIT).click()

    def password_field_is_too_short(self) -> bool:
        """Indica si el navegador marca la contraseña como demasiado corta."""
        field = self.driver.find_element(By.NAME, "new_password")
        return bool(
            self.driver.execute_script(
                "return arguments[0].validity.tooShort;", field
            )
        )

    # --- Consultas comunes ----------------------------------------------
    @property
    def current_path(self) -> str:
        """Ruta actual del navegador, sin dominio ni query string."""
        return urlparse(self.driver.current_url).path

    @property
    def current_token(self) -> str:
        """Token presente en la query string actual (cadena vacía si no hay)."""
        query = parse_qs(urlparse(self.driver.current_url).query)
        return query.get("token", [""])[0]

    def wait_for_path(self, path: str) -> None:
        """Espera hasta que el navegador llegue a la ruta indicada."""
        self.wait_for(lambda browser: urlparse(browser.current_url).path == path)

    @property
    def feedback(self) -> str:
        """Espera y devuelve el mensaje visible del formulario."""
        return self.wait_until_visible(FEEDBACK).text.strip()

    def feedback_is_visible(self) -> bool:
        """Indica sin esperar si hay un mensaje visible."""
        return self.driver.find_element(*FEEDBACK).is_displayed()
