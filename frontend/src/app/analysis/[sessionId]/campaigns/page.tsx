'use client';

import { CreativeAutopilot } from '@/components/creative/CreativeAutopilot';
import { Campaign, CampaignResult } from '@/lib/api';
import { use, useEffect, useState } from 'react';
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
    <div>
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
            <span className="text-sm text-gray-500">
              {data?.campaigns?.length || 0} campaigns
            </span>
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
  const categoryColors: Record<string, string> = {
    STAR: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    CASH_COW: 'bg-green-100 text-green-800 border-green-300',
    QUESTION_MARK: 'bg-blue-100 text-blue-800 border-blue-300',
    DOG: 'bg-red-100 text-red-800 border-red-300',
  };

  return (
    <div className="border rounded-lg overflow-hidden shadow-sm hover:shadow-md transition">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4">
        <div className="flex items-start justify-between">
          <div>
            <span className="text-sm opacity-75">Campaign #{index + 1}</span>
            <h3 className="text-xl font-bold">{campaign.title}</h3>
          </div>
          <span className={`px-3 py-1 rounded-full text-sm border ${
            categoryColors[campaign.target_category] || 'bg-gray-100 text-gray-800'
          }`}>
            {campaign.target_category?.replace('_', ' ')}
          </span>
        </div>
      </div>

      {/* Content */}
      <div className="p-6 space-y-6">
        {/* Objective */}
        <div>
          <h4 className="text-sm font-semibold text-gray-600 mb-1">🎯 Objective</h4>
          <p className="text-gray-800">{campaign.objective}</p>
        </div>

        {/* Social Media Copy */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-sm font-semibold text-gray-600">📱 Social Media Copy</h4>
            <button
              onClick={() => onCopy(campaign.copy.social_media)}
              className="text-xs px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded transition flex items-center gap-1"
            >
              {copied ? '✓ Copied!' : '📋 Copy'}
            </button>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg border border-gray-200 text-gray-800">
            {campaign.copy.social_media}
          </div>
        </div>

        {/* Email */}
        <div>
          <h4 className="text-sm font-semibold text-gray-600 mb-2">✉️ Email Campaign</h4>
          <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
            <p className="font-medium text-gray-900 mb-2">Subject: {campaign.copy.email_subject}</p>
            <p className="text-gray-700 text-sm">{campaign.copy.email_body}</p>
          </div>
        </div>

        {/* Details Grid */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <h4 className="text-sm font-semibold text-gray-600 mb-1">👥 Target Audience</h4>
            <p className="text-sm text-gray-800">{campaign.target_audience}</p>
          </div>
          <div>
            <h4 className="text-sm font-semibold text-gray-600 mb-1">⏰ Recommended Timing</h4>
            <p className="text-sm text-gray-800">{campaign.timing}</p>
          </div>
        </div>

        {/* Expected Impact */}
        <div className="bg-green-50 p-4 rounded-lg border border-green-200">
          <h4 className="text-sm font-semibold text-green-800 mb-1">📈 Expected Impact</h4>
          <p className="text-green-700">{campaign.expected_impact}</p>
        </div>

        {/* Rationale */}
        {campaign.rationale && (
          <div className="text-sm text-gray-600 border-t pt-4">
            <h4 className="font-semibold mb-1">💭 AI Rationale</h4>
            <p>{campaign.rationale}</p>
          </div>
        )}
      </div>
    </div>
  );
}

function LoadingSkeleton() {
  return (
    <div className="animate-pulse">
      <div className="flex items-center justify-between mb-6">
        <div className="h-6 bg-gray-200 rounded w-64"></div>
        <div className="h-4 bg-gray-200 rounded w-24"></div>
      </div>
      <div className="space-y-6">
        {[1, 2, 3].map((i) => (
          <div key={i} className="border rounded-lg overflow-hidden">
            <div className="h-20 bg-gray-200"></div>
            <div className="p-6 space-y-4">
              <div className="h-4 bg-gray-100 rounded w-3/4"></div>
              <div className="h-24 bg-gray-50 rounded"></div>
              <div className="h-16 bg-gray-50 rounded"></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Temporary component for Predictions (content from predictions/page.tsx will be moved here)
function PredictionsPanel({ data, sessionId }: { data: any; sessionId: string }) {
  const predictionCount = Array.isArray(data?.predictions)
    ? data.predictions.length
    : Array.isArray(data?.item_predictions)
      ? data.item_predictions.length
      : 0;

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">Sales Predictions</h2>
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-sm text-blue-800">
          📊 Predictions data available. Full implementation coming soon.
        </p>
        <p className="text-xs text-blue-600 mt-2">
          {predictionCount} predictions loaded
        </p>
      </div>
    </div>
  );
}
