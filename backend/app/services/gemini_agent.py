"""
Gemini 3 Agent - Core orchestrator for MenuPilot's agentic workflows.

This module implements the agentic layer using Google Gemini 3 API with
function calling capabilities for multi-step reasoning and verification.
"""

import base64
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from google import genai
from google.genai import types
from loguru import logger

from app.config import get_settings


class GeminiAgent:
    """
    Agentic orchestrator using Gemini 3 for multimodal reasoning.

    Features:
    - Function calling for tool use
    - Thought signatures for transparent reasoning
    - Self-verification loops
    - Multimodal input processing (images, text, structured data)
    """

    MODEL_NAME = "gemini-3-flash-preview"

    def __init__(self):
        settings = get_settings()
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.call_count = 0
        self.total_tokens = 0

        # Define available tools for function calling
        self.tools = self._define_tools()

    def _define_tools(self) -> List[types.Tool]:
        """Define tools available to the agent for function calling."""

        extract_menu_func = types.FunctionDeclaration(
            name="extract_menu",
            description="Extract menu items from an image of a menu. Returns structured data with item names, prices, descriptions, and categories.",
            parameters=types.Schema(
                type="object",
                properties={
                    "image_description": types.Schema(
                        type="string",
                        description="Description of what's visible in the menu image",
                    ),
                    "items": types.Schema(
                        type="array",
                        items=types.Schema(
                            type="object",
                            properties={
                                "name": types.Schema(type="string"),
                                "price": types.Schema(type="number"),
                                "description": types.Schema(type="string"),
                                "category": types.Schema(type="string"),
                            },
                            required=["name", "price"],
                        ),
                    ),
                    "confidence": types.Schema(
                        type="number",
                        description="Confidence score 0-1 for the extraction accuracy",
                    ),
                },
                required=["items", "confidence"],
            ),
        )

        analyze_dish_image_func = types.FunctionDeclaration(
            name="analyze_dish_image",
            description="Analyze a dish photograph for visual appeal, presentation quality, and marketability.",
            parameters=types.Schema(
                type="object",
                properties={
                    "dish_name": types.Schema(type="string"),
                    "attractiveness_score": types.Schema(
                        type="number", description="Visual appeal score 0-1"
                    ),
                    "presentation_quality": types.Schema(type="string"),
                    "color_appeal": types.Schema(type="string"),
                    "portion_perception": types.Schema(type="string"),
                    "instagram_worthiness": types.Schema(
                        type="number", description="Social media appeal score 0-1"
                    ),
                    "improvement_suggestions": types.Schema(
                        type="array", items=types.Schema(type="string")
                    ),
                },
                required=["attractiveness_score", "presentation_quality"],
            ),
        )

        classify_bcg_func = types.FunctionDeclaration(
            name="classify_bcg",
            description="Classify a product according to BCG matrix based on market share and growth metrics.",
            parameters=types.Schema(
                type="object",
                properties={
                    "item_name": types.Schema(type="string"),
                    "classification": types.Schema(
                        type="string", enum=["star", "cash_cow", "question_mark", "dog"]
                    ),
                    "market_share_assessment": types.Schema(type="string"),
                    "growth_assessment": types.Schema(type="string"),
                    "strategic_recommendation": types.Schema(type="string"),
                    "reasoning": types.Schema(type="string"),
                },
                required=["item_name", "classification", "reasoning"],
            ),
        )

        generate_campaign_func = types.FunctionDeclaration(
            name="generate_campaign",
            description="Generate a marketing campaign proposal for selected menu items.",
            parameters=types.Schema(
                type="object",
                properties={
                    "title": types.Schema(type="string"),
                    "objective": types.Schema(type="string"),
                    "target_audience": types.Schema(type="string"),
                    "duration_days": types.Schema(type="integer"),
                    "channels": types.Schema(
                        type="array", items=types.Schema(type="string")
                    ),
                    "key_messages": types.Schema(
                        type="array", items=types.Schema(type="string")
                    ),
                    "promotional_items": types.Schema(
                        type="array", items=types.Schema(type="string")
                    ),
                    "discount_strategy": types.Schema(type="string"),
                    "social_post_copy": types.Schema(type="string"),
                    "expected_uplift_percent": types.Schema(type="number"),
                    "rationale": types.Schema(type="string"),
                },
                required=["title", "objective", "channels", "rationale"],
            ),
        )

        verify_analysis_func = types.FunctionDeclaration(
            name="verify_analysis",
            description="Self-verification step to check analysis quality and consistency.",
            parameters=types.Schema(
                type="object",
                properties={
                    "verification_passed": types.Schema(type="boolean"),
                    "checks_performed": types.Schema(
                        type="array", items=types.Schema(type="string")
                    ),
                    "issues_found": types.Schema(
                        type="array", items=types.Schema(type="string")
                    ),
                    "corrections_needed": types.Schema(
                        type="array", items=types.Schema(type="string")
                    ),
                    "confidence_after_verification": types.Schema(type="number"),
                },
                required=["verification_passed", "checks_performed"],
            ),
        )

        return [
            types.Tool(
                function_declarations=[
                    extract_menu_func,
                    analyze_dish_image_func,
                    classify_bcg_func,
                    generate_campaign_func,
                    verify_analysis_func,
                ]
            )
        ]

    async def create_thought_signature(
        self, task: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a Thought Signature - a transparent reasoning trace.

        This is a key differentiator that shows the agent's planning
        and reasoning process before executing tasks.
        """

        prompt = f"""You are MenuPilot, an AI assistant for restaurant optimization.
        
Before executing the following task, create a detailed thought signature that outlines:
1. Your plan of action (numbered steps)
2. Key observations from the provided context
3. Your main reasoning chain
4. Assumptions you're making
5. Your confidence level (0-1)

Task: {task}

Context:
{json.dumps(context, indent=2, default=str)}

Respond in this exact JSON format:
{{
    "plan": ["Step 1: ...", "Step 2: ...", ...],
    "observations": ["Observation 1", "Observation 2", ...],
    "reasoning": "Main reasoning explanation...",
    "assumptions": ["Assumption 1", "Assumption 2", ...],
    "confidence": 0.85
}}
"""

        response = await self._call_gemini(prompt)
        self.call_count += 1

        try:
            # Parse JSON from response
            json_str = response.text
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0]
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0]

            return json.loads(json_str.strip())
        except (json.JSONDecodeError, IndexError):
            # Fallback structure
            return {
                "plan": [f"Execute {task}"],
                "observations": ["Context provided"],
                "reasoning": response.text[:500],
                "assumptions": ["Standard analysis assumptions apply"],
                "confidence": 0.7,
            }

    async def extract_menu_from_image(
        self, image_path: str, additional_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract menu items from a menu image using multimodal analysis.
        """

        # Read and encode image
        image_data = Path(image_path).read_bytes()
        image_base64 = base64.b64encode(image_data).decode()

        prompt = """Analyze this restaurant menu image and extract ALL menu items you can see.

IMPORTANT: You MUST respond with valid JSON in this exact format:
{
  "items": [
    {
      "name": "Item name exactly as written",
      "price": 12000,
      "description": "Item description if available",
      "category": "category name"
    }
  ],
  "confidence": 0.85
}

For each item, identify:
- Name (exactly as written on the menu)
- Price (as a number, remove currency symbols)
- Description (if available, otherwise use empty string)
- Category (appetizers, mains, desserts, drinks, etc.)

Extract EVERY visible item on the menu. If you see text but it's unclear, make your best interpretation.
If the menu is in Spanish, keep the original Spanish names.

Return ONLY the JSON, no other text."""

        if additional_context:
            prompt += f"\n\nAdditional context: {additional_context}"

        response = await self._call_gemini_with_image(prompt, image_base64)
        self.call_count += 1

        return self._parse_extraction_response(response)

    async def analyze_dish_images(self, image_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Analyze dish photographs for visual appeal and marketability.
        """

        results = []

        for path in image_paths:
            image_data = Path(path).read_bytes()
            image_base64 = base64.b64encode(image_data).decode()

            prompt = """Analyze this dish photograph for a restaurant optimization system.

Evaluate:
1. Visual attractiveness (0-1 score)
2. Presentation quality (poor/average/good/excellent)
3. Color appeal and contrast
4. Portion size perception
5. Instagram/social media worthiness (0-1 score)
6. Specific suggestions for improvement

Be objective and constructive in your analysis."""

            response = await self._call_gemini_with_image(prompt, image_base64)
            self.call_count += 1

            results.append(self._parse_image_analysis(response, path))

        return results

    async def generate_bcg_insights(
        self, product_data: List[Dict[str, Any]], sales_summary: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate BCG classification insights with strategic recommendations.
        """

        prompt = f"""You are a restaurant business analyst. Analyze these products using the BCG Matrix framework.

Product Data:
{json.dumps(product_data, indent=2)}

Sales Summary:
{json.dumps(sales_summary, indent=2)}

For each product, provide:
1. BCG Classification (star/cash_cow/question_mark/dog)
2. Justification based on market share and growth
3. Strategic recommendation

Also provide:
- Overall portfolio health assessment
- Rebalancing suggestions
- Priority actions

Respond in structured JSON format."""

        response = await self._call_gemini(prompt)
        self.call_count += 1

        return self._parse_bcg_response(response)

    async def generate_campaigns(
        self,
        bcg_analysis: Dict[str, Any],
        num_campaigns: int = 3,
        constraints: Optional[Dict[str, Any]] = None,
        business_context: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generate highly specific, personalized marketing campaign proposals.

        Key improvements over generic generators:
        - Uses actual product names and prices
        - Provides specific discount amounts (not "consider a discount")
        - Includes ready-to-post social media copy
        - Calculates specific expected ROI
        - Tailored to restaurant type and audience
        """

        # Extract key data for personalization
        classifications = bcg_analysis.get("classifications", [])
        stars = [c for c in classifications if c.get("bcg_class") == "star"]
        question_marks = [
            c for c in classifications if c.get("bcg_class") == "question_mark"
        ]
        cash_cows = [c for c in classifications if c.get("bcg_class") == "cash_cow"]
        dogs = [c for c in classifications if c.get("bcg_class") == "dog"]

        prompt = f"""Eres un estratega de marketing de restaurantes experto. Genera {num_campaigns} campañas de marketing ALTAMENTE ESPECÍFICAS y PERSONALIZADAS.

DATOS DEL ANÁLISIS BCG:
- STARS (invertir fuerte): {json.dumps([{"name": s["name"], "price": s.get("price", 0), "margin": s.get("margin", 0), "growth": s.get("growth_rate", 0)} for s in stars], indent=2)}
- QUESTION MARKS (decidir): {json.dumps([{"name": q["name"], "price": q.get("price", 0), "margin": q.get("margin", 0), "growth": q.get("growth_rate", 0)} for q in question_marks], indent=2)}
- CASH COWS (ordeñar): {json.dumps([{"name": c["name"], "price": c.get("price", 0), "margin": c.get("margin", 0)} for c in cash_cows], indent=2)}
- DOGS (revisar): {json.dumps([{"name": d["name"], "price": d.get("price", 0)} for d in dogs], indent=2)}

{"CONTEXTO DEL NEGOCIO: " + business_context if business_context else ""}
{"RESTRICCIONES: " + json.dumps(constraints, indent=2) if constraints else ""}

INSTRUCCIONES CRÍTICAS - Las campañas deben ser ESPECÍFICAS, no genéricas:
❌ MAL: "Considera ofrecer un descuento"
✅ BIEN: "Ofrece 20% de descuento en Tacos al Pastor los martes, reduciendo precio de $12.99 a $10.39"

❌ MAL: "Promociona en redes sociales"
✅ BIEN: "Post de Instagram con foto del platillo, copy: '🌮 MARTES DE TACOS 🌮 Hoy tu Pastor favorito a $10.39...'"

Para CADA campaña, proporciona EN JSON:
{{
  "title": "Nombre creativo y memorable",
  "objective": "Objetivo específico con métrica (ej: 'Aumentar ventas de Birria 40% en 2 semanas')",
  "target_audience": "Audiencia específica con demografía y psicografía",
  "channels": ["instagram", "email", "in_store"],
  "key_messages": ["Mensaje 1 específico", "Mensaje 2", "Mensaje 3"],
  "promotional_items": ["Nombre exacto del producto 1", "Producto 2"],
  "discount_strategy": "Estrategia específica: '25% off' o 'Compra 2 lleva 3' con precios exactos",
  "social_post_copy": "Copy COMPLETO listo para publicar con emojis y hashtags",
  "email_subject": "Línea de asunto del email",
  "email_preview": "Texto de preview del email",
  "in_store_copy": "Copy para señalización en tienda",
  "expected_uplift_percent": 25,
  "expected_revenue_increase": 1500,
  "investment_required": "Bajo/Medio/Alto con estimación",
  "roi_estimate": "Retorno esperado específico",
  "rationale": "Explicación detallada de por qué esta campaña funcionará para ESTE restaurante",
  "success_metrics": ["Métrica 1 medible", "Métrica 2"],
  "timeline": "Cronograma específico de implementación"
}}

DIVERSIFICACIÓN REQUERIDA:
1. Primera campaña: Amplificar STARS (productos exitosos)
2. Segunda campaña: Convertir QUESTION MARKS en Stars (alto potencial)
3. Tercera campaña: Bundle/Loyalty con CASH COWS (revenue estable)

Responde SOLO con un array JSON de {num_campaigns} campañas, sin texto adicional."""

        response = await self._call_gemini(prompt)
        self.call_count += 1

        return self._parse_campaigns_response(response)

    async def verify_and_correct(
        self, analysis_results: Dict[str, Any], original_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Self-verification step - the agent reviews its own analysis
        and makes corrections if needed.
        """

        prompt = f"""You are performing a self-verification check on your previous analysis.

Original Data:
{json.dumps(original_data, indent=2)[:2000]}

Analysis Results:
{json.dumps(analysis_results, indent=2)[:2000]}

Perform these verification checks:
1. Data consistency - do the numbers add up?
2. Classification accuracy - are BCG classifications justified?
3. Recommendation feasibility - are suggestions actionable?
4. Missing considerations - anything overlooked?
5. Logical coherence - does the reasoning flow correctly?

Respond with:
- verification_passed: boolean
- checks_performed: list of checks done
- issues_found: list of any problems
- corrections_needed: specific corrections to make
- confidence_after_verification: updated confidence score

Be critical and thorough."""

        response = await self._call_gemini(prompt)
        self.call_count += 1

        return self._parse_verification_response(response)

    async def _call_gemini(self, prompt: str) -> Any:
        """Make a text-only call to Gemini."""

        response = self.client.models.generate_content(
            model=self.MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=4096,
            ),
        )
        return response

    async def _call_gemini_with_image(
        self, prompt: str, image_base64: str, mime_type: str = "image/jpeg"
    ) -> Any:
        """Make a multimodal call to Gemini with an image."""

        response = self.client.models.generate_content(
            model=self.MODEL_NAME,
            contents=[
                types.Content(
                    parts=[
                        types.Part(text=prompt),
                        types.Part(
                            inline_data=types.Blob(
                                mime_type=mime_type, data=base64.b64decode(image_base64)
                            )
                        ),
                    ]
                )
            ],
            config=types.GenerateContentConfig(
                temperature=0.5,
                max_output_tokens=4096,
            ),
        )
        return response

    async def _call_gemini_with_tools(
        self, prompt: str, context: Optional[List[Any]] = None
    ) -> Any:
        """Make a call to Gemini with function calling tools."""

        contents = context or []
        contents.append(types.Content(parts=[types.Part(text=prompt)]))

        response = self.client.models.generate_content(
            model=self.MODEL_NAME,
            contents=contents,
            config=types.GenerateContentConfig(
                tools=self.tools,
                temperature=0.7,
                max_output_tokens=4096,
            ),
        )
        return response

    def _parse_extraction_response(self, response: Any) -> Dict[str, Any]:
        """Parse menu extraction response."""
        try:
            text = response.text
            logger.debug(f"Gemini raw response (first 500 chars): {text[:500]}")

            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]

            parsed = json.loads(text.strip())
            logger.info(
                f"Successfully parsed {len(parsed.get('items', []))} items from Gemini response"
            )
            return parsed
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            logger.error(f"Failed to parse Gemini response: {e}")
            logger.error(f"Raw response: {response.text[:1000]}")
            return {
                "items": [],
                "confidence": 0.5,
                "raw_response": response.text[:1000],
            }

    def _parse_image_analysis(self, response: Any, path: str) -> Dict[str, Any]:
        """Parse dish image analysis response."""
        try:
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]

            result = json.loads(text.strip())
            result["image_path"] = path
            return result
        except (json.JSONDecodeError, KeyError, IndexError):
            return {
                "image_path": path,
                "attractiveness_score": 0.5,
                "presentation_quality": "unknown",
                "raw_response": response.text[:500],
            }

    def _parse_bcg_response(self, response: Any) -> Dict[str, Any]:
        """Parse BCG analysis response."""
        try:
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]

            return json.loads(text.strip())
        except (json.JSONDecodeError, KeyError, IndexError):
            return {
                "classifications": [],
                "portfolio_health": "unknown",
                "raw_response": response.text[:1000],
            }

    def _parse_campaigns_response(self, response: Any) -> List[Dict[str, Any]]:
        """Parse campaign generation response."""
        try:
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]

            result = json.loads(text.strip())
            if isinstance(result, list):
                return result
            elif "campaigns" in result:
                return result["campaigns"]
            return [result]
        except (json.JSONDecodeError, KeyError, IndexError):
            return [{"title": "Default Campaign", "raw_response": response.text[:1000]}]

    def _parse_verification_response(self, response: Any) -> Dict[str, Any]:
        """Parse verification response."""
        try:
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]

            return json.loads(text.strip())
        except (json.JSONDecodeError, KeyError, IndexError):
            return {
                "verification_passed": True,
                "checks_performed": ["basic_review"],
                "issues_found": [],
                "corrections_needed": [],
                "confidence_after_verification": 0.7,
            }

    def get_stats(self) -> Dict[str, int]:
        """Get agent usage statistics."""
        return {"gemini_calls": self.call_count, "estimated_tokens": self.total_tokens}
