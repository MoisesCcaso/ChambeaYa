class RUC:
    def __init__(self, number=None):
        self.number = number

    def is_valid(self):
        """
        Validates the RUC number (format + check digit,
        SUNAT modulo 11 algorithm).
        """
        valid_prefixes = ("10", "15", "17", "20")
        factors = (5, 4, 3, 2, 7, 6, 5, 4, 3, 2)
        number = self.number

        if not number or not isinstance(number, str) or not number.isdigit() or len(number) != 11:
            return False

        if number[:2] not in valid_prefixes:
            return False

        digits = [int(d) for d in number[:10]]
        total = sum(d * f for d, f in zip(digits, factors))
        remainder = total % 11
        result = 11 - remainder

        if result == 10:
            check_digit = 0
        elif result == 11:
            check_digit = 1
        else:
            check_digit = result

        return check_digit == int(number[10])