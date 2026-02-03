from typing import Dict, List
import json
from google import genai
from google.genai import types
from loguru import logger
from app.core.config import get_settings
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
        self.image_model = "gemini-3-pro-image-preview" 
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
        
        # Asset 1: Post de Instagram (1:1)
        instagram_post = await self._generate_instagram_post(concept, brand_guidelines)
        assets.append(instagram_post)
        
        # Asset 2: Story de Instagram (9:16)
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
        Método genérico para generar assets visuales con Nano Banana Pro.
        """
        # Preparar referencias de marca
        reference_images = []
        if brand_guidelines and 'logo_path' in brand_guidelines:
            reference_images.append({
                "path": brand_guidelines['logo_path'],
                "type": "logo"
            })
            
        headline = concept.get('headline', '')
        if language != "es" and "translated_headlines" in concept and language in concept["translated_headlines"]:
             headline = concept["translated_headlines"][language]

        # Construir prompt final
        prompt = prompt_template.format(
            visual_description=concept.get('visual_description', ''),
            main_message=concept.get('main_message', ''),
            headline=headline,
            colors=brand_guidelines.get('colors', 'cálidos y apetitosos') if brand_guidelines else 'cálidos y apetitosos',
            photo_style=concept.get('photo_style', 'food photography profesional'),
            key_elements=concept.get('key_elements', '')
        )
        
        try:
            # Construir contenido para Gemini
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

            # Llamada al modelo
            response = self.client.models.generate_content(
                model=self.image_model,
                contents=content_parts,
                config=types.GenerateContentConfig(
                    response_modalities=['IMAGE', 'TEXT'],
                    temperature=0.7,
                    top_p=0.9
                )
            )
            
            # Extraer resultados
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
        Crea un POST DE INSTAGRAM (Cuadrado 1:1) profesional:
        
        DESCRIPCIÓN VISUAL: {visual_description}
        MENSAJE: {main_message}
        
        REQUISITOS:
        - Formato cuadrado perfecto.
        - TEXTO EN LA IMAGEN: "{headline}" (Tipografía moderna, legible, integrada).
        - Colores: {colors}.
        - Estilo: {photo_style}.
        - Elementos clave: {key_elements}.
        
        Usa composición centrada o regla de tercios. El texto debe ser el héroe junto al plato.
        """
        return await self._generate_image_asset(
            concept, "1080x1080", "1080x1080", "instagram_post", prompt, brand_guidelines
        )

    async def _generate_instagram_story(self, concept: Dict, brand_guidelines: Dict = None) -> Dict:
        prompt = """
        Crea una INSTAGRAM STORY (Vertical 9:16) inmersiva:
        
        DESCRIPCIÓN VISUAL: {visual_description}
        
        REQUISITOS:
        - Formato vertical alto (9:16).
        - Dejar espacio libre arriba y abajo para UI de Instagram.
        - TEXTO EN LA IMAGEN: "{headline}" (Grande, llamativo, en el centro o tercio superior).
        - Colores: {colors}.
        - Estilo: {photo_style}.
        
        La imagen debe invitar a hacer 'Tap'. Haz que el plato se vea grandioso y alto.
        """
        return await self._generate_image_asset(
            concept, "Vertical", "1080x1920", "instagram_story", prompt, brand_guidelines
        )

    async def _generate_web_banner(self, concept: Dict, brand_guidelines: Dict = None) -> Dict:
        prompt = """
        Crea un BANNER WEB (Landscape 1.91:1) para sitio web:
        
        DESCRIPCIÓN VISUAL: {visual_description}
        
        REQUISITOS:
        - Formato horizontal ancho.
        - Espacio negativo amplio a la derecha o izquierda para texto superpuesto (si se añade después) o incluir el texto "{headline}" limpiamente.
        - Colores: {colors}.
        - Estilo: {photo_style}.
        
        Composición limpia, editorial, estilo página de inicio de restaurante de lujo.
        """
        return await self._generate_image_asset(
            concept, "Landscape", "1200x628", "web_banner", prompt, brand_guidelines
        )

    async def _generate_printable_flyer(self, concept: Dict, brand_guidelines: Dict = None) -> Dict:
        prompt = """
        Crea un FLYER IMPRIMIBLE (Formato A4 vertical) de alta resolución:
        
        DESCRIPCIÓN VISUAL: {visual_description}
        
        REQUISITOS:
        - Formato papel vertical.
        - Diseño tipo poster/cartel.
        - TEXTO PRINCIPAL: "{headline}" en la parte superior.
        - Incluir espacio visual para "Escanea para ordenar" (simulado).
        - Colores: {colors}.
        - Estilo: {photo_style}.
        
        Debe verse como un póster impreso de alta calidad pegado en una pared o vitrina.
        """
        return await self._generate_image_asset(
            concept, "A4", "2480x3508", "printable_flyer", prompt, brand_guidelines
        )

    async def _generate_ab_variants(self, base_asset: Dict, strategy: Dict) -> List[Dict]:
        """Genera variantes A/B cambiando el enfoque creativo."""
        if not base_asset or not base_asset.get('concept'):
            return []
            
        variants = []
        
        # Variant A: Enfoque en Producto (Macro/Close-up)
        # Reutilizamos el concepto pero forzamos el estilo
        concept_a = {
            "headline": base_asset['concept'],
            "visual_description": "Extremo close-up macro del plato, enfocando texturas, gotas, brillo. Fondo desenfocado (bokeh).",
            "main_message": "Sabor intenso",
            "photo_style": "Macro food photography",
            "key_elements": "Textura, detalle, frescura"
        }
        variant_a = await self._generate_instagram_post(concept_a)
        variant_a['variant_type'] = "macro_focus"
        variants.append(variant_a)
        
        # Variant B: Enfoque en Lifestyle (Mesa, gente, ambiente)
        concept_b = {
            "headline": base_asset['concept'],
            "visual_description": "Plano abierto mostrando el plato en una mesa de restaurante con comensales felices difusos al fondo. Ambiente cálido y social.",
            "main_message": "Experiencia compartida",
            "photo_style": "Lifestyle dining",
            "key_elements": "Ambiente, mesa puesta, bebidas"
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
        Localiza la campaña regenerando assets con texto traducido.
        """
        localized = {}
        
        # Traducir conceptos primero (usando Reasoning model para rapidez)
        headlines = [a.get('concept') for a in campaign_assets if a.get('concept')]
        headlines = list(set(headlines)) # Unique
        
        if not headlines:
            return {}
            
        translation_prompt = f"""
        Traduce estos titulares de marketing a los idiomas solicitados.
        Mantén el tono persuasivo y corto.
        
        Titulares: {json.dumps(headlines)}
        Idiomas: {json.dumps(target_languages)}
        
        Responde JSON: {{ "original": {{ "lang": "translated" }} }}
        Ejemplo: {{ "Sabor Real": {{ "en": "Real Flavor", "fr": "Goût Royal" }} }}
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

        # Regenerar assets para cada idioma
        for lang in target_languages:
            lang_assets = []
            for asset in campaign_assets:
                # Recuperar concepto base para regenerar
                # (En un caso real, guardaríamos el 'concept' dict completo en el asset,
                # aquí reconstruimos uno parcial para la demo)
                
                original_headline = asset.get('concept')
                translated_headline = original_headline
                
                if original_headline in translations and lang in translations[original_headline]:
                    translated_headline = translations[original_headline][lang]
                
                # Reconstruir concepto mínimo
                concept_recreated = {
                    "headline": translated_headline,
                    "visual_description": f"Same visual as original: {asset.get('reasoning', '')}", # Simplificación
                    "main_message": "Localized content",
                    "key_elements": "Same as original"
                }
                
                # Determinar tipo y regenerar
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
