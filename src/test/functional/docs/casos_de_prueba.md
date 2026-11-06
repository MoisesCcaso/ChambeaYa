# Casos de prueba – Perfiles (I4)

Técnica de caja negra: **clases de equivalencia y análisis de valores límite**.  
Automatizados en [`test_perfiles.py`](../test_perfiles.py) (1 método por caso).

| ID | Objeto de prueba | Escenario / Acciones | Valores de prueba | Resultado esperado |
|:---|:---|:---|:---|:---|
| **PER-01** | Perfil practicante | Iniciar sesión como practicante, ir a `/app` → Perfil y guardar datos válidos (nombres y datos completos) | Nombres y datos completos (válidos) | Estado de guardado exitoso en `student-profile-status` / notificación de confirmación |
| **PER-02** | Perfil practicante | Iniciar sesión como practicante, ir a `/app` → Perfil y agregar una habilidad válida | Habilidad: `Python` | Aparece en `skills-list` |
| **PER-03** | Perfil practicante | Iniciar sesión como practicante, ir a `/app` → Perfil e intentar agregar habilidad vacía | Habilidad: `""` (cadena vacía) | No se agrega a la lista de habilidades |
| **PER-04** | Perfil practicante | Iniciar sesión como practicante, ir a `/app` → Perfil y agregar formación educativa válida | Formación: `Ing. de Sistemas` | Aparece en `education-list` |
| **PER-05** | Perfil empresa | Iniciar sesión como empresa, ir a `/app` → Perfil y guardar con RUC válido (11 dígitos numéricos) | RUC de 11 dígitos | Guardado exitoso en `company-profile-status` / notificación de confirmación |
| **PER-06** | Perfil empresa | Iniciar sesión como empresa, ir a `/app` → Perfil e intentar guardar con RUC inválido (límite 10 y 12 dígitos) | `1234567890` (10 dígitos), `123456789012` (12 dígitos) | Error de validación en campo RUC (`validity.valid` falso o mensaje de validación) |

---

## Entorno y datos de prueba

- Credenciales practicante demo: `practicante@demo.local` / `Demo1234`
- Credenciales empresa demo: `empresa@demo.local` / `Demo1234`
- Page Object: [`pages/profile_page.py`](../pages/profile_page.py)
- Archivo de prueba: [`test_perfiles.py`](../test_perfiles.py)
