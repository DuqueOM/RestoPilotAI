import httpx
from typing import List, Dict, Optional
from pydantic import BaseModel
from loguru import logger
from app.core.config import get_settings

class PlaceResult(BaseModel):
    place_id: str
    name: str
    address: str
    latitude: float
    longitude: float
    rating: Optional[float] = None
    total_ratings: Optional[int] = None
    price_level: Optional[int] = None
    types: List[str] = []
    phone_number: Optional[str] = None
    website: Optional[str] = None
    opening_hours: Optional[Dict] = None
    photos: List[str] = []  # Photo references

class PlacesService:
    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.google_places_api_key or self.settings.google_maps_api_key
        self.nearby_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        self.details_url = "https://maps.googleapis.com/maps/api/place/details/json"
        self.photo_url = "https://maps.googleapis.com/maps/api/place/photo"
    
    async def search_nearby_restaurants(
        self,
        latitude: float,
        longitude: float,
        radius_meters: int = 500,
        max_results: int = 10
    ) -> List[PlaceResult]:
        """
        Find restaurants near a location using Google Places API.
        If no API key is present, returns mock data.
        """
        if not self.api_key:
            logger.warning("GOOGLE_PLACES_API_KEY not found. Using mock places data.")
            return self._get_mock_places(latitude, longitude, max_results)

        params = {
            "location": f"{latitude},{longitude}",
            "radius": radius_meters,
            "type": "restaurant",
            "key": self.api_key
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(self.nearby_url, params=params)
            data = response.json()
        
        if data["status"] not in ["OK", "ZERO_RESULTS"]:
            logger.error(f"Places search failed: {data['status']} - {data.get('error_message', '')}")
            raise ValueError(f"Places search API error: {data['status']}")
        
        results = []
        places_data = data.get("results", [])[:max_results]
        
        # In a real high-throughput scenario, we might want to parallelize these calls
        # But for now, sequential is safer for rate limits unless we use asyncio.gather
        import asyncio
        tasks = [self._get_place_details(place["place_id"]) for place in places_data]
        details_results = await asyncio.gather(*tasks, return_exceptions=True)

        for res in details_results:
            if isinstance(res, PlaceResult):
                results.append(res)
            elif isinstance(res, Exception):
                logger.warning(f"Failed to get details for a place: {res}")
        
        return results
    
    async def _get_place_details(self, place_id: str) -> PlaceResult:
        """
        Get detailed information about a place.
        """
        if not self.api_key:
            return self._get_mock_place_details(place_id)

        params = {
            "place_id": place_id,
            "fields": "name,formatted_address,geometry,rating,user_ratings_total,"
                     "price_level,types,formatted_phone_number,website,opening_hours,photos",
            "key": self.api_key
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(self.details_url, params=params)
            data = response.json()
        
        if data["status"] != "OK":
             raise ValueError(f"Place details failed: {data['status']}")
        
        result = data["result"]
        location = result["geometry"]["location"]
        
        # Extract photo references
        photos = []
        if "photos" in result:
            photos = [photo["photo_reference"] for photo in result["photos"][:5]]
        
        return PlaceResult(
            place_id=place_id,
            name=result.get("name", "Unknown"),
            address=result.get("formatted_address", ""),
            latitude=location["lat"],
            longitude=location["lng"],
            rating=result.get("rating"),
            total_ratings=result.get("user_ratings_total"),
            price_level=result.get("price_level"),
            types=result.get("types", []),
            phone_number=result.get("formatted_phone_number"),
            website=result.get("website"),
            opening_hours=result.get("opening_hours"),
            photos=photos
        )
    
    def get_photo_url(self, photo_reference: str, max_width: int = 800) -> str:
        """
        Generate URL to download a place photo.
        """
        if not self.api_key:
            return "https://via.placeholder.com/800x600?text=Restaurant+Photo"
            
        return f"{self.photo_url}?photoreference={photo_reference}&maxwidth={max_width}&key={self.api_key}"

    def _get_mock_places(self, lat: float, lng: float, count: int) -> List[PlaceResult]:
        """Return mock places for demo."""
        mocks = [
            PlaceResult(
                place_id="mock_1",
                name="El Califa",
                address="Av. Paseo de la Reforma 222",
                latitude=lat + 0.001,
                longitude=lng + 0.001,
                rating=4.5,
                total_ratings=1250,
                price_level=2,
                types=["restaurant", "food", "point_of_interest", "establishment"],
                photos=["mock_photo_ref_1"]
            ),
             PlaceResult(
                place_id="mock_2",
                name="Pujol",
                address="Tennyson 133, Polanco",
                latitude=lat - 0.001,
                longitude=lng - 0.001,
                rating=4.8,
                total_ratings=3400,
                price_level=4,
                types=["restaurant", "food", "point_of_interest", "establishment"],
                 photos=["mock_photo_ref_2"]
            ),
            PlaceResult(
                place_id="mock_3",
                name="Sonora Grill",
                address="Av. Masaryk 100",
                latitude=lat + 0.002,
                longitude=lng - 0.002,
                rating=4.3,
                total_ratings=890,
                price_level=3,
                types=["restaurant", "steak_house", "food", "point_of_interest", "establishment"],
                 photos=["mock_photo_ref_3"]
            )
        ]
        return mocks[:count]

    def _get_mock_place_details(self, place_id: str) -> PlaceResult:
        # Should normally not be reached if _get_mock_places handles listing,
        # but needed if we mocked search but not details.
        # For simplicity, returning a generic mock.
        return PlaceResult(
            place_id=place_id,
            name="Mock Restaurant",
            address="123 Mock St",
            latitude=0.0,
            longitude=0.0,
            rating=4.0,
            total_ratings=100,
            price_level=2,
            types=["restaurant"],
            photos=["mock_ref"]
        )
