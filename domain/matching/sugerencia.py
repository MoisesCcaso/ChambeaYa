class Sugerencia:
    def __init__(self, id=None, practicante_id=None, convocatoria_id=None,
                 puntaje_match=None, habilidades_coincidentes=None):
        self.id = id
        self.practicante_id = practicante_id
        self.convocatoria_id = convocatoria_id
        self.puntaje_match = puntaje_match or 0.0
        self.habilidades_coincidentes = habilidades_coincidentes or []

    def calcular_compatibilidad(self, habilidades_practicante, habilidades_requeridas):
        if not habilidades_requeridas:
            self.puntaje_match = 0.0
            return self.puntaje_match

        set_practicante = {
            str(h).strip().casefold()
            for h in habilidades_practicante or []
            if str(h).strip()
        }
        set_requeridas = {
            str(h).strip().casefold()
            for h in habilidades_requeridas or []
            if str(h).strip()
        }
        if not set_requeridas:
            self.puntaje_match = 0.0
            self.habilidades_coincidentes = []
            return self.puntaje_match
        coincidentes = set_practicante & set_requeridas

        self.habilidades_coincidentes = list(coincidentes)
        self.puntaje_match = len(coincidentes) / len(set_requeridas) * 100
        return self.puntaje_match
