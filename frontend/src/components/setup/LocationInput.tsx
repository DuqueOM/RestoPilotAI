'use client';

import { GoogleMap, Marker, StandaloneSearchBox, useJsApiLoader } from '@react-google-maps/api';
import { Building2, Loader2, MapPin, Search, Star, X } from 'lucide-react';
import { useCallback, useEffect, useRef, useState } from 'react';

// Libraries must be defined outside component to avoid re-renders
const LIBRARIES: ("places" | "geometry" | "drawing" | "visualization")[] = ["places"];

interface Location {
  lat: number;
  lng: number;
  address: string;
  placeId?: string;
  name?: string;
  rating?: number;
  userRatingsTotal?: number;
  photos?: string[];
}

interface BusinessCandidate {
  name: string;
  address: string;
  placeId: string;
  lat: number;
  lng: number;
  rating?: number;
  userRatingsTotal?: number;
  types?: string[];
  photos?: string[];
}

interface NearbyPlace {
  competitor_id?: string;
  name: string;
  address: string;
  rating?: number;
  userRatingsTotal?: number;
  placeId: string;
  distance?: string;
  types?: string[];
  social_media?: Record<string, unknown>[];
  menu?: Record<string, unknown>;
  competitive_intelligence?: Record<string, unknown>;
  metadata?: Record<string, unknown>;
}

interface LocationInputProps {
  value?: string;
  onChange?: (value: string) => void;
  onLocationSelect?: (location: Location, nearbyCompetitors: NearbyPlace[]) => void;
  initialLocation?: Location;
  sessionId?: string;
  placeholder?: string;
  autoFocus?: boolean;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '';

export function LocationInput({ 
  value, 
  onChange, 
  onLocationSelect, 
  initialLocation, 
  sessionId,
  placeholder,
  autoFocus
}: LocationInputProps) {
  // Google Maps Loader
  const { isLoaded } = useJsApiLoader({
    id: 'google-map-script',
    googleMapsApiKey: process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY || '',
    libraries: LIBRARIES
  });

  const [searchQuery, setSearchQuery] = useState(value || '');
  const [isSearching, setIsSearching] = useState(false);
  const [candidates, setCandidates] = useState<BusinessCandidate[]>([]);
  const [showCandidates, setShowCandidates] = useState(false);
  const [selectedLocation, setSelectedLocation] = useState<Location | null>(initialLocation || null);
  const [error, setError] = useState<string | null>(null);
  
  // Map State
  const [showMapPicker, setShowMapPicker] = useState(false);
  const [mapCenter, setMapCenter] = useState({ lat: 40.7128, lng: -74.0060 }); // Default NY
  const [mapZoom, setMapZoom] = useState(13);
  const mapRef = useRef<google.maps.Map | null>(null);
  const searchBoxRef = useRef<google.maps.places.SearchBox | null>(null);

  // Sync internal state with prop value
  useEffect(() => {
    if (value !== undefined && value !== searchQuery) {
      setSearchQuery(value);
    }
  }, [value, searchQuery]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setSearchQuery(newValue);
    if (onChange) {
      onChange(newValue);
    }
  };

  // --- BUSINESS SEARCH ---

  const searchBusiness = async () => {
    if (!searchQuery.trim()) return;
    
    setIsSearching(true);
    setError(null);
    setCandidates([]);
    setShowCandidates(true);
    setShowMapPicker(false);
    
    try {
      const formData = new FormData();
      formData.append('query', searchQuery);
      if (selectedLocation) {
        formData.append('lat', selectedLocation.lat.toString());
        formData.append('lng', selectedLocation.lng.toString());
      }
      
      const response = await fetch(`${API_BASE}/api/v1/location/identify-business`, {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.detail || `Search failed (${response.status})`);
      }
      
      const data = await response.json();
      
      if (data.status === 'success' && data.candidates.length > 0) {
        setCandidates(data.candidates);
      } else {
        setCandidates([]);
      }
      setShowCandidates(true);
    } catch (err) {
      console.error('Search error:', err);
      setError('Failed to search for business. Please try again.');
      setShowCandidates(true);
    } finally {
      setIsSearching(false);
    }
  };

  const selectCandidate = async (candidate: BusinessCandidate) => {
    setShowCandidates(false);
    setShowMapPicker(false);
    
    const loc: Location = {
      lat: candidate.lat,
      lng: candidate.lng,
      address: candidate.address,
      placeId: candidate.placeId,
      name: candidate.name,
      rating: candidate.rating,
      userRatingsTotal: candidate.userRatingsTotal,
      photos: candidate.photos
    };
    
    setSelectedLocation(loc);
    setMapCenter({ lat: loc.lat, lng: loc.lng });
    setMapZoom(17);
    
    // Update the input text to the selected address
    if (onChange) {
      onChange(candidate.address);
    } else {
      setSearchQuery(candidate.address);
    }
    
    // Set business in backend and enrich
    if (sessionId) {
      try {
        const formData = new FormData();
        formData.append('session_id', sessionId);
        formData.append('place_id', candidate.placeId);
        formData.append('enrich_profile', 'true');
        
        formData.append('name', candidate.name);
        formData.append('address', candidate.address);
        formData.append('lat', candidate.lat.toString());
        formData.append('lng', candidate.lng.toString());
        
        await fetch(`${API_BASE}/api/v1/location/set-business`, {
          method: 'POST',
          body: formData
        });
      } catch (err) {
        console.error('Failed to set business:', err);
      }
    }
    
    // Load nearby competitors with enrichment
    await loadNearbyCompetitors(loc, true);
  };

  // --- MAP PICKER ---

  const enableMapPicker = () => {
    setShowCandidates(false);
    setShowMapPicker(true);
    // Try to get user location
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                setMapCenter({
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                });
                setMapZoom(15);
            },
            () => {
                console.log("Geolocation permission denied or error");
            }
        );
    }
  };

  const handleMapClick = async (e: google.maps.MapMouseEvent) => {
    if (!e.latLng) return;
    
    const lat = e.latLng.lat();
    const lng = e.latLng.lng();
    
    // Reverse Geocoding
    const geocoder = new google.maps.Geocoder();
    
    try {
        const response = await geocoder.geocode({ location: { lat, lng } });
        if (response.results && response.results[0]) {
            const result = response.results[0];
            const address = result.formatted_address;
            
            const loc: Location = {
                lat,
                lng,
                address: address,
                placeId: result.place_id,
                name: "Pinned Location"
            };
            
            setSelectedLocation(loc);
            setMapCenter({ lat, lng });
            
            if (onChange) {
                onChange(address);
            } else {
                setSearchQuery(address);
            }
            
            // Auto-load competitors for this pinned location
            await loadNearbyCompetitors(loc, true);
        }
    } catch (err) {
        console.error("Geocoding failed", err);
        // Fallback if geocoding fails
         const loc: Location = {
            lat,
            lng,
            address: `${lat.toFixed(6)}, ${lng.toFixed(6)}`,
            name: "Pinned Location"
        };
        setSelectedLocation(loc);
        if (onChange) onChange(loc.address);
    }
  };

  const onLoadMap = useCallback((map: google.maps.Map) => {
    mapRef.current = map;
  }, []);

  const onPlacesChanged = () => {
    const places = searchBoxRef.current?.getPlaces();
    if (places && places.length > 0) {
        const place = places[0];
        if (place.geometry && place.geometry.location) {
             const lat = place.geometry.location.lat();
             const lng = place.geometry.location.lng();
             setMapCenter({ lat, lng });
             setMapZoom(17);
        }
    }
  };

  const onSearchBoxLoad = (ref: google.maps.places.SearchBox) => {
      searchBoxRef.current = ref;
  };

  // --- COMPETITORS ---

  const loadNearbyCompetitors = async (location: Location, enrich: boolean = false) => {
    try {
      const formData = new FormData();
      formData.append('lat', location.lat.toString());
      formData.append('lng', location.lng.toString());
      formData.append('radius', '1500'); // 1.5km radius
      formData.append('address', location.address || searchQuery);
      formData.append('enrich', enrich.toString());
      
      if (sessionId) {
        formData.append('session_id', sessionId);
      }
      
      const response = await fetch(`${API_BASE}/api/v1/location/nearby-restaurants`, {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) throw new Error('Failed to load nearby places');
      
      const data = await response.json();
      const restaurants = data.restaurants || [];
      
      if (onLocationSelect) {
        onLocationSelect(location, restaurants);
      }
    } catch (err) {
      console.error('Nearby search error:', err);
      setError('Failed to load competitors.');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      searchBusiness();
    }
  };

  return (
    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
      
      {/* Search Input Area */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={handleInputChange}
              onKeyPress={handleKeyPress}
              placeholder={placeholder || "Search your restaurant address..."}
              autoFocus={autoFocus}
              className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
            />
          </div>
          <button
            onClick={searchBusiness}
            disabled={isSearching || !searchQuery.trim()}
            className="px-6 py-3 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            {isSearching ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <>
                <Search className="w-5 h-5" />
                Find
              </>
            )}
          </button>
        </div>
        
        {error && (
          <p className="mt-2 text-sm text-red-600">{error}</p>
        )}

        {/* Candidates List */}
        {showCandidates && (
          <div className="mt-4 space-y-3 animate-in fade-in slide-in-from-top-4">
            <h4 className="text-sm font-medium text-gray-700">
              {candidates.length > 0 ? "Select your business:" : "No exact matches found."}
            </h4>
            <div className="grid gap-3 max-h-96 overflow-y-auto">
              {candidates.map((candidate, idx) => (
                <button
                  key={candidate.placeId || `candidate-${idx}`}
                  onClick={() => selectCandidate(candidate)}
                  className="flex items-start gap-4 p-3 w-full text-left bg-white border border-gray-200 rounded-lg hover:border-emerald-500 hover:shadow-md transition-all group"
                >
                  <div className="w-12 h-12 rounded-lg bg-gray-100 flex items-center justify-center flex-shrink-0">
                    <Building2 className="w-6 h-6 text-gray-400" />
                  </div>
                  <div className="flex-1">
                    <h5 className="font-medium text-gray-900 group-hover:text-emerald-600 transition-colors">
                      {candidate.name}
                    </h5>
                    <p className="text-sm text-gray-500 line-clamp-2">{candidate.address}</p>
                    {candidate.rating && (
                      <div className="flex items-center gap-1 mt-1 text-xs font-medium text-amber-500">
                        <Star className="w-3 h-3 fill-amber-500" />
                        {candidate.rating}
                      </div>
                    )}
                  </div>
                </button>
              ))}

              {/* Manual Location Button */}
              <button
                onClick={enableMapPicker}
                className="flex items-center justify-center gap-2 p-4 w-full text-sm font-medium text-gray-600 bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg hover:border-emerald-500 hover:text-emerald-600 hover:bg-emerald-50 transition-all"
              >
                <div className="p-1 bg-gray-200 rounded-full">
                  <MapPin className="w-4 h-4" />
                </div>
                My business is not listed (Pin on Map)
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Map Picker Area (Large Square) */}
      {showMapPicker && isLoaded && (
          <div className="p-4 bg-gray-50 border-b border-gray-200 animate-in fade-in zoom-in-95 duration-300">
             <div className="flex items-center justify-between mb-2">
                 <h4 className="font-medium text-gray-900 flex items-center gap-2">
                    <MapPin className="w-4 h-4 text-emerald-600" />
                    Pin your location
                 </h4>
                 <button onClick={() => setShowMapPicker(false)} className="text-gray-400 hover:text-gray-600">
                    <X className="w-5 h-5" />
                 </button>
             </div>
             <div className="relative w-full aspect-square md:aspect-[4/3] rounded-xl overflow-hidden shadow-inner border border-gray-300">
                <GoogleMap
                    mapContainerStyle={{ width: '100%', height: '100%' }}
                    center={mapCenter}
                    zoom={mapZoom}
                    onLoad={onLoadMap}
                    onClick={handleMapClick}
                    options={{
                        streetViewControl: false,
                        mapTypeControl: false,
                        fullscreenControl: true
                    }}
                >
                    <StandaloneSearchBox onLoad={onSearchBoxLoad} onPlacesChanged={onPlacesChanged}>
                         <input
                            type="text"
                            placeholder="Search map..."
                            className="box-border border border-transparent w-60 h-8 px-3 rounded shadow-md text-sm outline-none absolute top-2 left-1/2 -translate-x-1/2 z-10"
                         />
                    </StandaloneSearchBox>
                    {selectedLocation && (
                        <Marker position={{ lat: selectedLocation.lat, lng: selectedLocation.lng }} />
                    )}
                </GoogleMap>
                <div className="absolute bottom-4 left-1/2 -translate-x-1/2 bg-white/90 backdrop-blur px-4 py-2 rounded-full shadow-lg text-xs font-medium text-gray-600 pointer-events-none">
                    Click anywhere to set your location
                </div>
             </div>
          </div>
      )}

      {/* Selected Location Preview (When not picking) */}
      {selectedLocation && !showCandidates && !showMapPicker && (
        <div className="relative">
          {isLoaded && (
              <div className="h-48 bg-gray-100">
                <GoogleMap
                    mapContainerStyle={{ width: '100%', height: '100%' }}
                    center={{ lat: selectedLocation.lat, lng: selectedLocation.lng }}
                    zoom={16}
                    options={{
                        disableDefaultUI: true,
                        draggable: false,
                        zoomControl: false,
                        scrollwheel: false,
                        disableDoubleClickZoom: true
                    }}
                >
                    <Marker position={{ lat: selectedLocation.lat, lng: selectedLocation.lng }} />
                </GoogleMap>
              </div>
          )}
          
          <div className="absolute bottom-4 left-4 right-4 bg-white/95 backdrop-blur-sm rounded-lg p-3 shadow-lg">
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-start gap-3">
                <div className="p-2 bg-emerald-100 rounded-lg">
                  <Building2 className="w-5 h-5 text-emerald-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">Selected Location</p>
                  <p className="text-sm text-gray-600 line-clamp-1">{selectedLocation.address}</p>
                </div>
              </div>
              <button 
                onClick={() => setShowMapPicker(true)}
                className="text-xs text-blue-600 hover:text-blue-700 font-medium whitespace-nowrap"
              >
                Change
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
