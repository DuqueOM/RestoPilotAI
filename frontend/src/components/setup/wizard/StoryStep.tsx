'use client';

import { GeminiPipelinePanel, PipelineStepDef } from '@/components/common/GeminiPipelinePanel';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { cn } from '@/lib/utils';
import { Mic, Sparkles, Square, Trash2, Wand2 } from 'lucide-react';
import { useRef, useState } from 'react';
import { useWizard } from './SetupWizard';

const STORY_PIPELINE_STEPS: PipelineStepDef[] = [
  { id: 'audio', label: 'Voice Note Processing', detail: 'Gemini 3 native audio transcription and sentiment extraction', gemini: true, capability: 'Audio' },
  { id: 'context', label: 'Business Context Analysis', detail: 'Extracting brand identity, values, and positioning', gemini: true, capability: 'Thinking' },
  { id: 'audience', label: 'Target Audience Profiling', detail: 'Building customer personas from your descriptions', gemini: true, capability: 'Thinking' },
  { id: 'challenges', label: 'Challenge & Goal Mapping', detail: 'Identifying actionable insights from your challenges and goals', gemini: true, capability: 'Thinking' },
  { id: 'strategy', label: 'Strategic Recommendations', detail: 'Generating personalized strategies based on your story', gemini: true, capability: 'Grounding' },
];

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
  const [isGenerating, setIsGenerating] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const startRecording = async () => {
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
        onAudioChange([...audioBlobs, blob]);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      console.error('Failed to start recording:', err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
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
        </div>
      </div>

      <Textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="min-h-[100px] resize-y bg-white focus:border-purple-400 focus:ring-purple-400"
      />

      {/* Voice recording — simple style matching Competitors */}
      <div className="flex items-center gap-3">
        <Label className="text-sm text-gray-600">Or describe by voice</Label>
        {isRecording ? (
          <Button type="button" variant="destructive" size="sm" onClick={stopRecording}>
            <Square className="h-4 w-4 mr-2" />
            Stop
          </Button>
        ) : (
          <Button type="button" variant="outline" size="sm" onClick={startRecording}>
            <Mic className="h-4 w-4 mr-2" />
            Record
          </Button>
        )}
        {isRecording && (
          <span className="flex items-center gap-2 text-red-600 text-sm animate-pulse">
            <span className="h-2 w-2 bg-red-600 rounded-full" />
            Recording...
          </span>
        )}
      </div>

      {/* Audio recordings list with Delete */}
      {audioBlobs.length > 0 && (
        <div className="space-y-2">
          {audioBlobs.map((blob, i) => (
            <div key={i} className="flex items-center gap-2 p-2 bg-gray-50 rounded">
              <Mic className="h-4 w-4 text-purple-600 flex-shrink-0" />
              <audio controls src={URL.createObjectURL(blob)} className="h-8 flex-1" />
              <button
                type="button"
                onClick={() => onAudioChange(audioBlobs.filter((_, idx) => idx !== i))}
                className="p-1 hover:bg-red-100 rounded text-gray-400 hover:text-red-600"
                title="Delete recording"
              >
                <Trash2 className="h-4 w-4" />
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
          <strong>Multimodal Tip:</strong> Write or record your story. Gemini 3 will transcribe voice notes and analyze all inputs during the full analysis pipeline.
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

      {/* Gemini 3 Pipeline Preview */}
      {(formData.historyContext || formData.valuesContext || formData.targetAudienceContext || formData.challengesContext || formData.goalsContext ||
        formData.historyAudio.length > 0 || formData.valuesAudio.length > 0 || formData.targetAudienceAudio.length > 0 || formData.challengesAudio.length > 0 || formData.goalsAudio.length > 0) && (
        <GeminiPipelinePanel
          title="Gemini 3 Story Intelligence Pipeline"
          steps={STORY_PIPELINE_STEPS}
          isRunning={false}
          isComplete={false}
          completeSummary="Pipeline will run during full analysis"
          defaultExpanded={true}
        />
      )}
    </div>
  );
}

export default StoryStep;
