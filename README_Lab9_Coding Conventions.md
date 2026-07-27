# 📏 Laboratorio 9 – Coding Conventions

**ChambeaYa - Convenciones de Codificación**

---

## 📋 Objetivo

Aplicar estándares, convenciones y estilos de programación que contribuyan a la legibilidad, el mantenimiento y la reutilización del software.

---

## 🐍 Convenciones Aplicadas (PEP 8)

### 1. Nombres de Clases (CamelCase)

```python
# ✅ Bueno
class SQLAlchemyUsuarioRepository:
    pass

class UsuarioApplicationService:
    pass

# ❌ Malo
class sqlalchemy_usuario_repository:
    pass
```

### 2. Nombres de Funciones y Métodos (snake_case)

```python
# ✅ Bueno
def registrar_usuario(datos_usuario):
    pass

def obtener_por_email(email):
    pass

# ❌ Malo
def registrarUsuario(datosUsuario):
    pass
```

### 3. Nombres de Constantes (MAYUSCULAS_SNAKE_CASE)

```python
# ✅ Bueno
MAX_INTENTOS_LOGIN = 5
TIEMPO_EXPIRACION_SESION = 3600

# ❌ Malo
maxIntentosLogin = 5
```

### 4. Docstrings en Funciones Públicas

```python
def autenticar(email: str, password: str) -> dict:
    """
    Autentica a un usuario con email y password.

    Args:
        email (str): Correo electrónico del usuario
        password (str): Contraseña sin encriptar

    Returns:
        dict: Datos del usuario autenticado

    Raises:
        AuthenticationError: Si las credenciales son inválidas
    """
    usuario = self.usuario_repo.obtener_por_email(email)
    if not usuario:
        raise AuthenticationError("Credenciales inválidas")
    return usuario.to_dict()
```

### 5. Manejo de Excepciones Específicas

```python
# ✅ Bueno
try:
    usuario = self.usuario_repo.obtener_por_email(email)
except SQLAlchemyError as e:
    logger.error(f"Error de base de datos: {e}")
    raise DatabaseError("Error al acceder a la base de datos")
except IntegrityError as e:
    logger.warning(f"Conflicto de integridad: {e}")
    raise DuplicateEntryError("El email ya está registrado")

# ❌ Malo
try:
    usuario = self.usuario_repo.obtener_por_email(email)
except Exception as e:
    raise Exception("Error")
```

### 6. Espaciado y Formato (PEP 8)

```python
# ✅ Bueno
def calcular_coincidencia(habilidades_a, habilidades_b):
    interseccion = set(habilidades_a) & set(habilidades_b)
    union = set(habilidades_a) | set(habilidades_b)
    return len(interseccion) / len(union) if union else 0

# ❌ Malo
def calcular_coincidencia(habilidades_a,habilidades_b):
    interseccion=set(habilidades_a)&set(habilidades_b)
    union=set(habilidades_a)|set(habilidades_b)
    return len(interseccion)/len(union) if union else 0
```

### 7. Organización de Imports

```python
# ✅ Bueno
import os
import uuid
from datetime import datetime

from flask import request, jsonify
from sqlalchemy.exc import SQLAlchemyError

from domain.perfil.entities import Perfil
from infrastructure.sqlalchemy_perfil_repository import SQLAlchemyPerfilRepository

# ❌ Malo
from infrastructure.sqlalchemy_perfil_repository import SQLAlchemyPerfilRepository
from datetime import datetime
from flask import request
```

## ✅ Resumen de Prácticas Aplicadas

| Categoría | Práctica | Archivo Ejemplo |
|-----------|----------|------------------|
| Nombres | Clases en CamelCase | `sqlalchemy_usuario_repository.py` |
| Nombres | Funciones en snake_case | `usuario_application_service.py` |
| Nombres | Constantes en MAYUSCULAS | `config.py` |
| Comentarios | Docstrings con Args/Returns/Raises | `perfil_application_service.py` |
| Errores | Excepciones específicas | `usuario_controller.py` |
| Formato | PEP 8 (espaciado, indentación) | Todos los archivos |
| Estructura | Imports organizados por grupos | Todos los archivos |

📅 Fecha: Julio 2026
