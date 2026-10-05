from typing import Any, Dict, List


class RiskEngine:
    """
    Detect risk indicators for BESTORA FIT service providers and offers.

    Risk score:
        0-24   = LOW
        25-49  = MEDIUM
        50-74  = HIGH
        75-100 = CRITICAL

    The risk score is provider-dependent:
    a stronger provider gets a lower baseline risk, while explicit
    risk indicators increase the score.
    """

    def analyze(
        self,
        provider,
        offer=None,
    ) -> Dict[str, Any]:
        """Analyze a provider and optional offer for risk indicators."""

        alerts: List[Dict[str, Any]] = []

        # ---------------------------------------------------------
        # 1. Provider-dependent baseline risk
        # ---------------------------------------------------------
        trust_score = self._get_trust_score(provider)

        # Higher trust -> lower baseline risk.
        # Keep a small minimum so a completely clean provider
        # does not appear to have literally zero risk.
        risk_score = max(5, round(100 - trust_score))

        # ---------------------------------------------------------
        # 2. Explicit provider risk indicators
        # ---------------------------------------------------------
        if not provider.verified:
            risk_score += 20
            alerts.append(
                {
                    "type": "UNVERIFIED_PROVIDER",
                    "severity": "HIGH",
                    "message": "Provider is not verified.",
                }
            )

        if provider.rating < 3.0:
            risk_score += 25
            alerts.append(
                {
                    "type": "LOW_RATING",
                    "severity": "HIGH",
                    "message": "Provider has a low customer rating.",
                }
            )
        elif provider.rating < 3.5:
            risk_score += 15
            alerts.append(
                {
                    "type": "BELOW_AVERAGE_RATING",
                    "severity": "MEDIUM",
                    "message": (
                        "Provider rating is below the preferred "
                        "quality threshold."
                    ),
                }
            )

        if provider.review_count < 5:
            risk_score += 15
            alerts.append(
                {
                    "type": "LIMITED_REVIEWS",
                    "severity": "MEDIUM",
                    "message": "Provider has very few customer reviews.",
                }
            )

        if provider.completed_jobs < 10:
            risk_score += 10
            alerts.append(
                {
                    "type": "LIMITED_JOB_HISTORY",
                    "severity": "LOW",
                    "message": (
                        "Provider has limited completed-job history."
                    ),
                }
            )

        if provider.response_rate < 60:
            risk_score += 15
            alerts.append(
                {
                    "type": "LOW_RESPONSE_RATE",
                    "severity": "MEDIUM",
                    "message": "Provider has a low response rate.",
                }
            )

        if provider.experience_years < 1:
            risk_score += 10
            alerts.append(
                {
                    "type": "LOW_EXPERIENCE",
                    "severity": "LOW",
                    "message": (
                        "Provider has less than one year "
                        "of reported experience."
                    ),
                }
            )

        # ---------------------------------------------------------
        # 3. Offer-level risk indicators
        # ---------------------------------------------------------
        if offer is not None:

            if offer.price <= 0:
                risk_score += 30
                alerts.append(
                    {
                        "type": "INVALID_PRICE",
                        "severity": "HIGH",
                        "message": "Offer has an invalid price.",
                    }
                )

            if not offer.availability:
                risk_score += 10
                alerts.append(
                    {
                        "type": "UNKNOWN_AVAILABILITY",
                        "severity": "LOW",
                        "message": (
                            "Offer availability is not specified."
                        ),
                    }
                )

        # ---------------------------------------------------------
        # 4. Keep score within 0-100
        # ---------------------------------------------------------
        risk_score = min(max(risk_score, 0), 100)

        return {
            "risk_score": risk_score,
            "risk_level": self.get_risk_level(risk_score),
            "alerts": alerts,
            "safe_to_recommend": risk_score < 50,
        }

    def _get_trust_score(self, provider) -> float:
        """
        Get the provider's trust score.

        If the provider already has a valid trust_score, use it.
        Otherwise calculate an estimated score from provider data.
        """

        existing_score = getattr(provider, "trust_score", None)

        if existing_score is not None:
            try:
                return min(max(float(existing_score), 0.0), 100.0)
            except (TypeError, ValueError):
                pass

        return self._estimate_trust(provider)

    @staticmethod
    def _estimate_trust(provider) -> float:
        """Estimate trust score using the same dimensions as TrustEngine."""

        score = 0.0

        # Rating: 30 points
        rating = min(max(float(provider.rating), 0.0), 5.0)
        score += (rating / 5.0) * 30.0

        # Reviews: 10 points
        review_score = min(provider.review_count / 100.0, 1.0)
        score += review_score * 10.0

        # Completed jobs: 15 points
        job_score = min(provider.completed_jobs / 100.0, 1.0)
        score += job_score * 15.0

        # Response rate: 15 points
        response_score = min(
            max(provider.response_rate, 0.0) / 100.0,
            1.0,
        )
        score += response_score * 15.0

        # Experience: 10 points
        experience_score = min(
            max(provider.experience_years, 0.0) / 10.0,
            1.0,
        )
        score += experience_score * 10.0

        # Verification: 20 points
        if provider.verified:
            score += 20.0

        return min(max(score, 0.0), 100.0)

    @staticmethod
    def get_risk_level(score: float) -> str:
        """Convert numeric risk score into a risk level."""

        score = min(max(float(score), 0.0), 100.0)

        if score >= 75:
            return "CRITICAL"

        if score >= 50:
            return "HIGH"

        if score >= 25:
            return "MEDIUM"

        return "LOW"

    def get_risk_summary(self, provider, offer=None):
        """Return a compact risk summary."""

        result = self.analyze(provider, offer)

        return {
            "risk_score": result["risk_score"],
            "safe_to_recommend": result["safe_to_recommend"],
            "alert_count": len(result["alerts"]),
            "alerts": result["alerts"],
        }


risk_engine = RiskEngine()  