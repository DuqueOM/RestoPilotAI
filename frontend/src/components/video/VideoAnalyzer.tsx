"use client";

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import {
    AlertCircle,
    CheckCircle2,
    Clock,
    Facebook,
    Instagram,
    Pause,
    Play,
    Star,
    TrendingUp,
    Upload,
    Video,
    Youtube,
    Zap
} from 'lucide-react';
import React, { useRef, useState } from 'react';

// ==================== Types ====================

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
  linkedin: number;
  youtube: number;
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
    optimal_length: {
      recommended: string;
      based_on: string;
    };
    best_platforms: Array<{
      platform: string;
      score: number;
      recommendation: string;
    }>;
    improvements: string[];
  };
}

interface VideoAnalyzerProps {
  onAnalysisComplete?: (result: VideoAnalysisResult) => void;
}

// ==================== Video Analyzer Component ====================

export const VideoAnalyzer: React.FC<VideoAnalyzerProps> = ({ onAnalysisComplete }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<VideoAnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [_currentTime, setCurrentTime] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('video/')) {
      setError('Please select a valid video file');
      return;
    }

    // Validate file size (100MB max)
    const maxSize = 100 * 1024 * 1024;
    if (file.size > maxSize) {
      setError('Video file too large. Maximum size: 100MB');
      return;
    }

    setSelectedFile(file);
    setVideoUrl(URL.createObjectURL(file));
    setError(null);
    setAnalysis(null);
  };

  const handleAnalyze = async () => {
    if (!selectedFile) return;

    setIsAnalyzing(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('video', selectedFile);
      formData.append('purpose', 'social_media');

      const response = await fetch('/api/v1/video/analyze', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Analysis failed');
      }

      const result: VideoAnalysisResult = await response.json();
      setAnalysis(result);
      onAnalysisComplete?.(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const seekToMoment = (timestamp: string) => {
    if (!videoRef.current) return;
    
    // Parse timestamp (MM:SS or HH:MM:SS)
    const parts = timestamp.split(':').map(Number);
    let seconds = 0;
    
    if (parts.length === 2) {
      seconds = parts[0] * 60 + parts[1];
    } else if (parts.length === 3) {
      seconds = parts[0] * 3600 + parts[1] * 60 + parts[2];
    }
    
    videoRef.current.currentTime = seconds;
    videoRef.current.play();
    setIsPlaying(true);
  };

  const togglePlayPause = () => {
    if (!videoRef.current) return;
    
    if (isPlaying) {
      videoRef.current.pause();
    } else {
      videoRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };

  const getPlatformIcon = (platform: string) => {
    const lowerPlatform = platform.toLowerCase();
    if (lowerPlatform.includes('instagram')) return <Instagram className="w-4 h-4" />;
    if (lowerPlatform.includes('youtube')) return <Youtube className="w-4 h-4" />;
    if (lowerPlatform.includes('facebook')) return <Facebook className="w-4 h-4" />;
    if (lowerPlatform.includes('tiktok')) return <Video className="w-4 h-4" />;
    return <Video className="w-4 h-4" />;
  };

  const getScoreColor = (score: number) => {
    if (score >= 9) return 'text-green-600 bg-green-50';
    if (score >= 7) return 'text-blue-600 bg-blue-50';
    if (score >= 5) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  const getMomentIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'engaging':
      case 'high_engagement':
        return <Zap className="w-4 h-4 text-yellow-500" />;
      case 'thumbnail':
      case 'best_thumbnail':
        return <Star className="w-4 h-4 text-purple-500" />;
      case 'shareable':
        return <TrendingUp className="w-4 h-4 text-green-500" />;
      default:
        return <Clock className="w-4 h-4 text-gray-500" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Upload Section */}
      <Card className="p-6">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xl font-bold text-gray-900 flex items-center gap-2">
              <Video className="w-6 h-6 text-blue-600" />
              Video Analysis
            </h3>
            <Badge variant="default" className="bg-purple-600">
              Gemini 3 Exclusive
            </Badge>
          </div>

          <p className="text-sm text-gray-600">
            Upload your restaurant video for AI-powered analysis. Get insights on content quality,
            platform suitability, and optimization recommendations.
          </p>

          {/* File Input */}
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors">
            <input
              ref={fileInputRef}
              type="file"
              accept="video/*"
              onChange={handleFileSelect}
              className="hidden"
            />
            
            {!selectedFile ? (
              <div className="space-y-3">
                <Video className="w-12 h-12 text-gray-400 mx-auto" />
                <div>
                  <Button
                    onClick={() => fileInputRef.current?.click()}
                    variant="outline"
                  >
                    <Upload className="w-4 h-4 mr-2" />
                    Select Video
                  </Button>
                </div>
                <p className="text-xs text-gray-500">
                  MP4, MOV, AVI • Max 100MB
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                <CheckCircle2 className="w-12 h-12 text-green-600 mx-auto" />
                <div>
                  <p className="font-medium text-gray-900">{selectedFile.name}</p>
                  <p className="text-sm text-gray-500">
                    {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                  </p>
                </div>
                <div className="flex gap-2 justify-center">
                  <Button
                    onClick={handleAnalyze}
                    disabled={isAnalyzing}
                  >
                    {isAnalyzing ? 'Analyzing...' : 'Analyze Video'}
                  </Button>
                  <Button
                    onClick={() => {
                      setSelectedFile(null);
                      setVideoUrl(null);
                      setAnalysis(null);
                    }}
                    variant="outline"
                  >
                    Change
                  </Button>
                </div>
              </div>
            )}
          </div>

          {error && (
            <div className="flex items-start gap-2 p-3 bg-red-50 border border-red-200 rounded-lg">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}
        </div>
      </Card>

      {/* Video Preview */}
      {videoUrl && (
        <Card className="p-6">
          <h4 className="font-semibold text-gray-900 mb-4">Video Preview</h4>
          <div className="relative bg-black rounded-lg overflow-hidden">
            <video
              ref={videoRef}
              src={videoUrl}
              className="w-full"
              onTimeUpdate={(e) => setCurrentTime(e.currentTarget.currentTime)}
              onPlay={() => setIsPlaying(true)}
              onPause={() => setIsPlaying(false)}
            />
            <div className="absolute bottom-4 left-4">
              <Button
                size="sm"
                onClick={togglePlayPause}
                className="bg-white/90 hover:bg-white text-gray-900"
              >
                {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
              </Button>
            </div>
          </div>
        </Card>
      )}

      {/* Analysis Results */}
      {analysis && (
        <div className="space-y-6">
          {/* Quality Scores */}
          <Card className="p-6">
            <h4 className="font-semibold text-gray-900 mb-4">Quality Assessment</h4>
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600">
                  {analysis.quality_scores.visual.toFixed(1)}
                </div>
                <div className="text-sm text-gray-600">Visual Quality</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-purple-600">
                  {analysis.quality_scores.audio?.toFixed(1) || 'N/A'}
                </div>
                <div className="text-sm text-gray-600">Audio Quality</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600">
                  {analysis.quality_scores.overall.toFixed(1)}
                </div>
                <div className="text-sm text-gray-600">Overall</div>
              </div>
            </div>
          </Card>

          {/* Content Type & Thumbnail */}
          <Card className="p-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h4 className="font-semibold text-gray-900">Content Analysis</h4>
                <p className="text-sm text-gray-600 mt-1">
                  Type: <span className="font-medium">{analysis.content_type}</span>
                </p>
              </div>
              {analysis.best_thumbnail_timestamp && (
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => seekToMoment(analysis.best_thumbnail_timestamp)}
                >
                  <Star className="w-4 h-4 mr-1" />
                  Best Thumbnail: {analysis.best_thumbnail_timestamp}
                </Button>
              )}
            </div>
          </Card>

          {/* Key Moments */}
          {analysis.key_moments.length > 0 && (
            <Card className="p-6">
              <h4 className="font-semibold text-gray-900 mb-4">🌟 Key Moments</h4>
              <div className="space-y-3">
                {analysis.key_moments.map((moment, idx) => (
                  <div
                    key={idx}
                    className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
                    onClick={() => seekToMoment(moment.timestamp)}
                  >
                    {getMomentIcon(moment.type)}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-mono text-sm font-medium text-blue-600">
                          {moment.timestamp}
                        </span>
                        <Badge variant="outline" className="text-xs">
                          {moment.type}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-700">{moment.description}</p>
                    </div>
                    <Play className="w-4 h-4 text-gray-400 flex-shrink-0" />
                  </div>
                ))}
              </div>
            </Card>
          )}

          {/* Platform Suitability */}
          <Card className="p-6">
            <h4 className="font-semibold text-gray-900 mb-4">📱 Platform Suitability</h4>
            <div className="space-y-3">
              {Object.entries(analysis.platform_suitability).map(([platform, score]) => (
                <div key={platform} className="flex items-center gap-3">
                  <div className="flex items-center gap-2 w-40">
                    {getPlatformIcon(platform)}
                    <span className="text-sm font-medium capitalize">
                      {platform.replace(/_/g, ' ')}
                    </span>
                  </div>
                  <div className="flex-1">
                    <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className={`h-full ${
                          score >= 9 ? 'bg-green-500' :
                          score >= 7 ? 'bg-blue-500' :
                          score >= 5 ? 'bg-yellow-500' :
                          'bg-red-500'
                        }`}
                        style={{ width: `${score * 10}%` }}
                      />
                    </div>
                  </div>
                  <Badge className={getScoreColor(score)}>
                    {score.toFixed(1)}/10
                  </Badge>
                </div>
              ))}
            </div>

            {/* Best Platforms */}
            {analysis.recommendations.best_platforms.length > 0 && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <p className="text-sm font-medium text-gray-700 mb-2">
                  Recommended Platforms:
                </p>
                <div className="flex flex-wrap gap-2">
                  {analysis.recommendations.best_platforms.map((platform, idx) => (
                    <Badge
                      key={idx}
                      variant={platform.recommendation === 'excellent' ? 'default' : 'secondary'}
                    >
                      {platform.platform.replace(/_/g, ' ')} • {platform.score.toFixed(1)}/10
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </Card>

          {/* Recommendations */}
          <Card className="p-6">
            <h4 className="font-semibold text-gray-900 mb-4">💡 Recommendations</h4>
            <div className="space-y-4">
              {/* Optimal Length */}
              <div>
                <p className="text-sm font-medium text-gray-700 mb-1">Optimal Length:</p>
                <p className="text-sm text-gray-600">
                  {analysis.recommendations.optimal_length.recommended}
                  <span className="text-gray-400 ml-1">
                    (based on {analysis.recommendations.optimal_length.based_on.replace(/_/g, ' ')})
                  </span>
                </p>
              </div>

              {/* Improvements */}
              {analysis.recommendations.improvements.length > 0 && (
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-2">Top Improvements:</p>
                  <ul className="space-y-2">
                    {analysis.recommendations.improvements.map((improvement, idx) => (
                      <li key={idx} className="flex items-start gap-2 text-sm text-gray-600">
                        <span className="text-blue-500 flex-shrink-0">→</span>
                        <span>{improvement}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};

export default VideoAnalyzer;
