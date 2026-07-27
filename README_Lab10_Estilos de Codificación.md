# 🎨 Laboratorio 10 – Estilos de Codificación

**ChambeaYa - Estilos de Programación Aplicados**

---

## 📋 Objetivo

Aplicar 4 estilos de programación en la implementación del proyecto.

---

## 📌 Estilos Aplicados

### 1. Estilo Cookbook (Recetas paso a paso)

**Definición:** Las funciones actúan como "recetas" donde cada paso es una acción clara, bien definida y secuencial.

**Ubicación:** `application/postulacion_application_service.py`

```python
def postularse(self, practicante_id: int, convocatoria_id: int) -> Dict:
    """
    ESTILO COOKBOOK: Cada paso es una instrucción clara.
    """
    # Paso 1: Validar perfil
    perfil = self.perfil_repo.obtener_por_usuario_id(practicante_id)
    if not perfil:
        raise ValueError("El practicante no tiene un perfil completo")

    # Paso 2: Validar convocatoria
    convocatoria = self.convocatoria_repo.obtener_por_id(convocatoria_id)
    if not convocatoria:
        raise ValueError("Convocatoria no encontrada")

    # Paso 3: Validar fecha límite
    if convocatoria.fecha_limite_postulacion < datetime.now().date():
        raise ValueError("La convocatoria ha expirado")

    # Paso 4: Validar duplicado
    existente = self.postulacion_repo.obtener_por_practicante_y_convocatoria(
        practicante_id, convocatoria_id
    )
    if existente:
        raise ValueError("Ya existe una postulación")

    # Paso 5: Crear y guardar
    postulacion = Postulacion(...)
    return self.postulacion_repo.guardar(postulacion).to_dict()
```

### 2. Estilo Pipeline (Procesamiento en etapas)

**Definición:** Los datos fluyen a través de etapas secuenciales.

**Ubicación:** `application/matching_application_service.py`

```python
def recomendar_convocatorias(self, practicante_id: int, limit: int = 10) -> List[Dict]:
    """
    ESTILO PIPELINE: Procesamiento en etapas secuenciales.
    """
    # Etapa 1: Obtener perfil
    perfil = self.perfil_repo.obtener_por_usuario_id(practicante_id)
    if not perfil or not perfil.habilidades:
        return []

    # Etapa 2: Filtrar convocatorias activas
    convocatorias = self.convocatoria_repo.listar_activas()
    if not convocatorias:
        return []

    # Etapa 3: Calcular score (Jaccard)
    def calcular_match(conv):
        habilidades_conv = conv.habilidades_requeridas or []
        interseccion = set(perfil.habilidades) & set(habilidades_conv)
        union = set(perfil.habilidades) | set(habilidades_conv)
        score = len(interseccion) / len(union) if union else 0
        return (conv, score, list(interseccion))

    # Etapa 4: Generar y ordenar
    matches = [calcular_match(c) for c in convocatorias]
    matches = [m for m in matches if m[1] > 0]
    matches.sort(key=lambda x: x[1], reverse=True)

    # Etapa 5: Formatear resultado
    return [{
        "convocatoria": conv.to_dict(),
        "score_match": score,
        "habilidades_match": habilidades_match
    } for conv, score, habilidades_match in matches[:limit]]
```

### 3. Estilo Things/Objects (Objetos con comportamiento)

**Definición:** Los objetos encapsulan estado y comportamiento.

**Ubicación:** `domain/perfil/practicante.py`

```python
@dataclass
class Practicante:
    """
    ESTILO THINGS/OBJECTS: Encapsula estado y comportamiento.
    """
    id: Optional[int]
    usuario_id: int
    habilidades: List[str]
    formacion_educativa: List[str]
    dni: str
    carnet_universitario: str

    def agregar_habilidad(self, habilidad: str) -> bool:
        if habilidad not in self.habilidades:
            self.habilidades.append(habilidad)
            return True
        return False

    def calcular_match(self, habilidades_convocatoria: List[str]) -> float:
        if not self.habilidades or not habilidades_convocatoria:
            return 0.0
        interseccion = set(self.habilidades) & set(habilidades_convocatoria)
        union = set(self.habilidades) | set(habilidades_convocatoria)
        return len(interseccion) / len(union) if union else 0.0

    def esta_completo(self) -> bool:
        return bool(self.habilidades) and bool(self.dni)
```

### 4. Estilo Error/Exception Handling (Manejo estructurado de errores)

**Definición:** Cada tipo de error se captura con su excepción específica y se devuelve una respuesta HTTP apropiada.

**Ubicación:** `presentation/postulacion_controller.py`

```python
@postulacion_blueprint.route('', methods=['POST'])
def crear_postulacion():
    try:
        usuario_id = session.get('usuario_id')
        if not usuario_id:
            return jsonify({"error": "No autenticado"}), 401

        if session.get('usuario_rol') != 'practicante':
            return jsonify({"error": "Solo practicantes pueden postularse"}), 403

        datos = request.get_json()
        if not datos or 'convocatoria_id' not in datos:
            return jsonify({"error": "Campo requerido"}), 400

        resultado = postulacion_service.postularse(
            practicante_id=usuario_id,
            convocatoria_id=datos['convocatoria_id']
        )

        return jsonify(resultado), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}")
        return jsonify({"error": "Error interno"}), 500
```

## ✅ Resumen de Estilos Aplicados

| Estilo | Ubicación | Beneficio |
|--------|-----------|-----------|
| Cookbook | `postulacion_application_service.py` | Código fácil de leer y seguir |
| Pipeline | `matching_application_service.py` | Procesamiento modular y extensible |
| Things/Objects | `domain/perfil/practicante.py` | Alta cohesión y encapsulamiento |
| Error Handling | `postulacion_controller.py` | Sistema robusto y depurable |

📅 Fecha: Julio 2026
