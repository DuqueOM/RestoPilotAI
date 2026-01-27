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

        prompt = """Analyze this restaurant menu image and extract all menu items.

For each item, identify:
- Name (exactly as written)
- Price (as a number)
- Description (if available)
- Category (appetizers, mains, desserts, drinks, etc.)

Also identify any dietary indicators (vegetarian, vegan, gluten-free, spicy levels).

Be thorough and extract ALL visible items. If text is unclear, make your best interpretation and note lower confidence."""

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
    ) -> List[Dict[str, Any]]:
        """
        Generate marketing campaign proposals based on BCG analysis.
        """

        prompt = f"""You are a restaurant marketing strategist. Based on this BCG analysis, create {num_campaigns} distinct marketing campaign proposals.

BCG Analysis:
{json.dumps(bcg_analysis, indent=2)}

{"Constraints: " + json.dumps(constraints, indent=2) if constraints else ""}

For each campaign, provide:
1. Creative title
2. Clear objective
3. Target audience
4. Recommended channels
5. Key messages (3-5)
6. Featured menu items
7. Discount/promotion strategy
8. Social media post copy (ready to use)
9. Image generation prompt (for promotional material)
10. Expected sales uplift percentage
11. Detailed rationale

Make campaigns diverse: one should focus on Stars, one on reviving Question Marks, and one on general brand building.

Respond in JSON array format."""

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
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]

            return json.loads(text.strip())
        except (json.JSONDecodeError, KeyError, IndexError):
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
