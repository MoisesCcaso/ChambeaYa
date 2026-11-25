"""Unit tests for the internships, deliverables and evaluations domain."""

import unittest
from datetime import datetime, timedelta, timezone

from internships.domain.deliverable import Deliverable
from internships.domain.evaluation import Evaluation
from internships.domain.internship import Internship


class TestInternshipStart(unittest.TestCase):
    def test_starts_internship_in_progress_and_empty(self):
        internship = Internship.start(11, 22)
        self.assertEqual(internship.job_application_id, 11)
        self.assertEqual(internship.intern_id, 22)
        self.assertEqual(internship.status, Internship.STATUS_IN_PROGRESS)
        self.assertEqual(internship.deliverables, [])
        self.assertEqual(internship.evaluations, [])

    def test_rejects_missing_required_data(self):
        for job_application_id, intern_id in ((None, 22), (11, None), (None, None)):
            with self.subTest(job_application_id=job_application_id, intern_id=intern_id):
                with self.assertRaisesRegex(ValueError, "postulación y practicante"):
                    Internship.start(job_application_id, intern_id)


class TestDeliverable(unittest.TestCase):
    def test_create_normalizes_file_and_records_date(self):
        deliverable = Deliverable.create(7, "  informe-final.pdf  ")
        self.assertEqual(deliverable.internship_id, 7)
        self.assertEqual(deliverable.file_name, "informe-final.pdf")
        self.assertEqual(deliverable.uploaded_at.tzinfo, timezone.utc)

    def test_rejects_empty_file(self):
        for file_name in (None, "", "   "):
            with self.subTest(file_name=file_name):
                with self.assertRaisesRegex(ValueError, "Debe adjuntarse un archivo"):
                    Deliverable.create(7, file_name)


class TestEvaluation(unittest.TestCase):
    def test_accepts_valid_scores_and_converts_them_to_float(self):
        for score, expected in ((0, 0.0), ("59.5", 59.5), (60, 60.0), (100, 100.0)):
            with self.subTest(score=score):
                evaluation = Evaluation.create(7, score)
                self.assertEqual(evaluation.internship_id, 7)
                self.assertEqual(evaluation.score, expected)
                self.assertEqual(evaluation.evaluated_at.tzinfo, timezone.utc)

    def test_rejects_out_of_range_scores(self):
        for score in (-0.01, 100.01):
            with self.subTest(score=score):
                with self.assertRaisesRegex(ValueError, "entre 0 y 100"):
                    Evaluation.create(7, score)

    def test_rejects_missing_score(self):
        with self.assertRaisesRegex(ValueError, "Debe indicarse un puntaje"):
            Evaluation.create(7, None)

    def test_rejects_non_numeric_score(self):
        for score in ("no-numérico", object()):
            with self.subTest(score=score):
                with self.assertRaisesRegex(ValueError, "debe ser numérico"):
                    Evaluation.create(7, score)

    def test_passes_from_sixty_points(self):
        for score, expected in ((None, False), (59.99, False), (60, True), (100, True)):
            with self.subTest(score=score):
                self.assertIs(Evaluation(score=score).is_approved(), expected)


class TestInternship(unittest.TestCase):
    def test_upload_deliverable_adds_it_to_the_internship(self):
        internship = Internship(id=7)
        deliverable = internship.upload_deliverable("informe.pdf")
        self.assertEqual(deliverable.internship_id, 7)
        self.assertEqual(internship.deliverables, [deliverable])

    def test_register_evaluation_adds_it_to_the_internship(self):
        internship = Internship(id=7)
        evaluation = internship.register_evaluation(85)
        self.assertEqual(evaluation.internship_id, 7)
        self.assertEqual(evaluation.score, 85.0)
        self.assertEqual(internship.evaluations, [evaluation])

    def test_cannot_finish_without_deliverables(self):
        internship = Internship(id=7)
        internship.register_evaluation(80)
        with self.assertRaisesRegex(ValueError, "sin entregables registrados"):
            internship.finish()
        self.assertEqual(internship.status, Internship.STATUS_IN_PROGRESS)

    def test_cannot_finish_without_an_approved_evaluation(self):
        internship = Internship(id=7)
        internship.upload_deliverable("informe.pdf")
        internship.register_evaluation(59)
        with self.assertRaisesRegex(ValueError, "sin una evaluación aprobada"):
            internship.finish()
        self.assertEqual(internship.status, Internship.STATUS_IN_PROGRESS)

    def test_finish_changes_status_when_rules_are_met(self):
        internship = Internship(id=7)
        internship.upload_deliverable("informe.pdf")
        internship.register_evaluation(60)
        self.assertIs(internship.finish(), internship)
        self.assertEqual(internship.status, Internship.STATUS_FINISHED)

    def test_cannot_finish_twice(self):
        internship = Internship(
            status=Internship.STATUS_FINISHED,
            deliverables=[Deliverable(file_name="informe.pdf")],
            evaluations=[Evaluation(score=90)],
        )
        with self.assertRaisesRegex(ValueError, "ya está finalizada"):
            internship.finish()

    def test_finished_does_not_allow_new_deliverables_or_evaluations(self):
        internship = Internship(status=Internship.STATUS_FINISHED)
        with self.assertRaisesRegex(ValueError, "entregables.*finalizada"):
            internship.upload_deliverable("otro-informe.pdf")
        with self.assertRaisesRegex(ValueError, "evaluaciones.*finalizada"):
            internship.register_evaluation(90)
        self.assertEqual(internship.deliverables, [])
        self.assertEqual(internship.evaluations, [])

    def test_remove_existing_deliverable_in_progress(self):
        deliverable = Deliverable(id=3, file_name="informe.pdf")
        internship = Internship(deliverables=[deliverable])
        self.assertIs(internship.remove_deliverable(3), deliverable)
        self.assertEqual(internship.deliverables, [])

    def test_remove_existing_evaluation_in_progress(self):
        evaluation = Evaluation(id=4, score=80)
        internship = Internship(evaluations=[evaluation])
        self.assertIs(internship.remove_evaluation(4), evaluation)
        self.assertEqual(internship.evaluations, [])

    def test_remove_rejects_a_missing_record(self):
        cases = (
            ("remove_deliverable", "Entregable no encontrado"),
            ("remove_evaluation", "Evaluación no encontrada"),
        )
        for method_name, text in cases:
            with self.subTest(method_name=method_name):
                with self.assertRaisesRegex(ValueError, text):
                    getattr(Internship(), method_name)(999)

    def test_finished_does_not_allow_removals(self):
        for method_name in ("remove_deliverable", "remove_evaluation"):
            with self.subTest(method_name=method_name):
                internship = Internship(status=Internship.STATUS_FINISHED)
                with self.assertRaisesRegex(ValueError, "práctica finalizada"):
                    getattr(internship, method_name)(1)

    def test_histories_are_sorted_without_altering_the_collections(self):
        now_value = datetime.now(timezone.utc)
        recent_deliverable = Deliverable(id=1, uploaded_at=now_value)
        older_deliverable = Deliverable(id=2, uploaded_at=now_value - timedelta(days=1))
        recent_evaluation = Evaluation(id=1, evaluated_at=now_value)
        older_evaluation = Evaluation(id=2, evaluated_at=now_value - timedelta(hours=1))
        internship = Internship(
            deliverables=[recent_deliverable, older_deliverable],
            evaluations=[recent_evaluation, older_evaluation],
        )

        self.assertEqual(
            internship.get_deliverables_history(),
            [older_deliverable, recent_deliverable],
        )
        self.assertEqual(
            internship.get_evaluations_history(),
            [older_evaluation, recent_evaluation],
        )
        self.assertEqual(internship.deliverables, [recent_deliverable, older_deliverable])
        self.assertEqual(internship.evaluations, [recent_evaluation, older_evaluation])


if __name__ == "__main__":
    unittest.main()
