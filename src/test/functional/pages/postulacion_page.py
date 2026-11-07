"""Page Objects de oportunidades, postulaciones y verificación de certificados."""

from selenium.webdriver.common.by import By

from .base_page import BasePage


class PostulacionPage(BasePage):
    """Vistas Oportunidades y Mis postulaciones del practicante en `/app`."""

    NAV_OPORTUNIDADES = (By.CSS_SELECTOR, '[data-view="oportunidades"]')
    PANEL_OPORTUNIDADES = (By.CSS_SELECTOR, '[data-view-panel="oportunidades"]')
    OPPORTUNITY_TITLES = (By.CSS_SELECTOR, "#opportunity-list .result-item h3")
    OPPORTUNITY_DETAIL = (By.ID, "opportunity-detail")
    DETAIL_STATUS_BADGE = (By.CSS_SELECTOR, "#opportunity-detail .detail-actions .status-badge")
    NAV_POSTULACIONES = (By.CSS_SELECTOR, '[data-view="postulaciones"]')
    PANEL_POSTULACIONES = (By.CSS_SELECTOR, '[data-view-panel="postulaciones"]')
    TOAST = (By.CSS_SELECTOR, "#toast-region .toast")

    def _click(self, element) -> None:
        """Hace scroll hasta el elemento y lo pulsa, con respaldo por JavaScript."""
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});",
            element,
        )
        try:
            element.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", element)

    # --- Oportunidades ---
    def open_oportunidades(self) -> "PostulacionPage":
        """Abre Oportunidades y espera a que cargue la lista o el estado vacío."""
        self._click(self.wait_until_clickable(self.NAV_OPORTUNIDADES))
        self.wait_until_visible(self.PANEL_OPORTUNIDADES)
        self.wait_for(
            lambda browser: browser.find_elements(
                By.CSS_SELECTOR,
                "#opportunity-list .result-item, #opportunity-list .empty-state",
            )
        )
        return self

    def opportunity_titles(self) -> list[str]:
        """Títulos de las convocatorias que muestra la lista."""
        return [
            heading.text.strip()
            for heading in self.driver.find_elements(*self.OPPORTUNITY_TITLES)
        ]

    def opportunity_is_listed(self, titulo: str) -> bool:
        """Indica si la convocatoria aparece en la lista de oportunidades."""
        return titulo in self.opportunity_titles()

    def select_opportunity(self, opening_id: int) -> "PostulacionPage":
        """Selecciona una convocatoria de la lista para ver su detalle."""
        item = self.wait_until_clickable(
            (By.CSS_SELECTOR, f'[data-select-opening="{opening_id}"]')
        )
        self._click(item)
        self.wait_until_visible(
            (By.CSS_SELECTOR, "#opportunity-detail .detail-actions")
        )
        return self

    def apply_button_is_present(self, opening_id: int) -> bool:
        """Indica si el detalle ofrece el botón de postular a esa convocatoria."""
        return bool(
            self.driver.find_elements(
                By.CSS_SELECTOR, f'[data-apply-opening="{opening_id}"]'
            )
        )

    def apply(self, opening_id: int) -> str:
        """Pulsa Postular y devuelve el texto del aviso que muestra la aplicación."""
        button = self.wait_until_clickable(
            (By.CSS_SELECTOR, f'[data-apply-opening="{opening_id}"]')
        )
        self._click(button)
        return self.wait_until_visible(self.TOAST).text.strip()

    def detail_status_class(self) -> str:
        """Clases CSS de la etiqueta de estado que reemplaza al botón de postular."""
        return self.wait_until_visible(self.DETAIL_STATUS_BADGE).get_attribute("class")

    # --- Mis postulaciones ---
    def open_postulaciones(self) -> "PostulacionPage":
        """Abre la vista Mis postulaciones."""
        self._click(self.wait_until_clickable(self.NAV_POSTULACIONES))
        self.wait_until_visible(self.PANEL_POSTULACIONES)
        return self

    @staticmethod
    def _row_xpath(titulo: str) -> str:
        return (
            f'//tbody[@id="applications-table"]'
            f'//tr[.//strong[normalize-space()="{titulo}"]]'
        )

    def application_count(self, titulo: str) -> int:
        """Número de filas de la tabla que corresponden a la convocatoria."""
        self.wait_for(
            lambda browser: browser.find_elements(
                By.CSS_SELECTOR, "#applications-table tr"
            )
        )
        return len(self.driver.find_elements(By.XPATH, self._row_xpath(titulo)))

    def application_has_status(self, titulo: str, estado: str) -> bool:
        """Indica si la postulación a la convocatoria muestra el estado indicado."""
        return self.wait_until_visible(
            (
                By.XPATH,
                f'{self._row_xpath(titulo)}//span[contains(@class, "status-{estado}")]',
            )
        ).is_displayed()


class VerificarCertificadoPage(BasePage):
    """Vista pública `/verificar-certificado` (no requiere sesión)."""

    CODE_INPUT = (By.CSS_SELECTOR, '#verify-form input[name="codigo"]')
    SUBMIT = (By.CSS_SELECTOR, '#verify-form button[type="submit"]')
    RESULT = (By.ID, "verification-result")

    def open_verificacion(self) -> "VerificarCertificadoPage":
        """Abre la página pública de verificación."""
        self.open("/verificar-certificado")
        self.wait_until_visible(self.CODE_INPUT)
        return self

    def verify(self, codigo: str) -> "VerificarCertificadoPage":
        """Escribe el código, envía el formulario y espera el resultado."""
        field = self.wait_until_visible(self.CODE_INPUT)
        field.clear()
        field.send_keys(codigo)
        self.wait_until_clickable(self.SUBMIT).click()
        self.wait_until_visible(self.RESULT)
        return self

    @property
    def result_text(self) -> str:
        """Texto del recuadro de resultado."""
        return self.driver.find_element(*self.RESULT).text.strip()

    @property
    def result_is_valid(self) -> bool:
        """True si el resultado se pintó como válido (clase `valid`)."""
        classes = self.driver.find_element(*self.RESULT).get_attribute("class").split()
        return "valid" in classes
