'use client';

import { ConfidenceIndicator } from '@/components/ai/ConfidenceIndicator';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';
import {
  AlertCircle,
  Camera,
  CheckCircle2,
  Film,
  Loader2,
  Mic,
  Pause,
  Play,
  RotateCcw,
  Sparkles,
  Upload,
  Video
} from 'lucide-react';
import { useCallback, useRef, useState } from 'react';

const API_BASE = '';

interface VideoAnalysisResult {
  transcription?: string;
  keyMoments?: {
    timestamp: string;
    description: string;
    relevance: 'high' | 'medium' | 'low';
  }[];
  extractedInsights?: string[];
  menuItems?: {
    name: string;
    description?: string;
    estimatedPrice?: number;
    category?: string;
  }[];
  atmosphereAnalysis?: {
    ambiance: string;
    lighting: string;
    seating: string;
    suggestions: string[];
  };
  confidence: number;
}

interface VideoAnalysisZoneProps {
  sessionId?: string;
  onAnalysisComplete?: (result: VideoAnalysisResult) => void;
  onError?: (error: string) => void;
  maxDurationSeconds?: number;
  acceptedFormats?: string[];
  className?: string;
}

type AnalysisStatus = 'idle' | 'uploading' | 'processing' | 'complete' | 'error';

export function VideoAnalysisZone({
  sessionId,
  onAnalysisComplete,
  onError,
  maxDurationSeconds = 300,
  acceptedFormats = ['video/mp4', 'video/webm', 'video/quicktime'],
  className,
}: VideoAnalysisZoneProps) {
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [status, setStatus] = useState<AnalysisStatus>('idle');
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<VideoAnalysisResult | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!acceptedFormats.includes(file.type)) {
      setError(`Unsupported format. Use: ${acceptedFormats.map(f => f.split('/')[1]).join(', ')}`);
      return;
    }

    // Validate file size (max 100MB)
    if (file.size > 100 * 1024 * 1024) {
      setError('File is too large. Max 100MB.');
      return;
    }

    setVideoFile(file);
    setVideoUrl(URL.createObjectURL(file));
    setError(null);
    setResult(null);
    setStatus('idle');
  }, [acceptedFormats]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file && acceptedFormats.includes(file.type)) {
      setVideoFile(file);
      setVideoUrl(URL.createObjectURL(file));
      setError(null);
      setResult(null);
      setStatus('idle');
    }
  }, [acceptedFormats]);

  const analyzeVideo = async () => {
    if (!videoFile) return;

    setStatus('uploading');
    setProgress(0);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('video', videoFile);
      if (sessionId) {
        formData.append('session_id', sessionId);
      }

      // Simulated progress for upload
      const progressInterval = setInterval(() => {
        setProgress(prev => Math.min(prev + 10, 40));
      }, 500);

      const response = await fetch(`${API_BASE}/api/v1/video/analyze`, {
        method: 'POST',
        body: formData,
      });

      clearInterval(progressInterval);
      setProgress(50);
      setStatus('processing');

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Analysis failed');
      }

      // Processing progress simulation
      const processingInterval = setInterval(() => {
        setProgress(prev => Math.min(prev + 5, 95));
      }, 1000);

      const data = await response.json();
      
      clearInterval(processingInterval);
      setProgress(100);
      setStatus('complete');

      const analysisResult: VideoAnalysisResult = {
        transcription: data.transcription,
        keyMoments: data.key_moments || [],
        extractedInsights: data.insights || [],
        menuItems: data.menu_items || [],
        atmosphereAnalysis: data.atmosphere,
        confidence: data.confidence || 0.85,
      };

      setResult(analysisResult);
      onAnalysisComplete?.(analysisResult);

    } catch (err) {
      setStatus('error');
      const errorMsg = err instanceof Error ? err.message : 'Error analyzing video';
      setError(errorMsg);
      onError?.(errorMsg);
    }
  };

  const reset = () => {
    setVideoFile(null);
    setVideoUrl(null);
    setStatus('idle');
    setProgress(0);
    setError(null);
    setResult(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const togglePlay = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  return (
    <div className={cn('rounded-xl border bg-white overflow-hidden', className)}>
      {/* Header */}
      <div className="p-4 bg-gradient-to-r from-indigo-50 to-purple-50 border-b">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-indigo-100 rounded-lg">
            <Video className="h-5 w-5 text-indigo-600" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">Video Analysis</h3>
            <p className="text-sm text-gray-600">
              Gemini 3 Vision analyzes your video in real-time
            </p>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        {/* Upload Zone */}
        {!videoFile && (
          <div
            className={cn(
              'border-2 border-dashed rounded-xl p-8 text-center transition-all cursor-pointer',
              'hover:border-indigo-400 hover:bg-indigo-50/50',
              error ? 'border-red-300 bg-red-50' : 'border-gray-300'
            )}
            onDrop={handleDrop}
            onDragOver={(e) => e.preventDefault()}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept={acceptedFormats.join(',')}
              onChange={handleFileSelect}
              className="hidden"
            />
            <div className="flex flex-col items-center gap-4">
              <div className="p-4 bg-gray-100 rounded-full">
                <Film className="h-8 w-8 text-gray-500" />
              </div>
              <div>
                <p className="font-medium text-gray-900">
                  Drag a video or click to select
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  MP4, WebM or MOV (max 100MB, {Math.floor(maxDurationSeconds / 60)} min)
                </p>
              </div>
              <Button variant="outline" type="button">
                <Upload className="h-4 w-4 mr-2" />
                Select video
              </Button>
            </div>
          </div>
        )}

        {/* Video Preview */}
        {videoFile && videoUrl && (
          <div className="space-y-4">
            <div className="relative rounded-lg overflow-hidden bg-black aspect-video">
              <video
                ref={videoRef}
                src={videoUrl}
                className="w-full h-full object-contain"
                onEnded={() => setIsPlaying(false)}
              />
              
              {/* Video Controls Overlay */}
              <div className="absolute inset-0 flex items-center justify-center bg-black/30 opacity-0 hover:opacity-100 transition-opacity">
                <button
                  onClick={togglePlay}
                  className="p-4 bg-white/90 rounded-full shadow-lg hover:bg-white transition-colors"
                >
                  {isPlaying ? (
                    <Pause className="h-8 w-8 text-gray-900" />
                  ) : (
                    <Play className="h-8 w-8 text-gray-900" />
                  )}
                </button>
              </div>

              {/* File Info */}
              <div className="absolute bottom-2 left-2 right-2 flex items-center justify-between">
                <span className="px-2 py-1 bg-black/70 text-white text-xs rounded">
                  {videoFile.name}
                </span>
                <span className="px-2 py-1 bg-black/70 text-white text-xs rounded">
                  {(videoFile.size / (1024 * 1024)).toFixed(1)} MB
                </span>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center gap-3">
              <Button
                onClick={analyzeVideo}
                disabled={status === 'uploading' || status === 'processing'}
                className="flex-1 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700"
              >
                {status === 'uploading' || status === 'processing' ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    {status === 'uploading' ? 'Uploading...' : 'Analyzing...'}
                  </>
                ) : (
                  <>
                    <Sparkles className="h-4 w-4 mr-2" />
                    Analyze with Gemini 3 Vision
                  </>
                )}
              </Button>
              <Button variant="outline" onClick={reset}>
                <RotateCcw className="h-4 w-4" />
              </Button>
            </div>

            {/* Progress Bar */}
            {(status === 'uploading' || status === 'processing') && (
              <div className="space-y-2">
                <Progress value={progress} className="h-2" />
                <p className="text-sm text-center text-gray-600">
                  {status === 'uploading' && 'Uploading video...'}
                  {status === 'processing' && 'Gemini 3 is analyzing the content...'}
                </p>
              </div>
            )}
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-medium text-red-800">Error</p>
              <p className="text-sm text-red-700">{error}</p>
            </div>
          </div>
        )}

        {/* Results Display */}
        {result && status === 'complete' && (
          <div className="mt-6 space-y-6 animate-in fade-in slide-in-from-bottom-4">
            {/* Success Header */}
            <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg border border-green-200">
              <div className="flex items-center gap-3">
                <CheckCircle2 className="h-6 w-6 text-green-600" />
                <div>
                  <p className="font-medium text-green-800">Analysis complete</p>
                  <p className="text-sm text-green-700">
                    {result.keyMoments?.length || 0} key moments detected
                  </p>
                </div>
              </div>
              <ConfidenceIndicator value={result.confidence} variant="badge" size="sm" />
            </div>

            {/* Transcription */}
            {result.transcription && (
              <div className="space-y-2">
                <h4 className="font-medium text-gray-900 flex items-center gap-2">
                  <Mic className="h-4 w-4 text-purple-600" />
                  Transcription
                </h4>
                <div className="p-4 bg-gray-50 rounded-lg text-sm text-gray-700 max-h-40 overflow-y-auto">
                  {result.transcription}
                </div>
              </div>
            )}

            {/* Key Moments */}
            {result.keyMoments && result.keyMoments.length > 0 && (
              <div className="space-y-2">
                <h4 className="font-medium text-gray-900 flex items-center gap-2">
                  <Camera className="h-4 w-4 text-indigo-600" />
                  Key Moments
                </h4>
                <div className="space-y-2">
                  {result.keyMoments.map((moment, idx) => (
                    <div
                      key={idx}
                      className={cn(
                        'p-3 rounded-lg border flex items-start gap-3',
                        moment.relevance === 'high' && 'bg-yellow-50 border-yellow-200',
                        moment.relevance === 'medium' && 'bg-blue-50 border-blue-200',
                        moment.relevance === 'low' && 'bg-gray-50 border-gray-200'
                      )}
                    >
                      <span className="font-mono text-xs bg-black/10 px-2 py-1 rounded">
                        {moment.timestamp}
                      </span>
                      <p className="text-sm text-gray-700">{moment.description}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Extracted Insights */}
            {result.extractedInsights && result.extractedInsights.length > 0 && (
              <div className="space-y-2">
                <h4 className="font-medium text-gray-900 flex items-center gap-2">
                  <Sparkles className="h-4 w-4 text-amber-600" />
                  Extracted Insights
                </h4>
                <ul className="space-y-1">
                  {result.extractedInsights.map((insight, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-sm text-gray-700">
                      <span className="text-amber-500">•</span>
                      {insight}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Menu Items Detected */}
            {result.menuItems && result.menuItems.length > 0 && (
              <div className="space-y-2">
                <h4 className="font-medium text-gray-900">
                  🍽️ Detected Menu Items
                </h4>
                <div className="grid grid-cols-2 gap-2">
                  {result.menuItems.map((item, idx) => (
                    <div key={idx} className="p-3 bg-orange-50 rounded-lg border border-orange-200">
                      <p className="font-medium text-gray-900">{item.name}</p>
                      {item.description && (
                        <p className="text-xs text-gray-600 mt-1">{item.description}</p>
                      )}
                      {item.estimatedPrice && (
                        <p className="text-sm font-medium text-orange-700 mt-1">
                          ~${item.estimatedPrice}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Footer Info */}
      <div className="px-4 py-3 bg-gray-50 border-t">
        <p className="text-xs text-gray-500 flex items-center gap-1">
          <Sparkles className="h-3 w-3" />
          Multimodal analysis with Gemini 3 Flash Vision
        </p>
      </div>
    </div>
  );
}

export default VideoAnalysisZone;
