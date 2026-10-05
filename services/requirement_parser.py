import json
import re
from typing import Any, Dict

from services.gemini_service import gemini_service


class RequirementParser:
    """Convert natural-language service requirements into structured data."""

    SYSTEM_INSTRUCTION = """
You are the requirement extraction engine for BESTORA FIT.

BESTORA FIT is a demand-first service marketplace.

Extract only information that is explicitly stated or strongly implied
by the user's request.

Return ONLY valid JSON with these keys:

{
    "category": "",
    "location": "",
    "budget_min": null,
    "budget_max": null,
    "preferred_date": "",
    "urgency": "",
    "requirements": []
}

Rules:
- category should be a concise service category.
- location should be the requested city or area.
- budget values must be numbers without currency symbols.
- If only one budget is given, use it as budget_max.
- preferred_date should be a simple human-readable date/time phrase.
- urgency should be one of: low, medium, high, urgent, or "".
- requirements should contain short specific requirements.
- Never invent information.
- Return JSON only.
"""

    def parse(self, text: str) -> Dict[str, Any]:
        """
        Parse a user's service requirement.

        Gemini is used when available. A deterministic local parser is
        used as a fallback so the application remains functional without AI.
        """

        if not text or not text.strip():
            raise ValueError("Requirement text cannot be empty.")

        cleaned_text = text.strip()

        if gemini_service.is_available:
            try:
                result = self._parse_with_gemini(cleaned_text)

                if self._is_valid_result(result):
                    return result

            except (RuntimeError, ValueError, json.JSONDecodeError):
                pass

        return self._parse_locally(cleaned_text)

    def _parse_with_gemini(self, text: str) -> Dict[str, Any]:
        """Parse requirements using Gemini."""

        response = gemini_service.generate_text(
            prompt=text,
            system_instruction=self.SYSTEM_INSTRUCTION,
        )

        response = self._clean_json_response(response)

        result = json.loads(response)

        return self._normalize_result(result)

    def _parse_locally(self, text: str) -> Dict[str, Any]:
        """
        Perform basic requirement extraction without an AI request.

        This fallback is intentionally deterministic and is useful for
        development, testing, and cases where Gemini is unavailable.
        """

        lower_text = text.lower()

        category = self._extract_category(lower_text)
        location = self._extract_location(text)

        budget_min, budget_max = self._extract_budget(lower_text)

        urgency = self._extract_urgency(lower_text)

        preferred_date = self._extract_date(lower_text)

        requirements = self._extract_requirements(text)

        return {
            "category": category,
            "location": location,
            "budget_min": budget_min,
            "budget_max": budget_max,
            "preferred_date": preferred_date,
            "urgency": urgency,
            "requirements": requirements,
        }

    @staticmethod
    def _clean_json_response(response: str) -> str:
        """Remove common Markdown JSON wrappers from an AI response."""

        response = response.strip()

        if response.startswith("```"):
            response = re.sub(
                r"^```(?:json)?\s*",
                "",
                response,
                flags=re.IGNORECASE,
            )

            response = re.sub(
                r"\s*```$",
                "",
                response,
            )

        return response.strip()

    @staticmethod
    def _normalize_result(result: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize AI output into the application's expected format."""

        return {
            "category": str(result.get("category") or "").strip(),
            "location": str(result.get("location") or "").strip(),
            "budget_min": RequirementParser._number_or_none(
                result.get("budget_min")
            ),
            "budget_max": RequirementParser._number_or_none(
                result.get("budget_max")
            ),
            "preferred_date": str(
                result.get("preferred_date") or ""
            ).strip(),
            "urgency": str(
                result.get("urgency") or ""
            ).strip().lower(),
            "requirements": [
                str(item).strip()
                for item in result.get("requirements", [])
                if str(item).strip()
            ],
        }

    @staticmethod
    def _number_or_none(value):
        """Convert a value to float when possible."""

        if value is None or value == "":
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _is_valid_result(result: Dict[str, Any]) -> bool:
        """Check whether the parser produced a usable result."""

        required_keys = {
            "category",
            "location",
            "budget_min",
            "budget_max",
            "preferred_date",
            "urgency",
            "requirements",
        }

        return (
            isinstance(result, dict)
            and required_keys.issubset(result.keys())
            and isinstance(result["requirements"], list)
        )

    @staticmethod
    def _extract_category(text: str) -> str:
        """Detect common service categories."""

        categories = {
            "electrician": "Electrical",
            "electrical": "Electrical",
            "plumber": "Plumbing",
            "plumbing": "Plumbing",
            "cleaning": "Cleaning",
            "cleaner": "Cleaning",
            "laptop repair": "Laptop Repair",
            "computer repair": "Laptop Repair",
            "laptop": "Laptop Repair",
            "ac repair": "AC Repair",
            "air conditioner": "AC Repair",
            "painting": "Painting",
            "mover": "Packers and Movers",
            "moving": "Packers and Movers",
            "packers": "Packers and Movers",
            "carpenter": "Carpentry",
            "carpentry": "Carpentry",
        }

        for keyword, category in categories.items():
            if keyword in text:
                return category

        return ""

    @staticmethod
    def _extract_location(text: str) -> str:
        """Extract a basic location from common request patterns."""

        patterns = [
            r"\bin\s+([A-Za-z][A-Za-z\s.-]{1,40}?)(?=\s+(?:today|tomorrow|for|under|below|within|at|around)\b|[,.]|$)",
            r"\bnear\s+([A-Za-z][A-Za-z\s.-]{1,40}?)(?=\s+(?:today|tomorrow|for|under|below|within|at|around)\b|[,.]|$)",
            r"\bat\s+([A-Za-z][A-Za-z\s.-]{1,40}?)(?=\s+(?:today|tomorrow|for|under|below|within|at|around)\b|[,.]|$)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)

            if match:
                location = match.group(1).strip()

                if location:
                    return location

        return ""

    @staticmethod
    def _extract_budget(text: str):
        """Extract common INR budget expressions."""

        range_patterns = [
            r"(?:₹|rs\.?|inr)?\s*(\d+(?:,\d+)*)\s*(?:to|-)\s*(?:₹|rs\.?|inr)?\s*(\d+(?:,\d+)*)",
            r"between\s+(?:₹|rs\.?|inr)?\s*(\d+(?:,\d+)*)\s+and\s+(?:₹|rs\.?|inr)?\s*(\d+(?:,\d+)*)",
        ]

        for pattern in range_patterns:
            match = re.search(pattern, text, re.IGNORECASE)

            if match:
                minimum = float(match.group(1).replace(",", ""))
                maximum = float(match.group(2).replace(",", ""))

                return minimum, maximum

        maximum_patterns = [
            r"(?:under|below|less than|upto|up to|within)\s+(?:₹|rs\.?|inr)?\s*(\d+(?:,\d+)*)",
            r"(?:budget|around|approximately|approx)\s+(?:of\s+)?(?:₹|rs\.?|inr)?\s*(\d+(?:,\d+)*)",
        ]

        for pattern in maximum_patterns:
            match = re.search(pattern, text, re.IGNORECASE)

            if match:
                maximum = float(match.group(1).replace(",", ""))

                return None, maximum

        return None, None

    @staticmethod
    def _extract_urgency(text: str) -> str:
        """Detect urgency from the request."""

        if any(
            phrase in text
            for phrase in [
                "immediately",
                "right now",
                "as soon as possible",
                "urgent",
                "emergency",
            ]
        ):
            return "urgent"

        if any(
            phrase in text
            for phrase in [
                "today",
                "same day",
                "within today",
            ]
        ):
            return "high"

        if any(
            phrase in text
            for phrase in [
                "tomorrow",
                "this week",
            ]
        ):
            return "medium"

        return ""

    @staticmethod
    def _extract_date(text: str) -> str:
        """Detect basic relative date expressions."""

        for phrase in [
            "right now",
            "today",
            "tomorrow",
            "this week",
            "this weekend",
            "next week",
        ]:
            if phrase in text:
                return phrase

        return ""

    @staticmethod
    def _extract_requirements(text: str):
        """Extract useful requirement phrases from the request."""

        requirements = []

        keywords = [
            "same day",
            "urgent",
            "emergency",
            "experienced",
            "verified",
            "nearby",
            "available today",
            "available tomorrow",
        ]

        lower_text = text.lower()

        for keyword in keywords:
            if keyword in lower_text:
                requirements.append(keyword)

        return requirements


# Shared requirement parser instance.
requirement_parser = RequirementParser() 