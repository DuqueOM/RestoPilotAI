'use client';

import { LocationInput } from '@/components/setup/LocationInput';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Building2, CheckCircle2, Facebook, Globe, Instagram, Loader2, MapPin, Star } from 'lucide-react';
import { useState } from 'react';
import { useWizard } from './SetupWizard';

export function LocationStep() {
  const { formData, updateFormData } = useWizard();
  const [showSocial, setShowSocial] = useState(false);
  const [isEnriching, setIsEnriching] = useState(false);
  const [enrichmentDone, setEnrichmentDone] = useState(false);

  const handleLocationChange = (value: string) => {
    updateFormData({ location: value });
  };

  const handleLocationSelect = (location: any, nearbyCompetitors?: any[]) => {
    // Clear stale enrichment data when a new business is selected
    setEnrichmentDone(false);
    updateFormData({
      location: location.address,
      placeId: location.placeId,
      businessName: location.name || formData.businessName,
      businessRating: location.rating,
      businessUserRatingsTotal: location.userRatingsTotal,
      nearbyCompetitors: nearbyCompetitors || [],
      enrichedProfile: undefined,
      instagram: '',
      facebook: '',
      tiktok: '',
      website: '',
      businessPhone: '',
      businessWebsite: '',
    });
  };

  const handleBusinessEnriched = (profile: any) => {
    setIsEnriching(false);
    setEnrichmentDone(true);

    const updates: Partial<typeof formData> = {
      enrichedProfile: profile,
    };

    // Auto-fill website and phone from enriched profile
    if (profile.contact?.website) {
      updates.website = profile.contact.website;
    }
    if (profile.contact?.phone) {
      updates.businessPhone = profile.contact.phone;
    }

    // Auto-fill social media from enriched profile (always overwrite — enrichment is authoritative)
    const socialMedia = profile.social_media || [];
    for (const sm of socialMedia) {
      if (sm.platform === 'instagram') {
        updates.instagram = sm.handle || sm.url?.replace(/.*instagram\.com\//, '').replace(/\/.*/, '') || '';
      }
      if (sm.platform === 'facebook') {
        updates.facebook = sm.handle || sm.url?.replace(/.*facebook\.com\//, '').replace(/\/.*/, '') || '';
      }
      if (sm.platform === 'tiktok') {
        updates.tiktok = sm.handle || sm.url?.replace(/.*tiktok\.com\/@?/, '').replace(/\/.*/, '') || '';
      }
    }

    // Auto-open social media section if we found any
    if (updates.instagram || updates.facebook || updates.tiktok || updates.website) {
      setShowSocial(true);
    }

    updateFormData(updates);
  };

  return (
    <div className="space-y-6">
      {/* Main Location Input */}
      <div className="space-y-2">
        <Label className="text-base font-medium flex items-center gap-2">
          <MapPin className="h-4 w-4 text-purple-600" />
          Restaurant Location *
        </Label>
        <p className="text-sm text-gray-500 mb-3">
          Search for your restaurant address to get local market insights
        </p>
        <LocationInput
          value={formData.location}
          onChange={handleLocationChange}
          onLocationSelect={handleLocationSelect}
          onBusinessEnriched={handleBusinessEnriched}
          onEnrichmentStarted={() => setIsEnriching(true)}
          placeholder="Ex: 123 Main St, New York, NY"
        />

        {/* Enrichment Status */}
        {isEnriching && (
          <div className="flex items-center gap-2 mt-3 p-3 bg-purple-50 rounded-lg border border-purple-100 animate-pulse">
            <Loader2 className="h-4 w-4 text-purple-600 animate-spin" />
            <span className="text-sm text-purple-700">Gemini is analyzing your business and finding social media...</span>
          </div>
        )}
        {enrichmentDone && !isEnriching && (
          <div className="flex items-center gap-2 mt-3 p-3 bg-green-50 rounded-lg border border-green-100">
            <CheckCircle2 className="h-4 w-4 text-green-600" />
            <span className="text-sm text-green-700">Business profile enriched with Google & Gemini data</span>
          </div>
        )}
      </div>

      {/* Business Name (auto-filled or manual) */}
      <div className="space-y-2">
        <Label className="text-base font-medium flex items-center gap-2">
          <Building2 className="h-4 w-4 text-purple-600" />
          Business Name
        </Label>
        <Input
          value={formData.businessName || ''}
          onChange={(e) => updateFormData({ businessName: e.target.value })}
          placeholder="Your restaurant name"
          className="text-lg"
        />
        {formData.businessRating && (
          <div className="flex items-center gap-3 text-sm text-gray-600">
            <span className="flex items-center gap-1">
              <Star className="h-4 w-4 fill-amber-400 text-amber-400" />
              {formData.businessRating}
            </span>
            {formData.businessUserRatingsTotal && (
              <span>({formData.businessUserRatingsTotal.toLocaleString()} reviews)</span>
            )}
          </div>
        )}
        <p className="text-xs text-gray-500">
          Auto-fills if you select your business from Google Maps
        </p>
      </div>

      {/* Social Media Toggle */}
      <div className="pt-4 border-t">
        <Button
          type="button"
          variant="ghost"
          onClick={() => setShowSocial(!showSocial)}
          className="text-purple-600 hover:text-purple-700 hover:bg-purple-50 -ml-2"
        >
          {showSocial ? '− Hide' : '+ Add'} social media (optional)
        </Button>
      </div>

      {/* Social Media Inputs */}
      {showSocial && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg animate-in fade-in slide-in-from-top-2">
          <div className="space-y-2">
            <Label className="text-sm flex items-center gap-2">
              <Instagram className="h-4 w-4 text-pink-600" />
              Instagram
            </Label>
            <div className="flex">
              <span className="inline-flex items-center px-3 bg-gray-100 border border-r-0 border-gray-300 rounded-l-md text-gray-500 text-sm">
                @
              </span>
              <Input
                value={formData.instagram || ''}
                onChange={(e) => updateFormData({ instagram: e.target.value })}
                placeholder="your_restaurant"
                className="rounded-l-none"
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label className="text-sm flex items-center gap-2">
              <Facebook className="h-4 w-4 text-blue-600" />
              Facebook
            </Label>
            <div className="flex">
              <span className="inline-flex items-center px-3 bg-gray-100 border border-r-0 border-gray-300 rounded-l-md text-gray-500 text-sm">
                fb.com/
              </span>
              <Input
                value={formData.facebook || ''}
                onChange={(e) => updateFormData({ facebook: e.target.value })}
                placeholder="your_page"
                className="rounded-l-none"
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label className="text-sm flex items-center gap-2">
              <svg className="h-4 w-4" viewBox="0 0 24 24" fill="currentColor">
                <path d="M19.59 6.69a4.83 4.83 0 01-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 01-5.2 1.74 2.89 2.89 0 012.31-4.64 2.93 2.93 0 01.88.13V9.4a6.84 6.84 0 00-1-.05A6.33 6.33 0 005 20.1a6.34 6.34 0 0010.86-4.43v-7a8.16 8.16 0 004.77 1.52v-3.4a4.85 4.85 0 01-1-.1z" />
              </svg>
              TikTok
            </Label>
            <div className="flex">
              <span className="inline-flex items-center px-3 bg-gray-100 border border-r-0 border-gray-300 rounded-l-md text-gray-500 text-sm">
                @
              </span>
              <Input
                value={formData.tiktok || ''}
                onChange={(e) => updateFormData({ tiktok: e.target.value })}
                placeholder="your_restaurant"
                className="rounded-l-none"
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label className="text-sm flex items-center gap-2">
              <Globe className="h-4 w-4 text-gray-600" />
              Website
            </Label>
            <Input
              value={formData.website || ''}
              onChange={(e) => updateFormData({ website: e.target.value })}
              placeholder="www.yourrestaurant.com"
            />
          </div>
        </div>
      )}

      {/* Info Card */}
      <div className="p-4 bg-purple-50 rounded-lg border border-purple-100">
        <h4 className="font-medium text-purple-900 mb-2">
          🧠 Why do we need your location?
        </h4>
        <ul className="text-sm text-purple-800 space-y-1">
          <li>• Gemini 3 will automatically find nearby competitors</li>
          <li>• It will analyze market trends in your area</li>
          <li>• It will compare prices with similar restaurants</li>
          <li>• It will identify unique local opportunities</li>
        </ul>
      </div>
    </div>
  );
}

export default LocationStep;
