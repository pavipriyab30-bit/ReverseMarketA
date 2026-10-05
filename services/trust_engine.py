from typing import Any, Dict


class TrustEngine:
    """
    Calculate a normalized trust score for service providers.

    The score combines:
    - Provider rating
    - Number of reviews
    - Completed jobs
    - Response rate
    - Experience
    - Verification status
    """

    RATING_WEIGHT = 30
    REVIEW_WEIGHT = 10
    COMPLETED_JOBS_WEIGHT = 15
    RESPONSE_WEIGHT = 15
    EXPERIENCE_WEIGHT = 10
    VERIFICATION_WEIGHT = 20

    def calculate_score(self, provider) -> float:
        """
        Calculate a provider trust score between 0 and 100.
        """

        rating_score = self._rating_score(provider.rating)

        review_score = self._review_score(
            provider.review_count
        )

        completed_jobs_score = self._completed_jobs_score(
            provider.completed_jobs
        )

        response_score = self._response_score(
            provider.response_rate
        )

        experience_score = self._experience_score(
            provider.experience_years
        )

        verification_score = (
            100.0 if provider.verified else 0.0
        )

        score = (
            rating_score * self.RATING_WEIGHT / 100
            + review_score * self.REVIEW_WEIGHT / 100
            + completed_jobs_score * self.COMPLETED_JOBS_WEIGHT / 100
            + response_score * self.RESPONSE_WEIGHT / 100
            + experience_score * self.EXPERIENCE_WEIGHT / 100
            + verification_score * self.VERIFICATION_WEIGHT / 100
        )

        return round(min(max(score, 0.0), 100.0), 2)

    def get_trust_level(self, score: float) -> str:
        """Convert a numerical trust score into a readable level."""

        if score >= 85:
            return "Excellent"

        if score >= 70:
            return "Good"

        if score >= 50:
            return "Average"

        if score >= 30:
            return "Low"

        return "Poor"

    def get_trust_profile(self, provider) -> Dict[str, Any]:
        """
        Return the complete trust profile for a provider.
        """

        score = self.calculate_score(provider)

        return {
            "score": score,
            "level": self.get_trust_level(score),
            "verified": bool(provider.verified),
            "rating": round(float(provider.rating), 2),
            "review_count": int(provider.review_count),
            "completed_jobs": int(provider.completed_jobs),
            "response_rate": round(
                float(provider.response_rate), 2
            ),
            "experience_years": int(
                provider.experience_years
            ),
        }

    @staticmethod
    def _rating_score(rating: float) -> float:
        """Convert a 0-5 rating into a 0-100 score."""

        rating = min(max(float(rating), 0.0), 5.0)

        return (rating / 5.0) * 100.0

    @staticmethod
    def _review_score(review_count: int) -> float:
        """
        Calculate review confidence.

        200 or more reviews receives the maximum score.
        """

        review_count = max(int(review_count), 0)

        return min(review_count / 200.0, 1.0) * 100.0

    @staticmethod
    def _completed_jobs_score(completed_jobs: int) -> float:
        """
        Calculate experience-through-volume score.

        500 or more completed jobs receives the maximum score.
        """

        completed_jobs = max(int(completed_jobs), 0)

        return min(completed_jobs / 500.0, 1.0) * 100.0

    @staticmethod
    def _response_score(response_rate: float) -> float:
        """Use the provider's response rate directly."""

        return min(max(float(response_rate), 0.0), 100.0)

    @staticmethod
    def _experience_score(experience_years: int) -> float:
        """
        Calculate experience score.

        10 or more years receives the maximum score.
        """

        experience_years = max(int(experience_years), 0)

        return min(experience_years / 10.0, 1.0) * 100.0


# Shared trust engine instance.
trust_engine = TrustEngine() 