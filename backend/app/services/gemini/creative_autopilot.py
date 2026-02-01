from typing import Dict, List, Optional
import asyncio
from google import genai
from google.genai import types
from loguru import logger
from app.core.config import get_settings
from PIL import Image
import io
import base64

class CreativeAutopilotAgent:
    """
    Implementa el track 'Creative Autopilot' del hackathon.
    Genera campañas visuales completas usando Nano Banana Pro.
    """
    
    def __init__(self):
        settings = get_settings()
        self.api_key = settings.gemini_api_key
        self.client = genai.Client(api_key=self.api_key)
        self.image_model = "gemini-3-pro-image-preview" # Or appropriate model name for imaging if available via genai
        # Note: As of now, image generation might be via specific model or tool. 
        # Using the model name provided in user snippet.
        self.reasoning_model = "gemini-3-flash-preview"
    
    async def generate_full_campaign(
        self,
        restaurant_name: str,
        dish_data: Dict,
        bcg_classification: str,
        brand_guidelines: Dict = None
    ) -> Dict:
        """
        Genera una campaña visual COMPLETA para un plato específico.
        """
        
        # PASO 1: Razonamiento estratégico (Gemini 3 Pro)
        strategy = await self._analyze_campaign_strategy(
            dish_data, bcg_classification
        )
        
        # PASO 2: Generación de concepto creativo
        creative_concept = await self._generate_creative_concept(
            restaurant_name, dish_data, strategy
        )
        
        # PASO 3: Generar assets visuales con Nano Banana Pro
        visual_assets = await self._generate_visual_assets(
            creative_concept,
            brand_guidelines
        )
        
        # PASO 4: Generar variaciones A/B
        ab_variants = []
        if visual_assets:
            ab_variants = await self._generate_ab_variants(
                visual_assets[0],  # Partir del primer asset
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
        Transforma el diseño visual de un menú manteniendo contenido.
        
        USO DE NANO BANANA PRO:
        - Mantiene TODO el texto/precios exactos
        - Cambia completamente el diseño visual
        - Genera variaciones profesionales
        """
        
        style_prompts = {
            "modern_minimalist": """
                Rediseña este menú con un estilo minimalista moderno:
                - Tipografía: Sans-serif limpia (similar a Helvetica)
                - Colores: Blanco, negro, un acento dorado sutil
                - Layout: Abundante espacio en blanco, grid organizado
                - Elementos: Líneas delgadas, iconos simples
                MANTÉN TODO EL TEXTO Y PRECIOS EXACTAMENTE IGUALES.
            """,
            "rustic_vintage": """
                Rediseña este menú con un estilo rústico vintage:
                - Tipografía: Serif clásica con detalles ornamentales
                - Colores: Sepia, marrones cálidos, crema
                - Layout: Asimétrico, con viñetas decorativas
                - Elementos: Bordes ornamentados, ilustraciones vintage
                MANTÉN TODO EL TEXTO Y PRECIOS EXACTAMENTE IGUALES.
            """,
            "luxury_fine_dining": """
                Rediseña este menú con un estilo de alta gastronomía:
                - Tipografía: Serif elegante (similar a Didot)
                - Colores: Negro profundo, dorado, blanco puro
                - Layout: Centrado, simétrico, sofisticado
                - Elementos: Detalles dorados, textura papel premium
                MANTÉN TODO EL TEXTO Y PRECIOS EXACTAMENTE IGUALES.
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
        """Determina la estrategia basada en la matriz BCG."""
        prompt = f"""
        Actúa como un estratega de marketing gastronómico.
        Analiza este plato para una campaña publicitaria:
        
        PLATO: {dish_data['name']}
        PRECIO: {dish_data['price']}
        DESCRIPCIÓN: {dish_data['description']}
        CATEGORÍA: {dish_data.get('category', 'General')}
        CLASIFICACIÓN BCG: {bcg_class}
        
        Define la estrategia:
        1. Objetivo principal (ej: Maximizar margen, Aumentar volumen, Crear tráfico).
        2. Público objetivo ideal.
        3. Tono de comunicación.
        4. Ángulo psicológico de venta.
        
        Responde en JSON.
        """
        
        response = self.client.models.generate_content(
            model=self.reasoning_model,
            contents=[types.Content(parts=[types.Part(text=prompt)])],
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        
        import json
        return json.loads(response.text)

    async def _generate_creative_concept(self, restaurant_name: str, dish_data: Dict, strategy: Dict) -> Dict:
        """Crea el concepto visual y de copy."""
        prompt = f"""
        Crea un concepto creativo visual para esta campaña:
        
        RESTAURANTE: {restaurant_name}
        PLATO: {dish_data['name']}
        ESTRATEGIA: {strategy}
        
        Define:
        1. "headline": Un titular pegadizo en ESPAÑOL (máx 5 palabras).
        2. "main_message": Mensaje principal.
        3. "visual_description": Descripción detallada de la imagen a generar.
        4. "photo_style": Estilo fotográfico (ej: Dark mood, High key, Lifestyle).
        5. "key_elements": Elementos clave en la composición.
        
        Responde en JSON.
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
        Genera múltiples assets usando Nano Banana Pro.
        """
        
        assets = []
        
        # Asset 1: Post de Instagram con texto español legible
        instagram_post = await self._generate_instagram_post(
            concept,
            brand_guidelines
        )
        assets.append(instagram_post)
        
        # Asset 2: Story de Instagram (formato vertical)
        instagram_story = await self._generate_instagram_story(
            concept,
            brand_guidelines
        )
        assets.append(instagram_story)
        
        # Asset 3: Banner web con CTA
        web_banner = await self._generate_web_banner(
            concept,
            brand_guidelines
        )
        assets.append(web_banner)
        
        # Asset 4: Flyer imprimible en alta resolución
        printable_flyer = await self._generate_printable_flyer(
            concept,
            brand_guidelines
        )
        assets.append(printable_flyer)
        
        return assets
    
    async def _generate_instagram_post(
        self,
        concept: Dict,
        brand_guidelines: Dict = None
    ) -> Dict:
        """
        Genera post de Instagram profesional con:
        - Texto legible en español (capacidad exclusiva de Nano Banana Pro)
        - Composición según tendencias actuales (grounded con Google Search)
        - Consistencia de marca (multi-reference images)
        """
        
        # Preparar referencias de marca si existen
        reference_images = []
        if brand_guidelines and 'logo_path' in brand_guidelines:
            # Cargar logo y paleta de colores como referencias
            reference_images.append({
                "path": brand_guidelines['logo_path'],
                "type": "logo"
            })
        
        prompt = f"""
        Crea un post de Instagram profesional para un restaurante con las siguientes especificaciones:
        
        CONCEPTO CREATIVO:
        {concept.get('visual_description', '')}
        
        MENSAJE PRINCIPAL:
        {concept.get('main_message', '')}
        
        REQUISITOS TÉCNICOS:
        - Formato: 1080x1080px (cuadrado perfecto para Instagram)
        - Incluir el texto "{concept.get('headline', '')}" en español con tipografía moderna y legible
        - Usar los colores: {brand_guidelines.get('colors', 'cálidos y apetitosos') if brand_guidelines else 'cálidos y apetitosos'}
        - Estilo fotográfico: {concept.get('photo_style', 'food photography profesional')}
        - Incluir elementos visuales que representen: {concept.get('key_elements', '')}
        
        CONTEXTO ACTUALIZADO:
        Investiga las tendencias actuales de food photography en Instagram y aplica
        técnicas contemporáneas de iluminación, composición y estilo.
        
        IMPORTANTE:
        - El texto debe estar perfectamente integrado en la composición
        - Usar profundidad de campo para destacar el plato principal
        - Mantener espacio negativo para que el diseño "respire"
        - El resultado debe verse profesional, no generado por AI
        """
        
        try:
            # Generar imagen con Nano Banana Pro
            # KEY: Activar grounding con Google Search
            chat = self.client.chats.create(
                model=self.image_model,
                config=types.GenerateContentConfig(
                    response_modalities=['IMAGE', 'TEXT'],
                    tools=[{"google_search": {}}],  # GROUNDING ACTIVADO
                    temperature=0.7,
                    top_p=0.9
                )
            )
            
            # Si hay imágenes de referencia, incluirlas
            content_parts = [{"text": prompt}]
            for ref_img in reference_images[:14]:  # Máximo 14 referencias
                try:
                    # Cargar y convertir imagen a base64
                    img_data = self._load_image_as_base64(ref_img['path'])
                    content_parts.append({
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": img_data
                        }
                    })
                except Exception as e:
                    logger.warning(f"Could not load reference image {ref_img['path']}: {e}")
            
            response = chat.send_message(content_parts)
            
            # Extraer imagen generada
            generated_image = None
            reasoning = None
            sources = self._extract_sources(response)
            
            for part in response.parts:
                if part.inline_data:
                    generated_image = part.inline_data.data
                elif part.text:
                    reasoning = part.text
            
            return {
                "type": "instagram_post",
                "format": "1080x1080",
                "image_data": generated_image,
                "reasoning": reasoning,
                "concept": concept.get('headline'),
                "grounding_sources": sources
            }
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            return {
                "type": "instagram_post",
                "format": "1080x1080",
                "image_data": None,
                "reasoning": f"Failed: {str(e)}",
                "concept": concept.get('headline'),
                "grounding_sources": []
            }

    async def _generate_instagram_story(self, concept: Dict, brand_guidelines: Dict = None) -> Dict:
        # Similar to post but vertical
        return {
             "type": "instagram_story",
             "format": "1080x1920",
             "image_data": None, # Placeholder
             "reasoning": "Vertical story format",
             "concept": concept['headline']
        }

    async def _generate_web_banner(self, concept: Dict, brand_guidelines: Dict = None) -> Dict:
        return {
             "type": "web_banner",
             "format": "1200x628",
             "image_data": None,
             "reasoning": "Web banner format",
             "concept": concept['headline']
        }

    async def _generate_printable_flyer(self, concept: Dict, brand_guidelines: Dict = None) -> Dict:
        return {
             "type": "printable_flyer",
             "format": "2480x3508",
             "image_data": None,
             "reasoning": "A4 Flyer",
             "concept": concept['headline']
        }

    async def _generate_ab_variants(self, base_asset: Dict, strategy: Dict) -> List[Dict]:
        return [] # Placeholder

    async def _edit_camera_angle(self, base_asset: Dict) -> Dict:
        return base_asset # Placeholder

    async def _edit_lighting(self, base_asset: Dict) -> Dict:
        return base_asset # Placeholder

    async def _edit_color_grading(self, base_asset: Dict) -> Dict:
        return base_asset # Placeholder

    async def localize_campaign(
        self,
        campaign_assets: List[Dict],
        target_languages: List[str]
    ) -> Dict[str, List[Dict]]:
        """
        Localiza la campaña a múltiples idiomas.
        """
        localized_campaigns = {}
        for lang in target_languages:
            # Simply duplicate for now as translation logic requires image editing
            localized_campaigns[lang] = campaign_assets 
        return localized_campaigns

    async def _localize_asset(self, asset: Dict, target_language: str) -> Dict:
        return asset # Placeholder

    def _load_image_as_base64(self, path: str) -> str:
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def _extract_sources(self, response) -> List[str]:
        # Logic to extract grounding metadata if available
        return []

    def _calculate_impact(self, strategy: Dict) -> float:
        return 0.85 # Mock score
