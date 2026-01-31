'use client'

import { Calendar, Check, Copy, MessageSquare, Target, TrendingUp } from 'lucide-react'
import { useState } from 'react'

interface Campaign {
  id: number
  title: string
  objective: string
  target_audience: string
  start_date: string
  end_date: string
  channels: string[]
  key_messages: string[]
  promotional_items: string[]
  social_post_copy: string
  expected_uplift_percent: number
  rationale: string
}

interface CampaignCardsProps {
  campaigns: Campaign[]
}

export default function CampaignCards({ campaigns }: CampaignCardsProps) {
  const [copiedId, setCopiedId] = useState<number | null>(null)

  const copyToClipboard = (text: string, id: number) => {
    navigator.clipboard.writeText(text)
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 2000)
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {campaigns.map((campaign) => (
        <div key={campaign.id} className="card flex flex-col">
          {/* Header */}
          <div className="mb-4">
            <h3 className="text-lg font-bold text-gray-900">{campaign.title}</h3>
            <p className="text-sm text-gray-600 mt-1">{campaign.objective}</p>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 gap-3 mb-4">
            <div className="bg-primary-50 rounded-lg p-3">
              <div className="flex items-center gap-2 text-primary-600">
                <TrendingUp className="h-4 w-4" />
                <span className="text-sm font-medium">Expected Uplift</span>
              </div>
              <p className="text-xl font-bold text-primary-700 mt-1">+{campaign.expected_uplift_percent}%</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-3">
              <div className="flex items-center gap-2 text-gray-600">
                <Calendar className="h-4 w-4" />
                <span className="text-sm font-medium">Duration</span>
              </div>
              <p className="text-sm font-medium text-gray-900 mt-1">
                {new Date(campaign.start_date).toLocaleDateString()} - {new Date(campaign.end_date).toLocaleDateString()}
              </p>
            </div>
          </div>

          {/* Target */}
          <div className="mb-4">
            <div className="flex items-center gap-2 text-gray-600 mb-1">
              <Target className="h-4 w-4" />
              <span className="text-sm font-medium">Target Audience</span>
            </div>
            <p className="text-sm text-gray-700">{campaign.target_audience}</p>
          </div>

          {/* Channels */}
          <div className="mb-4">
            <p className="text-sm font-medium text-gray-600 mb-2">Channels</p>
            <div className="flex flex-wrap gap-2">
              {campaign.channels.map((channel, idx) => (
                <span key={idx} className="px-2 py-1 bg-gray-100 rounded text-xs font-medium capitalize">
                  {channel.replace('_', ' ')}
                </span>
              ))}
            </div>
          </div>

          {/* Featured Items */}
          <div className="mb-4">
            <p className="text-sm font-medium text-gray-600 mb-2">Featured Items</p>
            <div className="flex flex-wrap gap-2">
              {campaign.promotional_items.slice(0, 4).map((item, idx) => (
                <span key={idx} className="px-2 py-1 bg-primary-50 text-primary-700 rounded text-xs font-medium">
                  {item}
                </span>
              ))}
            </div>
          </div>

          {/* Social Post Copy */}
          <div className="mt-auto">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2 text-gray-600">
                <MessageSquare className="h-4 w-4" />
                <span className="text-sm font-medium">Social Post</span>
              </div>
              <button
                onClick={() => copyToClipboard(campaign.social_post_copy, campaign.id)}
                className="text-sm text-primary-600 hover:text-primary-700 flex items-center gap-1"
              >
                {copiedId === campaign.id ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                {copiedId === campaign.id ? 'Copied!' : 'Copy'}
              </button>
            </div>
            <div className="bg-gray-50 rounded-lg p-3">
              <p className="text-sm text-gray-700 line-clamp-4">{campaign.social_post_copy}</p>
            </div>
          </div>

          {/* Rationale */}
          <details className="mt-4">
            <summary className="text-sm font-medium text-gray-600 cursor-pointer hover:text-primary-600">
              View Rationale
            </summary>
            <p className="text-sm text-gray-600 mt-2 p-3 bg-gray-50 rounded-lg">{campaign.rationale}</p>
          </details>
        </div>
      ))}
    </div>
  )
}
