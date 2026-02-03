"use client";

import React from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ExternalLink, CheckCircle2, Globe, Star, TrendingUp } from 'lucide-react';

// ==================== Types ====================

type SourceType = 
  | 'web_page'
  | 'review_site'
  | 'social_media'
  | 'news_article'
  | 'business_listing'
  | 'menu_site'
  | 'unknown';

interface GroundingSource {
  url: string;
  title: string;
  snippet?: string;
  source_type: SourceType;
  accessed_date: string;
  relevance_score?: number;
}

interface GroundedSourcesProps {
  sources: GroundingSource[];
  groundingScore?: number;
  showSnippets?: boolean;
  compact?: boolean;
}

interface CompetitorCardProps {
  competitor: {
    competitor_name: string;
    location: string;
    avg_price?: number;
    price_range?: { min: number; max: number };
    recent_changes: string[];
    menu_highlights: string[];
    customer_sentiment: string;
    sentiment_score?: number;
    social_presence: Record<string, string>;
    recent_promotions: string[];
    sources: GroundingSource[];
    grounding_score: number;
  };
}

// ==================== Source Icon Component ====================

const SourceIcon: React.FC<{ type: SourceType }> = ({ type }) => {
  const iconClass = "w-4 h-4";
  
  switch (type) {
    case 'review_site':
      return <Star className={`${iconClass} text-yellow-500`} />;
    case 'social_media':
      return <TrendingUp className={`${iconClass} text-blue-500`} />;
    case 'news_article':
      return <Globe className={`${iconClass} text-purple-500`} />;
    case 'business_listing':
      return <CheckCircle2 className={`${iconClass} text-green-500`} />;
    case 'menu_site':
      return <ExternalLink className={`${iconClass} text-orange-500`} />;
    default:
      return <Globe className={`${iconClass} text-gray-500`} />;
  }
};

// ==================== Grounded Sources Component ====================

export const GroundedSources: React.FC<GroundedSourcesProps> = ({
  sources,
  groundingScore,
  showSnippets = false,
  compact = false
}) => {
  if (!sources || sources.length === 0) {
    return null;
  }

  const getSourceTypeLabel = (type: SourceType): string => {
    const labels: Record<SourceType, string> = {
      web_page: 'Web',
      review_site: 'Reviews',
      social_media: 'Social',
      news_article: 'News',
      business_listing: 'Business',
      menu_site: 'Menu',
      unknown: 'Source'
    };
    return labels[type] || 'Source';
  };

  const formatDate = (dateString: string): string => {
    try {
      const date = new Date(dateString);
      const today = new Date();
      const diffTime = Math.abs(today.getTime() - date.getTime());
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      
      if (diffDays === 0) return 'today';
      if (diffDays === 1) return 'yesterday';
      if (diffDays < 7) return `${diffDays} days ago`;
      if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
      return date.toLocaleDateString();
    } catch {
      return 'recently';
    }
  };

  if (compact) {
    return (
      <div className="space-y-2">
        {groundingScore !== undefined && (
          <div className="flex items-center gap-2">
            <Badge variant={groundingScore > 0.8 ? "default" : "secondary"}>
              {(groundingScore * 100).toFixed(0)}% grounded
            </Badge>
            <span className="text-xs text-gray-500">
              {sources.length} {sources.length === 1 ? 'source' : 'sources'}
            </span>
          </div>
        )}
        
        <div className="flex flex-wrap gap-2">
          {sources.map((source, idx) => (
            <a
              key={idx}
              href={source.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 hover:underline"
            >
              <SourceIcon type={source.source_type} />
              <span>{source.title}</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          ))}
        </div>
      </div>
    );
  }

  return (
    <Card className="p-4 bg-blue-50 border-blue-200">
      <div className="space-y-3">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h4 className="font-semibold text-sm text-gray-900 flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-blue-600" />
            Grounded Sources
          </h4>
          {groundingScore !== undefined && (
            <Badge variant={groundingScore > 0.8 ? "default" : "secondary"}>
              {(groundingScore * 100).toFixed(0)}% confidence
            </Badge>
          )}
        </div>

        {/* Sources List */}
        <div className="space-y-2">
          {sources.map((source, idx) => (
            <div
              key={idx}
              className="bg-white rounded-lg p-3 border border-blue-100 hover:border-blue-300 transition-colors"
            >
              <div className="flex items-start gap-2">
                <SourceIcon type={source.source_type} />
                
                <div className="flex-1 min-w-0">
                  <a
                    href={source.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm font-medium text-blue-600 hover:text-blue-800 hover:underline flex items-center gap-1"
                  >
                    <span className="truncate">{source.title}</span>
                    <ExternalLink className="w-3 h-3 flex-shrink-0" />
                  </a>
                  
                  <div className="flex items-center gap-2 mt-1">
                    <Badge variant="outline" className="text-xs">
                      {getSourceTypeLabel(source.source_type)}
                    </Badge>
                    <span className="text-xs text-gray-500">
                      Accessed {formatDate(source.accessed_date)}
                    </span>
                    {source.relevance_score !== undefined && (
                      <span className="text-xs text-gray-500">
                        • {(source.relevance_score * 100).toFixed(0)}% relevant
                      </span>
                    )}
                  </div>

                  {showSnippets && source.snippet && (
                    <p className="text-xs text-gray-600 mt-2 line-clamp-2">
                      {source.snippet}
                    </p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="text-xs text-gray-500 pt-2 border-t border-blue-200">
          All information verified from {sources.length} independent {sources.length === 1 ? 'source' : 'sources'}
        </div>
      </div>
    </Card>
  );
};

// ==================== Competitor Card with Grounding ====================

export const CompetitorCard: React.FC<CompetitorCardProps> = ({ competitor }) => {
  const getSentimentColor = (sentiment: string) => {
    switch (sentiment.toLowerCase()) {
      case 'positive':
        return 'text-green-600 bg-green-50';
      case 'negative':
        return 'text-red-600 bg-red-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  const getSentimentEmoji = (sentiment: string) => {
    switch (sentiment.toLowerCase()) {
      case 'positive':
        return '😊';
      case 'negative':
        return '😞';
      default:
        return '😐';
    }
  };

  return (
    <Card className="p-6">
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div>
            <h3 className="text-xl font-bold text-gray-900">
              {competitor.competitor_name}
            </h3>
            <p className="text-sm text-gray-500">{competitor.location}</p>
          </div>
          
          {competitor.avg_price && (
            <div className="text-right">
              <div className="text-2xl font-bold text-gray-900">
                ${competitor.avg_price.toFixed(2)}
              </div>
              <div className="text-xs text-gray-500">avg price</div>
            </div>
          )}
        </div>

        {/* Price Range */}
        {competitor.price_range && (
          <div className="flex items-center gap-2 text-sm">
            <span className="text-gray-600">Price range:</span>
            <span className="font-medium">
              ${competitor.price_range.min.toFixed(2)} - ${competitor.price_range.max.toFixed(2)}
            </span>
          </div>
        )}

        {/* Customer Sentiment */}
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-600">Customer sentiment:</span>
          <Badge className={getSentimentColor(competitor.customer_sentiment)}>
            {getSentimentEmoji(competitor.customer_sentiment)} {competitor.customer_sentiment}
            {competitor.sentiment_score && ` (${(competitor.sentiment_score * 100).toFixed(0)}%)`}
          </Badge>
        </div>

        {/* Recent Changes */}
        {competitor.recent_changes.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-gray-900 mb-2">Recent Changes</h4>
            <ul className="space-y-1">
              {competitor.recent_changes.map((change, idx) => (
                <li key={idx} className="text-sm text-gray-700 flex items-start gap-2">
                  <span className="text-blue-500">•</span>
                  <span>{change}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Menu Highlights */}
        {competitor.menu_highlights.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-gray-900 mb-2">Menu Highlights</h4>
            <div className="flex flex-wrap gap-2">
              {competitor.menu_highlights.map((item, idx) => (
                <Badge key={idx} variant="secondary">
                  {item}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Social Presence */}
        {Object.keys(competitor.social_presence).length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-gray-900 mb-2">Social Media</h4>
            <div className="flex flex-wrap gap-2">
              {Object.entries(competitor.social_presence).map(([platform, handle]) => (
                handle && (
                  <a
                    key={platform}
                    href={handle.startsWith('http') ? handle : `https://${platform}.com/${handle}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-blue-600 hover:text-blue-800 hover:underline flex items-center gap-1"
                  >
                    {platform}: {handle}
                    <ExternalLink className="w-3 h-3" />
                  </a>
                )
              ))}
            </div>
          </div>
        )}

        {/* Recent Promotions */}
        {competitor.recent_promotions.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-gray-900 mb-2">Recent Promotions</h4>
            <ul className="space-y-1">
              {competitor.recent_promotions.map((promo, idx) => (
                <li key={idx} className="text-sm text-gray-700 flex items-start gap-2">
                  <span className="text-green-500">🎉</span>
                  <span>{promo}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Grounded Sources */}
        <GroundedSources
          sources={competitor.sources}
          groundingScore={competitor.grounding_score}
          showSnippets={false}
        />
      </div>
    </Card>
  );
};

export default GroundedSources;
