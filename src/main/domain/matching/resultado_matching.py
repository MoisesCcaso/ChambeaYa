class ResultadoMatching:
    def __init__(self, score_compatibilidad=0.0, practicante_id=None,
                 convocatoria_id=None, sugerencia=None, convocatoria=None):
        self.score_compatibilidad = score_compatibilidad
        self.practicante_id = practicante_id
        self.convocatoria_id = convocatoria_id
        self.sugerencia = sugerencia
        self.convocatoria = convocatoria

    def es_compatible(self, umbral=50.0):
        return self.score_compatibilidad >= umbral
