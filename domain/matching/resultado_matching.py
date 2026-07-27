# domain/matching/resultado_matching.py
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class ResultadoMatching:
    """Resultado del proceso de matching entre un practicante y convocatorias."""
    practicante_id: int
    sugerencias: List[Dict[str, Any]]
    total_sugerencias: int
    mejores_coincidencias: List[Dict[str, Any]]

    def filtrar_por_umbral(self, umbral: float = 0.3) -> 'ResultadoMatching':
        """Filtra sugerencias que superan el umbral."""
        filtradas = [s for s in self.sugerencias if s.get('score_match', 0) >= umbral]
        return ResultadoMatching(
            practicante_id=self.practicante_id,
            sugerencias=filtradas,
            total_sugerencias=len(filtradas),
            mejores_coincidencias=filtradas[:5]
        )

    def to_dict(self) -> dict:
        return {
            "practicante_id": self.practicante_id,
            "sugerencias": self.sugerencias,
            "total_sugerencias": self.total_sugerencias,
            "mejores_coincidencias": self.mejores_coincidencias
        }