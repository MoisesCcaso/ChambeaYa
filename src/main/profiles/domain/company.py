class Company:
    def __init__(
        self,
        id=None,
        user_id=None,
        legal_name=None,
        ruc=None,
        verified=False,
    ):
        self.id = id
        self.user_id = user_id
        self.legal_name = legal_name
        self.ruc = ruc
        self.verified = verified

    def verify_ruc(self):
        """
        Delegates validation to the RUC value object (self.ruc)
        and updates self.verified.
        """
        self.verified = bool(self.ruc) and self.ruc.is_valid()
        return self.verified
