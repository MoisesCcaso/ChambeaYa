"""I-13 - Isolated tests for the matching application service with doubles."""

from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import Mock, call

from matching.application.matching_application_service import MatchingApplicationService
from recruitment.domain.i_job_posting_repository import IJobPostingRepository
from matching.domain.i_suggestion_repository import ISuggestionRepository
from profiles.domain.i_intern_repository import IInternRepository


class TestMatchingApplicationService(TestCase):
    """Checks results and interactions without touching real infrastructure."""

    def setUp(self):
        self.profile_repository = Mock(spec=IInternRepository)
        self.job_posting_repository = Mock(spec=IJobPostingRepository)
        self.suggestion_repository = Mock(spec=ISuggestionRepository)
        self.matching_domain_service = Mock()

        self.intern = SimpleNamespace(id=17, skills=["python", "sql"])
        self.job_postings = [SimpleNamespace(id=31), SimpleNamespace(id=32)]
        self.result_1 = SimpleNamespace(
            job_posting_id=31,
            suggestion=SimpleNamespace(intern_id=17, job_posting_id=31),
        )
        self.result_2 = SimpleNamespace(
            job_posting_id=32,
            suggestion=SimpleNamespace(intern_id=17, job_posting_id=32),
        )
        self.results = [self.result_1, self.result_2]

        self.profile_repository.find_intern_by_user_id.return_value = self.intern
        self.job_posting_repository.find_all.return_value = self.job_postings
        self.matching_domain_service.filter_job_postings.return_value = self.results

        self.service = MatchingApplicationService(
            suggestion_repository=self.suggestion_repository,
            profile_repository=self.profile_repository,
            job_posting_repository=self.job_posting_repository,
            matching_domain_service=self.matching_domain_service,
        )

    def test_suggest_job_postings_returns_results_and_queries_dependencies(self):
        results = self.service.suggest_job_postings(user_id=5, threshold=65.0)

        self.assertIs(self.results, results)
        self.profile_repository.find_intern_by_user_id.assert_called_once_with(5)
        self.job_posting_repository.find_all.assert_called_once_with()
        self.matching_domain_service.filter_job_postings.assert_called_once_with(
            self.intern, self.job_postings, 65.0
        )
        self.suggestion_repository.save.assert_not_called()

    def test_calculate_for_intern_saves_each_suggestion_and_returns_results(self):
        results = self.service.calculate_for_intern(user_id=5)

        self.assertIs(self.results, results)
        self.profile_repository.find_intern_by_user_id.assert_called_once_with(5)
        self.job_posting_repository.find_all.assert_called_once_with()
        self.matching_domain_service.filter_job_postings.assert_called_once_with(
            self.intern, self.job_postings
        )
        self.suggestion_repository.save.assert_has_calls(
            [call(self.result_1.suggestion), call(self.result_2.suggestion)]
        )
        self.assertEqual(2, self.suggestion_repository.save.call_count)

    def test_calculate_for_intern_without_results_saves_nothing(self):
        self.matching_domain_service.filter_job_postings.return_value = []

        results = self.service.calculate_for_intern(user_id=5)

        self.assertEqual([], results)
        self.suggestion_repository.save.assert_not_called()

    def test_raises_if_the_intern_is_not_found(self):
        self.profile_repository.find_intern_by_user_id.return_value = None

        with self.assertRaisesRegex(ValueError, "Practicante no encontrado"):
            self.service.suggest_job_postings(user_id=404)

        self.profile_repository.find_intern_by_user_id.assert_called_once_with(404)
        self.job_posting_repository.find_all.assert_not_called()
        self.matching_domain_service.filter_job_postings.assert_not_called()

    def test_requires_the_three_repositories(self):
        service = MatchingApplicationService(
            profile_repository=self.profile_repository,
            job_posting_repository=self.job_posting_repository,
            matching_domain_service=self.matching_domain_service,
        )

        with self.assertRaisesRegex(RuntimeError, "suggestion repository"):
            service.suggest_job_postings(user_id=5)

        self.profile_repository.find_intern_by_user_id.assert_not_called()


if __name__ == "__main__":
    import unittest

    unittest.main()
