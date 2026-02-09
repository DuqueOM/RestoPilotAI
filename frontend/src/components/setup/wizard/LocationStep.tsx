'use client';

import { LocationInput } from '@/components/setup/LocationInput';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
    Building2, CheckCircle2, ChevronDown, ChevronRight,
    Facebook, Globe, Instagram, Loader2, MapPin, Search,
    ShoppingBag, Star, Truck, Zap
} from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { useWizard } from './SetupWizard';

// Pipeline steps shown during enrichment (for hackathon judges)
const ENRICHMENT_STEPS = [
  { id: 'place_details', label: 'Google Places API', detail: 'Fetching business details, photos, reviews...', icon: MapPin, gemini: false },
  { id: 'web_search', label: 'Gemini Search Grounding', detail: 'Searching the web for social media, delivery platforms...', icon: Search, gemini: true },
  { id: 'social_media', label: 'Social Media Discovery', detail: 'Identifying Facebook, Instagram, TikTok profiles...', icon: Instagram, gemini: true },
  { id: 'whatsapp', label: 'WhatsApp Business Detection', detail: 'Checking for WhatsApp Business catalog...', icon: Zap, gemini: false },
  { id: 'photos', label: 'Gemini Vision Analysis', detail: 'Analyzing business photos with multimodal AI...', icon: Star, gemini: true },
  { id: 'menu', label: 'Menu Extraction', detail: 'Extracting menu items from all discovered sources...', icon: ShoppingBag, gemini: true },
  { id: 'reviews', label: 'Review Sentiment Analysis', detail: 'Analyzing customer reviews with Gemini...', icon: Star, gemini: true },
  { id: 'consolidation', label: 'Intelligence Consolidation', detail: 'Fusing all data sources into a unified profile...', icon: Zap, gemini: true },
];

export function LocationStep() {
  const { formData, updateFormData } = useWizard();
  const [showSocial, setShowSocial] = useState(false);
  const [isEnriching, setIsEnriching] = useState(false);
  const [enrichmentDone, setEnrichmentDone] = useState(false);
  const [enrichmentFailed, setEnrichmentFailed] = useState(false);
  const [showPipeline, setShowPipeline] = useState(false);
  const [enrichmentStarted, setEnrichmentStarted] = useState(false);
  const [activeStep, setActiveStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState<Set<number>>(new Set());
  const stepTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Restore state if enrichedProfile already exists (e.g., from localStorage)
  useEffect(() => {
    if (formData.enrichedProfile && !enrichmentDone && !isEnriching) {
      setEnrichmentDone(true);
      setEnrichmentStarted(true);
      setCompletedSteps(new Set(ENRICHMENT_STEPS.map((_, i) => i)));
      setActiveStep(ENRICHMENT_STEPS.length);
      // Auto-open social section if we have social data
      if (formData.instagram || formData.facebook || formData.tiktok || formData.website || (formData.deliveryPlatforms || []).length) {
        setShowSocial(true);
      }
    }
  }, []); // Run once on mount

  // Animate pipeline steps while enrichment is running
  useEffect(() => {
    if (isEnriching) {
      setActiveStep(0);
      setCompletedSteps(new Set());
      let step = 0;
      stepTimerRef.current = setInterval(() => {
        step++;
        if (step < ENRICHMENT_STEPS.length) {
          setCompletedSteps(prev => new Set([...prev, step - 1]));
          setActiveStep(step);
        } else if (step === ENRICHMENT_STEPS.length) {
          setCompletedSteps(prev => new Set([...prev, step - 1]));
        }
      }, 5000); // ~5s per step ≈ 40s total (realistic for the pipeline)
    } else {
      if (stepTimerRef.current) clearInterval(stepTimerRef.current);
      if (enrichmentDone) {
        // Mark all steps as completed
        setCompletedSteps(new Set(ENRICHMENT_STEPS.map((_, i) => i)));
        setActiveStep(ENRICHMENT_STEPS.length);
      }
    }
    return () => { if (stepTimerRef.current) clearInterval(stepTimerRef.current); };
  }, [isEnriching, enrichmentDone]);

  const handleLocationChange = (value: string) => {
    updateFormData({ location: value });
  };

  const handleLocationSelect = (location: any, nearbyCompetitors?: any[]) => {
    setEnrichmentDone(false);
    setEnrichmentFailed(false);
    setEnrichmentStarted(false);
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
      deliveryPlatforms: [],
    });
  };

  const handleBusinessEnriched = (profile: any) => {
    setIsEnriching(false);
    
    if (!profile) {
      console.warn('[RestoPilot] Enrichment returned null profile — pipeline may have failed');
      setEnrichmentFailed(true);
      return;
    }
    
    console.log('[RestoPilot] Enrichment profile received:', {
      name: profile.name,
      social_media: profile.social_media,
      delivery_platforms: profile.delivery_platforms,
      contact: profile.contact,
      data_sources: profile.metadata?.data_sources,
    });
    
    setEnrichmentDone(true);

    const updates: Partial<typeof formData> = {
      enrichedProfile: profile,
    };

    // Auto-fill website and phone
    if (profile.contact?.website) {
      updates.website = profile.contact.website;
      updates.businessWebsite = profile.contact.website;
    }
    if (profile.contact?.phone) {
      updates.businessPhone = profile.contact.phone;
    } else if (profile.contact?.whatsapp_business) {
      // Fallback to WhatsApp number if phone is missing
      updates.businessPhone = profile.contact.whatsapp_business;
    }
    
    if (profile.website) {
      updates.website = updates.website || profile.website;
    }

    // Auto-fill social media
    const socialMedia = profile.social_media || [];
    console.log('[RestoPilot] Social media entries to process:', socialMedia);
    for (const sm of socialMedia) {
      const platform = (sm.platform || '').toLowerCase();
      if (platform === 'instagram') {
        updates.instagram = sm.handle || sm.url?.replace(/.*instagram\.com\//, '').replace(/[\/\?].*/, '') || '';
      }
      if (platform === 'facebook') {
        updates.facebook = sm.handle || sm.url?.replace(/.*facebook\.com\//, '').replace(/[\/\?].*/, '') || '';
      }
      if (platform === 'tiktok') {
        updates.tiktok = sm.handle || sm.url?.replace(/.*tiktok\.com\/@?/, '').replace(/[\/\?].*/, '') || '';
      }
    }

    // Auto-fill delivery platforms
    if (profile.delivery_platforms?.length) {
      updates.deliveryPlatforms = profile.delivery_platforms;
    }

    console.log('[RestoPilot] Auto-fill updates:', {
      instagram: updates.instagram,
      facebook: updates.facebook,
      tiktok: updates.tiktok,
      website: updates.website,
      deliveryPlatforms: updates.deliveryPlatforms,
    });

    // Auto-open social media section if we found anything
    if (updates.instagram || updates.facebook || updates.tiktok || updates.website || updates.deliveryPlatforms?.length) {
      setShowSocial(true);
    }

    updateFormData(updates);
  };

  const dataSources = formData.enrichedProfile?.metadata?.data_sources || [];
  const socialFound = (formData.enrichedProfile?.social_media || []).length;
  const deliveryFound = (formData.deliveryPlatforms || []).length;

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
          onEnrichmentStarted={() => { setIsEnriching(true); setShowPipeline(true); setEnrichmentStarted(true); setEnrichmentFailed(false); }}
          placeholder="Ex: 123 Main St, New York, NY"
        />

        {/* Enrichment Progress Panel — persists after completion for judges */}
        {(isEnriching || enrichmentDone || enrichmentFailed || enrichmentStarted) && (
          <div className={`mt-3 rounded-lg border overflow-hidden ${
            isEnriching ? 'border-purple-200' : enrichmentDone ? 'border-green-200' : 'border-amber-200'
          }`}>
            {/* Header */}
            <button
              onClick={() => setShowPipeline(!showPipeline)}
              className={`w-full flex items-center justify-between px-4 py-3 text-left transition-colors ${
                isEnriching ? 'bg-purple-50' : enrichmentDone ? 'bg-green-50' : 'bg-amber-50'
              }`}
            >
              <div className="flex items-center gap-2">
                {isEnriching ? (
                  <Loader2 className="h-4 w-4 text-purple-600 animate-spin" />
                ) : enrichmentDone ? (
                  <CheckCircle2 className="h-4 w-4 text-green-600" />
                ) : (
                  <CheckCircle2 className="h-4 w-4 text-amber-500" />
                )}
                <span className={`text-sm font-medium ${
                  isEnriching ? 'text-purple-700' : enrichmentDone ? 'text-green-700' : 'text-amber-700'
                }`}>
                  {isEnriching 
                    ? `Gemini 3 Enrichment Pipeline — Step ${Math.min(activeStep + 1, ENRICHMENT_STEPS.length)}/${ENRICHMENT_STEPS.length}` 
                    : enrichmentDone
                    ? `Business profile enriched — ${dataSources.length} sources, ${socialFound} social profiles${deliveryFound ? `, ${deliveryFound} delivery platform${deliveryFound > 1 ? 's' : ''}` : ''}`
                    : 'Enrichment completed with limited data — try selecting a different business'
                  }
                </span>
              </div>
              {showPipeline ? <ChevronDown className="h-4 w-4 text-gray-500" /> : <ChevronRight className="h-4 w-4 text-gray-500" />}
            </button>

            {/* Expandable Pipeline Steps — light theme matching page */}
            {showPipeline && (
              <div className="px-4 py-3 bg-white border-t border-gray-100 text-sm space-y-1.5 max-h-80 overflow-y-auto">
                <div className="text-xs text-gray-400 mb-2 font-medium uppercase tracking-wide">Gemini 3 Agentic Enrichment Pipeline</div>
                {ENRICHMENT_STEPS.map((step, i) => {
                  const isCompleted = completedSteps.has(i);
                  const isActive = activeStep === i && isEnriching;

                  return (
                    <div key={step.id} className={`flex items-start gap-2.5 py-1.5 px-2 rounded-md transition-all duration-500 ${
                      isActive ? 'bg-purple-50 ring-1 ring-purple-200' : 
                      isCompleted ? 'bg-green-50/50' : 'bg-gray-50/50'
                    }`}>
                      <div className="mt-0.5 flex-shrink-0">
                        {isCompleted ? (
                          <CheckCircle2 className="h-4 w-4 text-green-500" />
                        ) : isActive ? (
                          <Loader2 className="h-4 w-4 text-purple-500 animate-spin" />
                        ) : (
                          <div className="h-4 w-4 rounded-full border-2 border-gray-300" />
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-1.5">
                          <span className={`font-medium ${
                            isCompleted ? 'text-green-700' : isActive ? 'text-purple-700' : 'text-gray-400'
                          }`}>
                            {step.label}
                          </span>
                          {step.gemini && (
                            <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-sans font-medium ${
                              isCompleted ? 'bg-blue-100 text-blue-700' : isActive ? 'bg-purple-100 text-purple-700' : 'bg-gray-100 text-gray-400'
                            }`}>
                              Gemini 3
                            </span>
                          )}
                        </div>
                        {(isActive || isCompleted) && (
                          <div className={`text-xs mt-0.5 ${
                            isCompleted ? 'text-green-600' : 'text-purple-500'
                          }`}>
                            {isCompleted ? '✓ ' : '→ '}{step.detail}
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
                {(enrichmentDone || enrichmentFailed) && (
                  <div className={`mt-2 pt-2 border-t text-xs ${
                    enrichmentDone ? 'border-green-100 text-green-600' : 'border-amber-100 text-amber-600'
                  }`}>
                    {enrichmentDone
                      ? `Pipeline complete · ${dataSources.length} data sources fused · Confidence: ${((formData.enrichedProfile?.metadata?.confidence_score || 0) * 100).toFixed(0)}%`
                      : 'Pipeline finished with partial results — Place Details API may have returned stale data'
                    }
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Business Name */}
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
          {showSocial ? '− Hide' : '+ Add'} social media & delivery (optional)
        </Button>
      </div>

      {/* Social Media + Delivery Inputs */}
      {showSocial && (
        <div className="space-y-4 p-4 bg-gray-50 rounded-lg animate-in fade-in slide-in-from-top-2">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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

          {/* Delivery Platforms (auto-discovered) */}
          {(formData.deliveryPlatforms || []).length > 0 && (
            <div className="pt-3 border-t border-gray-200">
              <Label className="text-sm flex items-center gap-2 mb-2">
                <Truck className="h-4 w-4 text-orange-600" />
                Delivery Platforms
                <span className="text-xs bg-green-100 text-green-700 px-1.5 py-0.5 rounded-full">auto-discovered</span>
              </Label>
              <div className="flex flex-wrap gap-2">
                {(formData.deliveryPlatforms || []).map((dp: any, i: number) => 
                  dp.url ? (
                    <a
                      key={i}
                      href={dp.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-white border border-gray-200 rounded-full text-sm hover:bg-orange-50 hover:border-orange-300 transition-colors cursor-pointer"
                    >
                      <span>{dp.icon}</span>
                      <span className="font-medium">{dp.name}</span>
                      <Globe className="h-3 w-3 text-orange-500" />
                    </a>
                  ) : (
                    <span
                      key={i}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-gray-50 border border-gray-200 rounded-full text-sm text-gray-500"
                    >
                      <span>{dp.icon}</span>
                      <span className="font-medium">{dp.name}</span>
                      <span className="text-[10px] text-gray-400">detected</span>
                    </span>
                  )
                )}
              </div>
            </div>
          )}
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
