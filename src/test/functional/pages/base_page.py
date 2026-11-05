"""Operaciones comunes para los Page Objects funcionales."""

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BasePage:
    """Base mínima con navegación y esperas explícitas."""

    def __init__(self, driver, base_url: str, timeout: int = 10):
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.wait = WebDriverWait(driver, timeout)

    def open(self, path: str = "/") -> None:
        """Navega a una ruta absoluta o relativa a la aplicación."""
        is_absolute_url = path.startswith(("http://", "https://"))
        url = path if is_absolute_url else f"{self.base_url}/{path.lstrip('/')}"
        self.driver.get(url)

    def wait_for(self, condition):
        """Espera una condición de Selenium y devuelve su resultado."""
        return self.wait.until(condition)

    def wait_until_visible(self, locator):
        """Espera y devuelve un elemento visible."""
        return self.wait_for(EC.visibility_of_element_located(locator))

    def wait_until_clickable(self, locator):
        """Espera y devuelve un elemento habilitado para hacer clic."""
        return self.wait_for(EC.element_to_be_clickable(locator))
