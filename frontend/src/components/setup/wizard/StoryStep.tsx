'use client';

import { LiveTranscriptionBox } from '@/components/multimodal/LiveTranscriptionBox';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { cn } from '@/lib/utils';
import { Mic, Sparkles, Wand2 } from 'lucide-react';
import { useState } from 'react';
import { useWizard } from './SetupWizard';

interface ContextSectionProps {
  title: string;
  description: string;
  value: string;
  onChange: (value: string) => void;
  audioBlobs: Blob[];
  onAudioChange: (blobs: Blob[]) => void;
  placeholder: string;
  templatePrompt?: string;
}

function ContextSection({
  title,
  description,
  value,
  onChange,
  audioBlobs,
  onAudioChange,
  placeholder,
  templatePrompt,
}: ContextSectionProps) {
  const [showAudio, setShowAudio] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);

  const handleTranscription = (text: string) => {
    // Append transcribed text to current value
    const newValue = value ? `${value}\n\n[Transcription]: ${text}` : text;
    onChange(newValue);
    setShowAudio(false);
  };

  const handleAudioBlob = (blob: Blob) => {
    onAudioChange([...audioBlobs, blob]);
  };

  return (
    <div className="space-y-3 p-4 bg-gray-50/50 rounded-xl border border-gray-100 hover:border-purple-200 transition-colors">
      <div className="flex justify-between items-start">
        <div className="space-y-1">
          <Label className="text-base font-medium text-gray-900">{title}</Label>
          <p className="text-sm text-gray-500">{description}</p>
        </div>
        <div className="flex gap-2">
          {templatePrompt && (
            <Button
              variant="ghost"
              size="sm"
              className="text-purple-600 hover:text-purple-700 hover:bg-purple-50"
              onClick={() => {
                setIsGenerating(true);
                // Simulate AI generation
                setTimeout(() => {
                  onChange(value + (value ? '\n\n' : '') + templatePrompt);
                  setIsGenerating(false);
                }, 800);
              }}
              disabled={isGenerating}
            >
              <Wand2 className={cn("h-4 w-4 mr-1", isGenerating && "animate-spin")} />
              {isGenerating ? 'Generating...' : 'AI Ideas'}
            </Button>
          )}
          <Button
            variant={showAudio ? "secondary" : "outline"}
            size="sm"
            onClick={() => setShowAudio(!showAudio)}
            className={cn(showAudio && "bg-purple-100 text-purple-700 border-purple-200")}
          >
            <Mic className="h-4 w-4 mr-1" />
            {showAudio ? 'Close Voice' : 'Use Voice'}
          </Button>
        </div>
      </div>

      {showAudio ? (
        <div className="animate-in fade-in slide-in-from-top-2">
          <LiveTranscriptionBox
            onTranscriptionComplete={(text, segments) => handleTranscription(text)}
            onAudioBlob={handleAudioBlob}
            placeholder="Describe your story by speaking..."
            className="border-purple-200 shadow-sm"
          />
        </div>
      ) : (
        <Textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          className="min-h-[120px] resize-y bg-white focus:border-purple-400 focus:ring-purple-400"
        />
      )}
      
      {audioBlobs.length > 0 && (
        <div className="flex gap-2 flex-wrap">
          {audioBlobs.map((_, i) => (
            <div key={i} className="flex items-center gap-1 px-2 py-1 bg-purple-50 text-purple-700 rounded-md text-xs font-medium border border-purple-100">
              <Mic className="h-3 w-3" />
              Voice Note {i + 1}
              <button 
                onClick={() => onAudioChange(audioBlobs.filter((_, idx) => idx !== i))}
                className="ml-1 hover:text-purple-900"
              >
                ×
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export function StoryStep() {
  const { formData, updateFormData } = useWizard();

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2 mb-6 p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg border border-purple-100">
        <Sparkles className="h-5 w-5 text-purple-600" />
        <p className="text-sm text-purple-900">
          <strong>Multimodal Tip:</strong> You can write your story or simply press "Use Voice" and tell it naturally. Gemini 3 will transcribe and understand the emotional nuances.
        </p>
      </div>

      <div className="space-y-6">
        <ContextSection
          title="History & Origin"
          description="How did it all start? What is the story behind your recipes?"
          value={formData.historyContext}
          onChange={(val) => updateFormData({ historyContext: val })}
          audioBlobs={formData.historyAudio}
          onAudioChange={(blobs) => updateFormData({ historyAudio: blobs })}
          placeholder="Ex: Founded in 1985 by my grandmother, bringing authentic recipes from Oaxaca..."
          templatePrompt="Our story began when..."
        />

        <ContextSection
          title="Values & Mission"
          description="What do you stand for? Sustainability? Community? Quality?"
          value={formData.valuesContext}
          onChange={(val) => updateFormData({ valuesContext: val })}
          audioBlobs={formData.valuesAudio}
          onAudioChange={(blobs) => updateFormData({ valuesAudio: blobs })}
          placeholder="Ex: We believe in 'Farm to Table' ingredients and supporting local producers..."
          templatePrompt="Our core values are..."
        />

        <ContextSection
          title="Target Audience"
          description="Who are your ideal customers? Who do you want to attract?"
          value={formData.targetAudienceContext}
          onChange={(val) => updateFormData({ targetAudienceContext: val })}
          audioBlobs={formData.targetAudienceAudio}
          onAudioChange={(blobs) => updateFormData({ targetAudienceAudio: blobs })}
          placeholder="Ex: Young professionals (25-35) looking for healthy, quick options..."
          templatePrompt="Our ideal customer is..."
        />
        
        <ContextSection
          title="Current Challenges"
          description="What problems are you facing? Low traffic? Staffing? Competition?"
          value={formData.challengesContext}
          onChange={(val) => updateFormData({ challengesContext: val })}
          audioBlobs={formData.challengesAudio}
          onAudioChange={(blobs) => updateFormData({ challengesAudio: blobs })}
          placeholder="Ex: We struggle to attract people during dinner on weekdays..."
          templatePrompt="Our biggest challenge currently is..."
        />
        
        <ContextSection
          title="Future Goals"
          description="Where do you see the business in 1-2 years?"
          value={formData.goalsContext}
          onChange={(val) => updateFormData({ goalsContext: val })}
          audioBlobs={formData.goalsAudio}
          onAudioChange={(blobs) => updateFormData({ goalsAudio: blobs })}
          placeholder="Ex: We want to open a second location downtown..."
          templatePrompt="Our main goal is..."
        />
      </div>
    </div>
  );
}

export default StoryStep;
