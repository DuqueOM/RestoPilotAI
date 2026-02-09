'use client';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import {
    AlertCircle,
    CheckCircle2,
    ChevronDown,
    ChevronUp,
    Film,
    Instagram,
    Loader2,
    Play,
    Sparkles,
    Star,
    TrendingUp,
    Video,
    Zap,
} from 'lucide-react';
import { useCallback, useEffect, useRef, useState } from 'react';

interface KeyMoment {
  timestamp: string;
  description: string;
  type: string;
  engagement_potential?: string;
}

interface QualityScores {
  visual: number;
  audio: number | null;
  overall: number;
}

interface PlatformSuitability {
  instagram_reels: number;
  tiktok: number;
  youtube_shorts: number;
  facebook: number;
  [key: string]: number;
}

interface VideoAnalysisResult {
  filename: string;
  content_type: string;
  key_moments: KeyMoment[];
  quality_scores: QualityScores;
  platform_suitability: PlatformSuitability;
  best_thumbnail_timestamp: string;
  recommended_cuts: string[];
  recommendations: {
    optimal_length: { recommended: string; based_on: string };
    best_platforms: Array<{ platform: string; score: number; recommendation: string }>;
    improvements: string[];
  };
}

interface VideoInsightsPanelProps {
  file: File;
  autoAnalyze?: boolean;
  onAnalysisComplete?: (result: VideoAnalysisResult) => void;
  onRemove?: () => void;
  compact?: boolean;
}

export function VideoInsightsPanel({
  file,
  autoAnalyze = true,
  onAnalysisComplete,
  onRemove,
  compact = false,
}: VideoInsightsPanelProps) {
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState<VideoAnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState(!compact);
  const [duration, setDuration] = useState<string | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    const url = URL.createObjectURL(file);
    setVideoUrl(url);
    const video = document.createElement('video');
    video.preload = 'metadata';
    video.onloadedmetadata = () => {
      const mins = Math.floor(video.duration / 60);
      const secs = Math.floor(video.duration % 60);
      setDuration(`${mins}:${secs.toString().padStart(2, '0')}`);
    };
    video.src = url;
    return () => URL.revokeObjectURL(url);
  }, [file]);

  const analysisStarted = useRef(false);
  useEffect(() => {
    if (autoAnalyze && !analysisStarted.current) {
      analysisStarted.current = true;
      analyzeVideo();
    }
  }, [file]);

  const analyzeVideo = useCallback(async (retryCount = 0) => {
    setAnalyzing(true);
    setError(null);
    const MAX_RETRIES = 2;
    try {
      const formData = new FormData();
      formData.append('video', file);
      formData.append('purpose', 'social_media');

      const response = await fetch('/api/v1/video/analyze', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        // Retry on 500/503/429 (Gemini rate limit / server overload)
        if ((response.status === 500 || response.status === 503 || response.status === 429) && retryCount < MAX_RETRIES) {
          const backoff = (retryCount + 1) * 8000; // 8s, 16s
          console.warn(`[VideoAnalysis] ${file.name} failed (${response.status}), retrying in ${backoff}ms (attempt ${retryCount + 1}/${MAX_RETRIES})`);
          await new Promise(r => setTimeout(r, backoff));
          return analyzeVideo(retryCount + 1);
        }
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || `Analysis failed: ${response.status}`);
      }

      const data: VideoAnalysisResult = await response.json();
      setResult(data);
      setError(null); // Clear any previous error when result succeeds
      onAnalysisComplete?.(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Video analysis failed');
    } finally {
      setAnalyzing(false);
    }
  }, [file, onAnalysisComplete]);

  const seekToMoment = (timestamp: string) => {
    if (!videoRef.current) return;
    const parts = timestamp.split(':').map(Number);
    let seconds = 0;
    if (parts.length === 2) seconds = parts[0] * 60 + parts[1];
    else if (parts.length === 3) seconds = parts[0] * 3600 + parts[1] * 60 + parts[2];
    videoRef.current.currentTime = seconds;
    videoRef.current.play();
  };

  const getScoreColor = (score: number) => {
    if (score >= 8) return 'text-green-700 bg-green-50 border-green-200';
    if (score >= 6) return 'text-blue-700 bg-blue-50 border-blue-200';
    if (score >= 4) return 'text-amber-700 bg-amber-50 border-amber-200';
    return 'text-red-700 bg-red-50 border-red-200';
  };

  const platformIcons: Record<string, React.ReactNode> = {
    instagram_reels: <Instagram className="h-4 w-4" />,
    tiktok: <Video className="h-4 w-4" />,
    youtube_shorts: <Play className="h-4 w-4" />,
    facebook: <TrendingUp className="h-4 w-4" />,
  };

  const platformLabels: Record<string, string> = {
    instagram_reels: 'Instagram Reels',
    tiktok: 'TikTok',
    youtube_shorts: 'YouTube Shorts',
    facebook: 'Facebook',
  };

  return (
    <div className="rounded-xl border border-gray-200 overflow-hidden bg-white">
      {/* Header */}
      <div
        className="flex items-center gap-3 p-4 bg-gradient-to-r from-purple-50 to-indigo-50 border-b cursor-pointer"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="p-2 bg-purple-600 rounded-lg">
          <Film className="h-4 w-4 text-white" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <p className="text-sm font-semibold text-gray-900 truncate">{file.name}</p>
            <Badge className="bg-purple-600 text-white text-[10px] px-1.5 py-0">
              Gemini 3 Exclusive
            </Badge>
          </div>
          <p className="text-xs text-gray-500">
            {analyzing
              ? 'Gemini 3 is analyzing video content...'
              : result
              ? `${result.key_moments?.length || 0} key moments found`
              : error
              ? 'Analysis failed'
              : duration
              ? `Duration: ${duration}`
              : 'Ready'}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {analyzing && <Loader2 className="h-4 w-4 animate-spin text-purple-600" />}
          {result && !analyzing && <CheckCircle2 className="h-4 w-4 text-green-500" />}
          {error && <AlertCircle className="h-4 w-4 text-red-500" />}
          {expanded ? <ChevronUp className="h-4 w-4 text-gray-400" /> : <ChevronDown className="h-4 w-4 text-gray-400" />}
        </div>
      </div>

      {/* Content */}
      {expanded && (
        <div className="p-4 space-y-4">
          {/* Video Player */}
          {videoUrl && (
            <div className="relative rounded-lg overflow-hidden bg-black">
              <video
                ref={videoRef}
                src={videoUrl}
                className="w-full max-h-[250px] object-contain"
                controls
              />
              {analyzing && (
                <div className="absolute inset-0 bg-purple-900/20 backdrop-blur-[1px] flex items-center justify-center">
                  <div className="bg-white/95 rounded-xl px-5 py-3 shadow-lg flex items-center gap-3">
                    <Loader2 className="h-5 w-5 animate-spin text-purple-600" />
                    <div>
                      <p className="text-sm font-medium text-purple-700">Analyzing with Gemini 3...</p>
                      <p className="text-xs text-gray-500">Native video processing (no other AI can do this)</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Error — only show if no result */}
          {error && !result && (
            <div className="p-3 bg-red-50 rounded-lg border border-red-200">
              <p className="text-sm text-red-700">{error}</p>
              <Button size="sm" variant="outline" onClick={() => { analysisStarted.current = false; analyzeVideo(); }} className="mt-2">
                Retry Analysis
              </Button>
            </div>
          )}

          {/* Results */}
          {result && (
            <div className="space-y-4">
              {/* Quality Scores */}
              <div>
                <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Quality Scores</h4>
                <div className="grid grid-cols-3 gap-2">
                  {[
                    { label: 'Visual', score: result.quality_scores.visual },
                    { label: 'Audio', score: result.quality_scores.audio },
                    { label: 'Overall', score: result.quality_scores.overall },
                  ].map((s) => (
                    <div key={s.label} className={cn('rounded-lg border p-2.5 text-center', getScoreColor(s.score ?? 0))}>
                      <div className="text-lg font-bold">{s.score != null ? s.score.toFixed(1) : 'N/A'}</div>
                      <div className="text-xs">{s.label}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Platform Suitability */}
              <div>
                <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Recommended Platforms</h4>
                <p className="text-[10px] text-gray-400 mb-2">Compatibility score — how well this video fits each platform</p>
                <div className="grid grid-cols-2 gap-2">
                  {Object.entries(result.platform_suitability)
                    .filter(([key]) => ['instagram_reels', 'tiktok', 'youtube_shorts', 'facebook'].includes(key))
                    .sort(([, a], [, b]) => b - a)
                    .map(([platform, score]) => (
                      <div key={platform} className="flex items-center gap-2 p-2 rounded-lg bg-gray-50 border">
                        <div className="text-gray-600">{platformIcons[platform] || <Video className="h-4 w-4" />}</div>
                        <span className="text-xs text-gray-700 flex-1">{platformLabels[platform] || platform}</span>
                        <span className={cn('text-xs font-bold', score >= 7 ? 'text-green-600' : score >= 5 ? 'text-amber-600' : 'text-red-600')}>
                          {score.toFixed(1)}
                        </span>
                      </div>
                    ))}
                </div>
              </div>

              {/* Key Moments */}
              {result.key_moments && result.key_moments.length > 0 && (
                <div>
                  <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Key Moments</h4>
                  <div className="space-y-1.5">
                    {result.key_moments.slice(0, 5).map((moment, i) => (
                      <button
                        key={i}
                        onClick={() => seekToMoment(moment.timestamp)}
                        className="w-full flex items-center gap-2 p-2 rounded-lg hover:bg-purple-50 transition-colors text-left"
                      >
                        <span className="text-xs font-mono text-purple-600 bg-purple-50 px-1.5 py-0.5 rounded">
                          {moment.timestamp}
                        </span>
                        <span className="text-xs text-gray-700 flex-1 truncate">{moment.description}</span>
                        {moment.type === 'best_thumbnail' && <Star className="h-3 w-3 text-amber-500 flex-shrink-0" />}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Recommendations */}
              {result.recommendations?.improvements && result.recommendations.improvements.length > 0 && (
                <div>
                  <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Improvements</h4>
                  <div className="space-y-1">
                    {result.recommendations.improvements.slice(0, 4).map((imp, i) => (
                      <div key={i} className="flex items-start gap-2 text-xs text-gray-600">
                        <Zap className="h-3 w-3 text-amber-500 mt-0.5 flex-shrink-0" />
                        <span>{imp}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Not analyzed yet */}
          {!analyzing && !result && !error && (
            <div className="text-center py-4">
              <Button onClick={analyzeVideo} className="bg-purple-600 hover:bg-purple-700">
                <Sparkles className="h-4 w-4 mr-2" />
                Analyze with Gemini 3
              </Button>
            </div>
          )}
        </div>
      )}

      {/* Footer */}
      {expanded && (
        <div className="flex items-center justify-between px-4 py-2.5 bg-gray-50 border-t text-xs text-gray-500">
          <span className="inline-flex items-center gap-1 text-purple-600">
            <Sparkles className="h-3 w-3" />
            Gemini 3 Exclusive — Native video understanding
          </span>
          {onRemove && (
            <button onClick={onRemove} className="text-gray-400 hover:text-red-500 transition-colors">
              Remove
            </button>
          )}
        </div>
      )}
    </div>
  );
}

export default VideoInsightsPanel;
