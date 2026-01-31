"""
Menu Extraction Service - OCR and multimodal menu parsing.
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import fitz  # PyMuPDF
import pytesseract
from app.services.gemini.base_agent import GeminiAgent
from loguru import logger
from pdf2image import convert_from_path
from PIL import Image


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
            image_path: Path to the menu or PDF file
            use_ocr: Whether to use local OCR as preprocessing
            business_context: Additional context about the business

        Returns:
            Structured menu data with items, categories, and confidence scores
        """

        logger.info(f"Extracting menu from: {image_path}")

        # Check if it's a PDF - process ALL pages for better extraction
        file_path = Path(image_path)
        if file_path.suffix.lower() == ".pdf":
            logger.info(
                "PDF detected, processing all pages for comprehensive extraction..."
            )
            return await self.extract_from_pdf_all_pages(
                image_path, use_ocr=use_ocr, business_context=business_context
            )

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

        Handles multi-page PDFs by converting all pages and extracting
        text layers if available (for hybrid PDFs with selectable text).

        Returns path to the converted image (first page).
        """
        try:
            # Try PyMuPDF first (faster and better quality)
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            logger.info(f"PDF has {total_pages} pages, converting all...")

            output_paths = []
            extracted_text = []

            for page_num in range(total_pages):
                page = doc[page_num]

                # Extract text layer if available (for selectable text PDFs)
                page_text = page.get_text("text")
                if page_text and len(page_text.strip()) > 100:
                    logger.info(
                        f"Page {page_num + 1} has selectable text ({len(page_text)} chars)"
                    )
                    extracted_text.append(page_text)

                # Higher resolution for better OCR and image recognition
                pix = page.get_pixmap(
                    matrix=fitz.Matrix(3.0, 3.0)
                )  # Increased from 2.5 to 3.0

                # Save each page as PNG
                output_path = pdf_path.replace(".pdf", f"_page{page_num + 1}.png")
                pix.save(output_path)
                output_paths.append(output_path)
                logger.info(
                    f"Converted page {page_num + 1}/{total_pages}: {output_path}"
                )

            doc.close()

            # Store all page paths and extracted text for later processing
            self._pdf_pages = output_paths
            self._pdf_text_layers = extracted_text

            logger.info(
                f"PDF converted successfully: {total_pages} pages, {len(extracted_text)} pages with text layer"
            )
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
        Extract menu items from a PDF using Gemini Native PDF support.
        """
        logger.info(
            f"Extracting menu from PDF using Native Gemini File API: {pdf_path}"
        )

        try:
            # 1. Try Native PDF Extraction (Best for mixed content and context)
            gemini_result = await self.agent.extract_menu_from_pdf(
                pdf_path, additional_context=business_context
            )

            items = gemini_result.get("items", [])

            if items and len(items) > 5:
                logger.info(
                    f"Native PDF extraction successful. Found {len(items)} items."
                )

                # Post-process items
                processed_items = self._post_process_items(items)
                categories = self._extract_categories(processed_items)

                return {
                    "items": processed_items,
                    "categories": categories,
                    "item_count": len(processed_items),
                    "extraction_confidence": gemini_result.get("confidence", 0.9),
                    "method": "native_pdf",
                    "warnings": self._generate_warnings(processed_items, None),
                }
            else:
                logger.warning(
                    "Native PDF extraction found few items. Falling back to page-by-image extraction."
                )

        except Exception as e:
            logger.error(
                f"Native PDF extraction failed: {e}. Falling back to image extraction."
            )

        # Fallback: Convert to images and process page by page (Legacy method)
        return await self._extract_from_pdf_images_fallback(
            pdf_path, use_ocr, business_context
        )

    async def _extract_from_pdf_images_fallback(
        self,
        pdf_path: str,
        use_ocr: bool = True,
        business_context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Fallback: Extract menu items from ALL pages of a PDF by converting to images.
        """
        logger.info(
            f"Fallback: Extracting menu from all pages of PDF as images: {pdf_path}"
        )

        # Convert PDF to images
        first_page = await self._convert_pdf_to_image(pdf_path)

        all_items = []
        all_categories = {}
        total_confidence = 0
        warnings = []

        # Process each page with enriched context
        pages_to_process = getattr(self, "_pdf_pages", [first_page])
        text_layers = getattr(self, "_pdf_text_layers", [])

        for idx, page_path in enumerate(pages_to_process):
            logger.info(f"Processing page {idx + 1}/{len(pages_to_process)}")

            try:
                # Enrich context with text layer if available
                page_context = business_context or ""
                if idx < len(text_layers) and text_layers[idx]:
                    page_context += f"\n\nExtracted text from PDF (selectable text layer):\n{text_layers[idx][:3000]}"
                    # ... (rest of the logic remains similar but compacted)

                # Extract from this page
                ocr_text = None
                if use_ocr:
                    ocr_text = self._run_local_ocr(page_path)

                context = page_context
                if ocr_text:
                    context += f"\n\nOCR Pre-extraction (may contain errors):\n{ocr_text[:2000]}"

                gemini_result = await self.agent.extract_menu_from_image(
                    page_path, additional_context=context if context else None
                )

                processed_items = self._post_process_items(
                    gemini_result.get("items", [])
                )
                page_result = {
                    "items": processed_items,
                    "categories": self._extract_categories(
                        processed_items
                    ),  # Helper returns list of dicts
                    "extraction_confidence": gemini_result.get("confidence", 0.7),
                    "warnings": self._generate_warnings(processed_items, ocr_text),
                }

                # Merge items (avoid duplicates)
                existing_names = {item["name"].lower() for item in all_items}
                for item in page_result.get("items", []):
                    if item["name"].lower() not in existing_names:
                        all_items.append(item)
                        existing_names.add(item["name"].lower())

                # Merge categories logic...
                # Simpler merge for fallback
                for cat in page_result.get("categories", []):
                    # Assuming cat is a dict from _extract_categories
                    cat_name = cat["name"]
                    if cat_name not in all_categories:
                        all_categories[cat_name] = cat
                    else:
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
    """Analyzes dish photographs and videos for visual appeal metrics."""

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

    async def analyze_videos(
        self, video_paths: List[str], menu_items: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze dish videos using Gemini's video understanding capabilities.

        Args:
            video_paths: List of paths to dish videos
            menu_items: Optional list of item names to match

        Returns:
            Analysis results for each video
        """
        results = await self.agent.analyze_dish_videos(video_paths)

        # Try to match with menu items if provided
        if menu_items:
            results = self._match_to_menu(results, menu_items)

        # Calculate summary statistics
        summary = self._calculate_summary(results)

        return {"analyses": results, "summary": summary, "video_count": len(results)}

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
