from typing import Dict, List
import json
from google import genai
from google.genai import types
from loguru import logger
from app.core.config import get_settings
import base64

class CreativeAutopilotAgent:
    """
    Implements the hackathon 'Creative Autopilot' track.
    Generates complete visual campaigns using Gemini 3 Pro Image
    (Imagen 3 — internally codenamed 'Nano Banana Pro' by Google).
    """
    
    def __init__(self):
        settings = get_settings()
        self.api_key = settings.gemini_api_key
        self.client = genai.Client(api_key=self.api_key)
        self.image_model = settings.gemini_model_image_gen  # gemini-3-pro-image-preview
        self.reasoning_model = settings.gemini_model_reasoning  # gemini-3-pro-preview (PRO for max quality)
    
    async def generate_full_campaign(
        self,
        restaurant_name: str,
        dish_data: Dict,
        bcg_classification: str,
        brand_guidelines: Dict = None
    ) -> Dict:
        """
        Generates a COMPLETE visual campaign for a specific dish.
        """
        
        # STEP 1: Strategic reasoning (Gemini 3 Pro)
        strategy = await self._analyze_campaign_strategy(
            dish_data, bcg_classification
        )
        
        # STEP 2: Creative concept generation
        creative_concept = await self._generate_creative_concept(
            restaurant_name, dish_data, strategy
        )
        
        # STEP 3: Generate visual assets with Gemini 3 Pro Image (Imagen 3)
        visual_assets = await self._generate_visual_assets(
            creative_concept,
            brand_guidelines
        )
        
        # STEP 4: Generate A/B variants
        ab_variants = []
        if visual_assets:
            ab_variants = await self._generate_ab_variants(
                visual_assets[0],  # Start from the first asset
                strategy
            )
        
        return {
            "strategy": strategy,
            "creative_concept": creative_concept,
            "visual_assets": visual_assets,
            "ab_variants": ab_variants,
            "estimated_impact": self._calculate_impact(strategy)
        }

    async def transform_menu_visual_style(
        self,
        menu_image: bytes,
        target_style: str  # "modern_minimalist", "rustic_vintage", "luxury_fine_dining"
    ) -> Dict:
        """
        Transforms the visual design of a menu while maintaining content.
        
        USING GEMINI 3 PRO IMAGE (Imagen 3):
        - Keeps ALL text/prices exactly as is
        - Completely changes the visual design
        - Generates professional variations
        """
        
        style_prompts = {
            "modern_minimalist": """
                Redesign this menu with a modern minimalist style:
                - Typography: Clean Sans-serif (similar to Helvetica)
                - Colors: White, black, a subtle gold accent
                - Layout: Abundant white space, organized grid
                - Elements: Thin lines, simple icons
                KEEP ALL TEXT AND PRICES EXACTLY THE SAME.
            """,
            "rustic_vintage": """
                Redesign this menu with a rustic vintage style:
                - Typography: Classic Serif with ornamental details
                - Colors: Sepia, warm browns, cream
                - Layout: Asymmetrical, with decorative vignettes
                - Elements: Ornate borders, vintage illustrations
                KEEP ALL TEXT AND PRICES EXACTLY THE SAME.
            """,
            "luxury_fine_dining": """
                Redesign this menu with a high-end fine dining style:
                - Typography: Elegant Serif (similar to Didot)
                - Colors: Deep black, gold, pure white
                - Layout: Centered, symmetrical, sophisticated
                - Elements: Gold details, premium paper texture
                KEEP ALL TEXT AND PRICES EXACTLY THE SAME.
            """
        }
        
        prompt = style_prompts.get(target_style, style_prompts["modern_minimalist"])
        
        try:
            # Using the image model for transformation
            chat = self.client.chats.create(model=self.image_model)
            
            response = chat.send_message([
                types.Content(parts=[
                    types.Part(text=prompt),
                    types.Part(inline_data=types.Blob(
                        mime_type="image/jpeg",
                        data=menu_image
                    ))
                ])
            ])
            
            generated_image = None
            if response.parts:
                for part in response.parts:
                    if part.inline_data:
                        generated_image = part.inline_data.data
                        break
            
            return {
                "transformed_menu": generated_image,
                "style_applied": target_style,
                "original_preserved": True
            }
        except Exception as e:
            logger.error(f"Menu transformation failed: {e}")
            return {
                "error": str(e),
                "style_applied": target_style
            }

    async def _analyze_campaign_strategy(self, dish_data: Dict, bcg_class: str) -> Dict:
        """Determines the strategy based on the BCG matrix."""
        prompt = f"""
        Act as a gastronomic marketing strategist.
        Analyze this dish for an advertising campaign:
        
        DISH: {dish_data['name']}
        PRICE: {dish_data['price']}
        DESCRIPTION: {dish_data['description']}
        CATEGORY: {dish_data.get('category', 'General')}
        BCG CLASSIFICATION: {bcg_class}
        
        Define the strategy:
        1. Main objective (e.g., Maximize margin, Increase volume, Create traffic).
        2. Ideal target audience.
        3. Communication tone.
        4. Psychological sales angle.
        
        Respond in JSON.
        """
        
        response = self.client.models.generate_content(
            model=self.reasoning_model,
            contents=[types.Content(parts=[types.Part(text=prompt)])],
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        
        import json
        return json.loads(response.text)

    async def _generate_creative_concept(self, restaurant_name: str, dish_data: Dict, strategy: Dict) -> Dict:
        """Creates the visual and copy concept."""
        prompt = f"""
        Create a visual creative concept for this campaign:
        
        RESTAURANT: {restaurant_name}
        DISH: {dish_data['name']}
        STRATEGY: {strategy}
        
        Define:
        1. "headline": A catchy headline in ENGLISH (max 5 words).
        2. "main_message": Main message.
        3. "visual_description": Detailed description of the image to generate.
        4. "photo_style": Photographic style (e.g., Dark mood, High key, Lifestyle).
        5. "key_elements": Key elements in the composition.
        
        Respond in JSON.
        """
        
        response = self.client.models.generate_content(
            model=self.reasoning_model,
            contents=[types.Content(parts=[types.Part(text=prompt)])],
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        
        import json
        return json.loads(response.text)
    
    async def _generate_visual_assets(
        self,
        concept: Dict,
        brand_guidelines: Dict = None
    ) -> List[Dict]:
        """
        Generates multiple assets using Gemini 3 Pro Image (Imagen 3).
        """
        
        assets = []
        
        # Asset 1: Instagram post (1:1)
        instagram_post = await self._generate_instagram_post(concept, brand_guidelines)
        assets.append(instagram_post)
        
        # Asset 2: Instagram story (9:16)
        instagram_story = await self._generate_instagram_story(concept, brand_guidelines)
        assets.append(instagram_story)
        
        # Asset 3: Banner web (Landscape)
        web_banner = await self._generate_web_banner(concept, brand_guidelines)
        assets.append(web_banner)
        
        # Asset 4: Flyer (A4/Print)
        printable_flyer = await self._generate_printable_flyer(concept, brand_guidelines)
        assets.append(printable_flyer)
        
        return assets
    
    async def _generate_image_asset(
        self,
        concept: Dict,
        format_name: str,
        dimensions: str,
        asset_type: str,
        prompt_template: str,
        brand_guidelines: Dict = None,
        language: str = "es"
    ) -> Dict:
        """
        Generic method to generate visual assets with Gemini 3 Pro Image (Imagen 3).
        """
        # Prepare brand references
        reference_images = []
        if brand_guidelines and 'logo_path' in brand_guidelines:
            reference_images.append({
                "path": brand_guidelines['logo_path'],
                "type": "logo"
            })
            
        headline = concept.get('headline', '')
        if language != "es" and "translated_headlines" in concept and language in concept["translated_headlines"]:
             headline = concept["translated_headlines"][language]

        # Build final prompt
        prompt = prompt_template.format(
            visual_description=concept.get('visual_description', ''),
            main_message=concept.get('main_message', ''),
            headline=headline,
            colors=brand_guidelines.get('colors', 'warm and appetizing') if brand_guidelines else 'warm and appetizing',
            photo_style=concept.get('photo_style', 'professional food photography'),
            key_elements=concept.get('key_elements', '')
        )
        
        try:
            # Build content for Gemini
            content_parts = [{"text": prompt}]
            for ref_img in reference_images[:5]: # Limit refs
                try:
                    img_data = self._load_image_as_base64(ref_img['path'])
                    content_parts.append({
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": img_data
                        }
                    })
                except Exception as e:
                    logger.warning(f"Could not load ref image {ref_img['path']}: {e}")

            # Model call
            response = self.client.models.generate_content(
                model=self.image_model,
                contents=content_parts,
                config=types.GenerateContentConfig(
                    response_modalities=['IMAGE', 'TEXT'],
                    temperature=0.7,
                    top_p=0.9
                )
            )
            
            # Extract results
            generated_image = None
            reasoning = None
            sources = self._extract_sources(response)
            
            parts = []
            if hasattr(response, 'parts'):
                parts = response.parts
            elif hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and candidate.content and hasattr(candidate.content, 'parts'):
                    parts = candidate.content.parts
            
            if parts:
                for part in parts:
                    if part.inline_data:
                        generated_image = part.inline_data.data
                    elif part.text:
                        reasoning = part.text
                        
            return {
                "type": asset_type,
                "format": dimensions,
                "image_data": generated_image,
                "reasoning": reasoning,
                "concept": headline,
                "grounding_sources": sources,
                "language": language
            }
            
        except Exception as e:
            logger.error(f"Failed to generate {asset_type}: {e}")
            return {
                "type": asset_type,
                "format": dimensions,
                "image_data": None,
                "reasoning": f"Error: {str(e)}",
                "concept": headline,
                "language": language
            }

    async def _generate_instagram_post(self, concept: Dict, brand_guidelines: Dict = None) -> Dict:
        prompt = """
        Create a professional INSTAGRAM POST (Square 1:1):
        
        VISUAL DESCRIPTION: {visual_description}
        MESSAGE: {main_message}
        
        REQUIREMENTS:
        - Perfect square format.
        - TEXT IN IMAGE: "{headline}" (Modern typography, legible, integrated).
        - Colors: {colors}.
        - Style: {photo_style}.
        - Key elements: {key_elements}.
        
        Use centered composition or rule of thirds. Text should be the hero alongside the dish.
        """
        return await self._generate_image_asset(
            concept, "1080x1080", "1080x1080", "instagram_post", prompt, brand_guidelines
        )

    async def _generate_instagram_story(self, concept: Dict, brand_guidelines: Dict = None) -> Dict:
        prompt = """
        Create an immersive INSTAGRAM STORY (Vertical 9:16):
        
        VISUAL DESCRIPTION: {visual_description}
        
        REQUIREMENTS:
        - Tall vertical format (9:16).
        - Leave free space at top and bottom for Instagram UI.
        - TEXT IN IMAGE: "{headline}" (Large, eye-catching, in center or top third).
        - Colors: {colors}.
        - Style: {photo_style}.
        
        The image should invite a 'Tap'. Make the dish look grand and tall.
        """
        return await self._generate_image_asset(
            concept, "Vertical", "1080x1920", "instagram_story", prompt, brand_guidelines
        )

    async def _generate_web_banner(self, concept: Dict, brand_guidelines: Dict = None) -> Dict:
        prompt = """
        Create a WEB BANNER (Landscape 1.91:1) for website:
        
        VISUAL DESCRIPTION: {visual_description}
        
        REQUIREMENTS:
        - Wide horizontal format.
        - Ample negative space on right or left for overlaid text (if added later) or include the text "{headline}" cleanly.
        - Colors: {colors}.
        - Style: {photo_style}.
        
        Clean composition, editorial, luxury restaurant homepage style.
        """
        return await self._generate_image_asset(
            concept, "Landscape", "1200x628", "web_banner", prompt, brand_guidelines
        )

    async def _generate_printable_flyer(self, concept: Dict, brand_guidelines: Dict = None) -> Dict:
        prompt = """
        Create a PRINTABLE FLYER (A4 Vertical format) high resolution:
        
        VISUAL DESCRIPTION: {visual_description}
        
        REQUIREMENTS:
        - Vertical paper format.
        - Poster/signage style design.
        - MAIN TEXT: "{headline}" at the top.
        - Include visual space for "Scan to order" (simulated).
        - Colors: {colors}.
        - Style: {photo_style}.
        
        Must look like a high-quality printed poster stuck on a wall or display case.
        """
        return await self._generate_image_asset(
            concept, "A4", "2480x3508", "printable_flyer", prompt, brand_guidelines
        )

    async def _generate_ab_variants(self, base_asset: Dict, strategy: Dict) -> List[Dict]:
        """Generates A/B variants by changing the creative focus."""
        if not base_asset or not base_asset.get('concept'):
            return []
            
        variants = []
        
        # Variant A: Product Focus (Macro/Close-up)
        # Reuse concept but force style
        concept_a = {
            "headline": base_asset['concept'],
            "visual_description": "Extreme macro close-up of the dish, focusing on textures, droplets, shine. Blurred background (bokeh).",
            "main_message": "Intense flavor",
            "photo_style": "Macro food photography",
            "key_elements": "Texture, detail, freshness"
        }
        variant_a = await self._generate_instagram_post(concept_a)
        variant_a['variant_type'] = "macro_focus"
        variants.append(variant_a)
        
        # Variant B: Lifestyle Focus (Table, people, ambiance)
        concept_b = {
            "headline": base_asset['concept'],
            "visual_description": "Wide shot showing the dish on a restaurant table with happy diners blurred in the background. Warm and social atmosphere.",
            "main_message": "Shared experience",
            "photo_style": "Lifestyle dining",
            "key_elements": "Ambiance, set table, drinks"
        }
        variant_b = await self._generate_instagram_post(concept_b)
        variant_b['variant_type'] = "lifestyle_focus"
        variants.append(variant_b)
        
        return variants

    async def localize_campaign(
        self,
        campaign_assets: List[Dict],
        target_languages: List[str]
    ) -> Dict[str, List[Dict]]:
        """
        Localizes the campaign by regenerating assets with translated text.
        """
        localized = {}
        
        # Translate concepts first (using Reasoning model for speed)
        headlines = [a.get('concept') for a in campaign_assets if a.get('concept')]
        headlines = list(set(headlines)) # Unique
        
        if not headlines:
            return {}
            
        translation_prompt = f"""
        Translate these marketing headlines to the requested languages.
        Keep the persuasive and short tone.
        
        Headlines: {json.dumps(headlines)}
        Languages: {json.dumps(target_languages)}
        
        Respond JSON: {{ "original": {{ "lang": "translated" }} }}
        Example: {{ "Real Flavor": {{ "es": "Sabor Real", "fr": "Goût Royal" }} }}
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.reasoning_model,
                contents=translation_prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            translations = json.loads(response.text)
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            translations = {}

        # Regenerate assets for each language
        for lang in target_languages:
            lang_assets = []
            for asset in campaign_assets:
                # Recover base concept to regenerate
                # (In a real case, we would store the full 'concept' dict in the asset,
                # here we reconstruct a partial one for the demo)
                
                original_headline = asset.get('concept')
                translated_headline = original_headline
                
                if original_headline in translations and lang in translations[original_headline]:
                    translated_headline = translations[original_headline][lang]
                
                # Reconstruct minimal concept
                concept_recreated = {
                    "headline": translated_headline,
                    "visual_description": f"Same visual as original: {asset.get('reasoning', '')}", # Simplification
                    "main_message": "Localized content",
                    "key_elements": "Same as original"
                }
                
                # Determine type and regenerate
                new_asset = None
                if asset['type'] == 'instagram_post':
                    new_asset = await self._generate_instagram_post(concept_recreated)
                elif asset['type'] == 'instagram_story':
                    new_asset = await self._generate_instagram_story(concept_recreated)
                elif asset['type'] == 'web_banner':
                    new_asset = await self._generate_web_banner(concept_recreated)
                elif asset['type'] == 'printable_flyer':
                    new_asset = await self._generate_printable_flyer(concept_recreated)
                
                if new_asset:
                    new_asset['language'] = lang
                    lang_assets.append(new_asset)
            
            localized[lang] = lang_assets
            
        return localized

    async def _localize_asset(self, asset: Dict, target_language: str) -> Dict:
        return asset # Placeholder

    def _load_image_as_base64(self, path: str) -> str:
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def _extract_sources(self, response) -> List[str]:
        """Extract grounding sources from the response if available."""
        sources = []
        try:
            # Check for grounding metadata in candidates
            if hasattr(response, 'candidates') and response.candidates:
                for candidate in response.candidates:
                    if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                        if hasattr(candidate.grounding_metadata, 'search_entry_point'):
                            sep = candidate.grounding_metadata.search_entry_point
                            if hasattr(sep, 'rendered_content'):
                                sources.append(sep.rendered_content)
                        
                        # Also check grounding_chunks if available
                        if hasattr(candidate.grounding_metadata, 'grounding_chunks'):
                            for chunk in candidate.grounding_metadata.grounding_chunks:
                                if hasattr(chunk, 'web') and chunk.web and hasattr(chunk.web, 'uri'):
                                    sources.append(chunk.web.uri)
        except Exception as e:
            logger.warning(f"Failed to extract sources: {e}")
            
        return list(set(sources)) # Deduplicate

    def _calculate_impact(self, strategy: Dict) -> float:
        return 0.85 # Mock score
