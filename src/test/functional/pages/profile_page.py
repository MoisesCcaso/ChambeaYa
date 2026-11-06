"""Page Object para la vista de Perfil (/app -> Perfil)."""

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from .base_page import BasePage


class ProfilePage(BasePage):
    """Acciones y selectores para la vista de perfil de practicante y empresa."""

    NAV_PERFIL = (By.CSS_SELECTOR, '[data-view="perfil"]')
    PANEL_PERFIL = (By.CSS_SELECTOR, '[data-view-panel="perfil"]')

    # Perfil Practicante
    STUDENT_FORM = (By.ID, "student-profile-form")
    STUDENT_NOMBRES = (By.CSS_SELECTOR, '#student-profile-form input[name="nombres"]')
    STUDENT_APELLIDOS = (By.CSS_SELECTOR, '#student-profile-form input[name="apellidos"]')
    STUDENT_DNI = (By.CSS_SELECTOR, '#student-profile-form input[name="dni"]')
    STUDENT_CARNET = (By.CSS_SELECTOR, '#student-profile-form input[name="carnet_universitario"]')
    STUDENT_SUBMIT = (By.CSS_SELECTOR, '#student-profile-form button[type="submit"]')
    STUDENT_STATUS = (By.ID, "student-profile-status")

    # Habilidades
    SKILL_INPUT = (By.ID, "skill-input")
    ADD_SKILL_BUTTON = (By.ID, "add-skill")
    SKILLS_LIST = (By.ID, "skills-list")

    # Formación
    EDUCATION_INPUT = (By.ID, "education-input")
    ADD_EDUCATION_BUTTON = (By.ID, "add-education")
    EDUCATION_LIST = (By.ID, "education-list")

    # Perfil Empresa
    COMPANY_FORM = (By.ID, "company-profile-form")
    COMPANY_RAZON_SOCIAL = (By.CSS_SELECTOR, '#company-profile-form input[name="razon_social"]')
    COMPANY_RUC = (By.CSS_SELECTOR, '#company-profile-form input[name="ruc"]')
    COMPANY_SUBMIT = (By.CSS_SELECTOR, '#company-profile-form button[type="submit"]')
    COMPANY_STATUS = (By.ID, "company-profile-status")

    # Notificaciones / Feedback
    TOAST = (By.CSS_SELECTOR, "#toast-region .toast")

    def _click(self, element) -> None:
        """Hace scroll hacia el elemento y lo clickea de forma robusta."""
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", element
        )
        try:
            element.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", element)

    def open_profile(self) -> "ProfilePage":
        """Navega a la vista de perfil en /app."""
        btn = self.wait_until_clickable(self.NAV_PERFIL)
        self._click(btn)
        self.wait_until_visible(self.PANEL_PERFIL)
        return self

    def _set_input(self, locator, value: str) -> None:
        """Limpia el input con control+a y escribe el nuevo valor."""
        el = self.wait_until_visible(locator)
        self._click(el)
        el.send_keys(Keys.CONTROL, "a")
        el.send_keys(Keys.BACKSPACE)
        if value:
            el.send_keys(value)

    def fill_student_profile(
        self,
        nombres: str | None = None,
        apellidos: str | None = None,
        dni: str | None = None,
        carnet: str | None = None,
    ) -> "ProfilePage":
        """Completa los datos del formulario de practicante."""
        if nombres is not None:
            self._set_input(self.STUDENT_NOMBRES, nombres)
        if apellidos is not None:
            self._set_input(self.STUDENT_APELLIDOS, apellidos)
        if dni is not None:
            self._set_input(self.STUDENT_DNI, dni)
        if carnet is not None:
            self._set_input(self.STUDENT_CARNET, carnet)
        return self

    def submit_student_profile(self) -> None:
        """Envía el formulario de practicante."""
        btn = self.wait_until_clickable(self.STUDENT_SUBMIT)
        self._click(btn)

    def get_student_status(self) -> str:
        """Obtiene el texto de estado de guardado o notificación de practicante."""
        status_el = self.driver.find_element(*self.STUDENT_STATUS)
        text = status_el.text.strip()
        if text:
            return text
        toast = self.wait_until_visible(self.TOAST)
        return toast.text.strip()

    def remove_skill_if_present(self, skill_name: str) -> "ProfilePage":
        """Elimina una habilidad de la lista si ya se encuentra presente."""
        skills_container = self.wait_until_visible(self.SKILLS_LIST)
        tags = skills_container.find_elements(By.CSS_SELECTOR, ".tag")
        for tag in tags:
            if skill_name.lower() in tag.text.lower():
                remove_btn = tag.find_element(By.CSS_SELECTOR, "button[data-remove-skill]")
                self._click(remove_btn)
                break
        return self

    def add_skill(self, skill_name: str) -> "ProfilePage":
        """Añade una habilidad en el perfil de practicante."""
        self._set_input(self.SKILL_INPUT, skill_name)
        btn = self.wait_until_clickable(self.ADD_SKILL_BUTTON)
        self._click(btn)
        return self

    def get_skills(self) -> list[str]:
        """Obtiene la lista actual de habilidades mostradas en tags."""
        skills_container = self.wait_until_visible(self.SKILLS_LIST)
        tags = skills_container.find_elements(By.CSS_SELECTOR, ".tag")
        return [tag.text.strip() for tag in tags if tag.text.strip()]

    def remove_education_if_present(self, education_name: str) -> "ProfilePage":
        """Elimina una formación de la lista si ya se encuentra presente."""
        edu_container = self.wait_until_visible(self.EDUCATION_LIST)
        tags = edu_container.find_elements(By.CSS_SELECTOR, ".tag")
        for tag in tags:
            if education_name.lower() in tag.text.lower():
                remove_btn = tag.find_element(By.CSS_SELECTOR, "button[data-remove-education]")
                self._click(remove_btn)
                break
        return self

    def add_education(self, education_name: str) -> "ProfilePage":
        """Añade una formación en el perfil de practicante."""
        self._set_input(self.EDUCATION_INPUT, education_name)
        btn = self.wait_until_clickable(self.ADD_EDUCATION_BUTTON)
        self._click(btn)
        return self

    def get_education(self) -> list[str]:
        """Obtiene la lista actual de formaciones mostradas en tags."""
        edu_container = self.wait_until_visible(self.EDUCATION_LIST)
        tags = edu_container.find_elements(By.CSS_SELECTOR, ".tag")
        return [tag.text.strip() for tag in tags if tag.text.strip()]

    def fill_company_profile(
        self,
        razon_social: str | None = None,
        ruc: str | None = None,
    ) -> "ProfilePage":
        """Completa los datos del formulario de empresa."""
        if razon_social is not None:
            self._set_input(self.COMPANY_RAZON_SOCIAL, razon_social)
        if ruc is not None:
            self._set_input(self.COMPANY_RUC, ruc)
        return self

    def submit_company_profile(self) -> None:
        """Envía el formulario de empresa."""
        btn = self.wait_until_clickable(self.COMPANY_SUBMIT)
        self._click(btn)

    def get_company_status(self) -> str:
        """Obtiene el texto de estado de guardado o notificación de empresa."""
        status_el = self.driver.find_element(*self.COMPANY_STATUS)
        text = status_el.text.strip()
        if text:
            return text
        toast = self.wait_until_visible(self.TOAST)
        return toast.text.strip()

    def is_company_ruc_valid(self) -> bool:
        """Indica si el campo RUC cumple las restricciones del navegador (HTML5)."""
        ruc_el = self.driver.find_element(*self.COMPANY_RUC)
        return self.driver.execute_script("return arguments[0].validity.valid;", ruc_el)

    def company_ruc_validation_message(self) -> str:
        """Devuelve el mensaje de validación nativo del navegador para RUC."""
        ruc_el = self.driver.find_element(*self.COMPANY_RUC)
        return self.driver.execute_script("return arguments[0].validationMessage;", ruc_el)
