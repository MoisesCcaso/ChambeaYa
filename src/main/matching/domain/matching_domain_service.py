from matching.domain.skills_matching_strategy import SkillsMatchingStrategy
from matching.domain.suggestion import Suggestion
from recruitment.api import JobPosting


class MatchingDomainService:
    def __init__(self, matching_strategy=None):
        self.matching_strategy = (
            matching_strategy
            if matching_strategy is not None
            else SkillsMatchingStrategy()
        )

    def calculate_match(self, intern, job_posting):
        if intern is None or job_posting is None:
            return None

        suggestion = Suggestion(
            intern_id=intern.id,
            job_posting_id=job_posting.id,
            job_posting=job_posting,
            matching_strategy=self.matching_strategy,
        )
        suggestion.calculate_compatibility(
            intern.skills,
            job_posting.required_skills,
        )

        return suggestion

    def filter_job_postings(self, intern, job_postings, threshold=50.0):
        results = []
        for job_posting in job_postings:
            if job_posting.status != JobPosting.STATUS_PUBLISHED:
                continue
            suggestion = self.calculate_match(intern, job_posting)
            if suggestion is not None and suggestion.is_compatible(threshold):
                results.append(suggestion)

        return sorted(results, key=lambda r: r.match_score, reverse=True)
