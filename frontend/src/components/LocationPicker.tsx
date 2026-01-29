'use client';

import { Building2, Clock, ExternalLink, Loader2, MapPin, Search, Star, Users } from 'lucide-react';
import { useState } from 'react';

interface Location {
  lat: number;
  lng: number;
  address: string;
  placeId?: string;
}

interface NearbyPlace {
  name: string;
  address: string;
  rating?: number;
  userRatingsTotal?: number;
  placeId: string;
  distance?: string;
  types?: string[];
}

interface LocationPickerProps {
  onLocationSelect: (location: Location, nearbyCompetitors: NearbyPlace[]) => void;
  initialLocation?: Location;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function LocationPicker({ onLocationSelect, initialLocation }: LocationPickerProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [selectedLocation, setSelectedLocation] = useState<Location | null>(initialLocation || null);
  const [nearbyCompetitors, setNearbyCompetitors] = useState<NearbyPlace[]>([]);
  const [isLoadingNearby, setIsLoadingNearby] = useState(false);
  const [mapLoaded, setMapLoaded] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const searchLocation = async () => {
    if (!searchQuery.trim()) return;
    
    setIsSearching(true);
    setError(null);
    
    try {
      const formData = new FormData();
      formData.append('query', searchQuery);
      
      const response = await fetch(`${API_BASE}/api/v1/location/search`, {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        // Try to get detailed error from backend
        const errorData = await response.json().catch(() => null);
        const errorMsg = errorData?.detail || `Search failed (${response.status})`;
        throw new Error(errorMsg);
      }
      
      const data = await response.json();
      
      if (data.location) {
        const loc: Location = {
          lat: data.location.lat,
          lng: data.location.lng,
          address: data.location.address,
          placeId: data.location.place_id
        };
        setSelectedLocation(loc);
        
        // Load nearby competitors
        await loadNearbyCompetitors(loc);
      } else {
        throw new Error('No location found in response');
      }
    } catch (err) {
      console.error('Search error:', err);
      const errorMessage = err instanceof Error ? err.message : 'Search failed';
      setError(`Could not find location: ${errorMessage}. Try a more specific address or different search terms.`);
    } finally {
      setIsSearching(false);
    }
  };

  const loadNearbyCompetitors = async (location: Location) => {
    setIsLoadingNearby(true);
    
    try {
      const formData = new FormData();
      formData.append('lat', location.lat.toString());
      formData.append('lng', location.lng.toString());
      formData.append('radius', '1500'); // 1.5km radius
      
      const response = await fetch(`${API_BASE}/api/v1/location/nearby-restaurants`, {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) throw new Error('Failed to load nearby places');
      
      const data = await response.json();
      setNearbyCompetitors(data.restaurants || []);
      
      // Notify parent
      onLocationSelect(location, data.restaurants || []);
    } catch (err) {
      console.error('Nearby search error:', err);
    } finally {
      setIsLoadingNearby(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      searchLocation();
    }
  };

  const getMapEmbedUrl = (location: Location) => {
    const apiKey = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY;
    
    // Use OpenStreetMap if no Google API key (free, no API key required)
    if (!apiKey) {
      return `https://www.openstreetmap.org/export/embed.html?bbox=${location.lng - 0.01},${location.lat - 0.01},${location.lng + 0.01},${location.lat + 0.01}&layer=mapnik&marker=${location.lat},${location.lng}`;
    }
    
    return `https://www.google.com/maps/embed/v1/place?key=${apiKey}&q=${location.lat},${location.lng}&zoom=15`;
  };

  const openInGoogleMaps = () => {
    if (selectedLocation) {
      window.open(
        `https://www.google.com/maps/search/?api=1&query=${selectedLocation.lat},${selectedLocation.lng}`,
        '_blank'
      );
    }
  };

  return (
    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-emerald-500 to-teal-600 p-4 text-white">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-white/20 rounded-lg">
            <MapPin className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-semibold">Restaurant Location</h3>
            <p className="text-xs text-white/80">Find your restaurant and discover competitors</p>
          </div>
        </div>
      </div>

      {/* Search */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Search your restaurant address..."
              className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
            />
          </div>
          <button
            onClick={searchLocation}
            disabled={isSearching || !searchQuery.trim()}
            className="px-6 py-3 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            {isSearching ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <>
                <MapPin className="w-5 h-5" />
                Locate
              </>
            )}
          </button>
        </div>
        
        {error && (
          <p className="mt-2 text-sm text-red-600">{error}</p>
        )}
      </div>

      {/* Map Preview */}
      {selectedLocation && (
        <div className="relative">
          <div className="h-64 bg-gray-100">
            <iframe
              src={getMapEmbedUrl(selectedLocation)}
              width="100%"
              height="100%"
              style={{ border: 0 }}
              allowFullScreen
              loading="lazy"
              referrerPolicy="no-referrer-when-downgrade"
              className="w-full h-full"
            />
          </div>
          
          {/* Selected Location Info */}
          <div className="absolute bottom-4 left-4 right-4 bg-white/95 backdrop-blur-sm rounded-lg p-3 shadow-lg">
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-start gap-3">
                <div className="p-2 bg-emerald-100 rounded-lg">
                  <Building2 className="w-5 h-5 text-emerald-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">Your Location</p>
                  <p className="text-sm text-gray-600">{selectedLocation.address}</p>
                </div>
              </div>
              <button
                onClick={openInGoogleMaps}
                className="p-2 text-gray-500 hover:text-emerald-600 hover:bg-emerald-50 rounded-lg transition-colors"
                title="Open in Google Maps"
              >
                <ExternalLink className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Nearby Competitors */}
      {selectedLocation && (
        <div className="p-4">
          <div className="flex items-center justify-between mb-3">
            <h4 className="font-medium text-gray-900 flex items-center gap-2">
              <Users className="w-5 h-5 text-orange-500" />
              Nearby Competitors
            </h4>
            {isLoadingNearby && (
              <Loader2 className="w-4 h-4 animate-spin text-gray-400" />
            )}
          </div>

          {nearbyCompetitors.length > 0 ? (
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {nearbyCompetitors.map((place, idx) => (
                <div
                  key={place.placeId || idx}
                  className="p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <p className="font-medium text-gray-900 text-sm">{place.name}</p>
                      <p className="text-xs text-gray-500 mt-0.5">{place.address}</p>
                    </div>
                    {place.rating && (
                      <div className="flex items-center gap-1 text-sm">
                        <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
                        <span className="font-medium">{place.rating}</span>
                        {place.userRatingsTotal && (
                          <span className="text-gray-400 text-xs">({place.userRatingsTotal})</span>
                        )}
                      </div>
                    )}
                  </div>
                  {place.distance && (
                    <div className="flex items-center gap-1 mt-2 text-xs text-gray-500">
                      <Clock className="w-3 h-3" />
                      {place.distance}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : !isLoadingNearby ? (
            <p className="text-sm text-gray-500 text-center py-4">
              No nearby competitors found within 1.5km
            </p>
          ) : null}

          {nearbyCompetitors.length > 0 && (
            <p className="mt-3 text-xs text-gray-500 text-center">
              This data will be used by AI to provide competitive insights
            </p>
          )}
        </div>
      )}

      {/* Empty State */}
      {!selectedLocation && (
        <div className="p-8 text-center">
          <MapPin className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500">
            Search for your restaurant to see it on the map and discover nearby competitors
          </p>
        </div>
      )}
    </div>
  );
}
