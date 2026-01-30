'use client';

import { Building2, Clock, ExternalLink, Loader2, MapPin, Search, Star, Users } from 'lucide-react';
import { useState } from 'react';

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

interface LocationPickerProps {
  onLocationSelect: (location: Location, nearbyCompetitors: NearbyPlace[]) => void;
  initialLocation?: Location;
  sessionId?: string;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function LocationPicker({ onLocationSelect, initialLocation, sessionId }: LocationPickerProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [candidates, setCandidates] = useState<BusinessCandidate[]>([]);
  const [showCandidates, setShowCandidates] = useState(false);
  const [selectedLocation, setSelectedLocation] = useState<Location | null>(initialLocation || null);
  const [nearbyCompetitors, setNearbyCompetitors] = useState<NearbyPlace[]>([]);
  const [isLoadingNearby, setIsLoadingNearby] = useState(false);
  const [isEnriching, setIsEnriching] = useState(false);
  const [enrichProgress, setEnrichProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

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
    
    // Set business in backend and enrich
    if (sessionId) {
      setIsEnriching(true);
      try {
        const formData = new FormData();
        formData.append('session_id', sessionId);
        formData.append('place_id', candidate.placeId);
        formData.append('enrich_profile', 'true');
        
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
    setEnrichProgress(0);
    
    try {
      const formData = new FormData();
      formData.append('lat', location.lat.toString());
      formData.append('lng', location.lng.toString());
      formData.append('radius', '1500'); // 1.5km radius
      formData.append('address', location.address || searchQuery);
      formData.append('enrich', enrich.toString());
      
      const response = await fetch(`${API_BASE}/api/v1/location/nearby-restaurants`, {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) throw new Error('Failed to load nearby places');
      
      const data = await response.json();
      const restaurants = data.restaurants || [];
      setNearbyCompetitors(restaurants);
      
      onLocationSelect(location, restaurants);
    } catch (err) {
      console.error('Nearby search error:', err);
      setError('Failed to load competitors.');
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
            onClick={searchBusiness}
            disabled={isSearching || !searchQuery.trim()}
            className="px-6 py-3 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            {isSearching ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <>
                <Search className="w-5 h-5" />
                Find Business
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
                  {candidate.photos && candidate.photos.length > 0 ? (
                    <div className="w-16 h-16 rounded-lg bg-gray-100 overflow-hidden flex-shrink-0">
                      <img 
                        src={`https://maps.googleapis.com/maps/api/place/photo?maxwidth=100&photo_reference=${candidate.photos[0]}&key=${process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY}`}
                        alt={candidate.name}
                        className="w-full h-full object-cover"
                      />
                    </div>
                  ) : (
                    <div className="w-16 h-16 rounded-lg bg-gray-100 flex items-center justify-center flex-shrink-0">
                      <Building2 className="w-8 h-8 text-gray-400" />
                    </div>
                  )}
                  <div className="flex-1">
                    <h5 className="font-medium text-gray-900 group-hover:text-emerald-600 transition-colors">
                      {candidate.name}
                    </h5>
                    <p className="text-sm text-gray-500 line-clamp-2">{candidate.address}</p>
                    <div className="flex items-center gap-2 mt-1">
                      {candidate.rating && (
                        <div className="flex items-center gap-1 text-xs font-medium text-amber-500">
                          <Star className="w-3 h-3 fill-amber-500" />
                          {candidate.rating} ({candidate.userRatingsTotal})
                        </div>
                      )}
                      <span className="text-xs text-emerald-600 font-medium">Select this location</span>
                    </div>
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
              <div className="flex items-center gap-2 text-sm text-emerald-600">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span className="animate-pulse">Analyzing & Enriching Data...</span>
              </div>
            )}
          </div>

          {nearbyCompetitors.length > 0 ? (
            <div className="space-y-3 max-h-96 overflow-y-auto pr-1">
              {nearbyCompetitors.map((place, idx) => (
                <div
                  key={place.placeId || idx}
                  className="p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors border border-transparent hover:border-gray-200"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <p className="font-medium text-gray-900 text-sm">{place.name}</p>
                        {place.social_media && place.social_media.length > 0 && (
                          <div className="flex gap-1">
                            {place.social_media.map((sm: any, i: number) => (
                              <span key={i} title={sm.platform} className="text-xs">
                                {sm.platform === 'facebook' && '📘'}
                                {sm.platform === 'instagram' && '📸'}
                                {sm.platform === 'whatsapp_business' && '💬'}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                      <p className="text-xs text-gray-500 mt-0.5">{place.address}</p>
                      
                      {/* Enriched Data Badges */}
                      {place.competitive_intelligence && (
                        <div className="flex flex-wrap gap-1 mt-1.5">
                          {place.competitive_intelligence.cuisine_types?.slice(0, 2).map((tag: string, i: number) => (
                            <span key={i} className="px-1.5 py-0.5 bg-blue-50 text-blue-700 text-[10px] rounded-full border border-blue-100">
                              {tag}
                            </span>
                          ))}
                          {place.menu?.item_count > 0 && (
                            <span className="px-1.5 py-0.5 bg-emerald-50 text-emerald-700 text-[10px] rounded-full border border-emerald-100">
                              {place.menu.item_count} menu items
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                    {place.rating && (
                      <div className="flex flex-col items-end gap-1">
                        <div className="flex items-center gap-1 text-sm bg-white px-1.5 py-0.5 rounded border border-gray-100">
                          <Star className="w-3.5 h-3.5 text-yellow-400 fill-yellow-400" />
                          <span className="font-medium">{place.rating}</span>
                        </div>
                        {place.userRatingsTotal && (
                          <span className="text-gray-400 text-[10px]">({place.userRatingsTotal} reviews)</span>
                        )}
                      </div>
                    )}
                  </div>
                  {place.distance && (
                    <div className="flex items-center gap-1 mt-2 text-xs text-gray-500 border-t border-gray-100 pt-2">
                      <Clock className="w-3 h-3" />
                      {place.distance}
                      {place.metadata?.confidence_score && (
                        <span className="ml-auto text-emerald-600 font-medium" title="Data Confidence">
                           {Math.round(place.metadata.confidence_score * 100)}% Match
                        </span>
                      )}
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
      {!selectedLocation && !showCandidates && (
        <div className="p-8 text-center">
          <MapPin className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500">
            Search for your restaurant name to verify your business and discover nearby competitors
          </p>
        </div>
      )}
    </div>
  );
}
