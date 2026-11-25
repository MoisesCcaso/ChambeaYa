from matching.domain.skills_matching_strategy import SkillsMatchingStrategy


class Suggestion:
    def __init__(self, id=None, intern_id=None, job_posting_id=None,
                 match_score=None, matched_skills=None, job_posting=None,
                 matching_strategy=None):
        self.id = id
        self.intern_id = intern_id
        self.job_posting_id = job_posting_id
        self.match_score = match_score or 0.0
        self.matched_skills = matched_skills or []
        self.job_posting = job_posting
        self.matching_strategy = (
            matching_strategy
            if matching_strategy is not None
            else SkillsMatchingStrategy()
        )

    @property
    def compatibility_score(self):
        return self.match_score

    @property
    def suggestion(self):
        return self

    def is_compatible(self, threshold=50.0):
        return self.match_score >= threshold

    def calculate_compatibility(self, intern_skills, required_skills):
        self.match_score, self.matched_skills = (
            self.matching_strategy.calculate_compatibility(
                intern_skills, required_skills
            )
        )
        return self.match_score
