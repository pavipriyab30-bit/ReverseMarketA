import json
import re
from typing import Any, Dict, List, Optional

from services.gemini_service import gemini_service


class ProductRequirementParser:
    """Extract structured product requirements from natural language."""

    def parse(
        self,
        requirement_text: str,
    ) -> Dict[str, Any]:
        if not isinstance(requirement_text, str):
            raise ValueError(
                "Product requirement must be text."
            )

        requirement_text = requirement_text.strip()

        if not requirement_text:
            raise ValueError(
                "Product requirement cannot be empty."
            )

        if gemini_service.is_available:
            try:
                result = self._parse_with_gemini(
                    requirement_text
                )

                if result:
                    return self._normalize(result)

            except Exception:
                pass

        return self._parse_locally(
            requirement_text
        )

    def _parse_with_gemini(
        self,
        requirement_text: str,
    ) -> Optional[Dict[str, Any]]:
        prompt = f"""
Extract the product-shopping requirements from this request.

USER REQUEST:
{requirement_text}

Return ONLY valid JSON using exactly this structure:

{{
    "category": "",
    "budget_min": null,
    "budget_max": null,
    "preferred_brands": [],
    "required_features": [],
    "preferred_features": [],
    "excluded_features": [],
    "query": ""
}}

Rules:
- Do not invent requirements.
- budget values must be numbers only.
- category should be a simple product category.
- Required features are things the user explicitly requires.
- Preferred features are things the user says they prefer.
- Excluded features are things the user does not want.
- query should contain useful product-search keywords.
"""

        response = gemini_service.generate_text(
            prompt,
            system_instruction=(
                "You are a product requirement extraction "
                "engine. Return only valid JSON."
            ),
        )

        cleaned = response.strip()

        if cleaned.startswith("```"):
            cleaned = re.sub(
                r"^```(?:json)?\s*",
                "",
                cleaned,
            )

            cleaned = re.sub(
                r"\s*```$",
                "",
                cleaned,
            )

        return json.loads(cleaned)

    def _parse_locally(
        self,
        requirement_text: str,
    ) -> Dict[str, Any]:
        text = requirement_text.lower()

        category = self._detect_category(text)

        budget_min, budget_max = (
            self._extract_budget(text)
        )

        preferred_brands = (
            self._detect_brands(text)
        )

        required_features = (
            self._detect_features(text)
        )

        return {
            "category": category,
            "budget_min": budget_min,
            "budget_max": budget_max,
            "preferred_brands": preferred_brands,
            "required_features": required_features,
            "preferred_features": [],
            "excluded_features": [],
            "query": self._build_query(
                requirement_text,
                category,
                preferred_brands,
                required_features,
            ),
        }

    @staticmethod
    def _detect_category(
        text: str,
    ) -> str:
        categories = {
            "laptop": "Laptop",
            "notebook": "Laptop",
            "computer": "Laptop",
            "smartphone": "Smartphone",
            "phone": "Smartphone",
            "mobile": "Smartphone",
            "headphone": "Headphones",
            "headphones": "Headphones",
            "earbuds": "Headphones",
            "television": "Television",
            "tv": "Television",
        }

        for keyword, category in categories.items():
            if keyword in text:
                return category

        return ""

    @staticmethod
    def _extract_budget(
        text: str,
    ) -> tuple[Optional[float], Optional[float]]:
        pattern = (
            r"(?:₹|rs\.?|inr)?\s*"
            r"(\d+(?:,\d{3})*(?:\.\d+)?)"
            r"\s*(k|thousand|lakh|lakhs)?"
        )

        amounts = []

        for match in re.finditer(
            pattern,
            text,
            flags=re.IGNORECASE,
        ):
            raw_value = match.group(1).replace(
                ",",
                "",
            )

            multiplier = (
                match.group(2) or ""
            ).lower()

            try:
                value = float(raw_value)
            except ValueError:
                continue

            if multiplier in {
                "k",
                "thousand",
            }:
                value *= 1000

            elif multiplier in {
                "lakh",
                "lakhs",
            }:
                value *= 100000

            amounts.append(value)

        if not amounts:
            return None, None

        if any(
            phrase in text
            for phrase in [
                "under",
                "below",
                "less than",
                "within",
                "up to",
                "maximum",
                "max",
            ]
        ):
            return None, amounts[0]

        if len(amounts) >= 2:
            return (
                min(amounts[0], amounts[1]),
                max(amounts[0], amounts[1]),
            )

        return None, amounts[0]

    @staticmethod
    def _detect_brands(
        text: str,
    ) -> List[str]:
        known_brands = [
            "apple",
            "samsung",
            "oneplus",
            "lenovo",
            "asus",
            "sony",
            "lg",
            "xiaomi",
            "realme",
            "hp",
            "dell",
            "acer",
        ]

        return [
            brand.title()
            for brand in known_brands
            if brand in text
        ]

    @staticmethod
    def _detect_features(
        text: str,
    ) -> List[str]:
        feature_patterns = [
            "16gb ram",
            "8gb ram",
            "32gb ram",
            "512gb ssd",
            "1tb ssd",
            "256gb ssd",
            "good battery",
            "long battery life",
            "active noise cancellation",
            "noise cancellation",
            "4k",
            "5g",
            "amoled",
            "oled",
            "good camera",
        ]

        return [
            feature
            for feature in feature_patterns
            if feature in text
        ]

    @staticmethod
    def _build_query(
        original_text: str,
        category: str,
        brands: List[str],
        features: List[str],
    ) -> str:
        parts = []

        if category:
            parts.append(category)

        parts.extend(brands)
        parts.extend(features)

        if not parts:
            return original_text

        return " ".join(parts)

    @staticmethod
    def _normalize(
        result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Ensure Gemini output follows the application contract."""

        return {
            "category": str(
                result.get("category") or ""
            ).strip(),

            "budget_min": (
                float(result["budget_min"])
                if result.get("budget_min") is not None
                else None
            ),

            "budget_max": (
                float(result["budget_max"])
                if result.get("budget_max") is not None
                else None
            ),

            "preferred_brands": (
                result.get("preferred_brands")
                if isinstance(
                    result.get("preferred_brands"),
                    list,
                )
                else []
            ),

            "required_features": (
                result.get("required_features")
                if isinstance(
                    result.get("required_features"),
                    list,
                )
                else []
            ),

            "preferred_features": (
                result.get("preferred_features")
                if isinstance(
                    result.get("preferred_features"),
                    list,
                )
                else []
            ),

            "excluded_features": (
                result.get("excluded_features")
                if isinstance(
                    result.get("excluded_features"),
                    list,
                )
                else []
            ),

            "query": str(
                result.get("query") or ""
            ).strip(),
        }


# Shared Product Mode requirement parser.
product_requirement_parser = ProductRequirementParser() 