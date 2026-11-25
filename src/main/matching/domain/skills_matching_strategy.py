from matching.domain.matching_strategy import MatchingStrategy


class SkillsMatchingStrategy(MatchingStrategy):
    """Compatibility is the percentage of required skills the intern has."""

    def calculate_compatibility(self, intern_skills, required_skills):
        intern_skills = self._normalize_skills(intern_skills)
        required_skills = self._normalize_skills(required_skills)

        if not required_skills:
            return 0.0, []

        matched = intern_skills & required_skills
        score = len(matched) / len(required_skills) * 100
        return score, list(matched)

    def _normalize_skills(self, skills):
        return {
            str(skill).strip().casefold()
            for skill in skills or []
            if str(skill).strip()
        }
