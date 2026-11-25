"""I-04 - Unit tests for the profiles domain rules.

Code under test:
- src/main/profiles/domain/intern.py
- src/main/profiles/domain/company.py
- src/main/profiles/domain/ruc.py
- src/main/profiles/domain/full_name.py
"""

import unittest

from profiles.domain.company import Company
from profiles.domain.full_name import FullName
from profiles.domain.intern import Intern
from profiles.domain.ruc import RUC


class InternTest(unittest.TestCase):
    def test_verify_identity_accepts_dni_of_exactly_8_digits(self):
        intern = Intern(dni="71234567")

        result = intern.verify_identity()

        self.assertIs(result, intern)
        self.assertTrue(intern.identity_verified)

    def test_verify_identity_rejects_dni_with_wrong_length_or_non_numeric(self):
        dnis_invalidos = ("1234567", "123456789", "1234567A", "abcdefgh")

        for dni in dnis_invalidos:
            with self.subTest(dni=dni):
                intern = Intern(dni=dni)
                with self.assertRaisesRegex(
                    ValueError, "El DNI debe contener exactamente 8 dígitos"
                ):
                    intern.verify_identity()
                self.assertFalse(intern.identity_verified)

    def test_verify_identity_accepts_trimmed_card_of_at_least_4_characters(self):
        intern = Intern(university_id_card="  A123  ")

        result = intern.verify_identity()

        self.assertIs(result, intern)
        self.assertTrue(intern.identity_verified)

    def test_verify_identity_rejects_trimmed_card_shorter_than_4_characters(self):
        invalid_cards = ("123", "  AB1  ", "   x   ")

        for card in invalid_cards:
            with self.subTest(card=card):
                intern = Intern(university_id_card=card)
                with self.assertRaisesRegex(
                    ValueError, "El carnet universitario no es válido"
                ):
                    intern.verify_identity()
                self.assertFalse(intern.identity_verified)

    def test_verify_identity_rejects_missing_dni_and_card(self):
        intern = Intern()

        with self.assertRaisesRegex(
            ValueError, "Se requiere DNI o carnet universitario"
        ):
            intern.verify_identity()

    def test_calculate_score_adds_skills_education_identity_and_respects_caps(self):
        # No skills, education or verified identity -> 0.0
        vacio = Intern()
        self.assertEqual(vacio.calculate_score(), 0.0)
        self.assertEqual(vacio.reputation_score, 0.0)

        # 3 skills (15) + 2 education entries (10) + verified identity (25) = 50.0
        parcial = Intern(
            skills=["Python", "SQL", "Git"],
            education=["UNSA", "Inglés"],
            identity_verified=True,
        )
        self.assertEqual(parcial.calculate_score(), 50.0)
        self.assertEqual(parcial.reputation_score, 50.0)

        # Skills cap: up to 10 (12 skills -> counts 10 * 5 = 50.0)
        skills_cap = Intern(
            skills=[f"Habilidad {i}" for i in range(12)],
            identity_verified=False,
        )
        self.assertEqual(skills_cap.calculate_score(), 50.0)

        # Education cap: up to 5 (7 entries -> counts 5 * 5 = 25.0)
        education_cap = Intern(
            education=[f"Formacion {i}" for i in range(7)],
            identity_verified=False,
        )
        self.assertEqual(education_cap.calculate_score(), 25.0)

        # Total cap 100: 10 skills (50) + 5 education entries (25) + verified (25) = 100.0
        maximo = Intern(
            skills=[f"Habilidad {i}" for i in range(15)],
            education=[f"Formacion {i}" for i in range(8)],
            identity_verified=True,
        )
        self.assertEqual(maximo.calculate_score(), 100.0)
        self.assertEqual(maximo.reputation_score, 100.0)

    def test_update_details_changes_only_provided_fields(self):
        intern = Intern(
            first_names="Juan",
            last_names="Pérez",
            dni="70000001",
            university_id_card="20201234",
        )

        result = intern.update_details(
            first_names="Carlos",
            last_names="Gómez",
            dni="70000002",
            university_id_card="20209999",
        )

        self.assertIs(result, intern)
        self.assertEqual(intern.first_names, "Carlos")
        self.assertEqual(intern.last_names, "Gómez")
        self.assertEqual(intern.dni, "70000002")
        self.assertEqual(intern.university_id_card, "20209999")

        intern.update_details()
        self.assertEqual(intern.first_names, "Carlos")

    def test_names_are_stored_in_the_full_name_value_object(self):
        intern = Intern(first_names="Ana", last_names="Torres")
        self.assertIsInstance(intern.full_name, FullName)
        self.assertEqual(str(intern.full_name), "Ana Torres")

    def test_update_details_normalizes_and_keeps_the_omitted_field(self):
        intern = Intern(first_names="Ana", last_names="Torres")
        intern.update_details(first_names="  Lucía  ")
        self.assertEqual(intern.first_names, "Lucía")
        self.assertEqual(intern.last_names, "Torres")

    def test_update_details_rejects_blank_names(self):
        intern = Intern(first_names="Ana", last_names="Torres")
        for first_names, last_names in (("   ", "Torres"), ("Ana", ""), ("", "")):
            with self.subTest(first_names=first_names, last_names=last_names):
                with self.assertRaisesRegex(ValueError, "Nombres y apellidos son obligatorios"):
                    intern.update_details(first_names=first_names, last_names=last_names)
        self.assertEqual(str(intern.full_name), "Ana Torres")

    def test_new_intern_without_names_is_valid_until_profile_is_completed(self):
        intern = Intern(user_id=1)
        self.assertIsNone(intern.first_names)
        self.assertIsNone(intern.last_names)

    def test_add_and_replace_skills_and_education_normalizes_and_avoids_duplicates(self):
        intern = Intern()

        intern.add_skill("  Python  ")
        intern.add_skill("Python")
        intern.add_skill("   ")
        intern.add_skill(None)
        self.assertEqual(intern.skills, ["Python"])

        intern.add_education("  Ingeniería de Software  ")
        intern.add_education("Ingeniería de Software")
        intern.add_education("")
        intern.add_education(None)
        self.assertEqual(intern.education, ["Ingeniería de Software"])

        intern.replace_skills([" Flask ", "SQL", "Flask"])
        self.assertEqual(intern.skills, ["Flask", "SQL"])

        intern.replace_education([" UNSA ", "Certificación AWS", "UNSA"])
        self.assertEqual(intern.education, ["UNSA", "Certificación AWS"])

    def test_replace_skills_and_education_rejects_non_list_values(self):
        intern = Intern()

        with self.assertRaisesRegex(ValueError, "Las habilidades deben ser una lista"):
            intern.replace_skills("Python")

        with self.assertRaisesRegex(
            ValueError, "La formación educativa debe ser una lista"
        ):
            intern.replace_education(("UNSA",))


class RucAndCompanyTest(unittest.TestCase):
    def test_ruc_valid_by_prefix_and_check_digit(self):
        # Covers prefixes 10, 15, 17, 20 and the modulo 11 branches (10->0, 11->1 and the normal remainder)
        rucs_validos = (
            "20100070970",  # 11 - remainder == 10 -> digit 0
            "20100090971",  # 11 - remainder == 11 -> digit 1
            "20100070988",  # 11 - remainder == 8  -> digit 8
            "10100070974",  # valid prefix 10
            "15100070976",  # valid prefix 15
            "17100070979",  # valid prefix 17
        )

        for number in rucs_validos:
            with self.subTest(ruc=number):
                self.assertTrue(RUC(number).is_valid())

    def test_ruc_invalid_by_format_prefix_or_check_digit(self):
        rucs_invalidos = (
            None,
            "",
            12345678901,
            "2010007097",    # 10 digits
            "201000709701",  # 12 digits
            "2010007097A",   # not numeric
            "11100070971",   # invalid prefix 11
            "99100070970",   # invalid prefix 99
            "20100070975",   # wrong check digit
            "10100070970",   # wrong check digit
        )

        for number in rucs_invalidos:
            with self.subTest(ruc=number):
                self.assertFalse(RUC(number).is_valid())

    def test_company_verify_ruc_updates_verified_flag(self):
        valid_company = Company(
            legal_name="Tech SAC",
            ruc=RUC("20100070970"),
        )
        self.assertTrue(valid_company.verify_ruc())
        self.assertTrue(valid_company.verified)

        company_with_invalid_ruc = Company(
            legal_name="Tech SAC",
            ruc=RUC("20100070975"),
            verified=True,
        )
        self.assertFalse(company_with_invalid_ruc.verify_ruc())
        self.assertFalse(company_with_invalid_ruc.verified)

        company_without_ruc = Company(legal_name="Sin RUC", ruc=None, verified=True)
        self.assertFalse(company_without_ruc.verify_ruc())
        self.assertFalse(company_without_ruc.verified)


class FullNameTest(unittest.TestCase):
    def test_validate_trims_both_fields_and_formats_the_string(self):
        name = FullName(first_names="  Ana María  ", last_names="  Torres Díaz  ")

        result = name.validate()

        self.assertIs(result, name)
        self.assertEqual(name.first_names, "Ana María")
        self.assertEqual(name.last_names, "Torres Díaz")
        self.assertEqual(str(name), "Ana María Torres Díaz")

    def test_validate_rejects_missing_or_blank_first_or_last_name(self):
        casos_invalidos = (
            (None, "Torres"),
            ("", "Torres"),
            ("   ", "Torres"),
            ("Ana", None),
            ("Ana", ""),
            ("Ana", "   "),
            (None, None),
        )

        for first_names, last_names in casos_invalidos:
            with self.subTest(first_names=first_names, last_names=last_names):
                name = FullName(first_names=first_names, last_names=last_names)
                with self.assertRaisesRegex(
                    ValueError, "Nombres y apellidos son obligatorios"
                ):
                    name.validate()


if __name__ == "__main__":
    unittest.main()
