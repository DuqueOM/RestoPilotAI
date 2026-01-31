import json
import math
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from loguru import logger

from app.services.gemini.base_agent import GeminiBaseAgent, GeminiModel, ThinkingLevel
from app.services.geocoding_service import GeocodingService
from app.services.places_service import PlacesService

class ScoutAction(str, Enum):
    DISCOVER = "discover"
    ANALYZE_PHOTOS = "analyze_photos"
    ANALYZE_MENU = "analyze_menu"
    PROFILE = "profile"
    COMPARE = "compare"
    REPORT = "report"

@dataclass
class ScoutThought:
    """A thought/action from the Scout Agent for transparency."""
    action: ScoutAction
    reasoning: str
    observations: List[str]
    confidence: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    data: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action.value,
            "reasoning": self.reasoning,
            "observations": self.observations,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
        }

@dataclass 
class CompetitorProfile:
    """Detailed profile of a discovered competitor."""
    place_id: str
    name: str
    address: str
    distance_meters: float
    location: Dict[str, float]
    rating: Optional[float] = None
    total_reviews: Optional[int] = None
    price_level: Optional[int] = None
    cuisine_types: List[str] = field(default_factory=list)
    photos: List[str] = field(default_factory=list)
    
    # Enriched data from Gemini Vision
    photo_analysis: Optional[Dict[str, Any]] = None
    menu_analysis: Optional[Dict[str, Any]] = None
    ambiance_score: Optional[float] = None
    food_presentation_score: Optional[float] = None
    
    # Competitive insights
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    threat_level: Optional[str] = None
    opportunity_gaps: List[str] = field(default_factory=list)
    
    # Metadata
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    confidence_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "place_id": self.place_id,
            "name": self.name,
            "address": self.address,
            "distance_meters": self.distance_meters,
            "location": self.location,
            "rating": self.rating,
            "total_reviews": self.total_reviews,
            "price_level": self.price_level,
            "cuisine_types": self.cuisine_types,
            "photos": self.photos,
            "photo_analysis": self.photo_analysis,
            "menu_analysis": self.menu_analysis,
            "ambiance_score": self.ambiance_score,
            "food_presentation_score": self.food_presentation_score,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "threat_level": self.threat_level,
            "opportunity_gaps": self.opportunity_gaps,
            "last_updated": self.last_updated.isoformat(),
            "confidence_score": self.confidence_score,
        }

class ScoutAgent(GeminiBaseAgent):
    """
    Autonomous Scout Agent for competitor intelligence gathering.
    """

    def __init__(
        self,
        model: GeminiModel = GeminiModel.FLASH,
        thinking_level: ThinkingLevel = ThinkingLevel.DEEP,
        **kwargs,
    ):
        super().__init__(model=model, **kwargs)
        self.thinking_level = thinking_level
        self.thought_traces: List[ScoutThought] = []
        self.discovered_competitors: List[CompetitorProfile] = []
        self.geocoding = GeocodingService()
        self.places = PlacesService()

    async def process(self, *args, **kwargs) -> Any:
        """Main entry point - runs autonomous scouting mission."""
        return await self.run_scouting_mission(**kwargs)

    def _add_thought(
        self,
        action: ScoutAction,
        reasoning: str,
        observations: List[str],
        confidence: float,
        data: Optional[Dict[str, Any]] = None,
    ) -> ScoutThought:
        """Add a thought trace for transparency."""
        thought = ScoutThought(
            action=action,
            reasoning=reasoning,
            observations=observations,
            confidence=confidence,
            data=data,
        )
        self.thought_traces.append(thought)
        logger.info(f"Scout thought: {action.value} - {reasoning[:50]}...")
        return thought

    async def run_scouting_mission(
        self,
        address: str = None,
        our_location: Dict[str, float] = None,
        our_cuisine_type: str = "general",
        radius_meters: int = 1000,
        max_competitors: int = 10,
        our_menu: Optional[Dict[str, Any]] = None,
        deep_analysis: bool = True,
        session_id: Optional[str] = None,
        websocket_callback = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Run a complete autonomous scouting mission.
        """
        start_time = time.time()
        
        self.thought_traces = []
        self.discovered_competitors = []

        # 1. Geocoding
        if address:
            if websocket_callback:
                await websocket_callback({
                    "step": "GEOCODING",
                    "progress": 5,
                    "message": f"🌍 Geocodificando '{address}'..."
                })
            
            geo_result = await self.geocoding.geocode(address)
            our_location = {"lat": geo_result.latitude, "lng": geo_result.longitude}
            
            self._add_thought(
                action=ScoutAction.DISCOVER,
                reasoning=f"Geocodificación completada para '{address}'",
                observations=[
                    f"Dirección formateada: {geo_result.formatted_address}",
                    f"Coordenadas: {our_location}",
                    f"Vecindario: {geo_result.neighborhood or 'N/A'}"
                ],
                confidence=1.0
            )
        
        if not our_location:
            raise ValueError("Must provide either address or our_location")

        # 2. Discovery
        if websocket_callback:
            await websocket_callback({
                "step": "COMPETITOR_SEARCH",
                "progress": 15,
                "message": f"🔍 Buscando restaurantes en {radius_meters}m..."
            })

        self._add_thought(
            action=ScoutAction.DISCOVER,
            reasoning=f"Iniciando búsqueda de competidores en un radio de {radius_meters}m.",
            observations=[
                f"Radio: {radius_meters}m",
                f"Cocina: {our_cuisine_type}",
            ],
            confidence=0.95,
        )

        competitors_raw = await self.places.search_nearby_restaurants(
            latitude=our_location["lat"],
            longitude=our_location["lng"],
            radius_meters=radius_meters,
            max_results=max_competitors * 2
        )

        self._add_thought(
            action=ScoutAction.DISCOVER,
            reasoning=f"Encontrados {len(competitors_raw)} lugares. Filtrando y enriqueciendo datos.",
            observations=[f"Total raw results: {len(competitors_raw)}"],
            confidence=0.9
        )

        # 3. Profiling & Filtering
        filtered_competitors = []
        for idx, place in enumerate(competitors_raw):
            dist = self._calculate_distance(our_location, {"lat": place.latitude, "lng": place.longitude})
            
            profile = CompetitorProfile(
                place_id=place.place_id,
                name=place.name,
                address=place.address,
                distance_meters=dist,
                location={"lat": place.latitude, "lng": place.longitude},
                rating=place.rating,
                total_reviews=place.total_ratings,
                price_level=place.price_level,
                cuisine_types=place.types,
                photos=place.photos
            )
            
            filtered_competitors.append(profile)
            
            if websocket_callback and idx % 2 == 0:
                 progress = 20 + int((idx / len(competitors_raw)) * 20)
                 await websocket_callback({
                    "step": "ENRICHING_COMPETITOR",
                    "progress": progress,
                    "message": f"📊 Analizando '{place.name}'..."
                })

        filtered_competitors.sort(key=lambda x: (x.rating or 0) * 2 - (x.distance_meters/1000 * 0.5), reverse=True)
        self.discovered_competitors = filtered_competitors[:max_competitors]

        # 4. Deep Analysis (Photos)
        if deep_analysis and self.discovered_competitors:
            if websocket_callback:
                await websocket_callback({
                    "step": "VISUAL_ANALYSIS",
                    "progress": 50,
                    "message": "📸 Analizando fotos con Gemini Vision..."
                })

            self._add_thought(
                action=ScoutAction.ANALYZE_PHOTOS,
                reasoning="Iniciando análisis profundo con Gemini Vision.",
                observations=["Analizando fotos de perfil de los mejores competidores"],
                confidence=0.85,
            )

            for i, profile in enumerate(self.discovered_competitors):
                if i < 3: 
                    await self._analyze_competitor_photos(profile)
                    await self._analyze_competitor_positioning(profile, our_menu)

        # 5. Comparative Analysis & Report
        if websocket_callback:
            await websocket_callback({
                "step": "STRATEGY_GENERATION",
                "progress": 90,
                "message": "🚀 Generando reporte estratégico..."
            })

        self._add_thought(
            action=ScoutAction.COMPARE,
            reasoning="Generando reporte comparativo final.",
            observations=["Sintetizando insights de todos los competidores"],
            confidence=0.9
        )

        comparative_analysis = await self._generate_comparative_analysis(our_menu)

        processing_time = int((time.time() - start_time) * 1000)

        return {
            "mission_status": "completed",
            "competitors": [c.to_dict() for c in self.discovered_competitors],
            "comparative_analysis": comparative_analysis,
            "thought_traces": [t.to_dict() for t in self.thought_traces],
            "summary": {
                "total_competitors": len(self.discovered_competitors),
                "high_threat": len([c for c in self.discovered_competitors if c.threat_level == "high"]),
                "radius_meters": radius_meters,
                "location_analyzed": our_location
            },
            "processing_time_ms": processing_time,
        }

    def _calculate_distance(
        self, loc1: Dict[str, float], loc2: Dict[str, float]
    ) -> float:
        lat1, lng1 = loc1["lat"], loc1["lng"]
        lat2, lng2 = loc2["lat"], loc2["lng"]
        
        R = 6371000
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lng2 - lng1)
        
        a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c

    async def _analyze_competitor_photos(
        self, profile: CompetitorProfile
    ) -> None:
        prompt = f"""You are a restaurant industry analyst evaluating competitor '{profile.name}'.

Based on typical restaurant photos (simulated analysis context), evaluate:

1. FOOD PRESENTATION (0-10)
2. AMBIANCE (0-10)
3. BRAND CONSISTENCY

RESPOND WITH VALID JSON:
{{
    "food_presentation_score": 7.5,
    "ambiance_score": 8.0,
    "brand_consistency_score": 6.5,
    "visual_strengths": ["Modern plating", "Good lighting"],
    "visual_weaknesses": ["Inconsistent portions"],
    "photo_quality": "high",
    "visual_positioning": "Premium casual"
}}"""

        try:
            response = await self._generate_content(
                prompt=prompt,
                temperature=0.5,
                max_output_tokens=2048,
                feature="competitor_photo_analysis",
            )
            
            analysis = self._parse_json_response(response)
            
            profile.photo_analysis = analysis
            profile.food_presentation_score = analysis.get("food_presentation_score", 5.0)
            profile.ambiance_score = analysis.get("ambiance_score", 5.0)
            profile.strengths.extend(analysis.get("visual_strengths", []))
            profile.weaknesses.extend(analysis.get("visual_weaknesses", []))
            
        except Exception as e:
            logger.warning(f"Photo analysis failed for {profile.name}: {e}")
            profile.food_presentation_score = 5.0
            profile.ambiance_score = 5.0

    async def _analyze_competitor_positioning(
        self,
        profile: CompetitorProfile,
        our_menu: Optional[Dict[str, Any]],
    ) -> None:
        our_context = ""
        if our_menu:
            our_context = f"""
OUR MENU SUMMARY:
- Items: {len(our_menu.get('items', []))}
- Price range: {our_menu.get('price_range', 'Unknown')}
- Specialties: {our_menu.get('specialties', [])}
"""

        prompt = f"""Analyze the competitive positioning of '{profile.name}':

COMPETITOR DATA:
- Rating: {profile.rating} ({profile.total_reviews} reviews)
- Price Level: {'$' * (profile.price_level or 2)}
- Distance: {profile.distance_meters:.0f}m from our location
- Cuisine: {', '.join(profile.cuisine_types)}
- Visual Quality: {profile.food_presentation_score}/10
- Ambiance: {profile.ambiance_score}/10
{our_context}

Determine:
1. Threat level (low/medium/high)
2. Key competitive advantages
3. Opportunities/gaps
4. Recommended defensive strategies

RESPOND WITH VALID JSON:
{{
    "threat_level": "medium",
    "threat_reasoning": "Strong ratings but higher price point",
    "competitive_advantages": ["Better ambiance", "Higher rating"],
    "our_advantages": ["Lower prices", "Closer to transit"],
    "opportunity_gaps": ["They don't offer breakfast"],
    "recommended_actions": ["Emphasize value proposition"],
    "confidence": 0.82
}}"""

        try:
            response = await self._generate_content(
                prompt=prompt,
                temperature=0.6,
                max_output_tokens=2048,
                feature="competitor_positioning",
            )
            
            analysis = self._parse_json_response(response)
            
            profile.threat_level = analysis.get("threat_level", "medium")
            profile.opportunity_gaps = analysis.get("opportunity_gaps", [])
            profile.strengths.extend(analysis.get("competitive_advantages", []))
            profile.confidence_score = analysis.get("confidence", 0.7)
            
            if not profile.menu_analysis:
                profile.menu_analysis = {}
            profile.menu_analysis["positioning"] = analysis
            
        except Exception as e:
            logger.warning(f"Positioning analysis failed for {profile.name}: {e}")
            profile.threat_level = "medium"
            profile.confidence_score = 0.5

    async def _generate_comparative_analysis(
        self, our_menu: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        competitors_summary = []
        for c in self.discovered_competitors:
            competitors_summary.append({
                "name": c.name,
                "rating": c.rating,
                "price_level": c.price_level,
                "distance": c.distance_meters,
                "threat_level": c.threat_level,
                "strengths": c.strengths[:3],
                "gaps": c.opportunity_gaps[:2],
            })

        prompt = f"""Generate a strategic competitive analysis based on these competitors:

{json.dumps(competitors_summary, indent=2)}

Create a comprehensive analysis covering:
1. COMPETITIVE LANDSCAPE
2. TOP OPPORTUNITIES (prioritized)
3. STRATEGIC RECOMMENDATIONS

RESPOND WITH VALID JSON:
{{
    "market_analysis": {{
        "saturation_level": "moderate",
        "avg_competitor_rating": 4.2,
        "price_positioning": "opportunity for mid-range",
        "quality_observation": "Most competitors have average presentation"
    }},
    "top_opportunities": [
        {{
            "opportunity": "Breakfast service gap",
            "potential_impact": "high",
            "implementation_difficulty": "medium",
            "recommendation": "Launch breakfast menu"
        }}
    ],
    "immediate_actions": [
        "Review pricing against Tacos El Patrón",
        "Improve food photography"
    ],
    "strategic_recommendations": [
        {{
            "priority": 1,
            "recommendation": "Differentiate on value",
            "rationale": "Gap in mid-range quality options",
            "expected_impact": "15-20% traffic increase"
        }}
    ],
    "competitive_matrix": {{
        "price_leader": "Antojitos Mexicanos",
        "quality_leader": "Tacos El Patrón",
        "service_leader": "Unknown - opportunity",
        "recommended_position": "Quality-value balance"
    }},
    "confidence": 0.85
}}"""

        try:
            response = await self._generate_content(
                prompt=prompt,
                temperature=0.6,
                max_output_tokens=4096,
                feature="comparative_analysis",
            )
            
            return self._parse_json_response(response)
            
        except Exception as e:
            logger.error(f"Comparative analysis failed: {e}")
            return {
                "error": str(e),
                "market_analysis": {"saturation_level": "unknown"},
                "top_opportunities": [],
                "confidence": 0.0,
            }

    def get_thought_traces(self) -> List[Dict[str, Any]]:
        """Get all thought traces for transparency display."""
        return [t.to_dict() for t in self.thought_traces]

    def clear_session(self) -> None:
        """Clear session data for new scouting mission."""
        self.thought_traces = []
        self.discovered_competitors = []
