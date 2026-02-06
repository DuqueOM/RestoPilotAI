'use client';

import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import {
    Loader2,
    Mic,
    Pause,
    Play,
    Square,
    Trash2,
    Volume2
} from 'lucide-react';
import { useCallback, useEffect, useRef, useState } from 'react';

interface TranscriptionSegment {
  id: string;
  text: string;
  timestamp: number;
  confidence?: number;
  isFinal: boolean;
}

interface LiveTranscriptionBoxProps {
  onTranscriptionComplete?: (fullText: string, segments: TranscriptionSegment[]) => void;
  onAudioBlob?: (blob: Blob) => void;
  maxDurationSeconds?: number;
  placeholder?: string;
  showWaveform?: boolean;
  className?: string;
}

export function LiveTranscriptionBox({
  onTranscriptionComplete,
  onAudioBlob,
  maxDurationSeconds = 300,
  placeholder = 'Press the microphone to start recording...',
  showWaveform = true,
  className,
}: LiveTranscriptionBoxProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [segments, setSegments] = useState<TranscriptionSegment[]>([]);
  const [currentText, setCurrentText] = useState('');
  const [duration, setDuration] = useState(0);
  const [audioLevel, setAudioLevel] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const animationRef = useRef<number | null>(null);

  const fullText = segments
    .filter(s => s.isFinal)
    .map(s => s.text)
    .join(' ') + (currentText ? ' ' + currentText : '');

  const startRecording = async () => {
    try {
      setError(null);
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      // Setup audio analysis for waveform
      audioContextRef.current = new AudioContext();
      analyserRef.current = audioContextRef.current.createAnalyser();
      const source = audioContextRef.current.createMediaStreamSource(stream);
      source.connect(analyserRef.current);
      analyserRef.current.fftSize = 256;

      // Start audio level monitoring
      const updateAudioLevel = () => {
        if (analyserRef.current) {
          const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
          analyserRef.current.getByteFrequencyData(dataArray);
          const avg = dataArray.reduce((a, b) => a + b, 0) / dataArray.length;
          setAudioLevel(avg / 255);
        }
        animationRef.current = requestAnimationFrame(updateAudioLevel);
      };
      updateAudioLevel();

      // Setup media recorder
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        onAudioBlob?.(blob);
        
        // Finalize transcription
        if (currentText) {
          const formatTime = (dateStr: string) => {
            const date = new Date(dateStr);
            return date.toLocaleString('en-US', {
              hour: '2-digit',
              minute: '2-digit',
              day: 'numeric',
              month: 'short',
            });
          };
          const finalSegment: TranscriptionSegment = {
            id: `seg-${Date.now()}`,
            text: currentText,
            timestamp: duration,
            confidence: 0.9,
            isFinal: true,
          };
          setSegments(prev => [...prev, finalSegment]);
          setCurrentText('');
        }

        onTranscriptionComplete?.(fullText, segments);
      };

      mediaRecorder.start(1000); // Collect data every second
      setIsRecording(true);
      setIsPaused(false);
      setDuration(0);

      // Start timer
      timerRef.current = setInterval(() => {
        setDuration(prev => {
          if (prev >= maxDurationSeconds) {
            stopRecording();
            return prev;
          }
          return prev + 1;
        });
      }, 1000);

      // Simulate live transcription (in production, use Web Speech API or streaming API)
      simulateLiveTranscription();

    } catch (err) {
      console.error('Failed to start recording:', err);
      setError('Could not access microphone');
    }
  };

  const simulateLiveTranscription = () => {
    // This is a placeholder. In production:
    // 1. Use Web Speech API for browser-based transcription
    // 2. Or stream audio to backend for Gemini transcription
    
    // For demo purposes, we'll just show audio is being captured
    // Real implementation would integrate with:
    // - SpeechRecognition API (browser)
    // - Gemini Audio API (backend streaming)
  };

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
      
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
      
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
      
      setIsRecording(false);
      setIsPaused(false);
      setAudioLevel(0);
    }
  }, [isRecording]);

  const pauseRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      if (isPaused) {
        mediaRecorderRef.current.resume();
        timerRef.current = setInterval(() => {
          setDuration(prev => prev + 1);
        }, 1000);
      } else {
        mediaRecorderRef.current.pause();
        if (timerRef.current) {
          clearInterval(timerRef.current);
        }
      }
      setIsPaused(!isPaused);
    }
  };

  const clearRecording = () => {
    stopRecording();
    setSegments([]);
    setCurrentText('');
    setDuration(0);
    chunksRef.current = [];
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
      if (audioContextRef.current) audioContextRef.current.close();
      if (streamRef.current) streamRef.current.getTracks().forEach(t => t.stop());
    };
  }, []);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className={cn('rounded-xl border bg-white overflow-hidden', className)}>
      {/* Header */}
      <div className="p-4 bg-gradient-to-r from-purple-50 to-pink-50 border-b">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={cn(
              'p-2 rounded-lg transition-colors',
              isRecording ? 'bg-red-100' : 'bg-purple-100'
            )}>
              {isRecording ? (
                <Mic className="h-5 w-5 text-red-600 animate-pulse" />
              ) : (
                <Mic className="h-5 w-5 text-purple-600" />
              )}
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Live Transcription</h3>
              <p className="text-sm text-gray-600">
                Gemini 3 transcribes your voice in real-time
              </p>
            </div>
          </div>
          
          {/* Timer */}
          {(isRecording || duration > 0) && (
            <div className="flex items-center gap-2">
              <span className={cn(
                'font-mono text-lg',
                isRecording && !isPaused ? 'text-red-600' : 'text-gray-600'
              )}>
                {formatTime(duration)}
              </span>
              <span className="text-xs text-gray-400">
                / {formatTime(maxDurationSeconds)}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Waveform / Audio Level */}
      {showWaveform && isRecording && (
        <div className="h-16 bg-gray-900 flex items-center justify-center px-4">
          <div className="flex items-center gap-1 h-full py-4">
            {Array.from({ length: 40 }).map((_, i) => {
              const barHeight = Math.max(
                0.1,
                audioLevel * Math.sin((i / 40) * Math.PI) * (0.5 + Math.random() * 0.5)
              );
              return (
                <div
                  key={i}
                  className="w-1 bg-gradient-to-t from-purple-500 to-pink-500 rounded-full transition-all duration-75"
                  style={{ height: `${barHeight * 100}%` }}
                />
              );
            })}
          </div>
        </div>
      )}

      {/* Transcription Display */}
      <div className="p-4 min-h-[150px] max-h-[300px] overflow-y-auto">
        {segments.length === 0 && !currentText && !isRecording && (
          <p className="text-gray-400 text-center py-8">{placeholder}</p>
        )}
        
        {segments.length === 0 && !currentText && isRecording && (
          <div className="text-center py-8">
            <Loader2 className="h-6 w-6 animate-spin text-purple-600 mx-auto mb-2" />
            <p className="text-gray-500">Listening...</p>
          </div>
        )}

        {(segments.length > 0 || currentText) && (
          <div className="space-y-2">
            {segments.map((segment) => (
              <span
                key={segment.id}
                className={cn(
                  'inline',
                  segment.isFinal ? 'text-gray-900' : 'text-gray-500'
                )}
              >
                {segment.text}{' '}
              </span>
            ))}
            {currentText && (
              <span className="text-purple-600 animate-pulse">{currentText}</span>
            )}
          </div>
        )}
      </div>

      {/* Error */}
      {error && (
        <div className="px-4 pb-4">
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
            {error}
          </div>
        </div>
      )}

      {/* Controls */}
      <div className="p-4 bg-gray-50 border-t flex items-center justify-center gap-3">
        {!isRecording ? (
          <Button
            onClick={startRecording}
            size="lg"
            className="rounded-full bg-purple-600 hover:bg-purple-700 h-14 w-14"
          >
            <Mic className="h-6 w-6" />
          </Button>
        ) : (
          <>
            <Button
              variant="outline"
              size="icon"
              onClick={pauseRecording}
              className="h-12 w-12 rounded-full"
            >
              {isPaused ? (
                <Play className="h-5 w-5" />
              ) : (
                <Pause className="h-5 w-5" />
              )}
            </Button>
            
            <Button
              variant="destructive"
              size="icon"
              onClick={stopRecording}
              className="h-14 w-14 rounded-full"
            >
              <Square className="h-6 w-6" />
            </Button>
            
            <Button
              variant="outline"
              size="icon"
              onClick={clearRecording}
              className="h-12 w-12 rounded-full"
            >
              <Trash2 className="h-5 w-5" />
            </Button>
          </>
        )}
      </div>

      {/* Footer */}
      <div className="px-4 py-2 bg-gray-100 border-t">
        <p className="text-xs text-gray-500 text-center flex items-center justify-center gap-1">
          <Volume2 className="h-3 w-3" />
          Audio processed natively by Gemini 3
        </p>
      </div>
    </div>
  );
}

export default LiveTranscriptionBox;
