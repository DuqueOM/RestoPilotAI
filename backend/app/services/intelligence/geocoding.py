import httpx
from typing import Optional
from pydantic import BaseModel
from loguru import logger
from app.core.config import get_settings

class GeocodingResult(BaseModel):
    latitude: float
    longitude: float
    formatted_address: str
    neighborhood: Optional[str] = None
    city: str
    country: str

class GeocodingService:
    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.google_maps_api_key
        self.base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    
    async def geocode(self, address: str) -> GeocodingResult:
        """
        Convert address to coordinates using Google Maps Geocoding API.
        If no API key is present, returns a mock location for demo purposes.
        """
        if not self.api_key:
            logger.warning("GOOGLE_MAPS_API_KEY not found. Using mock geocoding data.")
            return self._get_mock_geocode(address)

        params = {
            "address": address,
            "key": self.api_key
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(self.base_url, params=params)
            data = response.json()
        
        if data["status"] != "OK":
            logger.error(f"Geocoding failed: {data['status']} - {data.get('error_message', '')}")
            if data["status"] == "ZERO_RESULTS":
                 raise ValueError(f"No location found for address: {address}")
            raise ValueError(f"Geocoding API error: {data['status']}")
        
        result = data["results"][0]
        location = result["geometry"]["location"]
        
        # Extract neighborhood, city, country
        address_components = result["address_components"]
        neighborhood = None
        city = None
        country = None
        
        for component in address_components:
            types = component["types"]
            if "neighborhood" in types or "sublocality" in types:
                neighborhood = component["long_name"]
            if "locality" in types:
                city = component["long_name"]
            if "country" in types:
                country = component["long_name"]
        
        return GeocodingResult(
            latitude=location["lat"],
            longitude=location["lng"],
            formatted_address=result["formatted_address"],
            neighborhood=neighborhood,
            city=city or "Unknown",
            country=country or "Unknown"
        )

    def _get_mock_geocode(self, address: str) -> GeocodingResult:
        """Return mock data for demo/testing without API key."""
        # Default to a location in Mexico City (Polanco) for demo
        return GeocodingResult(
            latitude=19.432608,
            longitude=-99.133209,
            formatted_address=address or "Av. Presidente Masaryk, Polanco, CDMX",
            neighborhood="Polanco",
            city="Ciudad de México",
            country="México"
        )
