"""Page Object para crear y consultar convocatorias de empresa."""

from selenium.webdriver.common.by import By

from .base_page import BasePage


class ConvocatoriaPage(BasePage):
    """Acciones y consultas de la vista de convocatorias en `/app`."""

    MENU = (By.CSS_SELECTOR, '[data-view="convocatorias"]')
    PANEL = (By.CSS_SELECTOR, '[data-view-panel="convocatorias"]')
    NEW_BUTTON = (By.ID, "new-opening-button")
    DIALOG = (By.ID, "opening-dialog")
    FORM = (By.ID, "opening-form")
    TITLE = (By.NAME, "titulo")
    DESCRIPTION = (By.NAME, "descripcion")
    SKILLS = (By.NAME, "habilidades_requeridas")
    BENEFITS = (By.NAME, "beneficios")
    SAVE_BUTTON = (By.CSS_SELECTOR, '#opening-form button[type="submit"]')
    TABLE = (By.ID, "openings-table")

    def open_convocatorias(self) -> "ConvocatoriaPage":
        """Abre la sección de convocatorias desde el menú de empresa."""
        self.wait_until_clickable(self.MENU).click()
        self.wait_until_visible(self.PANEL)
        return self

    def start_new_convocatoria(self) -> "ConvocatoriaPage":
        """Abre el formulario modal para crear una convocatoria."""
        self.wait_until_clickable(self.NEW_BUTTON).click()
        self.wait_until_visible(self.DIALOG)
        return self

    def fill_convocatoria(
        self,
        titulo: str,
        descripcion: str = "",
        habilidades: str = "",
        beneficios: str = "",
    ) -> "ConvocatoriaPage":
        """Completa los campos del formulario de convocatoria."""
        fields = (
            (self.TITLE, titulo),
            (self.DESCRIPTION, descripcion),
            (self.SKILLS, habilidades),
            (self.BENEFITS, beneficios),
        )
        for locator, value in fields:
            field = self.wait_until_visible(locator)
            field.clear()
            field.send_keys(value)
        return self

    def save_draft(self) -> None:
        """Guarda el formulario como borrador."""
        self.wait_until_clickable(self.SAVE_BUTTON).click()

    def create_draft(
        self,
        titulo: str,
        descripcion: str = "",
        habilidades: str = "",
        beneficios: str = "",
    ) -> None:
        """Completa y guarda una nueva convocatoria como borrador."""
        self.start_new_convocatoria()
        self.fill_convocatoria(titulo, descripcion, habilidades, beneficios)
        self.save_draft()
        self.wait_for(
            lambda _driver: self.driver.find_element(*self.DIALOG).get_attribute(
                "open"
            ) is None
        )
        self.convocatoria_row(titulo)

    def convocatoria_row(self, titulo: str):
        """Devuelve la fila de la tabla que corresponde al título indicado."""
        return self.wait_until_visible(
            (
                By.XPATH,
                f'//tbody[@id="openings-table"]//tr[.//strong[normalize-space()="{titulo}"]]'
            )
        )

    def convocatoria_is_borrador(self, titulo: str) -> bool:
        """Indica si la fila de la convocatoria muestra el estado borrador."""
        return "borrador" in self.convocatoria_row(titulo).text.casefold()

    def publish_convocatoria(self, titulo: str) -> None:
        """Publica el borrador identificado por su título y espera la actualización."""
        row = self.convocatoria_row(titulo)
        publish_button = row.find_element(
            By.CSS_SELECTOR, "[data-publish-opening]"
        )
        publish_button.click()
        self.wait_until_visible(
            (
                By.XPATH,
                f'//tbody[@id="openings-table"]//tr[.//strong[normalize-space()="{titulo}"]]//span[contains(@class, "status-publicada")]',
            )
        )

    def convocatoria_is_publicada(self, titulo: str) -> bool:
        """Indica si la tabla muestra la convocatoria como publicada."""
        return self.wait_until_visible(
            (
                By.XPATH,
                f'//tbody[@id="openings-table"]//tr[.//strong[normalize-space()="{titulo}"]]//span[contains(@class, "status-publicada")]',
            )
        ).is_displayed()
