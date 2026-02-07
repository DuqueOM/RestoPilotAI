"""
Menu Extraction Service - OCR and multimodal menu parsing.
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import fitz  # PyMuPDF
import pytesseract
from app.core.config import get_settings
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

    def _truncate_pdf(self, pdf_path: str, max_pages: int) -> str:
        """Truncate a PDF to max_pages and return the path to the truncated file."""
        try:
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            if total_pages <= max_pages:
                doc.close()
                return pdf_path

            logger.warning(
                f"PDF has {total_pages} pages, truncating to {max_pages} for processing"
            )
            # Create truncated copy
            truncated_path = pdf_path.replace(".pdf", f"_first{max_pages}.pdf")
            truncated_doc = fitz.open()
            truncated_doc.insert_pdf(doc, from_page=0, to_page=max_pages - 1)
            truncated_doc.save(truncated_path)
            truncated_doc.close()
            doc.close()
            return truncated_path
        except Exception as e:
            logger.error(f"PDF truncation failed: {e}")
            return pdf_path

    async def extract_from_pdf_all_pages(
        self,
        pdf_path: str,
        use_ocr: bool = True,
        business_context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Dual-Analysis Menu Extraction Pipeline.

        Showcases multiple Gemini 3 capabilities:
          Pass 1 — Document Intelligence: PDF text extraction + Gemini native PDF analysis
          Pass 2 — Vision Analysis: Convert pages to images + Gemini multimodal vision
          Pass 3 — Intelligent Fusion: Merge both analyses with Gemini reasoning
          Pass 4 — Vibe Engineering: Verification loop for quality assurance
        """
        import json as _json

        settings = get_settings()
        max_pages = settings.max_pdf_pages
        working_pdf = self._truncate_pdf(pdf_path, max_pages)

        logger.info(f"🔬 Dual-Analysis Pipeline starting for: {working_pdf}")

        # ── Pass 1: Document Intelligence (PDF text + Gemini native) ──
        pass1_items = []
        pdf_text_content = ""
        try:
            # 1a. Extract text layers from PDF with PyMuPDF
            doc = fitz.open(working_pdf)
            for i in range(len(doc)):
                page_text = doc[i].get_text("text")
                if page_text and len(page_text.strip()) > 20:
                    pdf_text_content += f"\n--- Page {i+1} ---\n{page_text}"
            doc.close()

            if pdf_text_content:
                logger.info(f"  Pass 1a: Extracted {len(pdf_text_content)} chars of text from PDF layers")

            # 1b. Gemini native PDF analysis (Document Intelligence)
            gemini_pdf_result = await self.agent.extract_menu_from_pdf(
                working_pdf, additional_context=business_context
            )
            pass1_items = gemini_pdf_result.get("items", [])
            logger.info(f"  Pass 1b: Gemini Document Intelligence found {len(pass1_items)} items")

        except Exception as e:
            logger.warning(f"  Pass 1 partial failure: {e}")

        # ── Pass 2: Vision Analysis (images + Gemini multimodal) ──
        pass2_items = []
        try:
            page_images = self._convert_pdf_to_images(working_pdf)
            logger.info(f"  Pass 2: Converted {len(page_images)} pages to images for Vision Analysis")

            for idx, img_path in enumerate(page_images):
                try:
                    page_context = business_context or ""
                    # Enrich with text layer if available
                    if pdf_text_content:
                        lines = pdf_text_content.split(f"--- Page {idx+1} ---")
                        if len(lines) > 1:
                            next_marker = lines[1].find("--- Page ")
                            page_text_slice = lines[1][:next_marker] if next_marker > 0 else lines[1]
                            page_context += f"\nText from this page:\n{page_text_slice[:1500]}"

                    # OCR preprocessing
                    ocr_text = None
                    if use_ocr:
                        ocr_text = self._run_local_ocr(img_path)
                    if ocr_text:
                        page_context += f"\nOCR extraction:\n{ocr_text[:1500]}"

                    vision_result = await self.agent.extract_menu_from_image(
                        img_path, additional_context=page_context if page_context else None
                    )
                    page_items = vision_result.get("items", [])
                    pass2_items.extend(page_items)
                    logger.info(f"    Page {idx+1}: Vision found {len(page_items)} items")
                except Exception as page_err:
                    logger.warning(f"    Page {idx+1} vision failed: {page_err}")

        except Exception as e:
            logger.warning(f"  Pass 2 failed: {e}")

        # ── Pass 3: Intelligent Fusion (Gemini reasoning) ──
        logger.info(f"  Pass 3: Fusing {len(pass1_items)} doc items + {len(pass2_items)} vision items")
        fused_items = await self._fuse_extractions(pass1_items, pass2_items, business_context)

        # Post-process
        processed_items = self._post_process_items(fused_items)
        categories = self._extract_categories(processed_items)

        # ── Pass 4: Vibe Engineering Verification ──
        verified_items, verification_notes = await self._vibe_verify_extraction(
            processed_items, pdf_text_content
        )

        final_items = verified_items if verified_items else processed_items
        final_categories = self._extract_categories(final_items)

        logger.info(
            f"✅ Dual-Analysis complete: {len(final_items)} verified items "
            f"(Pass1={len(pass1_items)}, Pass2={len(pass2_items)}, "
            f"Fused={len(fused_items)}, Final={len(final_items)})"
        )

        return {
            "items": final_items,
            "categories": final_categories,
            "item_count": len(final_items),
            "extraction_confidence": 0.92 if verification_notes else 0.85,
            "method": "dual_analysis_pipeline",
            "pipeline_details": {
                "pass1_document_intelligence": len(pass1_items),
                "pass2_vision_analysis": len(pass2_items),
                "pass3_fused": len(fused_items),
                "pass4_verified": len(final_items),
                "verification_notes": verification_notes,
            },
            "warnings": self._generate_warnings(final_items, pdf_text_content[:500] if pdf_text_content else None),
        }

    def _convert_pdf_to_images(self, pdf_path: str) -> List[str]:
        """Convert PDF pages to JPEG images for Vision Analysis."""
        output_paths = []
        try:
            doc = fitz.open(pdf_path)
            for i in range(len(doc)):
                page = doc[i]
                pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
                out_path = pdf_path.replace(".pdf", f"_vis_page{i+1}.jpg")
                pix.pil_save(out_path, format="JPEG", quality=85, optimize=True)
                output_paths.append(out_path)
            doc.close()
        except Exception as e:
            logger.error(f"PDF to image conversion failed: {e}")
        return output_paths

    async def _fuse_extractions(
        self,
        doc_items: List[Dict],
        vision_items: List[Dict],
        business_context: Optional[str] = None,
    ) -> List[Dict]:
        """Pass 3: Intelligently merge Document and Vision extraction results."""
        import json as _json

        # If only one source has data, use it directly
        if not doc_items and not vision_items:
            return []
        if not doc_items:
            return vision_items
        if not vision_items:
            return doc_items

        # Both have data — use Gemini to intelligently fuse
        # Use larger source as primary, smaller as supplement
        if len(doc_items) >= len(vision_items):
            primary, primary_label = doc_items, "Document Intelligence"
            secondary, secondary_label = vision_items, "Vision Analysis"
        else:
            primary, primary_label = vision_items, "Vision Analysis"
            secondary, secondary_label = doc_items, "Document Intelligence"

        try:
            # Limit items sent to fusion to avoid token overflow
            primary_sample = primary[:100]
            secondary_sample = secondary[:60]

            prompt = f"""You are an expert menu data engineer. You have TWO extraction results from the SAME restaurant menu.

PRIMARY SOURCE ({primary_label}, {len(primary)} items — this is the most complete source):
{_json.dumps(primary_sample, indent=1, default=str)[:5000]}

SUPPLEMENTARY SOURCE ({secondary_label}, {len(secondary)} items):
{_json.dumps(secondary_sample, indent=1, default=str)[:3000]}

{f"Business context: {business_context}" if business_context else ""}

YOUR TASK: Produce a UNIFIED menu that MAXIMIZES coverage.

CRITICAL RULES:
1. START with ALL items from the Primary source. This is your base.
2. ADD any items from the Supplementary source that do NOT appear in the Primary (different page, missed items).
3. If the SAME item exists in both, merge them: keep the best name, best price, best description.
4. ONLY remove an item if it is an EXACT duplicate (same name AND same price).
5. When in doubt, KEEP the item. It is better to have a few duplicates than to lose real menu items.
6. The final list should have AT LEAST as many items as the Primary source.

Respond ONLY with valid JSON:
{{
  "items": [
    {{"name": "Item Name", "price": 100.00, "description": "desc", "category": "Category", "confidence": 0.95}}
  ]
}}"""

            response_text = await self.agent.generate(
                prompt=prompt,
                thinking_level="STANDARD",
                temperature=0.2,
                max_output_tokens=8192,
            )

            if response_text:
                result = self.agent._parse_json_response(response_text)
                fused = result.get("items", [])
                if fused:
                    logger.info(f"  Pass 3: Gemini fusion produced {len(fused)} items")
                    return fused
        except Exception as e:
            logger.warning(f"  Pass 3 fusion failed: {e}")

        # Fallback: manual dedup merge
        return self._manual_merge(doc_items, vision_items)

    def _manual_merge(self, list_a: List[Dict], list_b: List[Dict]) -> List[Dict]:
        """Fallback merge: deduplicate by name."""
        seen = {}
        for item in list_a + list_b:
            name_key = (item.get("name", "")).strip().lower()
            if name_key and name_key not in seen:
                seen[name_key] = item
        return list(seen.values())

    async def _vibe_verify_extraction(
        self,
        items: List[Dict],
        raw_text: str,
    ) -> tuple:
        """Pass 4: Vibe Engineering — verify extraction quality and auto-correct."""
        if not items or len(items) < 2:
            return items, None

        try:
            import json as _json
            sample = items[:30]
            prompt = f"""You are a Quality Assurance agent (Vibe Engineering). Verify this menu extraction.

EXTRACTED ITEMS ({len(items)} total, showing first {len(sample)}):
{_json.dumps(sample, indent=1, default=str)[:3000]}

{f"RAW TEXT FROM PDF (reference):{chr(10)}{raw_text[:2000]}" if raw_text else ""}

VERIFY:
1. Do prices look reasonable? (Note: prices may be in COP, MXN, or other currencies — 15000-50000 COP is normal for Colombia)
2. Are categories consistent?
3. Are there EXACT duplicates (same name AND same price)? Only flag those.
4. Are there items with clearly wrong prices (e.g., 0, negative, or obviously misread)?

IMPORTANT: Be CONSERVATIVE. Only flag items for removal if they are EXACT duplicates.
Do NOT remove items just because they seem similar — menus often have variants (e.g., "Chivas 12 Trago" vs "Chivas 12 Botella" are DIFFERENT items).

Respond in JSON:
{{
  "quality_score": 0.0-1.0,
  "issues_found": ["issue1", "issue2"],
  "corrections": [
    {{"item_name": "name", "field": "price", "old_value": "X", "new_value": "Y", "reason": "why"}}
  ],
  "items_to_remove": ["only exact duplicate names here"],
  "verification_passed": true/false
}}"""

            response_text = await self.agent.generate(
                prompt=prompt,
                thinking_level="QUICK",
                temperature=0.1,
                max_output_tokens=4096,
            )

            if not response_text:
                return items, None

            verification = self.agent._parse_json_response(response_text)

            notes = {
                "quality_score": verification.get("quality_score", 0.8),
                "issues_found": verification.get("issues_found", []),
                "corrections_applied": 0,
                "items_removed": 0,
            }

            # Apply corrections
            corrections = verification.get("corrections", [])
            items_by_name = {i["name"].lower(): i for i in items}
            for corr in corrections:
                target = corr.get("item_name", "").lower()
                field = corr.get("field", "")
                new_val = corr.get("new_value")
                if target in items_by_name and field and new_val is not None:
                    try:
                        if field == "price":
                            items_by_name[target]["price"] = float(new_val)
                        else:
                            items_by_name[target][field] = new_val
                        notes["corrections_applied"] += 1
                    except (ValueError, KeyError):
                        pass

            # Remove flagged duplicates
            to_remove = {n.lower() for n in verification.get("items_to_remove", [])}
            if to_remove:
                items = [i for i in items if i["name"].lower() not in to_remove]
                notes["items_removed"] = len(to_remove)

            logger.info(
                f"  Pass 4: Vibe verification — score={notes['quality_score']}, "
                f"corrections={notes['corrections_applied']}, removed={notes['items_removed']}"
            )
            return items, notes

        except Exception as e:
            logger.warning(f"  Pass 4 verification failed: {e}")
            return items, None

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

            if price <= 0 or price > 500000:  # Sanity check (supports COP, MXN, etc.)
                continue

            # Build processed item
            processed_item = {
                "name": name,
                "price": round(float(price), 2),
                "description": (item.get("description") or "").strip() or None,
                "category": (item.get("category") or "").strip() or "Other",
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

    async def analyze_dish_image(self, image_path: str) -> Dict[str, Any]:
        """
        Analyze a single dish image for visual appeal and metadata.
        Used by AnalysisOrchestrator.
        """
        try:
            # Read image bytes from path
            image_data = Path(image_path).read_bytes()
            
            # We can use the agent's multimodal capability directly
            # Construct a prompt for analysis
            prompt = """
            Analyze this dish image for a restaurant menu.
            Provide:
            1. Likely item name
            2. Visual appeal score (0.0 to 1.0)
            3. Key ingredients visible
            4. Presentation quality (High/Medium/Low)
            
            Return JSON:
            {
                "item_name": "string",
                "score": float,
                "ingredients": ["string"],
                "presentation": "string",
                "improvement_tips": ["string"]
            }
            """
            
            response = await self.agent.generate(
                prompt=prompt,
                images=[image_data],
                thinking_level="QUICK"
            )
            
            # Parse JSON
            try:
                import json
                # Handle potential markdown code blocks
                text = response.replace("```json", "").replace("```", "").strip()
                return json.loads(text)
            except Exception:
                # Fallback
                return {"item_name": "Unknown", "score": 0.5}
                
        except Exception as e:
            logger.error(f"Dish image analysis failed: {e}")
            return {"item_name": "Error", "score": 0.0, "error": str(e)}


class DishImageAnalyzer:
    """Analyzes visual content (photos, videos, screenshots) for business intelligence."""

    def __init__(self, agent: GeminiAgent):
        self.agent = agent

    async def analyze_images(
        self, image_paths: List[str], menu_items: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze multiple images (dishes, decor, social).

        Args:
            image_paths: List of paths to images
            menu_items: Optional list of item names to match with images

        Returns:
            Analysis results for each image
        """

        # Use the new generic multimodal analyzer
        results = await self.agent.analyze_visual_context(image_paths)

        # Try to match with menu items if provided (only if content type is food)
        if menu_items:
            results = self._match_to_menu(results, menu_items)

        # Calculate summary statistics
        summary = self._calculate_summary(results)

        return {"analyses": results, "summary": summary, "image_count": len(results)}

    async def analyze_videos(
        self, video_paths: List[str], menu_items: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze videos using Gemini's multimodal capabilities.

        Args:
            video_paths: List of paths to videos
            menu_items: Optional list of item names to match

        Returns:
            Analysis results for each video
        """
        # Reuse the generic analyzer which handles video mime types now
        results = await self.agent.analyze_visual_context(video_paths)

        # Try to match with menu items if provided
        if menu_items:
            results = self._match_to_menu(results, menu_items)

        # Calculate summary statistics
        summary = self._calculate_summary(results)

        return {"analyses": results, "summary": summary, "video_count": len(results)}

    def _match_to_menu(
        self, analyses: List[Dict[str, Any]], menu_items: List[str]
    ) -> List[Dict[str, Any]]:
        """Attempt to match analyzed content to menu items."""

        for analysis in analyses:
            # Only match if it looks like a dish
            if analysis.get("content_type") == "food" or "dish_name" in analysis:
                dish_name = analysis.get("dish_name", "").lower()
                # If using new generic format, name might be in description or key_elements
                if not dish_name and "description" in analysis:
                     dish_name = analysis["description"][:50].lower()

                for item in menu_items:
                    if item.lower() in dish_name or dish_name in item.lower():
                        analysis["matched_menu_item"] = item
                        break

        return analyses

    def _calculate_summary(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary statistics across all visual content."""

        if not analyses:
            return {"avg_attractiveness": 0, "overall_quality": "unknown"}

        # Handle new generic structure vs old structure
        scores = []
        for a in analyses:
            # New format
            if "analysis" in a and "visual_appeal_score" in a["analysis"]:
                scores.append(a["analysis"]["visual_appeal_score"])
            # Old format fallback
            elif "attractiveness_score" in a:
                scores.append(a["attractiveness_score"])
            else:
                scores.append(0.5) # Default neutral

        avg_score = sum(scores) / len(scores) if scores else 0

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
            "content_types": [a.get("content_type", "unknown") for a in analyses],
            "best_content": max(analyses, key=lambda x: x.get("analysis", {}).get("visual_appeal_score", 0) if "analysis" in x else x.get("attractiveness_score", 0)) if analyses else None,
        }
