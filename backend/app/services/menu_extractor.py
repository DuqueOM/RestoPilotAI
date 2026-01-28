"""
Menu Extraction Service - OCR and multimodal menu parsing.
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import fitz  # PyMuPDF
import pytesseract
from loguru import logger
from pdf2image import convert_from_path
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
        Extract menu items from an image or PDF.

        Args:
            image_path: Path to the menuor PDF file
            use_ocr: Whether to use local OCR as preprocessing
            business_context: Additional context about the business

        Returns:
            Structured menu data with items, categories, and confidence scores
        """

        logger.info(f"Extracting menu from: {image_path}")

        # Check if it's a PDF and convert to images
        file_path = Path(image_path)
        if file_path.suffix.lower() == ".pdf":
            logger.info("PDF detected, converting to images...")
            image_path = await self._convert_pdf_to_image(image_path)

        # Step 1: Local OCR preprocessing (optional)
        ocr_text = None
        if use_ocr:
            ocr_text = self._run_local_ocr(image_path)
            logger.debug(f"OCR extracted {len(ocr_text) if ocr_text else 0} characters")

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

    async def _convert_pdf_to_image(self, pdf_path: str) -> str:
        """
        Convert PDF to images for processing.

        Handles multi-page PDFs by converting all pages and returning
        the first page path (other pages are processed separately).

        Returns path to the converted image (first page).
        """
        try:
            # Try PyMuPDF first (faster and better quality)
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            logger.info(f"PDF has {total_pages} pages, converting all...")

            output_paths = []
            for page_num in range(total_pages):
                page = doc[page_num]
                # Higher resolution for better OCR
                pix = page.get_pixmap(matrix=fitz.Matrix(2.5, 2.5))

                # Save each page as PNG
                output_path = pdf_path.replace(".pdf", f"_page{page_num + 1}.png")
                pix.save(output_path)
                output_paths.append(output_path)
                logger.info(
                    f"Converted page {page_num + 1}/{total_pages}: {output_path}"
                )

            doc.close()

            # Store all page paths for later processing
            self._pdf_pages = output_paths

            logger.info(f"PDF converted successfully: {total_pages} pages")
            return output_paths[0]  # Return first page for immediate processing

        except Exception as e:
            logger.warning(f"PyMuPDF conversion failed: {e}, trying pdf2image...")

            # Fallback to pdf2image (poppler-based)
            try:
                images = convert_from_path(pdf_path, dpi=200)
                output_paths = []

                for idx, image in enumerate(images):
                    output_path = pdf_path.replace(".pdf", f"_page{idx + 1}.png")
                    image.save(output_path, "PNG")
                    output_paths.append(output_path)
                    logger.info(
                        f"Converted page {idx + 1}/{len(images)} with pdf2image"
                    )

                self._pdf_pages = output_paths

                if output_paths:
                    return output_paths[0]

            except Exception as e2:
                logger.error(f"PDF conversion failed: {e2}")
                raise ValueError(f"Could not convert PDF to image: {e2}")

    async def extract_from_pdf_all_pages(
        self,
        pdf_path: str,
        use_ocr: bool = True,
        business_context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Extract menu items from ALL pages of a PDF.

        This is useful for multi-page menus where different sections
        are on different pages.
        """
        logger.info(f"Extracting menu from all pages of PDF: {pdf_path}")

        # Convert PDF to images
        first_page = await self._convert_pdf_to_image(pdf_path)

        all_items = []
        all_categories = {}
        total_confidence = 0
        warnings = []

        # Process each page
        pages_to_process = getattr(self, "_pdf_pages", [first_page])

        for idx, page_path in enumerate(pages_to_process):
            logger.info(f"Processing page {idx + 1}/{len(pages_to_process)}")

            try:
                # Extract from this page
                page_result = await self.extract_from_image(
                    page_path, use_ocr=use_ocr, business_context=business_context
                )

                # Merge items (avoid duplicates)
                existing_names = {item["name"].lower() for item in all_items}
                for item in page_result.get("items", []):
                    if item["name"].lower() not in existing_names:
                        all_items.append(item)
                        existing_names.add(item["name"].lower())

                # Merge categories
                for cat in page_result.get("categories", []):
                    cat_name = cat["name"]
                    if cat_name not in all_categories:
                        all_categories[cat_name] = cat
                    else:
                        # Merge items lists
                        all_categories[cat_name]["items"].extend(cat.get("items", []))

                total_confidence += page_result.get("extraction_confidence", 0.7)
                warnings.extend(page_result.get("warnings", []))

            except Exception as e:
                logger.error(f"Failed to process page {idx + 1}: {e}")
                warnings.append(f"Page {idx + 1} extraction failed: {str(e)}")

        avg_confidence = (
            total_confidence / len(pages_to_process) if pages_to_process else 0
        )

        return {
            "items": all_items,
            "categories": list(all_categories.values()),
            "item_count": len(all_items),
            "pages_processed": len(pages_to_process),
            "extraction_confidence": round(avg_confidence, 2),
            "ocr_used": use_ocr,
            "warnings": warnings,
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
