'use client';

import { ConfidenceIndicator } from '@/components/ai/ConfidenceIndicator';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import {
    ChevronLeft,
    ChevronRight,
    Copy,
    Download,
    Facebook,
    Heart,
    Instagram,
    MoreHorizontal,
    Share2,
    Sparkles,
    ThumbsUp,
    Twitter,
    Zap
} from 'lucide-react';
import { useState } from 'react';

export interface CampaignAsset {
  id: string;
  type: 'image' | 'video' | 'carousel' | 'story';
  platform: 'instagram' | 'facebook' | 'tiktok' | 'twitter' | 'general';
  imageUrl?: string;
  videoUrl?: string;
  carouselImages?: string[];
  headline: string;
  body: string;
  callToAction?: string;
  hashtags?: string[];
  targetAudience?: string;
  estimatedReach?: number;
  estimatedEngagement?: number;
  confidence: number;
  variant?: 'A' | 'B';
}

export interface Campaign {
  id: string;
  name: string;
  objective: string;
  targetDish?: string;
  assets: CampaignAsset[];
  reasoning?: string;
  status: 'draft' | 'ready' | 'scheduled' | 'active';
  createdAt: string;
}

interface CampaignPreviewGalleryProps {
  campaigns: Campaign[];
  onCampaignSelect?: (campaign: Campaign) => void;
  onAssetSelect?: (asset: CampaignAsset) => void;
  onCopyText?: (text: string) => void;
  onDownloadAsset?: (asset: CampaignAsset) => void;
  className?: string;
}

const PLATFORM_CONFIG = {
  instagram: { icon: Instagram, color: 'text-pink-600', bgColor: 'bg-pink-50', name: 'Instagram' },
  facebook: { icon: Facebook, color: 'text-blue-600', bgColor: 'bg-blue-50', name: 'Facebook' },
  tiktok: { icon: Zap, color: 'text-gray-900', bgColor: 'bg-gray-100', name: 'TikTok' },
  twitter: { icon: Twitter, color: 'text-sky-500', bgColor: 'bg-sky-50', name: 'Twitter' },
  general: { icon: Share2, color: 'text-gray-600', bgColor: 'bg-gray-50', name: 'General' },
};

function AssetPreviewCard({
  asset,
  onCopy,
  onDownload,
  onSelect,
}: {
  asset: CampaignAsset;
  onCopy?: (text: string) => void;
  onDownload?: () => void;
  onSelect?: () => void;
}) {
  const [currentSlide, setCurrentSlide] = useState(0);
  const platform = PLATFORM_CONFIG[asset.platform];
  const PlatformIcon = platform.icon;

  const fullText = `${asset.headline}\n\n${asset.body}${asset.hashtags ? '\n\n' + asset.hashtags.map(h => `#${h}`).join(' ') : ''}`;

  return (
    <div
      className="bg-white rounded-xl border shadow-sm overflow-hidden hover:shadow-md transition-shadow cursor-pointer"
      onClick={onSelect}
    >
      {/* Platform Header */}
      <div className={cn('px-4 py-2 flex items-center justify-between', platform.bgColor)}>
        <div className="flex items-center gap-2">
          <PlatformIcon className={cn('h-4 w-4', platform.color)} />
          <span className={cn('text-sm font-medium', platform.color)}>{platform.name}</span>
        </div>
        <div className="flex items-center gap-2">
          {asset.variant && (
            <Badge variant="outline" className="text-xs">
              Variant {asset.variant}
            </Badge>
          )}
          <Badge variant="secondary" className="text-xs capitalize">
            {asset.type}
          </Badge>
        </div>
      </div>

      {/* Image/Video Preview */}
      <div className="relative aspect-square bg-gray-100">
        {asset.type === 'carousel' && asset.carouselImages ? (
          <>
            <img
              src={asset.carouselImages[currentSlide]}
              alt={asset.headline}
              className="w-full h-full object-cover"
            />
            {/* Carousel Navigation */}
            {asset.carouselImages.length > 1 && (
              <>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setCurrentSlide(prev => prev > 0 ? prev - 1 : asset.carouselImages!.length - 1);
                  }}
                  className="absolute left-2 top-1/2 -translate-y-1/2 p-1 bg-black/50 rounded-full text-white hover:bg-black/70"
                >
                  <ChevronLeft className="h-4 w-4" />
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setCurrentSlide(prev => prev < asset.carouselImages!.length - 1 ? prev + 1 : 0);
                  }}
                  className="absolute right-2 top-1/2 -translate-y-1/2 p-1 bg-black/50 rounded-full text-white hover:bg-black/70"
                >
                  <ChevronRight className="h-4 w-4" />
                </button>
                {/* Dots */}
                <div className="absolute bottom-2 left-1/2 -translate-x-1/2 flex gap-1">
                  {asset.carouselImages.map((_, idx) => (
                    <div
                      key={idx}
                      className={cn(
                        'h-1.5 w-1.5 rounded-full',
                        idx === currentSlide ? 'bg-white' : 'bg-white/50'
                      )}
                    />
                  ))}
                </div>
              </>
            )}
          </>
        ) : asset.imageUrl ? (
          <img
            src={asset.imageUrl}
            alt={asset.headline}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <Sparkles className="h-12 w-12 text-gray-300" />
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-4 space-y-3">
        {/* Headline */}
        <h4 className="font-semibold text-gray-900 line-clamp-2">{asset.headline}</h4>
        
        {/* Body */}
        <p className="text-sm text-gray-600 line-clamp-3">{asset.body}</p>
        
        {/* Hashtags */}
        {asset.hashtags && asset.hashtags.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {asset.hashtags.slice(0, 5).map((tag, idx) => (
              <span key={idx} className="text-xs text-blue-600">#{tag}</span>
            ))}
            {asset.hashtags.length > 5 && (
              <span className="text-xs text-gray-400">+{asset.hashtags.length - 5}</span>
            )}
          </div>
        )}

        {/* CTA */}
        {asset.callToAction && (
          <div className="pt-2">
            <Button size="sm" className="w-full" variant="outline">
              {asset.callToAction}
            </Button>
          </div>
        )}
      </div>

      {/* Metrics Preview */}
      <div className="px-4 py-3 bg-gray-50 border-t flex items-center justify-between">
        <div className="flex items-center gap-4 text-xs text-gray-500">
          {asset.estimatedReach && (
            <span className="flex items-center gap-1">
              <ThumbsUp className="h-3 w-3" />
              ~{(asset.estimatedReach / 1000).toFixed(1)}K alcance
            </span>
          )}
          {asset.estimatedEngagement && (
            <span className="flex items-center gap-1">
              <Heart className="h-3 w-3" />
              ~{asset.estimatedEngagement}% eng.
            </span>
          )}
        </div>
        <ConfidenceIndicator value={asset.confidence} variant="minimal" size="xs" />
      </div>

      {/* Actions */}
      <div className="px-4 py-2 border-t flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="ghost"
            onClick={(e) => {
              e.stopPropagation();
              onCopy?.(fullText);
            }}
          >
            <Copy className="h-4 w-4" />
          </Button>
          {asset.imageUrl && (
            <Button
              size="sm"
              variant="ghost"
              onClick={(e) => {
                e.stopPropagation();
                onDownload?.();
              }}
            >
              <Download className="h-4 w-4" />
            </Button>
          )}
        </div>
        <Button size="sm" variant="ghost">
          <MoreHorizontal className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}

export function CampaignPreviewGallery({
  campaigns,
  onCampaignSelect,
  onAssetSelect,
  onCopyText,
  onDownloadAsset,
  className,
}: CampaignPreviewGalleryProps) {
  const [selectedCampaign, setSelectedCampaign] = useState<string | null>(
    campaigns.length > 0 ? campaigns[0].id : null
  );
  const [viewMode, _setViewMode] = useState<'grid' | 'list'>('grid');

  const currentCampaign = campaigns.find(c => c.id === selectedCampaign);

  if (campaigns.length === 0) {
    return (
      <div className={cn('text-center py-12 text-gray-500', className)}>
        <Sparkles className="h-12 w-12 mx-auto mb-4 text-gray-300" />
        <p>No campaigns generated yet</p>
      </div>
    );
  }

  return (
    <div className={cn('space-y-6', className)}>
      {/* Campaign Selector */}
      {campaigns.length > 1 && (
        <div className="flex items-center gap-2 overflow-x-auto pb-2">
          {campaigns.map((campaign) => (
            <button
              key={campaign.id}
              onClick={() => {
                setSelectedCampaign(campaign.id);
                onCampaignSelect?.(campaign);
              }}
              className={cn(
                'px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors',
                selectedCampaign === campaign.id
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              )}
            >
              {campaign.name}
              {campaign.targetDish && (
                <span className="ml-1 opacity-75">• {campaign.targetDish}</span>
              )}
            </button>
          ))}
        </div>
      )}

      {/* Current Campaign Info */}
      {currentCampaign && (
        <div className="p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl border border-purple-100">
          <div className="flex items-start justify-between">
            <div>
              <h3 className="font-semibold text-gray-900">{currentCampaign.name}</h3>
              <p className="text-sm text-gray-600 mt-1">{currentCampaign.objective}</p>
            </div>
            <Badge
              variant="outline"
              className={cn(
                currentCampaign.status === 'ready' && 'border-green-500 text-green-700',
                currentCampaign.status === 'draft' && 'border-gray-500 text-gray-700',
                currentCampaign.status === 'active' && 'border-blue-500 text-blue-700'
              )}
            >
              {currentCampaign.status}
            </Badge>
          </div>
          
          {currentCampaign.reasoning && (
            <div className="mt-3 p-3 bg-white/60 rounded-lg">
              <p className="text-xs text-gray-500 mb-1">💡 Gemini Reasoning:</p>
              <p className="text-sm text-gray-700">{currentCampaign.reasoning}</p>
            </div>
          )}
        </div>
      )}

      {/* Assets Grid */}
      {currentCampaign && (
        <div className={cn(
          'grid gap-4',
          viewMode === 'grid' ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3' : 'grid-cols-1'
        )}>
          {currentCampaign.assets.map((asset) => (
            <AssetPreviewCard
              key={asset.id}
              asset={asset}
              onCopy={onCopyText}
              onDownload={() => onDownloadAsset?.(asset)}
              onSelect={() => onAssetSelect?.(asset)}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default CampaignPreviewGallery;
