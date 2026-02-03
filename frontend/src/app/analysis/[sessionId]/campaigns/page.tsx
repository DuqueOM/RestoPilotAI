'use client';

import { api, Campaign, CampaignResult } from '@/lib/api';
import { use, useEffect, useState } from 'react';


interface CampaignsPageProps {
  params: Promise<{ sessionId: string }>;
}

export default function CampaignsPage({ params }: CampaignsPageProps) {
  const { sessionId } = use(params);
  const [data, setData] = useState<CampaignResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  useEffect(() => {
    const fetchCampaigns = async () => {
      try {
        // Check if this is a demo session
        const session = (sessionId === 'demo-session-001' || sessionId === 'margarita-pinta-demo-001')
          ? await api.getDemoSession()
          : await api.getSession(sessionId);
        if (session.campaigns) {
          setData(session.campaigns);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load campaigns');
      } finally {
        setLoading(false);
      }
    };

    fetchCampaigns();
  }, [sessionId]);

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

  if (!data || !data.campaigns?.length) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p className="text-4xl mb-4">📢</p>
        <p>No marketing campaigns generated yet.</p>
        <p className="text-sm mt-2">Complete BCG analysis to generate campaigns.</p>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold">AI-Generated Marketing Campaigns</h2>
        <span className="text-sm text-gray-500">
          {data.campaigns.length} campaigns
        </span>
      </div>

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
    </div>
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
