'use client';

import { GeminiCapabilityBadge } from '@/components/ai/GeminiCapabilityBadge';
import { GeminiPipelinePanel, MARATHON_PIPELINE_STEPS } from '@/components/common/GeminiPipelinePanel';
import { LiveTranscriptionBox } from '@/components/multimodal/LiveTranscriptionBox';
import { VideoAnalysisZone } from '@/components/multimodal/VideoAnalysisZone';
import {
    Brain,
    Camera,
    Eye,
    FileText,
    Image,
    Mic,
    Search,
    Shield,
    Sparkles,
    Video,
    Wand2,
    Zap,
} from 'lucide-react';
import { useParams } from 'next/navigation';
import { useState } from 'react';
import { useSessionData } from '../layout';

export default function IntelligencePage() {
  const params = useParams();
  const sessionId = params.sessionId as string;
  const { sessionData, isLoading } = useSessionData();
  const [activeDemo, setActiveDemo] = useState<'video' | 'audio'>('video');

  const unwrapped = (sessionData as any)?.data || sessionData;
  const restaurantName = unwrapped?.restaurant_info?.name || unwrapped?.restaurant_name || 'Restaurant';
  const menuItemCount = unwrapped?.menu?.items?.length || unwrapped?.menu_items?.length || 0;
  const hasCompetitors = !!(unwrapped?.competitor_analysis?.competitors?.length || unwrapped?.enriched_competitors?.length);
  const hasSentiment = !!unwrapped?.sentiment_analysis;
  const hasBCG = !!(unwrapped?.bcg_analysis?.items?.length || unwrapped?.bcg?.items?.length);
  const hasCampaigns = !!(Array.isArray(unwrapped?.campaigns) ? unwrapped.campaigns.length : unwrapped?.campaigns?.campaigns?.length);
  const hasSocialMedia = !!unwrapped?.sentiment_analysis?.social_media_analysis;

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse space-y-6">
          <div className="h-24 bg-gray-200 rounded-xl"></div>
          <div className="grid md:grid-cols-2 gap-4">
            {[1, 2, 3, 4].map(i => <div key={i} className="h-48 bg-gray-100 rounded-xl"></div>)}
          </div>
        </div>
        <GeminiPipelinePanel
          title="Marathon Agent Pipeline"
          steps={MARATHON_PIPELINE_STEPS}
          isRunning={true}
          isComplete={false}
          stepIntervalMs={3000}
        />
      </div>
    );
  }

  const capabilities = [
    {
      id: 'vision',
      title: 'Document Intelligence & Vision',
      subtitle: 'Menu extraction, dish photo analysis, visual quality scoring',
      icon: <Eye className="h-6 w-6 text-cyan-600" />,
      gradient: 'from-cyan-50 to-teal-50',
      border: 'border-cyan-200',
      badges: ['vision', 'pro', 'thinking'] as const,
      features: [
        { label: 'Menu Photo → Structured Data', desc: 'Upload a menu photo and Gemini 3 Pro Vision extracts every item with prices, descriptions, and categories into structured JSON', active: menuItemCount > 0 },
        { label: 'Dish Photo Analysis', desc: 'AI analyzes dish presentation quality, plating aesthetics, color composition, and food photography standards', active: true },
        { label: 'Visual Quality Scoring', desc: 'Automated scoring of food photography with actionable improvement suggestions for social media', active: true },
        { label: 'Competitor Visual Gap', desc: 'Compares your dish photos against competitor imagery to identify visual positioning gaps', active: hasCompetitors },
      ],
      stats: menuItemCount > 0 ? `${menuItemCount} items extracted` : 'Ready to analyze',
      model: 'gemini-3-pro-preview',
      thinkingLevel: 'DEEP',
    },
    {
      id: 'video',
      title: 'Native Video Understanding',
      subtitle: 'Restaurant walkthrough analysis, ambiance scoring, competitor video intel',
      icon: <Video className="h-6 w-6 text-pink-600" />,
      gradient: 'from-pink-50 to-rose-50',
      border: 'border-pink-200',
      badges: ['video', 'pro', 'thinking'] as const,
      features: [
        { label: 'Restaurant Video Analysis', desc: 'Upload a walkthrough video — Gemini 3 natively processes video frames to analyze ambiance, layout, decor, and customer experience', active: true },
        { label: 'Ambiance & Atmosphere Scoring', desc: 'AI evaluates lighting, music, seating arrangement, cleanliness, and overall vibe from video content', active: true },
        { label: 'Competitor Video Intelligence', desc: 'Analyze competitor restaurant videos to understand their positioning and identify differentiation opportunities', active: hasCompetitors },
        { label: 'Social Media Video Audit', desc: 'Evaluate your social media video content quality and suggest improvements for engagement', active: hasSocialMedia },
      ],
      stats: 'Native multimodal processing',
      model: 'gemini-3-pro-preview',
      thinkingLevel: 'EXHAUSTIVE',
    },
    {
      id: 'audio',
      title: 'Voice Understanding',
      subtitle: 'Audio transcription, customer feedback analysis, voice-to-insights',
      icon: <Mic className="h-6 w-6 text-emerald-600" />,
      gradient: 'from-emerald-50 to-green-50',
      border: 'border-emerald-200',
      badges: ['audio', 'pro', 'thinking'] as const,
      features: [
        { label: 'Voice-to-Business Context', desc: 'Describe your restaurant verbally — Gemini 3 transcribes and extracts structured business context, goals, and competitive landscape', active: true },
        { label: 'Customer Feedback Audio', desc: 'Upload audio recordings of customer feedback for AI-powered sentiment analysis and theme extraction', active: true },
        { label: 'Staff Meeting Insights', desc: 'Transcribe and analyze staff meetings to extract actionable operational insights', active: true },
        { label: 'Multilingual Support', desc: 'Native understanding of Spanish, English, and other languages without translation overhead', active: true },
      ],
      stats: 'Real-time transcription',
      model: 'gemini-3-pro-preview',
      thinkingLevel: 'DEEP',
    },
    {
      id: 'grounding',
      title: 'Google Search Grounding',
      subtitle: 'Real-time market intelligence, pricing benchmarks, trend analysis',
      icon: <Search className="h-6 w-6 text-amber-600" />,
      gradient: 'from-amber-50 to-orange-50',
      border: 'border-amber-200',
      badges: ['grounding', 'pro'] as const,
      features: [
        { label: 'Competitor Discovery', desc: 'Automatically discovers nearby competitors using Google Search with real-time data, ratings, and reviews', active: hasCompetitors },
        { label: 'Market Pricing Benchmarks', desc: 'Grounded search for current market pricing in your area to optimize your menu pricing strategy', active: true },
        { label: 'Social Media Sentiment', desc: 'Searches Instagram and Facebook for brand mentions, engagement patterns, and public sentiment signals', active: hasSocialMedia },
        { label: 'Trend Analysis', desc: 'Identifies food trends, seasonal patterns, and emerging cuisine preferences in your market', active: true },
      ],
      stats: hasCompetitors ? 'Active intelligence' : 'Ready to search',
      model: 'gemini-3-pro-preview + Google Search',
      thinkingLevel: 'EXHAUSTIVE',
    },
    {
      id: 'image-gen',
      title: 'Imagen 3 — Creative Generation',
      subtitle: 'Campaign visuals, menu redesign, A/B testing variants, localization',
      icon: <Image className="h-6 w-6 text-purple-600" />,
      gradient: 'from-purple-50 to-fuchsia-50',
      border: 'border-purple-200',
      badges: ['image-gen', 'creative-autopilot'] as const,
      features: [
        { label: 'Campaign Visual Generation', desc: 'Generates professional marketing visuals for social media campaigns using Imagen 3 with brand-consistent styling', active: hasCampaigns },
        { label: 'A/B Testing Variants', desc: 'Creates multiple visual variants (camera angles, lighting, color grading) for data-driven creative optimization', active: true },
        { label: 'Menu Style Transformation', desc: 'Transforms your menu design into different visual styles (minimalist, rustic, luxury) while preserving content', active: true },
        { label: 'Multilingual Localization', desc: 'Translates text within generated images to target languages while preserving design integrity', active: true },
      ],
      stats: hasCampaigns ? 'Generating assets' : 'Ready to create',
      model: 'gemini-3-pro-image-preview',
      thinkingLevel: 'DEEP',
    },
    {
      id: 'agents',
      title: 'Multi-Agent Intelligence',
      subtitle: 'Marathon Agent, Vibe Engineering, Multi-Agent Debate, Context Caching',
      icon: <Brain className="h-6 w-6 text-indigo-600" />,
      gradient: 'from-indigo-50 to-violet-50',
      border: 'border-indigo-200',
      badges: ['marathon', 'vibe', 'debate', 'context-cache'] as const,
      features: [
        { label: 'Marathon Agent', desc: '14-stage autonomous pipeline with checkpoints, state recovery, and transparent reasoning at every step', active: true },
        { label: 'Vibe Engineering', desc: 'Self-improving quality assurance loop — AI verifies its own output and iteratively improves until quality threshold is met', active: true },
        { label: 'Multi-Agent Debate', desc: 'Two AI agents argue opposing strategies (e.g., aggressive vs conservative pricing) to surface nuanced insights', active: true },
        { label: 'Context Caching', desc: 'Efficient token reuse across the pipeline — large documents cached with TTL for cost optimization', active: true },
      ],
      stats: '14-stage pipeline',
      model: 'gemini-3-pro-preview',
      thinkingLevel: 'EXHAUSTIVE',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="relative rounded-xl overflow-hidden bg-gradient-to-r from-indigo-50 via-purple-50 to-pink-50 border border-indigo-200/60">
        <div className="flex items-center gap-6 p-5">
          <div className="hidden sm:block flex-shrink-0">
            <div className="w-28 h-20 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-md">
              <Sparkles className="h-10 w-10 text-white" />
            </div>
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-3 flex-wrap">
              <h1 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                <Eye className="w-5 h-5 text-indigo-600" />
                AI Intelligence — Gemini 3 Capabilities
              </h1>
            </div>
            <p className="text-sm text-gray-500 mt-0.5">
              Every analysis in RestoPilotAI is powered by Gemini 3&apos;s multimodal capabilities
            </p>
            <div className="mt-2">
              <GeminiCapabilityBadge
                capabilities={['pro', 'vision', 'video', 'audio', 'image-gen', 'grounding', 'thinking', 'vibe', 'debate', 'marathon']}
                size="sm"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Pipeline Status */}
      <div className="bg-white rounded-xl border border-gray-200 p-4">
        <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
          <Zap className="h-4 w-4 text-indigo-600" />
          Pipeline Status for {restaurantName}
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          {[
            { label: 'Menu Items', value: menuItemCount, active: menuItemCount > 0, icon: <FileText className="h-3.5 w-3.5" /> },
            { label: 'Competitors', value: hasCompetitors ? 'Analyzed' : 'Pending', active: hasCompetitors, icon: <Search className="h-3.5 w-3.5" /> },
            { label: 'Sentiment', value: hasSentiment ? 'Complete' : 'Pending', active: hasSentiment, icon: <Mic className="h-3.5 w-3.5" /> },
            { label: 'BCG Matrix', value: hasBCG ? 'Classified' : 'Pending', active: hasBCG, icon: <Brain className="h-3.5 w-3.5" /> },
            { label: 'Campaigns', value: hasCampaigns ? 'Generated' : 'Pending', active: hasCampaigns, icon: <Wand2 className="h-3.5 w-3.5" /> },
          ].map((item) => (
            <div
              key={item.label}
              className={`rounded-lg p-3 text-center border ${
                item.active
                  ? 'bg-green-50 border-green-200 text-green-700'
                  : 'bg-gray-50 border-gray-200 text-gray-500'
              }`}
            >
              <div className="flex items-center justify-center gap-1 mb-1">
                {item.icon}
                <span className="text-xs font-medium">{item.label}</span>
              </div>
              <span className="text-sm font-bold">{item.value}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Interactive Demo: Try It Live */}
      <div className="bg-white rounded-xl border border-indigo-200 overflow-hidden">
        <div className="p-4 bg-gradient-to-r from-indigo-50 to-purple-50 border-b border-indigo-100">
          <h3 className="font-bold text-gray-900 flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-indigo-600" />
            Try It Live — Multimodal Input
          </h3>
          <p className="text-sm text-gray-500 mt-0.5">Upload a video or record audio to see Gemini 3 process it in real-time</p>
        </div>

        {/* Demo Tabs */}
        <div className="flex border-b">
          <button
            onClick={() => setActiveDemo('video')}
            className={`flex-1 px-4 py-3 text-sm font-medium transition-colors border-b-2 flex items-center justify-center gap-2 ${
              activeDemo === 'video'
                ? 'border-pink-500 text-pink-600 bg-pink-50/50'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <Video className="h-4 w-4" />
            Native Video Analysis
            <GeminiCapabilityBadge capabilities={['video']} size="xs" />
          </button>
          <button
            onClick={() => setActiveDemo('audio')}
            className={`flex-1 px-4 py-3 text-sm font-medium transition-colors border-b-2 flex items-center justify-center gap-2 ${
              activeDemo === 'audio'
                ? 'border-emerald-500 text-emerald-600 bg-emerald-50/50'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <Mic className="h-4 w-4" />
            Voice Understanding
            <GeminiCapabilityBadge capabilities={['audio']} size="xs" />
          </button>
        </div>

        {/* Demo Content */}
        <div className="p-4">
          {activeDemo === 'video' ? (
            <VideoAnalysisZone
              sessionId={sessionId}
              onAnalysisComplete={(result) => {
                console.log('[AI Intelligence] Video analysis complete:', result);
              }}
              onError={(error) => {
                console.warn('[AI Intelligence] Video analysis error:', error);
              }}
            />
          ) : (
            <LiveTranscriptionBox
              onTranscriptionComplete={(text, segments) => {
                console.log('[AI Intelligence] Transcription complete:', text, segments);
              }}
              placeholder="Press the microphone to start recording — Gemini 3 will transcribe and analyze your voice in real-time"
            />
          )}
        </div>
      </div>

      {/* Capability Cards */}
      <div className="space-y-4">
        {capabilities.map((cap) => (
          <div
            key={cap.id}
            className={`rounded-xl border ${cap.border} bg-gradient-to-r ${cap.gradient} overflow-hidden`}
          >
            <div className="p-5">
              <div className="flex items-start gap-4">
                <div className="p-3 bg-white rounded-xl shadow-sm flex-shrink-0">
                  {cap.icon}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3 flex-wrap mb-1">
                    <h3 className="font-bold text-gray-900">{cap.title}</h3>
                    <GeminiCapabilityBadge capabilities={[...cap.badges]} size="xs" />
                  </div>
                  <p className="text-sm text-gray-600 mb-3">{cap.subtitle}</p>

                  <div className="grid md:grid-cols-2 gap-2">
                    {cap.features.map((feat, idx) => (
                      <div
                        key={idx}
                        className={`rounded-lg p-3 border ${
                          feat.active
                            ? 'bg-white/80 border-white/60'
                            : 'bg-white/40 border-white/30 opacity-60'
                        }`}
                      >
                        <div className="flex items-center gap-2 mb-1">
                          <span className={`text-xs ${feat.active ? 'text-green-600' : 'text-gray-400'}`}>
                            {feat.active ? '●' : '○'}
                          </span>
                          <span className="text-sm font-semibold text-gray-800">{feat.label}</span>
                        </div>
                        <p className="text-xs text-gray-600 leading-relaxed">{feat.desc}</p>
                      </div>
                    ))}
                  </div>

                  <div className="flex items-center gap-4 mt-3 text-xs text-gray-500">
                    <span className="flex items-center gap-1">
                      <Camera className="h-3 w-3" />
                      Model: <code className="bg-white/60 px-1 rounded text-[10px]">{cap.model}</code>
                    </span>
                    <span className="flex items-center gap-1">
                      <Shield className="h-3 w-3" />
                      Thinking: <code className="bg-white/60 px-1 rounded text-[10px]">{cap.thinkingLevel}</code>
                    </span>
                    <span className="font-medium text-gray-700">{cap.stats}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Architecture Summary */}
      <div className="bg-gradient-to-r from-slate-900 to-indigo-950 rounded-xl p-6 text-white">
        <h3 className="font-bold text-lg mb-3 flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-amber-400" />
          Gemini 3 Architecture in RestoPilotAI
        </h3>
        <div className="grid md:grid-cols-3 gap-4 text-sm">
          <div>
            <p className="text-blue-300 font-semibold mb-1">Input Modalities</p>
            <ul className="space-y-1 text-gray-300">
              <li>📸 Images (menu photos, dish photos)</li>
              <li>🎥 Video (restaurant walkthroughs)</li>
              <li>🎙️ Audio (voice descriptions, feedback)</li>
              <li>📄 Documents (CSV, PDF menus)</li>
              <li>💬 Text (business context, goals)</li>
            </ul>
          </div>
          <div>
            <p className="text-purple-300 font-semibold mb-1">Processing Pipeline</p>
            <ul className="space-y-1 text-gray-300">
              <li>🧠 14-stage Marathon Agent</li>
              <li>🔍 Google Search Grounding</li>
              <li>💭 Thought Signatures (4 levels)</li>
              <li>⚡ Context Caching (TTL-based)</li>
              <li>🛡️ Vibe Engineering QA loop</li>
            </ul>
          </div>
          <div>
            <p className="text-pink-300 font-semibold mb-1">Output Capabilities</p>
            <ul className="space-y-1 text-gray-300">
              <li>📊 BCG Matrix classification</li>
              <li>🎯 Competitor intelligence</li>
              <li>💬 Multi-source sentiment</li>
              <li>🎨 Imagen 3 campaign visuals</li>
              <li>📈 Sales predictions</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
