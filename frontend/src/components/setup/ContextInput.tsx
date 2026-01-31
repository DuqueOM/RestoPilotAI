'use client'

import { Mic, MicOff, Sparkles, Wand2 } from 'lucide-react';
import { useCallback, useEffect, useRef, useState } from 'react';

interface ContextInputProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  template?: string;
  allowAudio?: boolean;
  onAudioChange?: (audio: Blob | null) => void;
}

export function ContextInput({ 
  label, 
  value, 
  onChange, 
  placeholder,
  template,
  allowAudio = false,
  onAudioChange
}: ContextInputProps) {
  const [isListening, setIsListening] = useState(false)
  const [isSupported, setIsSupported] = useState(false)
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null)
  const recognitionRef = useRef<any>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])

  useEffect(() => {
    if (typeof window !== 'undefined') {
      if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
        setIsSupported(true)
      }
    }
  }, [])

  const startListening = useCallback(async () => {
    // 1. Start Speech Recognition for text
    if (isSupported) {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
      recognitionRef.current = new SpeechRecognition()
      recognitionRef.current.continuous = true
      recognitionRef.current.interimResults = true
      recognitionRef.current.lang = 'es-ES' // Could be dynamic

      recognitionRef.current.onresult = (event: any) => {
        let transcript = ''
        for (let i = 0; i < event.results.length; i++) {
          transcript += event.results[i][0].transcript
        }
        // Append to existing value or replace? Usually append in these UIs
        // For now, let's just use the current session's transcript + existing value logic if needed
        // But here we might just want to append to what was there before the recording started.
        // Simplified: just update the text area.
        const currentText = value ? value + ' ' : ''
        if (event.results[0].isFinal) {
             onChange(currentText + transcript)
        }
      }
      
      recognitionRef.current.start()
    }

    // 2. Start Media Recorder for audio blob if requested
    if (allowAudio && onAudioChange) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
        const mediaRecorder = new MediaRecorder(stream)
        mediaRecorderRef.current = mediaRecorder
        chunksRef.current = []

        mediaRecorder.ondataavailable = (e) => {
          if (e.data.size > 0) chunksRef.current.push(e.data)
        }

        mediaRecorder.onstop = () => {
          const blob = new Blob(chunksRef.current, { type: 'audio/webm' })
          setAudioBlob(blob)
          onAudioChange(blob)
          stream.getTracks().forEach(track => track.stop())
        }

        mediaRecorder.start()
      } catch (err) {
        console.error('Microphone access denied', err)
      }
    }

    setIsListening(true)
  }, [isSupported, allowAudio, onAudioChange, value, onChange])

  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop()
    }
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop()
    }
    setIsListening(false)
  }, [])

  const applyTemplate = () => {
    if (template && !value) {
      onChange(template)
    }
  }

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label className="block text-sm font-medium text-gray-700">
          {label}
        </label>
        {template && !value && (
          <button 
            onClick={applyTemplate}
            className="text-xs flex items-center gap-1 text-purple-600 hover:text-purple-700"
          >
            <Wand2 className="w-3 h-3" />
            Use template
          </button>
        )}
      </div>

      <div className="relative">
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          className="w-full h-24 p-3 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none text-sm"
        />
        
        {(isSupported || allowAudio) && (
          <button
            type="button"
            onClick={isListening ? stopListening : startListening}
            className={`absolute right-2 top-2 p-2 rounded-full transition-all ${
              isListening 
                ? 'bg-red-100 text-red-600 animate-pulse' 
                : 'bg-gray-100 text-gray-600 hover:bg-blue-50 hover:text-blue-600'
            }`}
            title={isListening ? 'Stop recording' : 'Record voice input'}
          >
            {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
          </button>
        )}
      </div>
      
      {template && (
        <p className="text-xs text-gray-500 italic">
          Tip: {template}
        </p>
      )}
      
      {audioBlob && allowAudio && (
        <div className="flex items-center gap-2 text-xs text-green-600 bg-green-50 px-2 py-1 rounded w-fit">
          <Sparkles className="w-3 h-3" />
          Audio recording attached
          <button 
            onClick={() => {
              setAudioBlob(null)
              if (onAudioChange) onAudioChange(null)
            }}
            className="ml-2 text-gray-400 hover:text-red-500"
          >
            ×
          </button>
        </div>
      )}
    </div>
  )
}
