'use client';

import { CreativeAutopilot } from '@/components/creative/CreativeAutopilot';
import { Campaign, CampaignResult } from '@/lib/api';
import { cn } from '@/lib/utils';
import {
    Brain,
    CheckCircle2,
    ClipboardCopy,
    Clock,
    Download,
    Loader2,
    Mail,
    Megaphone,
    RefreshCw,
    Sparkles,
    Target,
    TrendingUp,
    Users,
    Zap
} from 'lucide-react';
import { use, useCallback, useEffect, useState } from 'react';
import { useSessionData } from '../layout';

interface CampaignsPageProps {
  params: Promise<{ sessionId: string }>;
}

export default function CampaignsPage({ params }: CampaignsPageProps) {
  const { sessionId } = use(params);
  const { sessionData, isLoading: sessionLoading } = useSessionData();
  const [data, setData] = useState<CampaignResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState<'campaigns' | 'predictions' | 'creative'>('campaigns');
  const [regenerating, setRegenerating] = useState(false);

  const handleRegenerateCampaigns = useCallback(async () => {
    setRegenerating(true);
    try {
      const unwrapped = (sessionData as any)?.data || sessionData;
      const menuItems = unwrapped?.menu_items || [];
      const topItems = menuItems.slice(0, 3);
      if (topItems.length === 0) {
        setError('No menu items available to generate campaigns');
        return;
      }
      const formData = new FormData();
      formData.append('dish_name', topItems[0]?.name || 'Featured Dish');
      formData.append('campaign_brief', `Create marketing campaigns for ${unwrapped?.restaurant_info?.name || 'the restaurant'}`);
      formData.append('platform', 'instagram');
      const response = await fetch('/api/v1/campaigns/quick-campaign', {
        method: 'POST',
        body: formData,
      });
      if (response.ok) {
        const result = await response.json();
        if (result.campaigns) {
          setData(prev => ({
            session_id: sessionId,
            campaigns: [...(prev?.campaigns || []), ...result.campaigns],
          }));
        }
      }
    } catch (err) {
      console.warn('Campaign regeneration failed:', err);
    } finally {
      setRegenerating(false);
    }
  }, [sessionData, sessionId]);

  useEffect(() => {
    const fetchCampaigns = async () => {
      try {
        // Use data from SessionContext
        const unwrappedData = (sessionData as any)?.data || sessionData;
        const campaignsRaw = unwrappedData?.campaigns;
        if (campaignsRaw) {
          if (Array.isArray(campaignsRaw)) {
            setData({ session_id: sessionId, campaigns: campaignsRaw });
          } else if (Array.isArray((campaignsRaw as any)?.campaigns)) {
            setData(campaignsRaw as CampaignResult);
          }
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load campaigns');
      } finally {
        setLoading(false);
      }
    };

    if (!sessionLoading && sessionData) {
      fetchCampaigns();
    }
  }, [sessionId, sessionData, sessionLoading]);

  const copyToClipboard = async (text: string, index: number) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 2000);
    } catch {
      console.error('Failed to copy');
    }
  };

  if (loading) {
    return <LoadingSkeleton />;
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-red-500 text-lg mb-2">⚠️ Error</div>
        <p className="text-gray-600">{error}</p>
      </div>
    );
  }

  // Extract additional data from sessionData
  const unwrappedData = (sessionData as any)?.data || sessionData;
  const predictions = unwrappedData?.predictions;
  const menuItems = unwrappedData?.menu_items || unwrappedData?.menu?.items || [];
  const bcgData = unwrappedData?.bcg_analysis || unwrappedData?.bcg;
  const restaurantName = unwrappedData?.restaurant_name || unwrappedData?.restaurant_info?.name || unwrappedData?.business_profile?.name || unwrappedData?.businessName || 'My Restaurant';

  return (
    <div className="space-y-6">
      {/* Page Header with Accent Image */}
      <div className="relative rounded-xl overflow-hidden bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-200/60">
        <div className="flex items-center gap-6 p-5">
          <div className="hidden sm:block flex-shrink-0 w-28 h-20 rounded-lg overflow-hidden shadow-md">
            <img src="/images/campaign-studio.png" alt="" className="w-full h-full object-cover" loading="lazy" />
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-3 flex-wrap">
              <h1 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-purple-600" />
                Creative Studio & Campaigns
              </h1>
              <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-gradient-to-r from-rose-50 to-purple-50 border border-purple-200/60 rounded-full text-[10px] font-semibold text-purple-700">
                <Zap className="h-2.5 w-2.5" /> Imagen 3 · Creative Autopilot
              </span>
            </div>
            <p className="text-sm text-gray-500 mt-0.5">AI-generated marketing campaigns, predictions, and creative assets</p>
          </div>
        </div>
      </div>

      {/* Sub-tabs */}
      <div className="flex border-b mb-6">
        <button
          onClick={() => setActiveTab('campaigns')}
          className={`px-4 py-2 font-medium transition-colors border-b-2 ${
            activeTab === 'campaigns'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-600 hover:text-gray-900'
          }`}
        >
          📢 Generated Campaigns
        </button>
        <button
          onClick={() => setActiveTab('predictions')}
          className={`px-4 py-2 font-medium transition-colors border-b-2 ${
            activeTab === 'predictions'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-600 hover:text-gray-900'
          }`}
        >
          📈 Sales Predictions
        </button>
        <button
          onClick={() => setActiveTab('creative')}
          className={`px-4 py-2 font-medium transition-colors border-b-2 ${
            activeTab === 'creative'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-600 hover:text-gray-900'
          }`}
        >
          🚀 Creative Autopilot
        </button>
      </div>

      {/* Content based on active tab */}
      {activeTab === 'campaigns' && (
        <div>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold">AI-Generated Marketing Campaigns</h2>
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-500">
                {data?.campaigns?.length || 0} campaigns
              </span>
              <button
                onClick={handleRegenerateCampaigns}
                disabled={regenerating}
                className="inline-flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-purple-700 bg-purple-50 border border-purple-200 rounded-lg hover:bg-purple-100 transition-colors disabled:opacity-50"
              >
                {regenerating ? (
                  <><Loader2 className="h-3.5 w-3.5 animate-spin" /> Generating...</>
                ) : (
                  <><RefreshCw className="h-3.5 w-3.5" /> New Campaign</>
                )}
              </button>
            </div>
          </div>

          {!data || !data.campaigns?.length ? (
            <div className="text-center py-12 text-gray-500">
              <p className="text-4xl mb-4">📢</p>
              <p>No marketing campaigns generated yet.</p>
              <p className="text-sm mt-2">Complete BCG analysis to generate campaigns.</p>
            </div>
          ) : (
            <>
              <div className="space-y-6">
                {data.campaigns.map((campaign, index) => (
                  <CampaignCard
                    key={index}
                    campaign={campaign}
                    index={index}
                    onCopy={(text) => copyToClipboard(text, index)}
                    copied={copiedIndex === index}
                  />
                ))}
              </div>

              {/* AI Thought Process */}
              {data.thought_process && (
                <div className="mt-8 p-4 bg-purple-50 border border-purple-200 rounded-lg">
                  <h3 className="text-lg font-semibold mb-2 text-purple-800">🧠 AI Thought Process</h3>
                  <p className="text-sm text-gray-700 whitespace-pre-wrap">{data.thought_process}</p>
                </div>
              )}
            </>
          )}
        </div>
      )}

      {/* Tab: Predictions */}
      {activeTab === 'predictions' && (
        <div>
          {predictions ? (
            <PredictionsPanel data={predictions} sessionId={sessionId} />
          ) : (
            <div className="text-center py-12 text-gray-500">
              <p className="text-4xl mb-4">📈</p>
              <p>No sales predictions available yet.</p>
              <p className="text-sm mt-2">Upload sales data to generate forecasts.</p>
            </div>
          )}
        </div>
      )}

      {/* Tab: Creative Autopilot */}
      {activeTab === 'creative' && (
        <div>
          <CreativeAutopilotPlaceholder 
            sessionId={sessionId}
            restaurantName={restaurantName}
            menuItems={menuItems}
            bcgData={bcgData}
          />
        </div>
      )}
    </div>
  );
}

function CreativeAutopilotPlaceholder({
  sessionId,
  restaurantName,
  menuItems,
}: {
  sessionId: string;
  restaurantName: string;
  menuItems: any[];
  bcgData: any;
}) {
  const normalizedMenuItems = Array.isArray(menuItems)
    ? menuItems
        .map((item, idx) => {
          if (!item || typeof item !== 'object') return null;
          const existingId = (item as any).id;
          const id = typeof existingId === 'number' && Number.isFinite(existingId) ? existingId : idx + 1;
          return { ...item, id };
        })
        .filter(Boolean)
    : [];

  return (
    <CreativeAutopilot
      sessionId={sessionId}
      initialRestaurantName={restaurantName}
      menuItems={normalizedMenuItems as any[]}
    />
  );
}

interface CampaignCardProps {
  campaign: Campaign;
  index: number;
  onCopy: (text: string) => void;
  copied: boolean;
}

function CampaignCard({ campaign, index, onCopy, copied }: CampaignCardProps) {
  const categoryConfig: Record<string, { bg: string; text: string; border: string; icon: React.ReactNode }> = {
    STAR: { bg: 'bg-yellow-50', text: 'text-yellow-700', border: 'border-yellow-200', icon: <Sparkles className="h-3.5 w-3.5" /> },
    CASH_COW: { bg: 'bg-green-50', text: 'text-green-700', border: 'border-green-200', icon: <TrendingUp className="h-3.5 w-3.5" /> },
    QUESTION_MARK: { bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-200', icon: <Target className="h-3.5 w-3.5" /> },
    DOG: { bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-200', icon: <Zap className="h-3.5 w-3.5" /> },
  };
  const catCfg = categoryConfig[campaign.target_category] || { bg: 'bg-gray-50', text: 'text-gray-700', border: 'border-gray-200', icon: <Megaphone className="h-3.5 w-3.5" /> };

  const handleDownload = () => {
    const content = `# ${campaign.title}\n\n## Objective\n${campaign.objective}\n\n## Social Media Copy\n${campaign.copy.social_media}\n\n## Email\nSubject: ${campaign.copy.email_subject}\n\n${campaign.copy.email_body}\n\n## Target Audience\n${campaign.target_audience}\n\n## Timing\n${campaign.timing}\n\n## Expected Impact\n${campaign.expected_impact}\n\n## AI Rationale\n${campaign.rationale || 'N/A'}`;
    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `campaign-${index + 1}-${campaign.title.slice(0, 30).replace(/\s+/g, '-').toLowerCase()}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="rp-card-interactive overflow-hidden p-0">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-5">
        <div className="flex items-start justify-between">
          <div>
            <span className="text-xs text-blue-200 font-medium">Campaign #{index + 1}</span>
            <h3 className="text-lg font-bold mt-0.5">{campaign.title}</h3>
          </div>
          <span className={cn('inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border', catCfg.bg, catCfg.text, catCfg.border)}>
            {catCfg.icon}
            {campaign.target_category?.replace('_', ' ')}
          </span>
        </div>
      </div>

      {/* Content */}
      <div className="p-5 space-y-5">
        {/* Objective */}
        <div>
          <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
            <Target className="h-3.5 w-3.5" /> Objective
          </h4>
          <p className="text-sm text-gray-800">{campaign.objective}</p>
        </div>

        {/* Social Media Copy */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider flex items-center gap-1.5">
              <Megaphone className="h-3.5 w-3.5" /> Social Media Copy
            </h4>
            <button
              onClick={() => onCopy(campaign.copy.social_media)}
              className="inline-flex items-center gap-1 text-xs px-2.5 py-1 bg-gray-100 hover:bg-purple-100 hover:text-purple-700 rounded-full transition-colors"
            >
              {copied ? <CheckCircle2 className="h-3 w-3 text-green-500" /> : <ClipboardCopy className="h-3 w-3" />}
              {copied ? 'Copied!' : 'Copy'}
            </button>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg border border-gray-200 text-sm text-gray-800 leading-relaxed">
            {campaign.copy.social_media}
          </div>
        </div>

        {/* Email */}
        <div>
          <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2 flex items-center gap-1.5">
            <Mail className="h-3.5 w-3.5" /> Email Campaign
          </h4>
          <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
            <p className="font-medium text-gray-900 text-sm mb-2">Subject: {campaign.copy.email_subject}</p>
            <p className="text-gray-700 text-sm leading-relaxed">{campaign.copy.email_body}</p>
          </div>
        </div>

        {/* Details Grid */}
        <div className="grid grid-cols-2 gap-4">
          <div className="p-3 bg-gray-50 rounded-lg">
            <h4 className="text-xs font-semibold text-gray-500 mb-1 flex items-center gap-1">
              <Users className="h-3 w-3" /> Target Audience
            </h4>
            <p className="text-sm text-gray-800">{campaign.target_audience}</p>
          </div>
          <div className="p-3 bg-gray-50 rounded-lg">
            <h4 className="text-xs font-semibold text-gray-500 mb-1 flex items-center gap-1">
              <Clock className="h-3 w-3" /> Timing
            </h4>
            <p className="text-sm text-gray-800">{campaign.timing}</p>
          </div>
        </div>

        {/* Expected Impact */}
        <div className="rp-card-success p-4">
          <h4 className="text-xs font-semibold text-green-700 mb-1 flex items-center gap-1">
            <TrendingUp className="h-3.5 w-3.5" /> Expected Impact
          </h4>
          <p className="text-sm text-green-800">{campaign.expected_impact}</p>
        </div>

        {/* Rationale */}
        {campaign.rationale && (
          <div className="border-t pt-4">
            <h4 className="text-xs font-semibold text-purple-600 mb-1.5 flex items-center gap-1">
              <Brain className="h-3.5 w-3.5" /> AI Rationale
            </h4>
            <p className="text-sm text-gray-600 leading-relaxed">{campaign.rationale}</p>
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center gap-2 pt-2 border-t">
          <button
            onClick={() => onCopy(`${campaign.title}\n\n${campaign.copy.social_media}\n\nEmail Subject: ${campaign.copy.email_subject}\n${campaign.copy.email_body}`)}
            className="inline-flex items-center gap-1.5 text-xs px-3 py-1.5 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors text-gray-700"
          >
            <ClipboardCopy className="h-3 w-3" /> Copy All
          </button>
          <button
            onClick={handleDownload}
            className="inline-flex items-center gap-1.5 text-xs px-3 py-1.5 bg-purple-50 hover:bg-purple-100 rounded-lg transition-colors text-purple-700"
          >
            <Download className="h-3 w-3" /> Download
          </button>
          <span className="ml-auto text-[10px] text-gray-400 flex items-center gap-1">
            <Sparkles className="h-3 w-3 text-purple-400" /> Generated by Gemini 3
          </span>
        </div>
      </div>
    </div>
  );
}

function LoadingSkeleton() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="rp-skeleton h-7 w-64 rounded" />
        <div className="rp-skeleton h-5 w-24 rounded-full" />
      </div>
      {[1, 2, 3].map((i) => (
        <div key={i} className="rounded-xl border border-gray-200 overflow-hidden">
          <div className="h-20 bg-gradient-to-r from-gray-200 to-gray-300 animate-pulse" />
          <div className="p-5 space-y-4">
            <div className="rp-skeleton h-4 w-3/4 rounded" />
            <div className="rp-skeleton h-24 w-full rounded-lg" />
            <div className="grid grid-cols-2 gap-3">
              <div className="rp-skeleton h-16 rounded-lg" />
              <div className="rp-skeleton h-16 rounded-lg" />
            </div>
            <div className="rp-skeleton h-14 w-full rounded-lg" />
          </div>
        </div>
      ))}
    </div>
  );
}

function PredictionsPanel({ data, sessionId }: { data: any; sessionId: string }) {
  const [neuralPredictions, setNeuralPredictions] = useState<any>(null);
  const [loadingNeural, setLoadingNeural] = useState(false);

  const predictionCount = Array.isArray(data?.predictions)
    ? data.predictions.length
    : Array.isArray(data?.item_predictions)
      ? data.item_predictions.length
      : 0;

  const predictions = data?.predictions || data?.item_predictions || [];

  const handleNeuralPredict = async () => {
    setLoadingNeural(true);
    try {
      const res = await fetch(`/api/v1/predict/neural?session_id=${sessionId}&horizon_days=14&use_ensemble=true`, {
        method: 'POST',
      });
      if (res.ok) {
        const result = await res.json();
        setNeuralPredictions(result);
      }
    } catch (err) {
      console.warn('Neural prediction failed:', err);
    } finally {
      setLoadingNeural(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold">Sales Predictions</h2>
        <button
          onClick={handleNeuralPredict}
          disabled={loadingNeural}
          className="inline-flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-blue-700 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 transition-colors disabled:opacity-50"
        >
          {loadingNeural ? (
            <><Loader2 className="h-3.5 w-3.5 animate-spin" /> Running Neural...</>
          ) : (
            <><Brain className="h-3.5 w-3.5" /> Neural Forecast</>
          )}
        </button>
      </div>

      {/* Standard Predictions */}
      {predictions.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {predictions.slice(0, 9).map((pred: any, idx: number) => (
            <div key={idx} className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-sm transition-shadow">
              <h4 className="font-semibold text-gray-900 mb-1">{pred.item_name || pred.name || `Item ${idx + 1}`}</h4>
              {pred.predicted_demand != null && (
                <p className="text-sm text-gray-600">Demand: <span className="font-medium text-blue-600">{Math.round(pred.predicted_demand)} units/day</span></p>
              )}
              {pred.predicted_revenue != null && (
                <p className="text-sm text-gray-600">Revenue: <span className="font-medium text-green-600">${pred.predicted_revenue?.toFixed(0)}/day</span></p>
              )}
              {pred.confidence != null && (
                <div className="mt-2">
                  <div className="flex justify-between text-xs text-gray-500 mb-1">
                    <span>Confidence</span>
                    <span>{(pred.confidence * 100).toFixed(0)}%</span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-1.5">
                    <div className="bg-blue-500 rounded-full h-1.5" style={{ width: `${pred.confidence * 100}%` }} />
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-blue-800">📊 {predictionCount > 0 ? `${predictionCount} predictions available` : 'Upload sales data to generate forecasts.'}</p>
        </div>
      )}

      {/* Neural Predictions Results */}
      {neuralPredictions && (
        <div className="bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-200 rounded-lg p-5">
          <h3 className="text-lg font-semibold text-indigo-900 mb-3 flex items-center gap-2">
            <Brain className="h-5 w-5" />
            Neural Network Forecast (14-day horizon)
          </h3>
          {neuralPredictions.predictions ? (
            <div className="grid gap-3 md:grid-cols-2">
              {Object.entries(neuralPredictions.predictions).slice(0, 6).map(([itemName, pred]: [string, any]) => (
                <div key={itemName} className="bg-white/80 rounded-lg p-3 border border-indigo-100">
                  <p className="font-medium text-gray-900 text-sm">{itemName}</p>
                  {pred?.baseline?.forecast && (
                    <p className="text-xs text-indigo-600 mt-1">
                      Forecast: {Array.isArray(pred.baseline.forecast)
                        ? `${pred.baseline.forecast.slice(-1)[0]?.toFixed(0)} units (day 14)`
                        : JSON.stringify(pred.baseline.forecast).slice(0, 60)}
                    </p>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-indigo-700">{JSON.stringify(neuralPredictions).slice(0, 200)}</p>
          )}
        </div>
      )}
    </div>
  );
}
