'use client';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { api, CreativeAutopilotResult } from '@/lib/api';
import { Image as ImageIcon, Loader2, Sparkles } from 'lucide-react';
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
  const [copiedId, setCopiedId] = useState<string | null>(null);

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

  const copyToClipboard = (text: string, id: string) => {
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
            <Label htmlFor="languages">Target Languages (comma separated)</Label>
            <Input
              id="languages"
              placeholder="e.g. en, es, fr"
              value={targetLanguages}
              onChange={(e) => setTargetLanguages(e.target.value)}
            />
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
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-gray-900">Generated Assets</h2>
            <div className="flex gap-2">
                <Button variant="outline" size="sm" onClick={() => window.open(result.demo_url, '_blank')}>
                    View Full Demo
                </Button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {result.campaign.visual_assets.map((asset, idx) => (
              <Card key={idx} className="overflow-hidden">
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
                      <span>Image generation failed</span>
                    </div>
                  )}
                  <div className="absolute top-2 right-2 bg-black/70 text-white text-xs px-2 py-1 rounded-full uppercase font-bold">
                    {asset.type.replace('_', ' ')}
                  </div>
                </div>
                <CardContent className="p-4 space-y-3">
                  <div className="flex justify-between items-start">
                    <div>
                        <h4 className="font-semibold text-gray-900">{asset.concept}</h4>
                        <p className="text-xs text-gray-500 capitalize">{asset.format}</p>
                    </div>
                    <Badge variant="secondary" className="text-xs">{asset.language?.toUpperCase()}</Badge>
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

          {result.campaign.localized_versions && Object.keys(result.campaign.localized_versions).length > 0 && (
            <div className="space-y-4 pt-6 border-t border-gray-200">
                <h3 className="text-xl font-bold text-gray-900">Localized Versions</h3>
                {Object.entries(result.campaign.localized_versions).map(([lang, assets]) => (
                    <div key={lang} className="space-y-4">
                        <h4 className="text-lg font-semibold text-gray-700 capitalize flex items-center gap-2">
                            <span className="text-2xl">{lang === 'en' ? '🇺🇸' : lang === 'fr' ? '🇫🇷' : '🌐'}</span>
                            {lang === 'en' ? 'English' : lang === 'fr' ? 'French' : lang}
                        </h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {assets.map((asset, idx) => (
                                <Card key={`${lang}-${idx}`} className="overflow-hidden border-blue-100">
                                    <div className="relative aspect-square bg-gray-100">
                                        {asset.image_data && (
                                            <img 
                                                src={`data:image/jpeg;base64,${asset.image_data}`} 
                                                alt={asset.concept} 
                                                className="object-cover w-full h-full"
                                            />
                                        )}
                                    </div>
                                    <CardContent className="p-4">
                                        <p className="font-medium text-gray-900">{asset.concept}</p>
                                    </CardContent>
                                </Card>
                            ))}
                        </div>
                    </div>
                ))}
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
