'use client';

import { GeminiPipelinePanel, PipelineStepDef } from '@/components/common/GeminiPipelinePanel';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import {
    FileText,
    Mic,
    Plus,
    Search,
    Sparkles,
    Square,
    Target,
    Trash2,
    Upload,
    X
} from 'lucide-react';
import { useRef, useState } from 'react';
import { useWizard } from './SetupWizard';

const COMPETITOR_PIPELINE_STEPS: PipelineStepDef[] = [
  { id: 'search', label: 'Nearby Restaurant Search', detail: 'Google Places API within 1 mile radius', gemini: false },
  { id: 'profile', label: 'Profile Enrichment', detail: 'Extracting ratings, reviews, hours, photos', gemini: true, capability: 'Grounding' },
  { id: 'social', label: 'Social Media Discovery', detail: 'Finding Instagram, Facebook, TikTok profiles', gemini: true, capability: 'Grounding' },
  { id: 'menu', label: 'Competitor Menu Analysis', detail: 'Extracting menus and pricing from web sources', gemini: true, capability: 'Vision' },
  { id: 'intelligence', label: 'Competitive Intelligence', detail: 'Generating comparative insights and positioning', gemini: true, capability: 'Thinking' },
];

export function CompetitorsStep() {
  const { formData, updateFormData } = useWizard();
  const [competitors, setCompetitors] = useState<string[]>(
    formData.competitorInput ? formData.competitorInput.split(',').map(s => s.trim()).filter(Boolean) : []
  );
  const [newCompetitor, setNewCompetitor] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const addCompetitor = () => {
    if (newCompetitor.trim() && !competitors.includes(newCompetitor.trim())) {
      const updated = [...competitors, newCompetitor.trim()];
      setCompetitors(updated);
      updateFormData({ competitorInput: updated.join(', ') });
      setNewCompetitor('');
    }
  };

  const removeCompetitor = (index: number) => {
    const updated = competitors.filter((_, i) => i !== index);
    setCompetitors(updated);
    updateFormData({ competitorInput: updated.join(', ') });
  };

  const handleAutoFindChange = (checked: boolean) => {
    updateFormData({ autoFindCompetitors: checked });
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    updateFormData({ competitorFiles: [...formData.competitorFiles, ...files] });
  };

  const removeFile = (index: number) => {
    updateFormData({
      competitorFiles: formData.competitorFiles.filter((_, i) => i !== index),
    });
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
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
        updateFormData({ competitorAudio: [...formData.competitorAudio, blob] });
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

  const removeAudio = (index: number) => {
    updateFormData({
      competitorAudio: formData.competitorAudio.filter((_, i) => i !== index),
    });
  };

  return (
    <div className="space-y-6">
      {/* Auto-Find Toggle */}
      <div className="p-4 bg-gradient-to-r from-purple-50 to-indigo-50 rounded-xl border border-purple-100">
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-3">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Sparkles className="h-5 w-5 text-purple-600" />
            </div>
            <div>
              <Label htmlFor="auto-find" className="text-base font-medium text-gray-900 cursor-pointer">
                Automatically find competitors
              </Label>
              <p className="text-sm text-gray-600 mt-1">
                Gemini 3 + Google Search will find similar restaurants near your location
              </p>
            </div>
          </div>
          <Switch
            id="auto-find"
            checked={formData.autoFindCompetitors}
            onCheckedChange={handleAutoFindChange}
          />
        </div>
        {formData.autoFindCompetitors && (
          <div className="mt-4 p-3 bg-white/60 rounded-lg">
            <p className="text-sm text-purple-800 flex items-center gap-2">
              <Search className="h-4 w-4" />
              Competitors will be searched within a 1 mile radius of your location
            </p>
          </div>
        )}
      </div>

      {/* Manual Competitor Input */}
      <div className="space-y-4">
        <div>
          <Label className="text-base font-medium flex items-center gap-2">
            <Target className="h-5 w-5 text-orange-500" />
            Known Competitors
          </Label>
          <p className="text-sm text-gray-500 mt-1">
            Add restaurants that you consider direct competition
          </p>
        </div>

        {/* Add Competitor Input */}
        <div className="flex gap-2">
          <Input
            value={newCompetitor}
            onChange={(e) => setNewCompetitor(e.target.value)}
            placeholder="Competitor name"
            onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addCompetitor())}
            className="flex-1"
          />
          <Button type="button" onClick={addCompetitor} disabled={!newCompetitor.trim()}>
            <Plus className="h-4 w-4 mr-2" />
            Add
          </Button>
        </div>

        {/* Competitor Tags */}
        {competitors.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {competitors.map((comp, index) => (
              <div
                key={index}
                className="flex items-center gap-2 px-3 py-1.5 bg-orange-50 text-orange-800 rounded-full border border-orange-200"
              >
                <Target className="h-3 w-3" />
                <span className="text-sm font-medium">{comp}</span>
                <button
                  type="button"
                  onClick={() => removeCompetitor(index)}
                  className="p-0.5 hover:bg-orange-200 rounded-full"
                >
                  <X className="h-3 w-3" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* File Upload */}
      <div className="space-y-3">
        <Label className="text-sm text-gray-600">
          Upload competitor menus or info (optional)
        </Label>
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.jpg,.jpeg,.png,.webp"
          multiple
          onChange={handleFileChange}
          className="hidden"
        />
        <Button
          type="button"
          variant="outline"
          onClick={() => fileInputRef.current?.click()}
        >
          <Upload className="h-4 w-4 mr-2" />
          Upload files
        </Button>

        {formData.competitorFiles.length > 0 && (
          <div className="space-y-2">
            {formData.competitorFiles.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-2 bg-gray-50 rounded-lg"
              >
                <div className="flex items-center gap-2">
                  <FileText className="h-4 w-4 text-gray-400" />
                  <span className="text-sm text-gray-700 truncate">{file.name}</span>
                </div>
                <button
                  type="button"
                  onClick={() => removeFile(index)}
                  className="p-1 hover:bg-red-100 rounded text-gray-400 hover:text-red-600"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Audio Recording */}
      <div className="space-y-3">
        <Label className="text-sm text-gray-600">
          Or describe your competitors by voice
        </Label>
        <div className="flex items-center gap-3">
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

        {formData.competitorAudio.length > 0 && (
          <div className="space-y-2">
            {formData.competitorAudio.map((blob, index) => (
              <div key={index} className="flex items-center gap-2 p-2 bg-gray-50 rounded">
                <Mic className="h-4 w-4 text-purple-600" />
                <audio controls src={URL.createObjectURL(blob)} className="h-8 flex-1" />
                <button
                  type="button"
                  onClick={() => removeAudio(index)}
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

      {/* Gemini 3 Pipeline Preview */}
      {(formData.autoFindCompetitors || competitors.length > 0 || formData.competitorFiles.length > 0) && (
        <GeminiPipelinePanel
          title="Gemini 3 Competitive Intelligence Pipeline"
          steps={COMPETITOR_PIPELINE_STEPS}
          isRunning={false}
          isComplete={false}
          completeSummary="Pipeline will run during full analysis"
          defaultExpanded={true}
        />
      )}

      {/* Info Card */}
      <div className="p-4 bg-blue-50 rounded-lg border border-blue-100">
        <h4 className="font-medium text-blue-900 mb-2">
          🔍 Competitive Analysis with Grounding
        </h4>
        <p className="text-sm text-blue-800">
          Gemini 3 will use <strong>Google Search Grounding</strong> to get 
          up-to-date information about your competitors: menus, prices, reviews 
          and social media presence. The pipeline above will run when you start the full analysis.
        </p>
      </div>
    </div>
  );
}

export default CompetitorsStep;
