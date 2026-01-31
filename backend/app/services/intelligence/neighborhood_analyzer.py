"""
Neighborhood Analyzer - Location-based demographic and market intelligence.

Analyzes the business environment around a restaurant location:
- Nearby points of interest (offices, schools, gyms, etc.)
- Foot traffic patterns and peak hours
- Demographic insights based on surrounding businesses
- Target customer profile generation
- Location-specific menu and pricing recommendations
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from loguru import logger

from app.services.gemini.base_agent import GeminiBaseAgent, GeminiModel


@dataclass
class PointOfInterest:
    """A nearby point of interest affecting customer demographics."""
    name: str
    poi_type: str  # office, school, gym, hospital, university, etc.
    distance_meters: float
    
    estimated_daily_traffic: int = 0
    peak_hours: List[str] = field(default_factory=list)
    customer_profile: str = ""  # e.g., "Young professionals", "Students"
    
    relevance_score: float = 0.0  # How relevant to restaurant business
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "poi_type": self.poi_type,
            "distance_meters": self.distance_meters,
            "estimated_daily_traffic": self.estimated_daily_traffic,
            "peak_hours": self.peak_hours,
            "customer_profile": self.customer_profile,
            "relevance_score": self.relevance_score,
        }


@dataclass
class DemographicInsight:
    """Demographic insight for the neighborhood."""
    segment: str  # e.g., "Office Workers", "Students", "Families"
    estimated_percentage: float  # Percentage of nearby traffic
    
    characteristics: List[str] = field(default_factory=list)
    dining_preferences: List[str] = field(default_factory=list)
    price_sensitivity: str = "medium"  # low, medium, high
    peak_dining_times: List[str] = field(default_factory=list)
    
    menu_opportunities: List[str] = field(default_factory=list)
    marketing_channels: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "segment": self.segment,
            "estimated_percentage": self.estimated_percentage,
            "characteristics": self.characteristics,
            "dining_preferences": self.dining_preferences,
            "price_sensitivity": self.price_sensitivity,
            "peak_dining_times": self.peak_dining_times,
            "menu_opportunities": self.menu_opportunities,
            "marketing_channels": self.marketing_channels,
        }


@dataclass
class NeighborhoodProfile:
    """Complete neighborhood analysis profile."""
    location: Dict[str, float]  # lat, lng
    address: str
    
    # Points of interest
    pois: List[PointOfInterest] = field(default_factory=list)
    
    # Demographics
    demographics: List[DemographicInsight] = field(default_factory=list)
    primary_customer_segment: str = ""
    
    # Traffic patterns
    estimated_daily_foot_traffic: int = 0
    peak_hours: Dict[str, List[str]] = field(default_factory=dict)  # day -> hours
    slow_hours: Dict[str, List[str]] = field(default_factory=dict)
    
    # Business recommendations
    pricing_recommendation: str = ""
    menu_recommendations: List[str] = field(default_factory=list)
    marketing_recommendations: List[str] = field(default_factory=list)
    promotional_opportunities: List[Dict[str, Any]] = field(default_factory=list)
    
    # Thought traces for transparency
    thought_traces: List[Dict[str, Any]] = field(default_factory=list)
    confidence_score: float = 0.0
    processing_time_ms: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "location": self.location,
            "address": self.address,
            "pois": [p.to_dict() for p in self.pois],
            "demographics": [d.to_dict() for d in self.demographics],
            "primary_customer_segment": self.primary_customer_segment,
            "estimated_daily_foot_traffic": self.estimated_daily_foot_traffic,
            "peak_hours": self.peak_hours,
            "slow_hours": self.slow_hours,
            "pricing_recommendation": self.pricing_recommendation,
            "menu_recommendations": self.menu_recommendations,
            "marketing_recommendations": self.marketing_recommendations,
            "promotional_opportunities": self.promotional_opportunities,
            "thought_traces": self.thought_traces,
            "confidence_score": self.confidence_score,
            "processing_time_ms": self.processing_time_ms,
        }


class NeighborhoodAnalyzer(GeminiBaseAgent):
    """
    Analyzes the neighborhood around a restaurant location to provide
    demographic insights and business recommendations.
    
    Uses location data to:
    - Identify nearby POIs affecting customer demographics
    - Estimate foot traffic patterns
    - Generate targeted marketing recommendations
    - Suggest menu and pricing optimizations
    """

    def __init__(
        self,
        model: GeminiModel = GeminiModel.FLASH,
        **kwargs,
    ):
        super().__init__(model=model, **kwargs)
        self.thought_traces: List[Dict[str, Any]] = []

    async def process(self, *args, **kwargs) -> Any:
        """Main entry point."""
        return await self.analyze_neighborhood(**kwargs)

    def _add_thought(
        self,
        step: str,
        reasoning: str,
        observations: List[str],
        confidence: float,
    ) -> None:
        """Add a thought trace for transparency."""
        self.thought_traces.append({
            "step": step,
            "reasoning": reasoning,
            "observations": observations,
            "confidence": confidence,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    async def analyze_neighborhood(
        self,
        location: Dict[str, float],
        address: str,
        our_cuisine_type: str = "general",
        our_price_range: str = "mid-range",
        radius_meters: int = 500,
        **kwargs,
    ) -> NeighborhoodProfile:
        """
        Analyze the neighborhood around a restaurant location.
        
        Args:
            location: {"lat": float, "lng": float}
            address: Human-readable address
            our_cuisine_type: Type of cuisine we serve
            our_price_range: Our price positioning
            radius_meters: Analysis radius
            
        Returns:
            NeighborhoodProfile with complete analysis
        """
        import time
        start_time = time.time()
        
        self.thought_traces = []

        self._add_thought(
            step="Initialization",
            reasoning=f"Iniciando análisis de vecindario para ubicación: {address}",
            observations=[
                f"Radio de análisis: {radius_meters}m",
                f"Tipo de cocina: {our_cuisine_type}",
                f"Rango de precio: {our_price_range}",
            ],
            confidence=0.95,
        )

        # Step 1: Discover POIs
        pois = await self._discover_pois(location, radius_meters)

        self._add_thought(
            step="POI Discovery",
            reasoning=f"Identificados {len(pois)} puntos de interés relevantes en el área",
            observations=[
                f"Oficinas: {len([p for p in pois if p.poi_type == 'office'])}",
                f"Escuelas/Universidades: {len([p for p in pois if p.poi_type in ['school', 'university']])}",
                f"Comercios: {len([p for p in pois if p.poi_type in ['retail', 'shopping']])}",
            ],
            confidence=0.82,
        )

        # Step 2: Analyze demographics
        demographics = await self._analyze_demographics(pois, our_cuisine_type)

        self._add_thought(
            step="Demographic Analysis",
            reasoning="Analizando perfiles demográficos basados en POIs cercanos",
            observations=[
                f"Segmentos identificados: {len(demographics)}",
                f"Segmento primario: {demographics[0].segment if demographics else 'Unknown'}",
            ],
            confidence=0.78,
        )

        # Step 3: Estimate traffic patterns
        traffic_data = await self._estimate_traffic_patterns(pois, demographics)

        # Step 4: Generate recommendations
        recommendations = await self._generate_recommendations(
            pois, demographics, our_cuisine_type, our_price_range
        )

        self._add_thought(
            step="Recommendations",
            reasoning="Generando recomendaciones estratégicas basadas en el análisis de vecindario",
            observations=[
                f"Recomendaciones de menú: {len(recommendations.get('menu', []))}",
                f"Recomendaciones de marketing: {len(recommendations.get('marketing', []))}",
                f"Oportunidades promocionales: {len(recommendations.get('promotions', []))}",
            ],
            confidence=0.85,
        )

        processing_time = int((time.time() - start_time) * 1000)

        # Determine primary segment
        primary_segment = demographics[0].segment if demographics else "General"

        return NeighborhoodProfile(
            location=location,
            address=address,
            pois=pois,
            demographics=demographics,
            primary_customer_segment=primary_segment,
            estimated_daily_foot_traffic=traffic_data.get("daily_traffic", 0),
            peak_hours=traffic_data.get("peak_hours", {}),
            slow_hours=traffic_data.get("slow_hours", {}),
            pricing_recommendation=recommendations.get("pricing", ""),
            menu_recommendations=recommendations.get("menu", []),
            marketing_recommendations=recommendations.get("marketing", []),
            promotional_opportunities=recommendations.get("promotions", []),
            thought_traces=self.thought_traces,
            confidence_score=0.82,
            processing_time_ms=processing_time,
        )

    async def _discover_pois(
        self,
        location: Dict[str, float],
        radius: int,
    ) -> List[PointOfInterest]:
        """
        Discover points of interest near the location.
        In production, this would call Google Places API.
        """
        # Simulated POI data for demo
        simulated_pois = [
            PointOfInterest(
                name="Torre Corporativa Reforma",
                poi_type="office",
                distance_meters=150,
                estimated_daily_traffic=2000,
                peak_hours=["12:00-14:00", "18:00-19:00"],
                customer_profile="Profesionales 25-45 años",
                relevance_score=0.9,
            ),
            PointOfInterest(
                name="Centro Comercial Plaza Norte",
                poi_type="shopping",
                distance_meters=300,
                estimated_daily_traffic=5000,
                peak_hours=["13:00-15:00", "18:00-21:00"],
                customer_profile="Familias y jóvenes",
                relevance_score=0.85,
            ),
            PointOfInterest(
                name="Universidad Tecnológica",
                poi_type="university",
                distance_meters=400,
                estimated_daily_traffic=8000,
                peak_hours=["11:00-14:00", "17:00-19:00"],
                customer_profile="Estudiantes 18-25 años",
                relevance_score=0.8,
            ),
            PointOfInterest(
                name="Hospital General",
                poi_type="hospital",
                distance_meters=500,
                estimated_daily_traffic=3000,
                peak_hours=["07:00-09:00", "12:00-14:00", "19:00-21:00"],
                customer_profile="Personal médico, visitantes",
                relevance_score=0.7,
            ),
            PointOfInterest(
                name="Gimnasio FitLife",
                poi_type="gym",
                distance_meters=200,
                estimated_daily_traffic=500,
                peak_hours=["06:00-08:00", "18:00-21:00"],
                customer_profile="Jóvenes fitness 20-35 años",
                relevance_score=0.6,
            ),
        ]

        return simulated_pois

    async def _analyze_demographics(
        self,
        pois: List[PointOfInterest],
        cuisine_type: str,
    ) -> List[DemographicInsight]:
        """Analyze demographics based on nearby POIs."""
        
        # Calculate segment weights based on POIs
        segment_data = {}
        
        for poi in pois:
            if poi.poi_type == "office":
                segment = "Profesionales de Oficina"
                if segment not in segment_data:
                    segment_data[segment] = {
                        "traffic": 0,
                        "characteristics": ["Tiempo limitado para almuerzo", "Presupuesto medio-alto"],
                        "preferences": ["Servicio rápido", "Opciones saludables", "Para llevar"],
                        "sensitivity": "medium",
                        "peak_times": ["12:00-14:00"],
                        "menu_ops": ["Menú ejecutivo", "Combos de almuerzo", "Ensaladas"],
                        "channels": ["LinkedIn", "Email corporativo", "Apps de delivery"],
                    }
                segment_data[segment]["traffic"] += poi.estimated_daily_traffic
                
            elif poi.poi_type == "university":
                segment = "Estudiantes Universitarios"
                if segment not in segment_data:
                    segment_data[segment] = {
                        "traffic": 0,
                        "characteristics": ["Presupuesto limitado", "Horarios flexibles"],
                        "preferences": ["Porciones grandes", "Precios accesibles", "Ambiente casual"],
                        "sensitivity": "high",
                        "peak_times": ["13:00-15:00", "19:00-21:00"],
                        "menu_ops": ["Promociones 2x1", "Descuento estudiante", "Platillos económicos"],
                        "channels": ["Instagram", "TikTok", "WhatsApp grupos"],
                    }
                segment_data[segment]["traffic"] += poi.estimated_daily_traffic
                
            elif poi.poi_type == "shopping":
                segment = "Compradores y Familias"
                if segment not in segment_data:
                    segment_data[segment] = {
                        "traffic": 0,
                        "characteristics": ["Buscan experiencia completa", "Disposición a gastar"],
                        "preferences": ["Menú variado", "Opciones para niños", "Ambiente agradable"],
                        "sensitivity": "medium",
                        "peak_times": ["14:00-16:00", "19:00-21:00"],
                        "menu_ops": ["Menú infantil", "Postres", "Opciones para compartir"],
                        "channels": ["Facebook", "Google Maps", "Influencers locales"],
                    }
                segment_data[segment]["traffic"] += poi.estimated_daily_traffic
                
            elif poi.poi_type == "gym":
                segment = "Entusiastas Fitness"
                if segment not in segment_data:
                    segment_data[segment] = {
                        "traffic": 0,
                        "characteristics": ["Conscientes de salud", "Dispuestos a pagar más por calidad"],
                        "preferences": ["Opciones saludables", "Información nutricional", "Proteína"],
                        "sensitivity": "low",
                        "peak_times": ["07:00-09:00", "18:00-20:00"],
                        "menu_ops": ["Bowl de proteína", "Smoothies", "Ensaladas con pollo"],
                        "channels": ["Instagram fitness", "Apps de salud"],
                    }
                segment_data[segment]["traffic"] += poi.estimated_daily_traffic

            elif poi.poi_type == "hospital":
                segment = "Personal de Salud"
                if segment not in segment_data:
                    segment_data[segment] = {
                        "traffic": 0,
                        "characteristics": ["Turnos irregulares", "Necesitan opciones rápidas"],
                        "preferences": ["Disponibilidad extendida", "Para llevar", "Café"],
                        "sensitivity": "medium",
                        "peak_times": ["07:00-08:00", "12:00-14:00", "20:00-22:00"],
                        "menu_ops": ["Desayunos", "Café de especialidad", "Snacks rápidos"],
                        "channels": ["WhatsApp", "Recomendación directa"],
                    }
                segment_data[segment]["traffic"] += poi.estimated_daily_traffic

        # Calculate percentages
        total_traffic = sum(s["traffic"] for s in segment_data.values())
        
        demographics = []
        for segment, data in segment_data.items():
            pct = (data["traffic"] / total_traffic * 100) if total_traffic > 0 else 0
            demographics.append(DemographicInsight(
                segment=segment,
                estimated_percentage=round(pct, 1),
                characteristics=data["characteristics"],
                dining_preferences=data["preferences"],
                price_sensitivity=data["sensitivity"],
                peak_dining_times=data["peak_times"],
                menu_opportunities=data["menu_ops"],
                marketing_channels=data["channels"],
            ))

        # Sort by percentage
        demographics.sort(key=lambda x: -x.estimated_percentage)
        
        return demographics

    async def _estimate_traffic_patterns(
        self,
        pois: List[PointOfInterest],
        demographics: List[DemographicInsight],
    ) -> Dict[str, Any]:
        """Estimate foot traffic patterns based on POIs and demographics."""
        
        # Aggregate peak hours
        all_peak_hours = set()
        for poi in pois:
            all_peak_hours.update(poi.peak_hours)
        
        # Estimate daily traffic (simplified)
        total_daily = sum(poi.estimated_daily_traffic for poi in pois)
        # Restaurant capture rate ~5-10% of foot traffic
        estimated_potential = int(total_daily * 0.07)
        
        # Define patterns by day
        weekday_peak = ["12:00-14:00", "19:00-21:00"]
        weekend_peak = ["13:00-15:00", "20:00-22:00"]
        
        weekday_slow = ["15:00-18:00"]
        weekend_slow = ["10:00-12:00"]
        
        return {
            "daily_traffic": estimated_potential,
            "peak_hours": {
                "weekday": weekday_peak,
                "weekend": weekend_peak,
            },
            "slow_hours": {
                "weekday": weekday_slow,
                "weekend": weekend_slow,
            },
        }

    async def _generate_recommendations(
        self,
        pois: List[PointOfInterest],
        demographics: List[DemographicInsight],
        cuisine_type: str,
        price_range: str,
    ) -> Dict[str, Any]:
        """Generate strategic recommendations using Gemini."""
        
        # Build context
        demo_summary = "\n".join([
            f"- {d.segment} ({d.estimated_percentage}%): {', '.join(d.characteristics[:2])}"
            for d in demographics[:4]
        ])
        
        poi_summary = "\n".join([
            f"- {p.name} ({p.poi_type}): {p.distance_meters}m, ~{p.estimated_daily_traffic} personas/día"
            for p in pois[:5]
        ])

        prompt = f"""Eres un consultor de restaurantes analizando una ubicación.

PERFIL DEL NEGOCIO:
- Tipo de cocina: {cuisine_type}
- Rango de precio: {price_range}

PUNTOS DE INTERÉS CERCANOS:
{poi_summary}

DEMOGRAFÍA DEL ÁREA:
{demo_summary}

Genera recomendaciones estratégicas específicas para este restaurante.

RESPONDE CON JSON VÁLIDO:
{{
    "pricing": "Recomendación de estrategia de precios basada en demografía",
    "menu": [
        "Recomendación específica de menú 1",
        "Recomendación específica de menú 2",
        "Recomendación específica de menú 3"
    ],
    "marketing": [
        "Estrategia de marketing 1 con canal específico",
        "Estrategia de marketing 2 con canal específico"
    ],
    "promotions": [
        {{
            "name": "Nombre de promoción",
            "target_segment": "Segmento objetivo",
            "timing": "Cuándo implementar",
            "expected_impact": "Impacto esperado",
            "description": "Descripción detallada"
        }}
    ],
    "unique_opportunities": [
        "Oportunidad única basada en la combinación específica de POIs"
    ]
}}"""

        try:
            response = await self._generate_content(
                prompt=prompt,
                temperature=0.6,
                max_output_tokens=4096,
                feature="neighborhood_recommendations",
            )

            result = self._parse_json_response(response)
            
            return {
                "pricing": result.get("pricing", "Mantener precios competitivos"),
                "menu": result.get("menu", []),
                "marketing": result.get("marketing", []),
                "promotions": result.get("promotions", []),
            }

        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            
            # Fallback recommendations
            return {
                "pricing": "Considerar precios competitivos basados en el segmento principal",
                "menu": [
                    "Agregar opciones de almuerzo rápido para oficinistas",
                    "Considerar menú estudiantil con descuento",
                ],
                "marketing": [
                    "Publicidad en redes sociales enfocada en demografía local",
                    "Programa de lealtad para clientes frecuentes",
                ],
                "promotions": [
                    {
                        "name": "Happy Hour",
                        "target_segment": "Profesionales de oficina",
                        "timing": "Lunes a Viernes 17:00-19:00",
                        "expected_impact": "Incremento 15-20% en ventas tarde",
                        "description": "Descuento en bebidas y entradas",
                    }
                ],
            }
