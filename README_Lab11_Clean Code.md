# 🧹 Laboratorio 11 – Clean Code

**ChambeaYa - Prácticas de Codificación Legible**

---

## 📋 Objetivo

Demostrar la corrección de bugs, code smells y vulnerabilities aplicando prácticas de codificación legible en el proyecto.

---

## 📌 Prácticas Aplicadas (1 por categoría)

| Categoría | Práctica | Archivo |
|-----------|----------|---------|
| Nombres | Nombres descriptivos | `postulacion_application_service.py` |
| Funciones | Funciones pequeñas (< 15 líneas) | `matching_application_service.py` |
| Comentarios | Comentarios del "por qué" | `certificacion_application_service.py` |
| Estructura | Organización por capas (DDD) | Todo el proyecto |
| Objetos/Datos | Entidades con comportamiento | `domain/perfil/practicante.py` |
| Errores | Excepciones específicas | `postulacion_controller.py` |
| Clases | Responsabilidad Única (SRP) | `matching_application_service.py` |

---

## 1. Nombres Descriptivos

```python
# ❌ Malo
def p(self, pid: int, cid: int) -> Dict:
    pass

# ✅ Bueno
def postularse(self, practicante_id: int, convocatoria_id: int) -> Dict:
    pass
```

## 2. Funciones Pequeñas con un Propósito Único

```python
# ❌ Malo - Función de 40+ líneas
def recomendar(self, practicante_id: int) -> List[Dict]:
    # 40+ líneas de código
    pass

# ✅ Bueno - Funciones de < 15 líneas
def recomendar_convocatorias(self, practicante_id: int) -> List[Dict]:
    perfil = self._obtener_perfil(practicante_id)
    convocatorias = self._obtener_convocatorias_activas()
    sugerencias = self._calcular_sugerencias(perfil, convocatorias)
    return self._formatear_resultado(sugerencias)
```

## 3. Comentarios que Explican el "Por Qué"

```python
# ❌ Malo - Comentario obvio
# Obtener práctica
practica = self.practica_repo.obtener_por_id(practica_id)

# ✅ Bueno - Comentario con regla de negocio
# La práctica debe estar completada para generar un certificado
# Regla definida por el cliente para garantizar autenticidad
if practica.estado != 'completada':
    raise ValueError("Solo prácticas completadas generan certificados")
```

## 4. Estructura de Código Fuente Organizada (DDD)

```bash
ChambeaYa/
├── domain/          # Reglas de negocio
├── application/     # Casos de uso
├── infrastructure/  # Persistencia
├── presentation/    # Controladores
└── frameworks/      # Frameworks (Flask, SQLAlchemy)
```

## 5. Objetos con Comportamiento

```python
# ❌ Malo - Objeto anémico
@dataclass
class Practicante:
    habilidades: List[str]
    # Sin métodos

# ✅ Bueno - Objeto con comportamiento
@dataclass
class Practicante:
    habilidades: List[str]

    def agregar_habilidad(self, habilidad: str) -> bool:
        if habilidad not in self.habilidades:
            self.habilidades.append(habilidad)
            return True
        return False
```

## 6. Tratamiento de Errores con Excepciones Específicas

```python
# ❌ Malo - Manejo genérico
try:
    resultado = servicio.postularse(...)
except Exception as e:
    return jsonify({"error": "Error"}), 500

# ✅ Bueno - Excepciones específicas
try:
    resultado = servicio.postularse(...)
    return jsonify(resultado), 201
except ValueError as e:
    return jsonify({"error": str(e)}), 400
except PermissionError as e:
    return jsonify({"error": str(e)}), 403
except Exception as e:
    logger.error(f"Error inesperado: {str(e)}")
    return jsonify({"error": "Error interno"}), 500
```

## 7. Clases con Responsabilidad Única (SRP)

```python
# ❌ Malo - Múltiples responsabilidades
class MatchingService:
    def recomendar(self): ...      # Matching
    def guardar(self): ...         # Persistencia
    def notificar(self): ...       # Notificaciones
    def reporte(self): ...         # Reportes

# ✅ Bueno - Clases con SRP
class MatchingService: ...
class SugerenciaRepository: ...
class NotificacionService: ...
class ReporteService: ...
```

## 🛠 Resultado de SonarLint

| Métrica | Antes | Después |
|---------|-------|---------|
| Issues de SonarLint | 25 | 0 |
| Severidad "Critical" | 3 | 0 |
| Code Smells | 18 | 0 |

`images/sonarlint_resultado.png`

📅 Fecha: Julio 2026
