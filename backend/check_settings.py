from app.core.config import get_settings
from app.api.deps import load_session

print("Loading settings...")
settings = get_settings()
print(f"GOOGLE_MAPS_API_KEY loaded: {bool(settings.google_maps_api_key)}")
if settings.google_maps_api_key:
    print(f"Key preview: {settings.google_maps_api_key[:5]}...")
else:
    print("Key is empty!")

print(f"GOOGLE_PLACES_API_KEY loaded: {bool(settings.google_places_api_key)}")
