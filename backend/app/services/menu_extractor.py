"""
Menu Extraction Service - OCR and multimodal menu parsing.
"""

import re
from typing import Any, Dict, List, Optional

import pytesseract
from loguru import logger
from PIL import Image

from app.services.gemini_agent import GeminiAgent


class MenuExtractor:
    """
    Extracts structured menu data from images using OCR and Gemini multimodal.

    Uses a hybrid approach:
    1. Local OCR (Tesseract) for initial text extraction
    2. Gemini multimodal for structure understanding and verification
    """

    def __init__(self, agent: GeminiAgent):
        self.agent = agent

    async def extract_from_image(
        self,
        image_path: str,
        use_ocr: bool = True,
        business_context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Extract menu items from an image.

        Args:
            image_path: Path to the menu image
            use_ocr: Whether to use local OCR as preprocessing
            business_context: Additional context about the business

        Returns:
            Structured menu data with items, categories, and confidence scores
        """

        logger.info(f"Extracting menu from: {image_path}")

        # Step 1: Local OCR preprocessing (optional)
        ocr_text = None
        if use_ocr:
            ocr_text = self._run_local_ocr(image_path)
            logger.debug(f"OCR extracted {len(ocr_text)} characters")

        # Step 2: Gemini multimodal extraction
        context = business_context or ""
        if ocr_text:
            context += (
                f"\n\nOCR Pre-extraction (may contain errors):\n{ocr_text[:2000]}"
            )

        gemini_result = await self.agent.extract_menu_from_image(
            image_path, additional_context=context if context else None
        )

        # Step 3: Post-process and validate
        processed_items = self._post_process_items(gemini_result.get("items", []))

        # Step 4: Categorize items
        categories = self._extract_categories(processed_items)

        return {
            "items": processed_items,
            "categories": categories,
            "item_count": len(processed_items),
            "extraction_confidence": gemini_result.get("confidence", 0.7),
            "ocr_used": use_ocr,
            "warnings": self._generate_warnings(processed_items, ocr_text),
        }

    def _run_local_ocr(self, image_path: str) -> str:
        """Run Tesseract OCR on the image."""
        try:
            image = Image.open(image_path)

            # Preprocess for better OCR
            if image.mode != "RGB":
                image = image.convert("RGB")

            # Run OCR with Spanish and English support
            text = pytesseract.image_to_string(
                image, lang="spa+eng", config="--psm 6"  # Assume uniform block of text
            )

            return text
        except Exception as e:
            logger.warning(f"OCR failed: {e}")
            return ""

    def _post_process_items(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean and validate extracted items."""

        processed = []

        for item in items:
            # Skip items without name or price
            if not item.get("name") or item.get("price") is None:
                continue

            # Clean name
            name = item["name"].strip()
            name = re.sub(r"\s+", " ", name)  # Normalize whitespace

            # Validate and clean price
            price = item["price"]
            if isinstance(price, str):
                # Extract numeric value from string
                price_match = re.search(r"[\d,.]+", price.replace(",", "."))
                if price_match:
                    price = float(price_match.group().replace(",", "."))
                else:
                    continue

            if price <= 0 or price > 10000:  # Sanity check
                continue

            # Build processed item
            processed_item = {
                "name": name,
                "price": round(float(price), 2),
                "description": item.get("description", "").strip() or None,
                "category": item.get("category", "").strip() or "Other",
                "confidence": item.get("confidence", 0.8),
                "dietary_tags": self._extract_dietary_tags(item),
            }

            processed.append(processed_item)

        return processed

    def _extract_dietary_tags(self, item: Dict[str, Any]) -> List[str]:
        """Extract dietary information from item data."""

        tags = []
        name_desc = f"{item.get('name', '')} {item.get('description', '')}".lower()

        # Vegetarian indicators
        if any(
            kw in name_desc for kw in ["vegetariano", "vegetarian", "veggie", "(v)"]
        ):
            tags.append("vegetarian")

        # Vegan indicators
        if any(kw in name_desc for kw in ["vegano", "vegan", "plant-based", "(vg)"]):
            tags.append("vegan")
            tags.append("vegetarian")  # Vegan implies vegetarian

        # Gluten-free indicators
        if any(
            kw in name_desc
            for kw in ["sin gluten", "gluten-free", "gluten free", "(gf)"]
        ):
            tags.append("gluten-free")

        # Spicy indicators
        if any(kw in name_desc for kw in ["picante", "spicy", "hot", "🌶"]):
            tags.append("spicy")

        return list(set(tags))

    def _extract_categories(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Group items by category."""

        categories_dict = {}

        for idx, item in enumerate(items):
            cat = item.get("category", "Other")
            if cat not in categories_dict:
                categories_dict[cat] = {
                    "name": cat,
                    "items": [],
                    "display_order": len(categories_dict),
                }
            categories_dict[cat]["items"].append(item["name"])

        return list(categories_dict.values())

    def _generate_warnings(
        self, items: List[Dict[str, Any]], ocr_text: Optional[str]
    ) -> List[str]:
        """Generate warnings about potential extraction issues."""

        warnings = []

        if len(items) == 0:
            warnings.append("No items could be extracted from the image")
        elif len(items) < 3:
            warnings.append("Very few items extracted - image quality may be poor")

        # Check for price anomalies
        prices = [item["price"] for item in items if item.get("price")]
        if prices:
            avg_price = sum(prices) / len(prices)
            for item in items:
                if item.get("price", 0) > avg_price * 5:
                    warnings.append(
                        f"Unusually high price detected for '{item['name']}'"
                    )

        # Check for low confidence items
        low_conf_items = [i for i in items if i.get("confidence", 1) < 0.6]
        if low_conf_items:
            warnings.append(
                f"{len(low_conf_items)} items have low extraction confidence"
            )

        return warnings


class DishImageAnalyzer:
    """Analyzes dish photographs for visual appeal metrics."""

    def __init__(self, agent: GeminiAgent):
        self.agent = agent

    async def analyze_images(
        self, image_paths: List[str], menu_items: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze multiple dish images.

        Args:
            image_paths: List of paths to dish images
            menu_items: Optional list of item names to match with images

        Returns:
            Analysis results for each image
        """

        results = await self.agent.analyze_dish_images(image_paths)

        # Try to match with menu items if provided
        if menu_items:
            results = self._match_to_menu(results, menu_items)

        # Calculate summary statistics
        summary = self._calculate_summary(results)

        return {"analyses": results, "summary": summary, "image_count": len(results)}

    def _match_to_menu(
        self, analyses: List[Dict[str, Any]], menu_items: List[str]
    ) -> List[Dict[str, Any]]:
        """Attempt to match analyzed images to menu items."""

        # This is a simplified matching - in production would use
        # more sophisticated matching or user input
        for analysis in analyses:
            if "dish_name" in analysis:
                # Find closest menu item match
                dish_name = analysis["dish_name"].lower()
                for item in menu_items:
                    if item.lower() in dish_name or dish_name in item.lower():
                        analysis["matched_menu_item"] = item
                        break

        return analyses

    def _calculate_summary(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary statistics across all images."""

        if not analyses:
            return {"avg_attractiveness": 0, "overall_quality": "unknown"}

        attractiveness_scores = [a.get("attractiveness_score", 0.5) for a in analyses]

        avg_score = sum(attractiveness_scores) / len(attractiveness_scores)

        quality = "poor"
        if avg_score >= 0.8:
            quality = "excellent"
        elif avg_score >= 0.6:
            quality = "good"
        elif avg_score >= 0.4:
            quality = "average"

        return {
            "avg_attractiveness": round(avg_score, 2),
            "overall_quality": quality,
            "best_image": max(analyses, key=lambda x: x.get("attractiveness_score", 0)),
            "needs_improvement": [
                a for a in analyses if a.get("attractiveness_score", 1) < 0.5
            ],
        }
