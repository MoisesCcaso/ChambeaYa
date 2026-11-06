"""Page Object para los flujos de inicio de sesión."""

from urllib.parse import urlparse

from selenium.webdriver.common.by import By

from .base_page import BasePage


class LoginPage(BasePage):
    """Acciones y consultas de la vista de inicio de sesión."""

    def open_login(self) -> None:
        """Abre el formulario de ingreso."""
        self.open("/ingresar")

    def login(self, email: str, password: str) -> None:
        """Completa las credenciales y envía el formulario."""
        self.wait_until_visible((By.NAME, "email")).send_keys(email)
        self.wait_until_visible((By.NAME, "password")).send_keys(password)
        self.wait_until_clickable(
            (By.CSS_SELECTOR, "#auth-form button[type='submit']")
        ).click()

    def wait_for_path(self, path: str) -> None:
        """Espera hasta que el navegador llegue a la ruta indicada."""
        self.wait_for(lambda _driver: self.current_path == path)

    @property
    def current_path(self) -> str:
        """Ruta actual del navegador, sin dominio ni query string."""
        return urlparse(self.driver.current_url).path

    @property
    def role_label(self) -> str:
        """Espera la carga del rol y devuelve su etiqueta en el panel."""
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
        """Espera la opción de convocatorias del menú de empresa."""
        return self.wait_until_visible(
            (By.CSS_SELECTOR, '[data-view="convocatorias"]')
        ).is_displayed()

    @property
    def error_message(self) -> str:
        """Espera y devuelve el mensaje de error del formulario."""
        return self.wait_until_visible((By.ID, "form-feedback")).text.strip()
