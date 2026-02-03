from typing import Dict, List
import json
from google import genai
from google.genai import types
from loguru import logger
from app.core.config import get_settings

class VibeEngineeringAgent:
    """
    Implementa el patrón 'Vibe Engineering' del hackathon.
    
    Características:
    - Auto-verificación de outputs
    - Loops de mejora iterativa
    - Testing autónomo
    - Validación de calidad sin intervención humana
    """
    
    def __init__(self):
        settings = get_settings()
        self.api_key = settings.gemini_api_key
        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-3-flash-preview"
        self.max_iterations = 3
        self.quality_threshold = 0.85
    
    async def verify_and_improve_analysis(
        self,
        analysis_type: str,
        analysis_result: Dict,
        source_data: Dict,
        auto_improve: bool = True
    ) -> Dict:
        """
        Verifica la calidad de un análisis y lo mejora iterativamente.
        
        LOOP AUTÓNOMO:
        1. Verificar calidad del análisis inicial
        2. Si quality_score < threshold:
           a. Identificar problemas específicos
           b. Regenerar análisis con correcciones
           c. Volver a paso 1
        3. Continuar hasta alcanzar threshold o max_iterations
        """
        import time
        from datetime import datetime
        
        start_time = time.time()
        iteration = 0
        current_analysis = analysis_result
        verification_history = []
        improvement_iterations = []
        
        while iteration < self.max_iterations:
            iter_start = time.time()
            
            # VERIFICACIÓN AUTÓNOMA
            verification = await self._autonomous_verify(
                analysis_type,
                current_analysis,
                source_data
            )
            
            verification_history.append(verification)
            quality_score = verification.get('quality_score', 0)
            
            # Si la calidad es suficiente, terminar
            if quality_score >= self.quality_threshold:
                break
            
            # Si no hay auto-improve, devolver con advertencia
            if not auto_improve:
                break
            
            # Si es la última iteración, no intentamos mejorar para no desperdiciar tokens sin re-verificar
            if iteration == self.max_iterations - 1:
                break

            # MEJORA AUTÓNOMA
            identified_issues = verification.get('identified_issues', [])
            improved_analysis = await self._autonomous_improve(
                analysis_type,
                current_analysis,
                identified_issues,
                source_data
            )
            
            # Record improvement metrics
            iter_duration = (time.time() - iter_start) * 1000
            improvement_iterations.append({
                "iteration": iteration + 1,
                "timestamp": datetime.now().isoformat(),
                "quality_before": quality_score,
                "quality_after": 0, # Will be updated in next loop or final check
                "issues_fixed": [i.get('issue', 'Issue') for i in identified_issues],
                "duration_ms": iter_duration
            })
            
            current_analysis = improved_analysis
            iteration += 1
        
        # Update final quality score in last improvement iteration if we verified it
        if improvement_iterations and verification_history:
             last_quality = verification_history[-1].get('quality_score', 0)
             # This is an approximation as we verified 'current_analysis' which IS 'improved_analysis' from previous step
             improvement_iterations[-1]['quality_after'] = last_quality

        total_duration = (time.time() - start_time) * 1000
        
        return {
            "final_analysis": current_analysis,
            "verification_history": verification_history,
            "iterations_required": iteration + 1,
            "quality_achieved": verification_history[-1].get('quality_score', 0) if verification_history else 0,
            "auto_improved": auto_improve and iteration > 0,
            "improvement_iterations": improvement_iterations,
            "total_duration_ms": total_duration
        }
    
    async def _autonomous_verify(
        self,
        analysis_type: str,
        analysis: Dict,
        source_data: Dict
    ) -> Dict:
        """
        Verificación autónoma de calidad usando Gemini 3.
        
        El modelo actúa como "reviewer crítico" y evalúa:
        - Coherencia lógica
        - Precisión factual
        - Completitud
        - Aplicabilidad práctica
        """
        
        # Safe serialization for prompt
        def default_serializer(obj):
            return str(obj)

        verification_prompt = f"""
        Eres un AUDITOR EXPERTO evaluando la calidad de un análisis de restaurante.
        
        TIPO DE ANÁLISIS: {analysis_type}
        
        DATOS ORIGINALES:
        {json.dumps(source_data, indent=2, default=default_serializer)}
        
        ANÁLISIS A VERIFICAR:
        {json.dumps(analysis, indent=2, default=default_serializer)}
        
        Tu tarea es evaluar la CALIDAD del análisis en múltiples dimensiones:
        
        1. PRECISIÓN FACTUAL (0-1):
           - ¿Los números y cálculos son correctos?
           - ¿Las conclusiones se derivan lógicamente de los datos?
        
        2. COMPLETITUD (0-1):
           - ¿Se analizaron todos los aspectos relevantes?
           - ¿Falta algún insight importante?
        
        3. APLICABILIDAD (0-1):
           - ¿Las recomendaciones son accionables?
           - ¿Tiene sentido para un dueño de restaurante real?
        
        4. CLARIDAD (0-1):
           - ¿La explicación es comprensible?
           - ¿Los términos técnicos están bien explicados?
        
        Devuelve un JSON con la siguiente estructura:
        {{
            "quality_score": float (promedio de las 4 dimensiones),
            "precision_score": float,
            "completeness_score": float,
            "applicability_score": float,
            "clarity_score": float,
            "identified_issues": [
                {{
                    "issue": "descripción del problema",
                    "severity": "high|medium|low",
                    "category": "precision|completeness|applicability|clarity",
                    "suggestion": "cómo corregirlo"
                }}
            ],
            "strengths": ["punto fuerte 1", "punto fuerte 2", ...],
            "overall_assessment": "resumen ejecutivo de 2-3 líneas"
        }}
        
        SÉ RIGUROSO Y CRÍTICO. Un análisis mediocre debe recibir score < 0.7.
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=verification_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.3  # Baja temperatura para consistencia
                )
            )
            
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return {"quality_score": 0, "error": str(e)}
    
    async def _autonomous_improve(
        self,
        analysis_type: str,
        current_analysis: Dict,
        identified_issues: List[Dict],
        source_data: Dict
    ) -> Dict:
        """
        Mejora autónoma del análisis basándose en issues identificados.
        """
        
        # Priorizar issues por severidad
        high_priority = [i for i in identified_issues if i.get('severity') == 'high']
        medium_priority = [i for i in identified_issues if i.get('severity') == 'medium']
        
        # Safe serialization
        def default_serializer(obj):
            return str(obj)

        improvement_prompt = f"""
        Eres un ANALISTA SENIOR corrigiendo un análisis previo.
        
        ANÁLISIS ORIGINAL:
        {json.dumps(current_analysis, indent=2, default=default_serializer)}
        
        PROBLEMAS IDENTIFICADOS (ALTA PRIORIDAD):
        {json.dumps(high_priority, indent=2)}
        
        PROBLEMAS IDENTIFICADOS (MEDIA PRIORIDAD):
        {json.dumps(medium_priority, indent=2)}
        
        DATOS ORIGINALES DE REFERENCIA:
        {json.dumps(source_data, indent=2, default=default_serializer)}
        
        Tu tarea es REGENERAR el análisis corrigiendo TODOS los problemas identificados.
        
        Directrices:
        1. Mantén los aspectos correctos del análisis original
        2. Corrige ESPECÍFICAMENTE cada issue listado
        3. Si falta información, incorpórala
        4. Si hay errores de cálculo, corrígelos
        5. Si las recomendaciones no son accionables, hazlas más concretas
        
        IMPORTANTE: 
        - Devuelve el análisis completo mejorado, no solo los cambios
        - Mantén la misma estructura JSON del análisis original
        - Agrega un campo "improvements_made" listando qué corregiste
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=improvement_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.4
                )
            )
            
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"Improvement failed: {e}")
            return current_analysis
    
    async def verify_campaign_assets(
        self,
        campaign_assets: List[Dict],
        brand_guidelines: Dict,
        auto_improve: bool = True
    ) -> Dict:
        """
        Verifica la calidad de assets visuales generados.
        
        VERIFICACIONES AUTÓNOMAS:
        - ¿El texto es legible?
        - ¿Los colores respetan el brand?
        - ¿La composición es profesional?
        - ¿El mensaje es claro?
        """
        
        verified_assets = []
        
        for asset in campaign_assets:
            # Skip assets without image data
            if not asset.get('image_data'):
                verified_assets.append(asset)
                continue

            # Verificación visual usando Gemini Vision
            verification = await self._verify_visual_asset(
                asset,
                brand_guidelines
            )
            
            # Si la calidad es baja y auto_improve está activo
            if verification.get('quality_score', 0) < self.quality_threshold and auto_improve:
                # Mejorar el asset (Placeholder - requires re-generation logic which might be complex)
                # For now, we just tag it. In a full implementation, this would call CreativeAutopilot to regenerate.
                # Since we don't have direct access to regenerate here without circular deps or complex passing,
                # we'll flag it.
                
                # improved = await self._improve_visual_asset(asset, verification['issues'])
                # verified_assets.append(improved)
                
                verified_assets.append({
                    **asset,
                    "verification": verification,
                    "needs_improvement": True
                })
            else:
                verified_assets.append({
                    **asset,
                    "verification": verification
                })
        
        # Avoid division by zero
        count = len(verified_assets)
        avg_quality = sum(a.get('verification', {}).get('quality_score', 0) for a in verified_assets) / count if count > 0 else 0
        
        return {
            "verified_assets": verified_assets,
            "overall_quality": avg_quality
        }
    
    async def _verify_visual_asset(
        self,
        asset: Dict,
        brand_guidelines: Dict
    ) -> Dict:
        """
        Verifica un asset visual usando Gemini Vision.
        """
        
        prompt = f"""
        Eres un DIRECTOR CREATIVO evaluando un asset de marketing.
        
        BRAND GUIDELINES:
        {json.dumps(brand_guidelines, indent=2)}
        
        Evalúa esta imagen en las siguientes dimensiones:
        
        1. LEGIBILIDAD DEL TEXTO (0-1):
           - ¿El texto es completamente legible?
           - ¿Hay errores ortográficos?
        
        2. ADHERENCIA A MARCA (0-1):
           - ¿Respeta la paleta de colores?
           - ¿El estilo es consistente con la marca?
        
        3. CALIDAD TÉCNICA (0-1):
           - ¿La resolución es adecuada?
           - ¿La composición es profesional?
        
        4. EFECTIVIDAD DEL MENSAJE (0-1):
           - ¿El mensaje es claro de inmediato?
           - ¿Genera deseo de acción?
        
        Devuelve JSON:
        {{
            "quality_score": float,
            "text_legibility": float,
            "brand_adherence": float,
            "technical_quality": float,
            "message_effectiveness": float,
            "issues": [
                {{"issue": "...", "severity": "high|medium|low", "suggestion": "..."}}
            ],
            "assessment": "evaluación de 2-3 líneas"
        }}
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    types.Content(
                        parts=[
                            types.Part(text=prompt),
                            types.Part(inline_data=types.Blob(
                                mime_type="image/jpeg",
                                data=asset['image_data']
                            ))
                        ]
                    )
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"Visual verification failed: {e}")
            return {"quality_score": 0, "error": str(e)}
