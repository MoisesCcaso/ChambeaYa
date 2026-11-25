class Empresa:
    def __init__(
        self,
        id=None,
        user_id=None,
        razon_social=None,
        ruc=None,
        verificada=False,
    ):
        self.id = id
        self.user_id = user_id
        self.razon_social = razon_social
        self.ruc = ruc
        self.verificada = verificada

    def verificar_ruc(self):
        """
        Delega la validación en el value object RUC (self.ruc)
        y actualiza self.verificada.
        """
        self.verificada = bool(self.ruc) and self.ruc.es_valido()
        return self.verificada
