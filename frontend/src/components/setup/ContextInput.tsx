'use client';

import { FileText, Mic, Pause, Play, Square, Trash2 } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { toast } from 'sonner';

interface ContextInputProps {
  label: string;
  placeholder: string;
  value: string;
  onChange: (value: string) => void;
  allowAudio?: boolean;
  onAudioChange?: (audios: Blob[]) => void;
  template?: string; // Short tip
  detailedTemplate?: string; // Full text to fill
}

export function ContextInput({
  label,
  placeholder,
  value,
  onChange,
  allowAudio = false,
  onAudioChange,
  template,
  detailedTemplate
}: ContextInputProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [audioList, setAudioList] = useState<{ blob: Blob; url: string; id: string }[]>([]);
  const [playingId, setPlayingId] = useState<string | null>(null);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const audioRefs = useRef<{ [key: string]: HTMLAudioElement }>({});

  useEffect(() => {
    // Cleanup URLs on unmount
    return () => {
      audioList.forEach(a => URL.revokeObjectURL(a.url));
    };
  }, [audioList]);

  const startRecording = async () => {
    if (!allowAudio || !onAudioChange) return;

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        const url = URL.createObjectURL(blob);
        const newAudio = { blob, url, id: Date.now().toString() };
        
        const newList = [...audioList, newAudio];
        setAudioList(newList);
        if (onAudioChange) onAudioChange(newList.map(a => a.blob));
        
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      console.error('Error accessing microphone:', err);
      toast.error('Could not access microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const deleteAudio = (id: string) => {
    const newList = audioList.filter(a => a.id !== id);
    setAudioList(newList);
    if (onAudioChange) onAudioChange(newList.map(a => a.blob));
  };

  const togglePlayback = (id: string) => {
    const audio = audioRefs.current[id];
    if (!audio) return;

    if (playingId === id) {
      audio.pause();
      setPlayingId(null);
    } else {
      // Stop others
      if (playingId && audioRefs.current[playingId]) {
        audioRefs.current[playingId].pause();
      }
      audio.play();
      setPlayingId(id);
      audio.onended = () => setPlayingId(null);
    }
  };

  const handleUseTemplate = () => {
    if (detailedTemplate) {
      onChange(detailedTemplate);
    } else if (template) {
      // Fallback if detailed not provided but template tip is
      onChange(`Here is my context based on the tip: ${template}\n\n[Please expand...]`);
    }
  };

  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center">
        <label className="text-sm font-medium text-gray-700">
          {label}
        </label>
        {detailedTemplate && !value && (
          <button
            onClick={handleUseTemplate}
            className="text-xs text-blue-600 hover:text-blue-800 flex items-center gap-1 transition-colors"
          >
            <FileText className="w-3 h-3" />
            Use Template
          </button>
        )}
      </div>
      
      <div className="relative">
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          className="w-full h-32 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none bg-white"
        />
        
        {allowAudio && (
          <div className="absolute bottom-3 right-3 flex gap-2">
            <button
              onClick={isRecording ? stopRecording : startRecording}
              className={`p-2 rounded-full transition-all shadow-md ${
                isRecording 
                  ? 'bg-red-500 text-white animate-pulse ring-4 ring-red-200' 
                  : 'bg-white text-gray-500 border border-gray-200 hover:bg-gray-50 hover:text-blue-600'
              }`}
              title={isRecording ? "Stop Recording" : "Record Audio Context"}
            >
              {isRecording ? <Square className="w-4 h-4 fill-current" /> : <Mic className="w-5 h-5" />}
            </button>
          </div>
        )}
      </div>

      {/* Audio List */}
      {audioList.length > 0 && (
        <div className="flex flex-wrap gap-2 mt-2">
          {audioList.map((audio, idx) => (
            <div key={audio.id} className="flex items-center gap-2 bg-blue-50 px-3 py-1.5 rounded-full border border-blue-100">
              <button 
                onClick={() => togglePlayback(audio.id)}
                className="text-blue-600 hover:text-blue-800"
              >
                {playingId === audio.id ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
              </button>
              <span className="text-xs text-blue-700 font-medium">Recording {idx + 1}</span>
              <button 
                onClick={() => deleteAudio(audio.id)}
                className="text-red-400 hover:text-red-600 ml-1"
              >
                <Trash2 className="w-3 h-3" />
              </button>
              <audio 
                ref={el => { if(el) audioRefs.current[audio.id] = el }} 
                src={audio.url} 
                className="hidden" 
              />
            </div>
          ))}
        </div>
      )}

      {template && (
        <p className="text-xs text-gray-500 flex items-start gap-1">
          <span className="font-semibold">Tip:</span> {template}
        </p>
      )}
    </div>
  );
}
