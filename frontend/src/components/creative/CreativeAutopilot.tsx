'use client';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { api, CreativeAutopilotResult } from '@/lib/api';
import { Brain, Download, Globe, Image as ImageIcon, Loader2, Sparkles, TrendingUp } from 'lucide-react';
import { useState } from 'react';
import { toast } from 'sonner';

interface CreativeAutopilotProps {
  sessionId: string;
  initialRestaurantName?: string;
  menuItems?: any[];
}

export function CreativeAutopilot({ sessionId, initialRestaurantName = '', menuItems = [] }: CreativeAutopilotProps) {
  const [restaurantName, setRestaurantName] = useState(initialRestaurantName);
  const [dishId, setDishId] = useState('');
  const [targetLanguages, setTargetLanguages] = useState('en, es');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<CreativeAutopilotResult | null>(null);
  const [_copiedId, setCopiedId] = useState<string | null>(null);
  const [activeAssetTab, setActiveAssetTab] = useState<string>('all');
  const [showVariants, setShowVariants] = useState(false);

  const handleGenerate = async () => {
    if (!restaurantName || !dishId) {
      toast.error('Please fill in all required fields');
      return;
    }

    setIsLoading(true);
    try {
      const languages = targetLanguages.split(',').map(l => l.trim());
      const data = await api.generateCreativeAssets(
        restaurantName,
        parseInt(dishId),
        sessionId,
        languages
      );
      setResult(data);
      toast.success('Campaign assets generated successfully!');
    } catch (error) {
      console.error('Generation failed:', error);
      toast.error('Failed to generate creative assets. Please check your inputs and try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const _copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    toast.success('Text copied to clipboard!');
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="space-y-8">
      <Card className="border-purple-100 shadow-sm">
        <CardHeader className="bg-purple-50/50">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-purple-600" />
            <CardTitle>Creative Autopilot Setup</CardTitle>
          </div>
          <CardDescription>
            Generate comprehensive multi-channel campaigns automatically using Gemini 3.
          </CardDescription>
        </CardHeader>
        <CardContent className="pt-6 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="restaurant-name">Restaurant Name</Label>
              <Input
                id="restaurant-name"
                placeholder="e.g. The Authentic Flavor"
                value={restaurantName}
                onChange={(e) => setRestaurantName(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="dish-id">Select Dish</Label>
              {menuItems.length > 0 ? (
                <Select value={dishId} onValueChange={setDishId}>
                  <SelectTrigger id="dish-id">
                    <SelectValue placeholder="Select a dish..." />
                  </SelectTrigger>
                  <SelectContent>
                    {menuItems.map((item) => (
                      <SelectItem key={item.id} value={item.id.toString()}>
                        {item.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              ) : (
                <Input
                  id="dish-id"
                  type="number"
                  placeholder="e.g. 1"
                  value={dishId}
                  onChange={(e) => setDishId(e.target.value)}
                />
              )}
            </div>
          </div>
          
          <div className="space-y-2">
            <Label>Target Languages</Label>
            <div className="flex flex-wrap gap-2">
              {[{code: 'es', label: 'Español', flag: '🇪🇸'}, {code: 'en', label: 'English', flag: '🇺🇸'}, {code: 'fr', label: 'Français', flag: '🇫🇷'}, {code: 'pt', label: 'Português', flag: '🇧🇷'}, {code: 'it', label: 'Italiano', flag: '🇮🇹'}, {code: 'de', label: 'Deutsch', flag: '🇩🇪'}].map(lang => {
                const isActive = targetLanguages.split(',').map(l => l.trim()).includes(lang.code);
                return (
                  <button
                    key={lang.code}
                    type="button"
                    onClick={() => {
                      const langs = targetLanguages.split(',').map(l => l.trim()).filter(Boolean);
                      if (isActive) {
                        setTargetLanguages(langs.filter(l => l !== lang.code).join(', '));
                      } else {
                        setTargetLanguages([...langs, lang.code].join(', '));
                      }
                    }}
                    className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${
                      isActive
                        ? 'bg-purple-100 border-purple-300 text-purple-800'
                        : 'bg-gray-50 border-gray-200 text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    <span>{lang.flag}</span> {lang.label}
                  </button>
                );
              })}
            </div>
          </div>

          <Button 
            onClick={handleGenerate} 
            disabled={isLoading}
            className="w-full bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Generating Assets...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 mr-2" />
                Generate Campaign
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {result && (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
          {/* Strategy & Concept Summary */}
          {result.campaign.strategy && (
            <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-5 border border-purple-200">
              <h3 className="font-bold text-purple-900 mb-2 flex items-center gap-2">
                <Brain className="h-4 w-4" /> Campaign Strategy
              </h3>
              <p className="text-sm text-purple-800 font-medium">{(result.campaign.strategy as any)?.key_message || (result.campaign.strategy as any)?.approach || 'AI-optimized strategy'}</p>
              {(result.campaign.creative_concept as any)?.theme && (
                <p className="text-xs text-purple-600 mt-1">Theme: {(result.campaign.creative_concept as any)?.theme}</p>
              )}
            </div>
          )}

          {/* Impact Metrics */}
          {result.campaign.estimated_impact != null && (
            <div className="grid grid-cols-3 gap-3">
              <div className="bg-white border rounded-lg p-3 text-center">
                <p className="text-xs text-gray-500">Engagement Score</p>
                <p className="text-2xl font-bold text-purple-700">
                  {typeof result.campaign.estimated_impact === 'object'
                    ? (result.campaign.estimated_impact as any)?.engagement_score || '8.0'
                    : result.campaign.estimated_impact}
                  <span className="text-sm font-normal text-gray-400">/10</span>
                </p>
              </div>
              <div className="bg-white border rounded-lg p-3 text-center">
                <p className="text-xs text-gray-500">Est. Reach</p>
                <p className="text-sm font-semibold text-gray-700 mt-1">
                  {(result.campaign.estimated_impact as any)?.estimated_reach || '1K-5K'}
                </p>
              </div>
              <div className="bg-white border rounded-lg p-3 text-center">
                <p className="text-xs text-gray-500">Est. CTR</p>
                <p className="text-sm font-semibold text-gray-700 mt-1">
                  {(result.campaign.estimated_impact as any)?.estimated_ctr || '3.5-5.5%'}
                </p>
              </div>
            </div>
          )}

          {/* Asset Type Tabs */}
          <div className="flex items-center justify-between">
            <div className="flex gap-1 bg-gray-100 rounded-lg p-1">
              {['all', 'instagram', 'web', 'print'].map(tab => (
                <button
                  key={tab}
                  onClick={() => setActiveAssetTab(tab)}
                  className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
                    activeAssetTab === tab
                      ? 'bg-white text-gray-900 shadow-sm'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  {tab === 'all' ? 'All Assets' : tab === 'instagram' ? '📱 Instagram' : tab === 'web' ? '🌐 Web' : '🖨️ Print'}
                </button>
              ))}
            </div>
            {result.campaign.ab_variants && result.campaign.ab_variants.length > 0 && (
              <button
                onClick={() => setShowVariants(!showVariants)}
                className={`inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border transition-colors ${
                  showVariants ? 'bg-amber-50 border-amber-200 text-amber-700' : 'bg-gray-50 border-gray-200 text-gray-600'
                }`}
              >
                <TrendingUp className="h-3 w-3" />
                A/B Variants ({result.campaign.ab_variants.length})
              </button>
            )}
          </div>

          {/* Visual Assets Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {result.campaign.visual_assets
              .filter(asset => {
                if (activeAssetTab === 'all') return true;
                if (activeAssetTab === 'instagram') return asset.type?.includes('instagram');
                if (activeAssetTab === 'web') return asset.type?.includes('web') || asset.type?.includes('banner');
                if (activeAssetTab === 'print') return asset.type?.includes('print') || asset.type?.includes('flyer');
                return true;
              })
              .map((asset, idx) => (
              <Card key={idx} className="overflow-hidden group">
                <div className="relative aspect-square bg-gray-100 flex items-center justify-center">
                  {asset.image_data ? (
                    <img 
                      src={`data:image/jpeg;base64,${asset.image_data}`} 
                      alt={asset.concept || 'Generated Asset'} 
                      className="object-cover w-full h-full"
                    />
                  ) : (
                    <div className="text-gray-400 flex flex-col items-center">
                      <ImageIcon className="w-12 h-12 mb-2" />
                      <span>Image generation pending</span>
                    </div>
                  )}
                  <div className="absolute top-2 right-2 bg-black/70 text-white text-xs px-2 py-1 rounded-full uppercase font-bold">
                    {asset.type?.replace(/_/g, ' ')}
                  </div>
                  <div className="absolute bottom-2 left-2 bg-purple-600/90 text-white text-[10px] px-2 py-0.5 rounded-full">
                    Gemini 3 Pro Image
                  </div>
                  {/* Download overlay */}
                  {asset.image_data && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        const link = document.createElement('a');
                        link.href = `data:image/jpeg;base64,${asset.image_data}`;
                        link.download = `${asset.type || 'asset'}_${idx}.jpg`;
                        link.click();
                      }}
                      className="absolute top-2 left-2 bg-white/90 hover:bg-white p-1.5 rounded-lg shadow-sm opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <Download className="h-4 w-4 text-gray-700" />
                    </button>
                  )}
                </div>
                <CardContent className="p-4 space-y-3">
                  <div className="flex justify-between items-start">
                    <div>
                        <h4 className="font-semibold text-gray-900">{asset.concept}</h4>
                        <p className="text-xs text-gray-500 capitalize">{asset.format}</p>
                    </div>
                    <Badge variant="secondary" className="text-xs">{asset.language?.toUpperCase() || 'ES'}</Badge>
                  </div>
                  {asset.reasoning && (
                    <p className="text-sm text-gray-600 bg-gray-50 p-2 rounded border border-gray-100 italic">
                      "{asset.reasoning}"
                    </p>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>

          {/* A/B Variants */}
          {showVariants && result.campaign.ab_variants && result.campaign.ab_variants.length > 0 && (
            <div className="space-y-4 pt-4 border-t border-amber-200">
              <h3 className="text-lg font-bold text-amber-900 flex items-center gap-2">
                <TrendingUp className="h-5 w-5" /> A/B Testing Variants
              </h3>
              <p className="text-sm text-amber-700">These variants test different visual approaches for scientific optimization.</p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {result.campaign.ab_variants.map((variant, idx) => (
                  <div key={idx} className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-bold text-amber-800">Variant {String.fromCharCode(65 + idx)}</span>
                      <span className="text-xs text-amber-600 capitalize">{variant.variant_type?.replace(/_/g, ' ') || 'Alternative'}</span>
                    </div>
                    {variant.image_data ? (
                      <img src={`data:image/jpeg;base64,${variant.image_data}`} alt={`Variant ${idx}`} className="w-full rounded-md" />
                    ) : (
                      <div className="h-32 bg-amber-100 rounded-md flex items-center justify-center text-amber-500 text-sm">
                        Variant preview
                      </div>
                    )}
                    <p className="text-xs text-amber-700 mt-2">{variant.reasoning || 'Testing visual variation for engagement optimization'}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Localized Versions */}
          {result.campaign.localized_versions && Object.keys(result.campaign.localized_versions).length > 0 && (
            <div className="space-y-4 pt-6 border-t border-gray-200">
                <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                  <Globe className="h-5 w-5 text-blue-600" /> Localized Versions
                </h3>
                <p className="text-sm text-gray-500">Text translated INSIDE the image while preserving design — a unique Gemini 3 capability.</p>
                {Object.entries(result.campaign.localized_versions).map(([lang, assets]) => (
                    <div key={lang} className="space-y-4">
                        <h4 className="text-base font-semibold text-gray-700 capitalize flex items-center gap-2">
                            <span className="text-xl">{lang === 'en' ? '🇺🇸' : lang === 'fr' ? '🇫🇷' : lang === 'pt' ? '🇧🇷' : lang === 'it' ? '🇮🇹' : lang === 'de' ? '🇩🇪' : '🌐'}</span>
                            {lang === 'en' ? 'English' : lang === 'fr' ? 'French' : lang === 'pt' ? 'Portuguese' : lang === 'it' ? 'Italian' : lang === 'de' ? 'German' : lang}
                        </h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {assets.map((asset, idx) => (
                                <Card key={`${lang}-${idx}`} className="overflow-hidden border-blue-100">
                                    <div className="relative aspect-square bg-gray-100">
                                        {asset.image_data ? (
                                            <img src={`data:image/jpeg;base64,${asset.image_data}`} alt={asset.concept} className="object-cover w-full h-full" />
                                        ) : (
                                            <div className="h-full flex items-center justify-center text-gray-400">
                                              <Globe className="w-8 h-8" />
                                            </div>
                                        )}
                                    </div>
                                    <CardContent className="p-3">
                                        <p className="font-medium text-gray-900 text-sm">{asset.concept}</p>
                                    </CardContent>
                                </Card>
                            ))}
                        </div>
                    </div>
                ))}
            </div>
          )}

          {/* Thought Signature */}
          {(result.campaign as any)?.thought_signature && (
            <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
              <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1">
                <Brain className="h-3 w-3" /> Thought Signature
              </h4>
              <p className="text-sm text-slate-700">{(result.campaign as any).thought_signature?.reasoning || (result.campaign as any).thought_signature?.summary || 'AI reasoning trace available'}</p>
              {(result.campaign as any).thought_signature?.confidence != null && (
                <p className="text-xs text-slate-500 mt-1">Confidence: {((result.campaign as any).thought_signature.confidence * 100).toFixed(0)}%</p>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function Badge({ children, variant = "default", className = "" }: { children: React.ReactNode, variant?: "default" | "secondary" | "outline", className?: string }) {
    const variants = {
        default: "bg-purple-100 text-purple-800 border-transparent",
        secondary: "bg-gray-100 text-gray-800 border-transparent",
        outline: "text-gray-800 border-gray-200"
    };
    return (
        <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 ${variants[variant]} ${className}`}>
            {children}
        </span>
    );
}
