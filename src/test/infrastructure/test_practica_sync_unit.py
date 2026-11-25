"""Pruebas unitarias aisladas para SqlAlchemyPracticaRepository._sync_collection (Issue #181)."""

from datetime import datetime, timezone
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

from domain.practica_evaluacion.entregable import Entregable
from domain.practica_evaluacion.evaluacion import Evaluacion
from domain.practica_evaluacion.practica import Practica


def _ensure_orm_stubs():
    """Provee dobles ligeros de los modelos ORM cuando SQLAlchemy no está instalado en el entorno."""
    try:
        import shared.database  # noqa: F401
        return
    except ModuleNotFoundError:
        pass

    class DummyEntregableModel:
        def __init__(self, id=None, archivo=None, fecha_subida=None):
            self.id = id
            self.archivo = archivo
            self.fecha_subida = fecha_subida

    class DummyEvaluacionModel:
        def __init__(self, id=None, puntaje=None, fecha_evaluacion=None):
            self.id = id
            self.puntaje = puntaje
            self.fecha_evaluacion = fecha_evaluacion

    class DummyPracticaModel:
        query = MagicMock()

        def __init__(self, id=None, postulacion_id=None, intern_id=None, status=None):
            self.id = id
            self.postulacion_id = postulacion_id
            self.intern_id = intern_id
            self.status = status
            self.entregables = []
            self.evaluaciones = []

    db_mod = ModuleType("shared.database")
    db_mod.db = SimpleNamespace(session=MagicMock())

    practica_mod = ModuleType("frameworks.sqlalchemy_orm.models.practica_model")
    practica_mod.PracticaModel = DummyPracticaModel

    entregable_mod = ModuleType("frameworks.sqlalchemy_orm.models.entregable_model")
    entregable_mod.EntregableModel = DummyEntregableModel

    evaluacion_mod = ModuleType("frameworks.sqlalchemy_orm.models.evaluacion_model")
    evaluacion_mod.EvaluacionModel = DummyEvaluacionModel

    sys.modules.setdefault("frameworks.sqlalchemy_orm", ModuleType("frameworks.sqlalchemy_orm"))
    sys.modules.setdefault("frameworks.sqlalchemy_orm.models", ModuleType("frameworks.sqlalchemy_orm.models"))
    sys.modules["shared.database"] = db_mod
    sys.modules["frameworks.sqlalchemy_orm.models.practica_model"] = practica_mod
    sys.modules["frameworks.sqlalchemy_orm.models.entregable_model"] = entregable_mod
    sys.modules["frameworks.sqlalchemy_orm.models.evaluacion_model"] = evaluacion_mod


_ensure_orm_stubs()
from infrastructure.sqlalchemy_practica_repository import SqlAlchemyPracticaRepository  # noqa: E402


class TestPracticaRepositorySyncCollection(unittest.TestCase):
    """Verifica el método extraído _sync_collection (Extract Method)."""

    def setUp(self):
        self.repo = SqlAlchemyPracticaRepository()

    def test_sync_collection_elimina_huerfanos_y_agrega_nuevos_sin_duplicar(self):
        existente_conservado = SimpleNamespace(id=1, value="conservado")
        existente_huerfano = SimpleNamespace(id=2, value="eliminar")
        model_collection = [existente_conservado, existente_huerfano]

        domain_collection = [
            SimpleNamespace(id=1, value="conservado"),
            SimpleNamespace(id=None, value="nuevo"),
        ]

        self.repo._sync_collection(
            model_collection,
            domain_collection,
            lambda item: SimpleNamespace(id=None, value=item.value),
        )

        self.assertEqual(len(model_collection), 2)
        self.assertIs(model_collection[0], existente_conservado)
        self.assertEqual(model_collection[1].value, "nuevo")

    def test_save_sincroniza_entregables_y_evaluaciones_mediante_sync_collection(self):
        from shared.database import db
        from frameworks.sqlalchemy_orm.models.entregable_model import EntregableModel
        from frameworks.sqlalchemy_orm.models.evaluacion_model import EvaluacionModel

        fecha = datetime(2026, 11, 20, 10, 0, tzinfo=timezone.utc)
        entregable_keep = EntregableModel(archivo="keep.pdf", fecha_subida=fecha)
        entregable_keep.id = 10
        entregable_drop = EntregableModel(archivo="drop.pdf", fecha_subida=fecha)
        entregable_drop.id = 11

        eval_keep = EvaluacionModel(puntaje=80, fecha_evaluacion=fecha)
        eval_keep.id = 20
        eval_drop = EvaluacionModel(puntaje=50, fecha_evaluacion=fecha)
        eval_drop.id = 21

        model = SimpleNamespace(
            id=5,
            postulacion_id=1,
            intern_id=2,
            status=Practica.ESTADO_EN_CURSO,
            entregables=[entregable_keep, entregable_drop],
            evaluaciones=[eval_keep, eval_drop],
        )

        practica = Practica(
            id=5,
            postulacion_id=1,
            intern_id=2,
            status=Practica.ESTADO_FINALIZADA,
            entregables=[
                Entregable(id=10, practica_id=5, archivo="keep.pdf", fecha_subida=fecha),
                Entregable(id=None, practica_id=5, archivo="new.pdf", fecha_subida=fecha),
            ],
            evaluaciones=[
                Evaluacion(id=20, practica_id=5, puntaje=80, fecha_evaluacion=fecha),
                Evaluacion(id=None, practica_id=5, puntaje=95, fecha_evaluacion=fecha),
            ],
        )

        with (
            patch.object(db.session, "get", return_value=model),
            patch.object(db.session, "commit"),
        ):
            result = self.repo.save(practica)

        self.assertEqual([e.archivo for e in model.entregables], ["keep.pdf", "new.pdf"])
        self.assertEqual([ev.puntaje for ev in model.evaluaciones], [80, 95])
        self.assertEqual(result.status, Practica.ESTADO_FINALIZADA)


if __name__ == "__main__":
    unittest.main()
