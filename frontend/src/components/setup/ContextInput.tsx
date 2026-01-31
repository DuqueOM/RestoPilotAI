'use client'

import { Building2, Mic, MicOff, Sparkles, Target, Users } from 'lucide-react'
import { useCallback, useEffect, useRef, useState } from 'react'

interface BusinessContextInputProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
}

export default function BusinessContextInput({ value, onChange, placeholder }: BusinessContextInputProps) {
  const [isListening, setIsListening] = useState(false)
  const [isSupported, setIsSupported] = useState(false)
  const recognitionRef = useRef<any>(null)

  useEffect(() => {
    // Check for Web Speech API support
    if (typeof window !== 'undefined' && ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window)) {
      setIsSupported(true)
    }
  }, [])

  const startListening = useCallback(() => {
    if (!isSupported) return

    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    recognitionRef.current = new SpeechRecognition()
    
    recognitionRef.current.continuous = true
    recognitionRef.current.interimResults = true
    recognitionRef.current.lang = 'es-ES' // Spanish by default, can be made configurable

    recognitionRef.current.onresult = (event: any) => {
      let transcript = ''
      for (let i = 0; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript
      }
      onChange(value + (value ? ' ' : '') + transcript)
    }

    recognitionRef.current.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error)
      setIsListening(false)
    }

    recognitionRef.current.onend = () => {
      setIsListening(false)
    }

    recognitionRef.current.start()
    setIsListening(true)
  }, [isSupported, onChange, value])

  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop()
      setIsListening(false)
    }
  }, [])

  const suggestions = [
    { icon: Building2, label: 'Tipo de restaurante', example: 'Restaurante mexicano casual, 50 asientos' },
    { icon: Users, label: 'Público objetivo', example: 'Familias, jóvenes profesionales, 25-45 años' },
    { icon: Target, label: 'Diferenciadores', example: 'Ingredientes orgánicos, recetas tradicionales' },
  ]

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 mb-2">
        <Sparkles className="h-5 w-5 text-purple-500" />
        <h3 className="font-semibold text-gray-900">Contexto del Negocio</h3>
        <span className="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded-full">Opcional</span>
      </div>
      
      <p className="text-sm text-gray-600">
        Ayuda a nuestros agentes de IA a entender mejor tu negocio para generar análisis y campañas más personalizadas.
      </p>

      <div className="relative">
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder || "Describe tu restaurante, tipo de cocina, público objetivo, ubicación, competencia cercana, diferenciadores, eventos especiales, horarios pico, etc."}
          className="w-full h-32 p-4 pr-12 border border-gray-300 rounded-xl resize-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all text-sm"
        />
        
        {isSupported && (
          <button
            type="button"
            onClick={isListening ? stopListening : startListening}
            className={`absolute right-3 top-3 p-2 rounded-full transition-all ${
              isListening 
                ? 'bg-red-100 text-red-600 animate-pulse' 
                : 'bg-gray-100 text-gray-600 hover:bg-purple-100 hover:text-purple-600'
            }`}
            title={isListening ? 'Detener grabación' : 'Dictar con voz'}
          >
            {isListening ? <MicOff className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
          </button>
        )}
      </div>

      {isListening && (
        <div className="flex items-center gap-2 text-sm text-red-600">
          <span className="relative flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
          </span>
          Escuchando... Habla sobre tu negocio
        </div>
      )}

      {/* Quick suggestions */}
      <div className="space-y-2">
        <p className="text-xs text-gray-500 font-medium">Sugerencias de información útil:</p>
        <div className="flex flex-wrap gap-2">
          {suggestions.map((suggestion, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => onChange(value + (value ? '\n' : '') + suggestion.example)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs bg-gray-50 hover:bg-purple-50 text-gray-600 hover:text-purple-700 rounded-full border border-gray-200 hover:border-purple-200 transition-all"
            >
              <suggestion.icon className="h-3.5 w-3.5" />
              {suggestion.label}
            </button>
          ))}
        </div>
      </div>

      {/* Character count */}
      <div className="flex justify-between text-xs text-gray-400">
        <span>El contexto ayuda a los agentes a dar recomendaciones más específicas</span>
        <span>{value.length} / 2000</span>
      </div>
    </div>
  )
}
