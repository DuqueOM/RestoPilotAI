'use client';

import { CheckCircle2, ChevronDown, ChevronRight, Loader2 } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';

export interface PipelineStepDef {
  id: string;
  label: string;
  detail: string;
  gemini?: boolean;
  capability?: string; // e.g., 'Vision', 'Grounding', 'Thinking', 'Image Gen'
}

export interface GeminiPipelinePanelProps {
  title: string;
  steps: PipelineStepDef[];
  isRunning: boolean;
  isComplete: boolean;
  isFailed?: boolean;
  completeSummary?: string;
  failedSummary?: string;
  stepIntervalMs?: number; // Time per step animation, default 4000
  defaultExpanded?: boolean;
}

export function GeminiPipelinePanel({
  title,
  steps,
  isRunning,
  isComplete,
  isFailed = false,
  completeSummary,
  failedSummary,
  stepIntervalMs = 4000,
  defaultExpanded = true,
}: GeminiPipelinePanelProps) {
  const [showPipeline, setShowPipeline] = useState(defaultExpanded);
  const [activeStep, setActiveStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState<Set<number>>(new Set());
  const stepTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Animate pipeline steps while running
  useEffect(() => {
    if (isRunning) {
      setActiveStep(0);
      setCompletedSteps(new Set());
      let step = 0;
      stepTimerRef.current = setInterval(() => {
        step++;
        if (step < steps.length) {
          setCompletedSteps(prev => new Set([...prev, step - 1]));
          setActiveStep(step);
        } else if (step === steps.length) {
          setCompletedSteps(prev => new Set([...prev, step - 1]));
        }
      }, stepIntervalMs);
    } else {
      if (stepTimerRef.current) clearInterval(stepTimerRef.current);
      if (isComplete || isFailed) {
        setCompletedSteps(new Set(steps.map((_, i) => i)));
        setActiveStep(steps.length);
      }
    }
    return () => { if (stepTimerRef.current) clearInterval(stepTimerRef.current); };
  }, [isRunning, isComplete, isFailed, steps.length, stepIntervalMs]);

  // Don't render if nothing has started
  if (!isRunning && !isComplete && !isFailed) return null;

  return (
    <div className={`rounded-lg border overflow-hidden ${
      isRunning ? 'border-purple-200' : isComplete ? 'border-green-200' : 'border-amber-200'
    }`}>
      {/* Header */}
      <button
        onClick={() => setShowPipeline(!showPipeline)}
        className={`w-full flex items-center justify-between px-4 py-3 text-left transition-colors ${
          isRunning ? 'bg-purple-50' : isComplete ? 'bg-green-50' : 'bg-amber-50'
        }`}
      >
        <div className="flex items-center gap-2">
          {isRunning ? (
            <Loader2 className="h-4 w-4 text-purple-600 animate-spin" />
          ) : isComplete ? (
            <CheckCircle2 className="h-4 w-4 text-green-600" />
          ) : (
            <CheckCircle2 className="h-4 w-4 text-amber-500" />
          )}
          <span className={`text-sm font-medium ${
            isRunning ? 'text-purple-700' : isComplete ? 'text-green-700' : 'text-amber-700'
          }`}>
            {isRunning
              ? `${title} — Step ${Math.min(activeStep + 1, steps.length)}/${steps.length}`
              : isComplete
              ? (completeSummary || `${title} — Complete`)
              : (failedSummary || `${title} — Completed with limited data`)
            }
          </span>
        </div>
        {showPipeline ? <ChevronDown className="h-4 w-4 text-gray-500" /> : <ChevronRight className="h-4 w-4 text-gray-500" />}
      </button>

      {/* Expandable Pipeline Steps */}
      {showPipeline && (
        <div className="px-4 py-3 bg-white border-t border-gray-100 text-sm space-y-1.5 max-h-80 overflow-y-auto">
          <div className="text-xs text-gray-400 mb-2 font-medium uppercase tracking-wide">
            Gemini 3 Agentic Pipeline
          </div>
          {steps.map((step, i) => {
            const isDone = completedSteps.has(i);
            const isActive = activeStep === i && isRunning;

            return (
              <div key={step.id} className={`flex items-start gap-2.5 py-1.5 px-2 rounded-md transition-all duration-500 ${
                isActive ? 'bg-purple-50 ring-1 ring-purple-200' :
                isDone ? 'bg-green-50/50' : 'bg-gray-50/50'
              }`}>
                <div className="mt-0.5 flex-shrink-0">
                  {isDone ? (
                    <CheckCircle2 className="h-4 w-4 text-green-500" />
                  ) : isActive ? (
                    <Loader2 className="h-4 w-4 text-purple-500 animate-spin" />
                  ) : (
                    <div className="h-4 w-4 rounded-full border-2 border-gray-300" />
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-1.5">
                    <span className={`font-medium ${
                      isDone ? 'text-green-700' : isActive ? 'text-purple-700' : 'text-gray-400'
                    }`}>
                      {step.label}
                    </span>
                    {step.gemini && (
                      <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-sans font-medium ${
                        isDone ? 'bg-blue-100 text-blue-700' : isActive ? 'bg-purple-100 text-purple-700' : 'bg-gray-100 text-gray-400'
                      }`}>
                        Gemini 3
                      </span>
                    )}
                    {step.capability && (
                      <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-sans font-medium ${
                        isDone ? 'bg-indigo-100 text-indigo-700' : isActive ? 'bg-purple-100 text-purple-600' : 'bg-gray-100 text-gray-400'
                      }`}>
                        {step.capability}
                      </span>
                    )}
                  </div>
                  {(isActive || isDone) && (
                    <div className={`text-xs mt-0.5 ${
                      isDone ? 'text-green-600' : 'text-purple-500'
                    }`}>
                      {isDone ? '✓ ' : '→ '}{step.detail}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
          {(isComplete || isFailed) && (
            <div className={`mt-2 pt-2 border-t text-xs ${
              isComplete ? 'border-green-100 text-green-600' : 'border-amber-100 text-amber-600'
            }`}>
              {isComplete
                ? (completeSummary || 'Pipeline complete')
                : (failedSummary || 'Pipeline finished with partial results')
              }
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ============================================================================
// Pre-defined step configurations for each analysis type
// ============================================================================

export const ENRICHMENT_PIPELINE_STEPS: PipelineStepDef[] = [
  { id: 'place_details', label: 'Google Places API', detail: 'Fetching business details, photos, reviews...', gemini: false },
  { id: 'web_search', label: 'Gemini Search Grounding', detail: 'Searching the web for social media, delivery platforms...', gemini: true, capability: 'Grounding' },
  { id: 'social_media', label: 'Social Media Discovery', detail: 'Identifying & validating Facebook, Instagram, TikTok profiles...', gemini: true },
  { id: 'whatsapp', label: 'WhatsApp Business Detection', detail: 'Checking for WhatsApp Business catalog...', gemini: false },
  { id: 'photos', label: 'Gemini Vision Analysis', detail: 'Analyzing business photos with multimodal AI...', gemini: true, capability: 'Vision' },
  { id: 'menu', label: 'Menu Extraction', detail: 'Extracting menu items from all discovered sources...', gemini: true, capability: 'Document AI' },
  { id: 'reviews', label: 'Review Sentiment Analysis', detail: 'Analyzing customer reviews with Gemini...', gemini: true, capability: 'Thinking' },
  { id: 'consolidation', label: 'Intelligence Consolidation', detail: 'Fusing all data sources into a unified profile...', gemini: true },
];

export const BCG_PIPELINE_STEPS: PipelineStepDef[] = [
  { id: 'data_load', label: 'Data Ingestion', detail: 'Loading menu items and sales records...', gemini: false },
  { id: 'popularity_calc', label: 'Popularity Analysis', detail: 'Calculating sales volume and order frequency...', gemini: false },
  { id: 'profitability_calc', label: 'Profitability Analysis', detail: 'Computing contribution margins and cost ratios...', gemini: false },
  { id: 'bcg_classify', label: 'BCG Classification', detail: 'Classifying items: Stars, Plowhorses, Puzzles, Dogs...', gemini: true, capability: 'Thinking' },
  { id: 'recommendations', label: 'Strategic Recommendations', detail: 'Generating pricing and promotion strategies per category...', gemini: true, capability: 'Thinking' },
  { id: 'vibe_verify', label: 'Vibe Engineering Verification', detail: 'Auto-verifying analysis quality and consistency...', gemini: true, capability: 'Vibe Check' },
];

export const COMPETITOR_PIPELINE_STEPS: PipelineStepDef[] = [
  { id: 'discovery', label: 'Competitor Discovery', detail: 'Finding nearby restaurants via Google Places...', gemini: false },
  { id: 'enrich', label: 'Profile Enrichment', detail: 'Enriching competitor profiles with web data...', gemini: true, capability: 'Grounding' },
  { id: 'menu_extract', label: 'Menu Extraction', detail: 'Extracting competitor menus from web sources...', gemini: true, capability: 'Vision' },
  { id: 'price_compare', label: 'Price Comparison', detail: 'Comparing prices across competitor menus...', gemini: true, capability: 'Thinking' },
  { id: 'positioning', label: 'Market Positioning', detail: 'Analyzing competitive advantages and gaps...', gemini: true, capability: 'Thinking' },
  { id: 'debate', label: 'Multi-Agent Debate', detail: 'AI agents debating competitive strategy...', gemini: true, capability: 'Multi-Agent' },
];

export const SENTIMENT_PIPELINE_STEPS: PipelineStepDef[] = [
  { id: 'reviews_collect', label: 'Review Collection', detail: 'Gathering Google Maps reviews and ratings...', gemini: false },
  { id: 'social_scan', label: 'Social Media Scan', detail: 'Analyzing Instagram & Facebook presence...', gemini: true, capability: 'Grounding' },
  { id: 'nlp_analysis', label: 'Sentiment NLP', detail: 'Analyzing review text for sentiment and themes...', gemini: true, capability: 'Thinking' },
  { id: 'topic_extract', label: 'Topic Extraction', detail: 'Identifying recurring themes: food, service, ambiance...', gemini: true },
  { id: 'competitor_compare', label: 'Competitor Sentiment', detail: 'Comparing sentiment vs. nearby competitors...', gemini: true },
  { id: 'insights', label: 'Actionable Insights', detail: 'Generating improvement recommendations...', gemini: true, capability: 'Thinking' },
];

export const CAMPAIGN_PIPELINE_STEPS: PipelineStepDef[] = [
  { id: 'context_gather', label: 'Context Gathering', detail: 'Collecting BCG data, sentiment, and competitor insights...', gemini: false },
  { id: 'strategy', label: 'Campaign Strategy', detail: 'Planning campaign objectives and target audience...', gemini: true, capability: 'Thinking' },
  { id: 'copy_gen', label: 'Copy Generation', detail: 'Writing marketing copy for social media and print...', gemini: true, capability: 'Creative' },
  { id: 'image_gen', label: 'Image Generation', detail: 'Creating campaign visuals with Imagen 3...', gemini: true, capability: 'Image Gen' },
  { id: 'ab_test', label: 'A/B Variant Creation', detail: 'Generating alternative versions for testing...', gemini: true },
  { id: 'grounding', label: 'Market Validation', detail: 'Verifying campaign claims with Google Search...', gemini: true, capability: 'Grounding' },
];

export const MARATHON_PIPELINE_STEPS: PipelineStepDef[] = [
  { id: 'init', label: 'Pipeline Initialization', detail: 'Creating session and loading business context...', gemini: false },
  { id: 'menu_ingest', label: 'Menu Processing', detail: 'OCR + Vision analysis of menu images...', gemini: true, capability: 'Vision' },
  { id: 'sales_ingest', label: 'Sales Data Processing', detail: 'Parsing and validating sales records...', gemini: false },
  { id: 'audio_process', label: 'Audio Understanding', detail: 'Transcribing and analyzing voice inputs...', gemini: true, capability: 'Audio' },
  { id: 'video_process', label: 'Video Analysis', detail: 'Analyzing restaurant video content...', gemini: true, capability: 'Video' },
  { id: 'bcg_analysis', label: 'BCG Classification', detail: 'Running menu engineering matrix analysis...', gemini: true, capability: 'Thinking' },
  { id: 'competitor_discovery', label: 'Competitor Discovery', detail: 'Finding and enriching nearby competitors...', gemini: true, capability: 'Grounding' },
  { id: 'competitor_analysis', label: 'Competitive Analysis', detail: 'Deep comparison with competitor offerings...', gemini: true, capability: 'Thinking' },
  { id: 'sentiment', label: 'Sentiment Analysis', detail: 'Analyzing reviews and social media signals...', gemini: true, capability: 'Grounding' },
  { id: 'social_media_sentiment', label: 'Social Media Intelligence', detail: 'Deep analysis of social presence and engagement...', gemini: true, capability: 'Grounding' },
  { id: 'campaigns', label: 'Campaign Generation', detail: 'Creating AI-powered marketing campaigns...', gemini: true, capability: 'Image Gen' },
  { id: 'vibe_check', label: 'Vibe Engineering QA', detail: 'Self-verifying all results for quality...', gemini: true, capability: 'Vibe Check' },
  { id: 'debate', label: 'Multi-Agent Debate', detail: 'Cross-validating findings via agent debate...', gemini: true, capability: 'Multi-Agent' },
  { id: 'final', label: 'Report Consolidation', detail: 'Assembling final analysis report with citations...', gemini: true },
];

export const MENU_UPLOAD_STEPS: PipelineStepDef[] = [
  { id: 'upload', label: 'File Upload', detail: 'Uploading menu images to server...', gemini: false },
  { id: 'ocr', label: 'OCR Processing', detail: 'Extracting text from menu images...', gemini: true, capability: 'Vision' },
  { id: 'structure', label: 'Menu Structuring', detail: 'Identifying categories, items, prices, descriptions...', gemini: true, capability: 'Document AI' },
  { id: 'validation', label: 'Data Validation', detail: 'Cross-checking extracted items for accuracy...', gemini: true, capability: 'Thinking' },
];

export const SALES_UPLOAD_STEPS: PipelineStepDef[] = [
  { id: 'upload', label: 'File Upload', detail: 'Uploading sales data spreadsheet...', gemini: false },
  { id: 'parse', label: 'Data Parsing', detail: 'Parsing rows, columns, and date formats...', gemini: false },
  { id: 'match', label: 'Menu Matching', detail: 'Matching sales records to menu items...', gemini: true, capability: 'Thinking' },
  { id: 'stats', label: 'Statistics Computation', detail: 'Computing daily/weekly sales metrics...', gemini: false },
];
