'use client';

import { Building2, Loader2, Search, Star } from 'lucide-react';
import { useEffect, useState } from 'react';

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
  social_media?: any[];
  menu?: any;
  competitive_intelligence?: any;
  metadata?: any;
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

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export function LocationInput({ 
  value, 
  onChange, 
  onLocationSelect, 
  initialLocation, 
  sessionId,
  placeholder,
  autoFocus
}: LocationInputProps) {
  const [searchQuery, setSearchQuery] = useState(value || '');
  const [isSearching, setIsSearching] = useState(false);
  const [candidates, setCandidates] = useState<BusinessCandidate[]>([]);
  const [showCandidates, setShowCandidates] = useState(false);
  const [selectedLocation, setSelectedLocation] = useState<Location | null>(initialLocation || null);
  const [nearbyCompetitors, setNearbyCompetitors] = useState<NearbyPlace[]>([]);
  const [isLoadingNearby, setIsLoadingNearby] = useState(false);
  const [isEnriching, setIsEnriching] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Sync internal state with prop value
  useEffect(() => {
    if (value !== undefined) {
      setSearchQuery(value);
    }
  }, [value]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setSearchQuery(newValue);
    if (onChange) {
      onChange(newValue);
    }
  };

  const searchBusiness = async () => {
    if (!searchQuery.trim()) return;
    
    setIsSearching(true);
    setError(null);
    setCandidates([]);
    setShowCandidates(true);
    
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
        setError('No businesses found. Try a more specific name or address.');
        setShowCandidates(false);
      }
    } catch (err) {
      console.error('Search error:', err);
      setError('Failed to search for business. Please try again.');
      setShowCandidates(false);
    } finally {
      setIsSearching(false);
    }
  };

  const selectCandidate = async (candidate: BusinessCandidate) => {
    setShowCandidates(false);
    
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
    
    // Update the input text to the selected address
    if (onChange) {
      onChange(candidate.address);
    } else {
      setSearchQuery(candidate.address);
    }
    
    // Set business in backend and enrich
    if (sessionId) {
      setIsEnriching(true);
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
      } finally {
        setIsEnriching(false);
      }
    }
    
    // Load nearby competitors with enrichment
    await loadNearbyCompetitors(loc, true);
  };

  const loadNearbyCompetitors = async (location: Location, enrich: boolean = false) => {
    setIsLoadingNearby(true);
    
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
      setNearbyCompetitors(restaurants);
      
      if (onLocationSelect) {
        onLocationSelect(location, restaurants);
      }
    } catch (err) {
      console.error('Nearby search error:', err);
      setError('Failed to load competitors.');
    } finally {
      setIsLoadingNearby(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      searchBusiness();
    }
  };

  const getMapEmbedUrl = (location: Location) => {
    const apiKey = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY;
    
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
      {/* Header (Hidden if simple input mode, or keep it?) 
          The user design in page.tsx wraps this in a section, so maybe we keep the internal styling 
          but simplify if needed. For now, let's keep the rich UI as it adds value. 
      */}
      
      {/* Search */}
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

        {/* Candidates Selection */}
        {showCandidates && candidates.length > 0 && (
          <div className="mt-4 space-y-3 animate-in fade-in slide-in-from-top-4">
            <h4 className="text-sm font-medium text-gray-700">Select your business:</h4>
            <div className="grid gap-3 max-h-96 overflow-y-auto">
              {candidates.map((candidate) => (
                <button
                  key={candidate.placeId}
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
            </div>
          </div>
        )}
      </div>

      {/* Map Preview */}
      {selectedLocation && !showCandidates && (
        <div className="relative">
          <div className="h-48 bg-gray-100">
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
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
