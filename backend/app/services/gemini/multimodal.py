"""
Gemini Multimodal Agent - Vision + text extraction capabilities.

Handles:
- Menu image extraction
- Dish photo analysis
- Document processing (PDFs)
- Visual quality assessment
"""

import base64
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from loguru import logger

from app.services.gemini.base_agent import GeminiBaseAgent, GeminiModel


class MultimodalAgent(GeminiBaseAgent):
    """
    Agent specialized in multimodal processing.

    Capabilities:
    - Extract structured data from menu images
    - Analyze dish photographs for visual appeal
    - Process PDF documents
    - Evaluate presentation quality
    """

    def __init__(
        self,
        model: GeminiModel = GeminiModel.VISION,  # Use VISION model by default
        **kwargs,
    ):
        super().__init__(model_name=model, **kwargs)
        # Use vision model from settings for multimodal tasks
        self.model_name = self.settings.gemini_model_vision

    async def process(self, *args, **kwargs) -> Any:
        """Main entry point - routes to specific extraction method."""
        task = kwargs.get("task", "extract_menu")

        if task == "extract_menu":
            return await self.extract_menu_from_image(**kwargs)
        elif task == "analyze_dish":
            return await self.analyze_dish_image(**kwargs)
        elif task == "extract_competitor":
            return await self.extract_competitor_menu(**kwargs)
        else:
            raise ValueError(f"Unknown task: {task}")

    async def extract_menu_from_image(
        self,
        image_source: Union[str, bytes],
        additional_context: Optional[str] = None,
        language_hint: str = "auto",
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Extract menu items from a menu image.

        Args:
            image_source: Image path, base64 string, or bytes
            additional_context: Additional context about the restaurant
            language_hint: Expected language (auto, es, en, etc.)

        Returns:
            Structured menu data with items, categories, and confidence
        """
        # Load image
        if isinstance(image_source, str):
            if Path(image_source).exists():
                image_bytes = Path(image_source).read_bytes()
                image_base64 = base64.b64encode(image_bytes).decode()
            else:
                # Assume it's already base64
                image_base64 = image_source
        else:
            image_base64 = base64.b64encode(image_source).decode()

        # Detect mime type
        mime_type = self._detect_mime_type(image_base64)

        prompt = f"""You are a professional menu data extraction specialist. Analyze this restaurant menu image and extract ALL visible menu items with high accuracy.

INSTRUCTIONS:
1. Extract EVERY visible item on the menu, including partially visible ones
2. Maintain original names exactly as written (preserve language, accents, special characters)
3. Parse prices correctly (handle various formats: $, MXN, USD, etc.)
4. Identify logical categories/sections
5. Extract descriptions when available
6. Note any special markers (vegetarian 🌱, spicy 🌶️, popular ⭐, etc.)

{"Additional context: " + additional_context if additional_context else ""}
{"Expected language: " + language_hint if language_hint != "auto" else ""}

RESPOND WITH VALID JSON ONLY:
{{
    "items": [
        {{
            "name": "Item name exactly as written",
            "price": 12.50,
            "currency": "MXN",
            "description": "Description if available, empty string otherwise",
            "category": "Category name",
            "tags": ["vegetarian", "spicy", "popular"],
            "sizes": [
                {{"size": "regular", "price": 12.50}},
                {{"size": "large", "price": 15.00}}
            ]
        }}
    ],
    "categories": [
        {{
            "name": "Category Name",
            "item_count": 5,
            "description": "Category description if any"
        }}
    ],
    "metadata": {{
        "language": "es",
        "currency_detected": "MXN",
        "menu_type": "restaurant",
        "estimated_items_visible": 25
    }},
    "extraction_quality": {{
        "confidence": 0.92,
        "items_clear": 22,
        "items_partial": 3,
        "items_unclear": 0,
        "warnings": ["Some prices partially obscured"]
    }}
}}

Extract EVERY item visible. Be thorough and accurate."""

        try:
            # Use Gemini 3 Vision natively - no external OCR needed
            image_bytes = base64.b64decode(image_base64)
            
            response = await self.generate(
                prompt=prompt,
                images=[image_bytes],
                thinking_level="STANDARD",
                return_full_response=False,
                mime_type=mime_type,
                temperature=0.3,
                max_output_tokens=8192,
                feature="menu_extraction"
            )

            result = self._parse_json_response(response)

            # Validate and enrich result
            result = self._validate_menu_extraction(result)

            logger.info(
                "Menu extraction completed",
                extra={
                    "items_extracted": len(result.get("items", [])),
                    "confidence": result.get("extraction_quality", {}).get(
                        "confidence", 0
                    ),
                },
            )

            return result

        except Exception as e:
            logger.error(f"Menu extraction failed: {e}")
            return {
                "items": [],
                "categories": [],
                "metadata": {"error": str(e)},
                "extraction_quality": {"confidence": 0, "error": str(e)},
            }

    async def analyze_dish_image(
        self,
        image_source: Union[str, bytes],
        dish_name: Optional[str] = None,
        menu_context: Optional[List[str]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Analyze a dish photograph for visual appeal and marketability.

        Args:
            image_source: Dish photo
            dish_name: Known dish name (if any)
            menu_context: List of menu item names for matching

        Returns:
            Visual analysis with scores and recommendations
        """
        # Load image
        if isinstance(image_source, str):
            if Path(image_source).exists():
                image_bytes = Path(image_source).read_bytes()
                image_base64 = base64.b64encode(image_bytes).decode()
            else:
                image_base64 = image_source
        else:
            image_base64 = base64.b64encode(image_source).decode()

        mime_type = self._detect_mime_type(image_base64)

        menu_context_str = ""
        if menu_context:
            menu_context_str = (
                f"\nMenu items to match against: {', '.join(menu_context[:50])}"
            )

        prompt = f"""You are a professional food photographer and restaurant marketing consultant. Analyze this dish photograph for visual appeal and commercial potential.

{"Known dish name: " + dish_name if dish_name else "Identify the dish from the image."}
{menu_context_str}

Evaluate comprehensively and provide scores from 0-10:

RESPOND WITH VALID JSON:
{{
    "dish_identification": {{
        "name": "Identified or matched dish name",
        "confidence": 0.95,
        "matched_menu_item": "Exact menu item if matched",
        "cuisine_type": "Mexican",
        "dish_category": "Main course"
    }},
    "visual_scores": {{
        "overall_attractiveness": 8.5,
        "color_appeal": 9.0,
        "composition": 7.5,
        "lighting_quality": 8.0,
        "focus_sharpness": 9.0,
        "background_appeal": 7.0
    }},
    "presentation_analysis": {{
        "plating_style": "Modern rustic",
        "plating_quality": 8.0,
        "garnish_effectiveness": 7.5,
        "portion_perception": "generous",
        "portion_score": 8.0,
        "professional_level": "restaurant_quality"
    }},
    "marketability": {{
        "instagram_worthiness": 8.5,
        "menu_photo_suitability": 9.0,
        "appetite_appeal": 8.5,
        "premium_perception": 7.5,
        "target_audience": "Young professionals, foodies"
    }},
    "improvement_suggestions": [
        {{
            "area": "Lighting",
            "current_issue": "Slight shadow on left side",
            "recommendation": "Use fill light from the left",
            "impact_potential": "high"
        }}
    ],
    "strengths": [
        "Vibrant colors pop against the plate",
        "Good depth of field focusing on the dish",
        "Appetizing steam/freshness visible"
    ],
    "overall_verdict": {{
        "commercial_ready": true,
        "overall_score": 8.2,
        "summary": "High-quality dish photo suitable for marketing"
    }}
}}

Be objective and constructive in your analysis."""

        try:
            # Use Gemini 3 Vision for professional dish analysis
            image_bytes = base64.b64decode(image_base64)
            
            response = await self.generate(
                prompt=prompt,
                images=[image_bytes],
                thinking_level="STANDARD",
                return_full_response=False,
                mime_type=mime_type,
                temperature=0.4,
                max_output_tokens=4096,
                feature="dish_analysis"
            )

            result = self._parse_json_response(response)

            # Add computed attractiveness score
            if "visual_scores" in result:
                scores = result["visual_scores"]
                result["attractiveness_score"] = sum(scores.values()) / len(scores) / 10

            return result

        except Exception as e:
            logger.error(f"Dish analysis failed: {e}")
            return {
                "error": str(e),
                "attractiveness_score": 0.5,
                "visual_scores": {},
            }

    async def analyze_dish_professional(
        self,
        image_source: Union[str, bytes],
        dish_name: str,
        dish_category: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Professional gastronomy critic analysis of dish photograph.
        
        CRÍTICO PARA HACKATHON: "Food Porn AI" - Análisis de clase mundial.
        
        Args:
            image_source: Dish photo
            dish_name: Name of the dish
            dish_category: Category (appetizer, main, dessert, etc.)
            
        Returns:
            Professional analysis with detailed scores and recommendations
        """
        # Load image
        if isinstance(image_source, str):
            if Path(image_source).exists():
                image_bytes = Path(image_source).read_bytes()
                image_base64 = base64.b64encode(image_bytes).decode()
            else:
                image_base64 = image_source
        else:
            image_base64 = base64.b64encode(image_source).decode()

        mime_type = self._detect_mime_type(image_base64)

        prompt = f"""Actúa como CRÍTICO GASTRONÓMICO DE CLASE MUNDIAL especializado en fotografía culinaria y presentación profesional.

Analiza esta foto del plato: "{dish_name}" (Categoría: {dish_category})

Evalúa en escala 0-10 con criterios PROFESIONALES:

1. COMPOSICIÓN VISUAL
   - Regla de tercios aplicada
   - Balance de elementos en el plato
   - Punto focal claro y definido
   - Uso efectivo del espacio negativo
   - Ángulo de fotografía apropiado

2. ILUMINACIÓN PROFESIONAL
   - Dirección y calidad de luz
   - Sombras apropiadas que añaden profundidad
   - Destacado de texturas
   - Color temperature correcto
   - Evita sobreexposición/subexposición

3. EMPLATADO PROFESIONAL
   - Precisión y limpieza del plato
   - Altura y volumen (dimensionalidad)
   - Uso estratégico del color
   - Garnish apropiado y no excesivo
   - Técnicas de emplatado modernas

4. APETITOSIDAD ("Food Porn Factor")
   - Texturas visibles y atractivas
   - Colores vibrantes y naturales
   - Frescura aparente de ingredientes
   - Factor "craveable" (provoca deseo)
   - Steam/moisture visible si aplica

5. "INSTAGRAMABILIDAD"
   - Aesthetic trending actual
   - Shareability en redes sociales
   - Visual storytelling
   - Elementos únicos/memorables
   - Wow factor

RESPONDE CON JSON VÁLIDO:
{{
    "overall_score": 8.5,
    "scores": {{
        "composition": 8.0,
        "lighting": 9.0,
        "plating": 8.5,
        "appetizing": 9.0,
        "instagramability": 8.0
    }},
    "strengths": [
        "Iluminación natural perfecta que resalta texturas",
        "Colores vibrantes del plato contrastan con fondo neutro",
        "Garnish minimalista pero efectivo"
    ],
    "weaknesses": [
        "Composición ligeramente descentrada",
        "Podría beneficiarse de más altura en el emplatado"
    ],
    "specific_improvements": [
        {{
            "issue": "Composición no sigue regla de tercios",
            "suggestion": "Reposicionar plato 1/3 hacia la izquierda",
            "priority": "medium",
            "expected_impact": "Mejorará balance visual en 15%"
        }},
        {{
            "issue": "Falta profundidad en el plato",
            "suggestion": "Agregar altura con técnica de stacking",
            "priority": "high",
            "expected_impact": "Aumentará percepción de valor en 20%"
        }}
    ],
    "professional_assessment": "Plato bien ejecutado con potencial comercial alto. La iluminación natural es excepcional y los colores son vibrantes. Con ajustes menores en composición y altura, podría alcanzar nivel de revista gastronómica.",
    "comparable_to": "Nivel de Pujol o Quintonil en presentación, pero con estilo más casual",
    "market_positioning": {{
        "current_level": "upscale_casual",
        "potential_level": "fine_dining",
        "price_point_suggested": "$$$ (150-250 MXN)",
        "target_audience": "Millennials, foodies, Instagram influencers"
    }},
    "technical_details": {{
        "estimated_camera_angle": "45 degrees",
        "lighting_type": "natural_window",
        "color_palette": ["vibrant_green", "warm_brown", "white"],
        "plating_style": "modern_rustic",
        "portion_size_perception": "generous"
    }},
    "actionable_recommendations": [
        "Usar este estilo de iluminación consistentemente",
        "Invertir en platos de color neutro para mejor contraste",
        "Capacitar staff en técnicas de altura en emplatado"
    ],
    "instagram_optimization": {{
        "hashtag_suggestions": ["#FoodPorn", "#MexicanCuisine", "#Foodie"],
        "best_posting_time": "12:00-14:00, 19:00-21:00",
        "caption_angle": "Highlight freshness and traditional techniques",
        "filter_recommendation": "None - natural colors are perfect"
    }}
}}

Sé específico, profesional y constructivo. Este análisis será usado para mejorar el negocio."""

        try:
            # Use Gemini 3 Vision with DEEP thinking for professional analysis
            image_bytes = base64.b64decode(image_base64)
            
            response = await self.generate(
                prompt=prompt,
                images=[image_bytes],
                thinking_level="DEEP",  # Professional analysis requires deeper thinking
                return_full_response=False,
                mime_type=mime_type,
                temperature=0.5,  # Balance between creativity and precision
                max_output_tokens=6144,
                feature="professional_dish_analysis"
            )

            result = self._parse_json_response(response)
            
            # Add metadata
            result["dish_name"] = dish_name
            result["dish_category"] = dish_category
            result["analysis_type"] = "professional_gastronomy_critic"
            result["model_used"] = self.model_name
            
            logger.info(
                "Professional dish analysis completed",
                extra={
                    "dish": dish_name,
                    "overall_score": result.get("overall_score", 0),
                    "model": self.model_name
                }
            )

            return result

        except Exception as e:
            logger.error(f"Professional dish analysis failed: {e}")
            return {
                "error": str(e),
                "overall_score": 0,
                "scores": {},
                "dish_name": dish_name,
                "dish_category": dish_category
            }

    async def analyze_batch_dish_images(
        self,
        images: List[Union[str, bytes]],
        menu_context: Optional[List[str]] = None,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """
        Analyze multiple dish images.

        Args:
            images: List of dish photos
            menu_context: Menu items for matching

        Returns:
            List of analysis results
        """
        results = []

        for i, image in enumerate(images):
            logger.info(f"Analyzing dish image {i + 1}/{len(images)}")
            result = await self.analyze_dish_image(
                image_source=image,
                menu_context=menu_context,
                **kwargs,
            )
            result["image_index"] = i
            results.append(result)

        # Generate summary
        summary = self._generate_batch_summary(results)

        return {
            "analyses": results,
            "summary": summary,
            "image_count": len(images),
        }

    async def extract_competitor_menu(
        self,
        image_source: Union[str, bytes],
        competitor_name: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Extract menu from competitor restaurant image.

        Args:
            image_source: Competitor menu image
            competitor_name: Name of competitor (if known)

        Returns:
            Structured competitor menu data
        """
        if isinstance(image_source, str):
            if Path(image_source).exists():
                image_bytes = Path(image_source).read_bytes()
                image_base64 = base64.b64encode(image_bytes).decode()
            else:
                image_base64 = image_source
        else:
            image_base64 = base64.b64encode(image_source).decode()

        mime_type = self._detect_mime_type(image_base64)

        prompt = f"""Analyze this competitor restaurant menu image for competitive intelligence.

{"Competitor: " + competitor_name if competitor_name else ""}

Extract comprehensive data for competitive analysis:

RESPOND WITH VALID JSON:
{{
    "competitor_info": {{
        "name": "{competitor_name or 'Unknown Competitor'}",
        "cuisine_type": "Mexican",
        "price_positioning": "mid-range",
        "brand_style": "Modern casual"
    }},
    "items": [
        {{
            "name": "Item name",
            "price": 85.00,
            "currency": "MXN",
            "category": "Category",
            "description": "Description if visible",
            "appears_popular": true,
            "special_offer": false
        }}
    ],
    "pricing_analysis": {{
        "currency": "MXN",
        "price_range": {{"min": 45, "max": 250}},
        "average_price": 95,
        "price_tier": "mid-range",
        "value_positioning": "Competitive pricing with generous portions"
    }},
    "menu_analysis": {{
        "total_items": 35,
        "categories": ["Appetizers", "Tacos", "Mains", "Drinks"],
        "unique_offerings": ["Specialty item 1", "Signature dish"],
        "promotional_items": ["Happy hour specials"],
        "visual_quality": 7.5
    }},
    "competitive_observations": [
        "Strong focus on traditional dishes",
        "Limited vegetarian options",
        "Competitive pricing on main dishes"
    ],
    "extraction_confidence": 0.88
}}"""

        try:
            # Use Gemini 3 Vision for competitor analysis
            image_bytes = base64.b64decode(image_base64)
            
            response = await self.generate(
                prompt=prompt,
                images=[image_bytes],
                thinking_level="STANDARD",
                return_full_response=False,
                mime_type=mime_type,
                temperature=0.3,
                max_output_tokens=8192,
                feature="competitor_extraction"
            )

            result = self._parse_json_response(response)
            result["source_type"] = "image"

            return result

        except Exception as e:
            logger.error(f"Competitor extraction failed: {e}")
            return {
                "error": str(e),
                "items": [],
                "extraction_confidence": 0,
            }

    async def analyze_customer_photos(
        self,
        photos: List[Union[str, bytes]],
        menu_items: Optional[List[str]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Analyze customer-posted photos for sentiment and quality insights.

        Args:
            photos: List of customer photos
            menu_items: Known menu items to match

        Returns:
            Visual sentiment analysis with per-dish insights
        """
        if not photos:
            return {"analyses": [], "summary": {}}

        # Prepare images
        image_data = []
        for photo in photos[:20]:  # Limit to 20 photos
            if isinstance(photo, str):
                if Path(photo).exists():
                    image_bytes = Path(photo).read_bytes()
                    image_data.append(base64.b64encode(image_bytes).decode())
                else:
                    image_data.append(photo)
            else:
                image_data.append(base64.b64encode(photo).decode())

        menu_context = ""
        if menu_items:
            menu_context = f"\nKnown menu items: {', '.join(menu_items[:30])}"

        prompt = f"""Analyze these customer-posted restaurant photos for sentiment and quality insights.

{menu_context}

For EACH photo, evaluate:
1. Dish identification (match to menu if possible)
2. Presentation quality as received by customer
3. Portion size perception
4. Visual appeal of how it looks in real conditions
5. Any issues visible (messy plating, wrong items, etc.)

RESPOND WITH VALID JSON:
{{
    "photo_analyses": [
        {{
            "photo_index": 0,
            "dish_identified": "Tacos al Pastor",
            "matched_menu_item": "Tacos al Pastor",
            "match_confidence": 0.95,
            "presentation_score": 7.5,
            "portion_perception": "adequate",
            "portion_score": 7.0,
            "visual_appeal": 8.0,
            "photo_quality": "good",
            "issues_noted": [],
            "positive_aspects": ["Good color", "Fresh looking"],
            "sentiment_indicators": ["positive"]
        }}
    ],
    "aggregate_insights": {{
        "dishes_most_photographed": ["Tacos al Pastor", "Guacamole"],
        "average_presentation_score": 7.8,
        "portion_satisfaction": {{
            "small": 2,
            "adequate": 8,
            "generous": 5
        }},
        "common_issues": ["Inconsistent plating on tacos"],
        "common_positives": ["Fresh ingredients visible"],
        "overall_visual_sentiment": "positive"
    }},
    "per_dish_summary": {{
        "Tacos al Pastor": {{
            "photo_count": 5,
            "avg_presentation": 8.0,
            "avg_portion_score": 7.5,
            "sentiment": "positive",
            "key_feedback": "Consistently well-presented"
        }}
    }},
    "recommendations": [
        {{
            "dish": "Burrito Grande",
            "issue": "Portion appears smaller than name suggests",
            "recommendation": "Increase portion or rename",
            "priority": "high"
        }}
    ]
}}"""

        try:
            # Convert all images to bytes for Gemini 3 Vision
            image_bytes_list = [base64.b64decode(img) for img in image_data]
            
            response = await self.generate(
                prompt=prompt,
                images=image_bytes_list,
                thinking_level="STANDARD",
                return_full_response=False,
                temperature=0.4,
                max_output_tokens=8192,
                feature="customer_photo_analysis"
            )

            return self._parse_json_response(response)

        except Exception as e:
            logger.error(f"Customer photo analysis failed: {e}")
            return {
                "photo_analyses": [],
                "aggregate_insights": {"error": str(e)},
                "per_dish_summary": {},
            }

    def _detect_mime_type(self, image_data: str) -> str:
        """Detect MIME type from base64 image data."""
        try:
            # Check magic bytes
            decoded = base64.b64decode(image_data[:100])

            if decoded[:8] == b"\x89PNG\r\n\x1a\n":
                return "image/png"
            elif decoded[:2] == b"\xff\xd8":
                return "image/jpeg"
            elif decoded[:4] == b"GIF8":
                return "image/gif"
            elif decoded[:4] == b"RIFF" and decoded[8:12] == b"WEBP":
                return "image/webp"
            elif decoded[:4] == b"%PDF":
                return "application/pdf"
        except Exception:
            pass

        return "image/jpeg"  # Default

    def _validate_menu_extraction(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and enrich menu extraction results."""
        # Ensure required fields
        if "items" not in result:
            result["items"] = []

        if "categories" not in result:
            result["categories"] = []

        if "extraction_quality" not in result:
            result["extraction_quality"] = {
                "confidence": 0.5,
                "items_clear": len(result["items"]),
            }

        # Validate each item
        valid_items = []
        for item in result.get("items", []):
            if not isinstance(item, dict):
                continue

            # Ensure required fields
            if "name" not in item or not item["name"]:
                continue

            # Normalize price
            if "price" in item:
                try:
                    item["price"] = float(item["price"])
                except (ValueError, TypeError):
                    item["price"] = 0.0
            else:
                item["price"] = 0.0

            # Ensure category
            if "category" not in item or not item["category"]:
                item["category"] = "Uncategorized"

            # Ensure description
            if "description" not in item:
                item["description"] = ""

            valid_items.append(item)

        result["items"] = valid_items

        return result

    def _generate_batch_summary(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary from batch of dish analyses."""
        if not analyses:
            return {}

        # Calculate averages
        scores = []
        for a in analyses:
            if "attractiveness_score" in a:
                scores.append(a["attractiveness_score"])
            elif "visual_scores" in a:
                vs = a["visual_scores"]
                if vs:
                    scores.append(sum(vs.values()) / len(vs) / 10)

        avg_score = sum(scores) / len(scores) if scores else 0

        return {
            "total_images": len(analyses),
            "average_attractiveness": round(avg_score, 2),
            "high_quality_count": sum(1 for s in scores if s >= 0.7),
            "needs_improvement_count": sum(1 for s in scores if s < 0.5),
        }


# Alias for backward compatibility
GeminiMultimodalAgent = MultimodalAgent
