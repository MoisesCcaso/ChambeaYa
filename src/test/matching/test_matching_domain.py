"""Unit tests for the matching domain (I-11).

Framework: unittest
Coverage: Coverage.py

Covers:
  - Suggestion.calculate_compatibility  (calculation and normalization)
  - Suggestion.is_compatible            (compatibility rule / threshold)
  - MatchingDomainService               (calculate_match and filter_job_postings)
"""

import unittest

from recruitment.domain.job_posting import JobPosting
from matching.domain.matching_domain_service import MatchingDomainService
from matching.domain.suggestion import Suggestion
from profiles.domain.intern import Intern


def make_intern(skills, id=1):
    return Intern(id=id, skills=skills)


def create_job_posting(skills, id=1, status=JobPosting.STATUS_PUBLISHED):
    return JobPosting(id=id, status=status, required_skills=skills)


class SuggestionCalculationTest(unittest.TestCase):
    """Compatibility score calculation."""

    def setUp(self):
        self.suggestion = Suggestion(intern_id=1, job_posting_id=2)

    def test_default_values(self):
        s = Suggestion()
        self.assertIsNone(s.id)
        self.assertEqual(0.0, s.match_score)
        self.assertEqual([], s.matched_skills)

    def test_full_match_gives_100(self):
        score = self.suggestion.calculate_compatibility(
            ["python", "sql"], ["python", "sql"]
        )
        self.assertEqual(100.0, score)
        self.assertEqual(100.0, self.suggestion.match_score)

    def test_partial_match(self):
        score = self.suggestion.calculate_compatibility(
            ["python"], ["python", "sql"]
        )
        self.assertEqual(50.0, score)
        self.assertEqual(["python"], self.suggestion.matched_skills)

    def test_no_matches_gives_zero(self):
        score = self.suggestion.calculate_compatibility(["java"], ["python", "sql"])
        self.assertEqual(0.0, score)
        self.assertEqual([], self.suggestion.matched_skills)

    def test_extra_intern_skills_do_not_penalize(self):
        score = self.suggestion.calculate_compatibility(
            ["python", "sql", "docker", "git"], ["python", "sql"]
        )
        self.assertEqual(100.0, score)

    def test_one_third_ratio(self):
        score = self.suggestion.calculate_compatibility(
            ["python"], ["python", "sql", "git"]
        )
        self.assertAlmostEqual(100 / 3, score)

    def test_empty_required_gives_zero(self):
        self.assertEqual(0.0, self.suggestion.calculate_compatibility(["python"], []))

    def test_required_none_gives_zero(self):
        self.assertEqual(0.0, self.suggestion.calculate_compatibility(["python"], None))

    def test_intern_without_skills_gives_zero(self):
        self.assertEqual(0.0, self.suggestion.calculate_compatibility([], ["python"]))

    def test_intern_none_gives_zero(self):
        self.assertEqual(0.0, self.suggestion.calculate_compatibility(None, ["python"]))

    def test_recalculating_updates_the_score(self):
        self.suggestion.calculate_compatibility(["python"], ["python"])
        self.suggestion.calculate_compatibility(["java"], ["python"])
        self.assertEqual(0.0, self.suggestion.match_score)


class SuggestionNormalizationTest(unittest.TestCase):
    """Skill normalization (case, spaces, empty, duplicates)."""

    def setUp(self):
        self.suggestion = Suggestion()

    def test_ignores_case(self):
        score = self.suggestion.calculate_compatibility(["PYTHON"], ["python"])
        self.assertEqual(100.0, score)

    def test_ignores_surrounding_spaces(self):
        score = self.suggestion.calculate_compatibility(["  python  "], ["python"])
        self.assertEqual(100.0, score)

    def test_uses_casefold(self):
        score = self.suggestion.calculate_compatibility(["STRASSE"], ["straße"])
        self.assertEqual(100.0, score)

    def test_discards_empty_or_blank_skills(self):
        score = self.suggestion.calculate_compatibility(
            ["python", "", "   "], ["python", "", "  "]
        )
        self.assertEqual(100.0, score)

    def test_duplicates_are_counted_once(self):
        score = self.suggestion.calculate_compatibility(
            ["python", "Python", " PYTHON "], ["python", "sql", "SQL"]
        )
        self.assertEqual(50.0, score)
        self.assertEqual(1, len(self.suggestion.matched_skills))

    def test_converts_non_text_values_to_string(self):
        score = self.suggestion.calculate_compatibility([101, "python"], ["101", "python"])
        self.assertEqual(100.0, score)

    def test_blank_only_required_gives_zero_and_clears_matched(self):
        self.suggestion.matched_skills = ["previa"]
        score = self.suggestion.calculate_compatibility(["python"], ["", "   "])
        self.assertEqual(0.0, score)
        self.assertEqual([], self.suggestion.matched_skills)

    def test_matched_skills_are_stored_normalized(self):
        self.suggestion.calculate_compatibility([" Python ", "SQL"], ["python", "Sql"])
        self.assertCountEqual(["python", "sql"], self.suggestion.matched_skills)


class SuggestionCompatibilityTest(unittest.TestCase):
    """Structure and compatibility rule in Suggestion (Move Method / Inline Class)."""

    def test_default_values(self):
        r = Suggestion()
        self.assertEqual(0.0, r.match_score)
        self.assertEqual(0.0, r.compatibility_score)
        self.assertIsNone(r.intern_id)
        self.assertIsNone(r.job_posting_id)
        self.assertIs(r, r.suggestion)
        self.assertIsNone(r.job_posting)

    def test_stores_the_received_values(self):
        posting = JobPosting(id=2)
        r = Suggestion(
            intern_id=1,
            job_posting_id=2,
            match_score=75.0,
            matched_skills=["python"],
            job_posting=posting,
        )
        self.assertEqual(75.0, r.match_score)
        self.assertEqual(75.0, r.compatibility_score)
        self.assertEqual(1, r.intern_id)
        self.assertEqual(2, r.job_posting_id)
        self.assertEqual(["python"], r.matched_skills)
        self.assertIs(posting, r.job_posting)

    def test_is_compatible_above_the_threshold(self):
        self.assertTrue(Suggestion(match_score=80.0).is_compatible())

    def test_is_compatible_at_the_exact_limit(self):
        self.assertTrue(Suggestion(match_score=50.0).is_compatible())

    def test_is_not_compatible_below_the_threshold(self):
        self.assertFalse(Suggestion(match_score=49.99).is_compatible())

    def test_is_compatible_with_custom_threshold(self):
        r = Suggestion(match_score=30.0)
        self.assertFalse(r.is_compatible())
        self.assertTrue(r.is_compatible(threshold=30))
        self.assertTrue(r.is_compatible(threshold=10))


class MatchingDomainServiceCalculateMatchTest(unittest.TestCase):
    """MatchingDomainService.calculate_match."""

    def setUp(self):
        self.service = MatchingDomainService()

    def test_intern_none_returns_none(self):
        self.assertIsNone(self.service.calculate_match(None, create_job_posting(["python"])))

    def test_job_posting_none_returns_none(self):
        self.assertIsNone(self.service.calculate_match(make_intern(["python"]), None))

    def test_both_none_returns_none(self):
        self.assertIsNone(self.service.calculate_match(None, None))

    def test_returns_result_with_ids_and_score(self):
        intern = make_intern(["Python", "SQL"], id=7)
        job_posting = create_job_posting(["python", "sql", "git", "docker"], id=9)

        result = self.service.calculate_match(intern, job_posting)

        self.assertIsInstance(result, Suggestion)
        self.assertEqual(50.0, result.match_score)
        self.assertEqual(50.0, result.compatibility_score)
        self.assertEqual(7, result.intern_id)
        self.assertEqual(9, result.job_posting_id)
        self.assertIs(job_posting, result.job_posting)

    def test_the_associated_suggestion_reflects_the_calculation(self):
        intern = make_intern(["python"], id=3)
        job_posting = create_job_posting(["python", "sql"], id=4)

        result = self.service.calculate_match(intern, job_posting)

        self.assertIsInstance(result, Suggestion)
        self.assertEqual(3, result.intern_id)
        self.assertEqual(4, result.job_posting_id)
        self.assertEqual(50.0, result.match_score)
        self.assertEqual(["python"], result.matched_skills)

    def test_job_posting_without_skills_gives_zero_score(self):
        result = self.service.calculate_match(
            make_intern(["python"]), create_job_posting([])
        )
        self.assertEqual(0.0, result.compatibility_score)

    def test_calculate_match_does_not_filter_by_status(self):
        job_posting = create_job_posting(["python"], status=JobPosting.STATUS_CLOSED)
        result = self.service.calculate_match(make_intern(["python"]), job_posting)
        self.assertEqual(100.0, result.compatibility_score)


class MatchingDomainServiceFilterTest(unittest.TestCase):
    """MatchingDomainService.filter_job_postings."""

    def setUp(self):
        self.service = MatchingDomainService()
        self.intern = make_intern(["python", "sql"], id=1)

    def test_empty_list_returns_empty_list(self):
        self.assertEqual([], self.service.filter_job_postings(self.intern, []))

    def test_excludes_draft_and_closed_job_postings(self):
        job_postings = [
            create_job_posting(["python"], id=1, status=JobPosting.STATUS_DRAFT),
            create_job_posting(["python"], id=2, status=JobPosting.STATUS_CLOSED),
            create_job_posting(["python"], id=3, status=JobPosting.STATUS_PUBLISHED),
        ]
        results = self.service.filter_job_postings(self.intern, job_postings)
        self.assertEqual([3], [r.job_posting_id for r in results])

    def test_excludes_job_postings_without_status(self):
        job_postings = [create_job_posting(["python"], id=1, status=None)]
        self.assertEqual([], self.service.filter_job_postings(self.intern, job_postings))

    def test_excludes_those_below_the_default_threshold(self):
        job_postings = [
            create_job_posting(["python"], id=1),                      # 100
            create_job_posting(["python", "java", "go"], id=2),        # 33.3
        ]
        results = self.service.filter_job_postings(self.intern, job_postings)
        self.assertEqual([1], [r.job_posting_id for r in results])

    def test_includes_those_equal_to_the_threshold(self):
        job_postings = [create_job_posting(["python", "java"], id=1)]  # exactly 50
        results = self.service.filter_job_postings(self.intern, job_postings)
        self.assertEqual(1, len(results))
        self.assertEqual(50.0, results[0].compatibility_score)

    def test_custom_threshold(self):
        job_postings = [
            create_job_posting(["python", "java", "go"], id=1),  # 33.3
            create_job_posting(["python"], id=2),                # 100
        ]
        results = self.service.filter_job_postings(
            self.intern, job_postings, threshold=30.0
        )
        self.assertEqual(2, len(results))

    def test_zero_threshold_includes_published_without_matches(self):
        job_postings = [create_job_posting(["java"], id=1)]
        results = self.service.filter_job_postings(
            self.intern, job_postings, threshold=0.0
        )
        self.assertEqual([1], [r.job_posting_id for r in results])

    def test_sorts_by_descending_score(self):
        job_postings = [
            create_job_posting(["python", "java"], id=1),                  # 50
            create_job_posting(["python", "sql"], id=2),                   # 100
            create_job_posting(["python", "sql", "java", "go"], id=3),     # 50
            create_job_posting(["python", "sql", "java"], id=4),           # 66.6
        ]
        results = self.service.filter_job_postings(self.intern, job_postings)
        scores = [r.compatibility_score for r in results]
        self.assertEqual(sorted(scores, reverse=True), scores)
        self.assertEqual(2, results[0].job_posting_id)
        self.assertEqual(4, results[1].job_posting_id)

    def test_every_result_is_compatible_with_the_threshold(self):
        job_postings = [create_job_posting(["python"], id=i) for i in range(1, 4)]
        for r in self.service.filter_job_postings(self.intern, job_postings, 60.0):
            self.assertTrue(r.is_compatible(60.0))

    def test_intern_none_returns_empty_list(self):
        job_postings = [create_job_posting(["python"], id=1)]
        self.assertEqual([], self.service.filter_job_postings(None, job_postings))

    def test_intern_without_skills_returns_empty_list(self):
        job_postings = [create_job_posting(["python"], id=1)]
        results = self.service.filter_job_postings(make_intern([]), job_postings)
        self.assertEqual([], results)


if __name__ == "__main__":
    unittest.main()