'use client';

import { ConfirmDialog } from '@/components/ui/ConfirmDialog';
import {
    ArrowRight,
    Brain,
    Camera,
    CheckCircle2,
    FileText,
    Globe,
    Image,
    Loader2,
    MapPin,
    MessageSquare,
    Mic,
    Palette,
    Play,
    Search,
    Sparkles,
    Target,
    Video,
    Zap
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useCallback, useState } from 'react';
import { CompetitorsStep } from './CompetitorsStep';
import { DataUploadStep } from './DataUploadStep';
import { LocationStep } from './LocationStep';
import { SetupWizard, useWizard, WizardFormData } from './SetupWizard';
import { StoryStep } from './StoryStep';

function WizardStepContent() {
  const { currentStep } = useWizard();

  switch (currentStep) {
    case 0:
      return <LocationStep />;
    case 1:
      return <DataUploadStep />;
    case 2:
      return <CompetitorsStep />;
    case 3:
      return <StoryStep />;
    default:
      return <LocationStep />;
  }
}

interface WizardPageProps {
  onSessionCreated?: (sessionId: string) => void;
}

function getDataSummary(data: WizardFormData) {
  const items: { icon: React.ReactNode; label: string; detail: string; present: boolean }[] = [
    {
      icon: <MapPin className="h-4 w-4 text-purple-600" />,
      label: 'Location',
      detail: data.businessName || data.location || 'Not provided',
      present: !!data.location,
    },
    {
      icon: <FileText className="h-4 w-4 text-orange-500" />,
      label: 'Menu Files',
      detail: data.menuFiles.length > 0 ? `${data.menuFiles.length} file(s)` : 'None',
      present: data.menuFiles.length > 0,
    },
    {
      icon: <FileText className="h-4 w-4 text-green-500" />,
      label: 'Sales Data',
      detail: data.salesFiles.length > 0 ? `${data.salesFiles.length} file(s)` : 'None',
      present: data.salesFiles.length > 0,
    },
    {
      icon: <Image className="h-4 w-4 text-blue-500" />,
      label: 'Dish Photos',
      detail: data.photoFiles.length > 0 ? `${data.photoFiles.length} photo(s)` : 'None',
      present: data.photoFiles.length > 0,
    },
    {
      icon: <Video className="h-4 w-4 text-purple-500" />,
      label: 'Videos',
      detail: data.videoFiles.length > 0 ? `${data.videoFiles.length} video(s)` : 'None',
      present: data.videoFiles.length > 0,
    },
    {
      icon: <MessageSquare className="h-4 w-4 text-teal-500" />,
      label: 'Business Story',
      detail: [data.historyContext, data.valuesContext, data.goalsContext].filter(Boolean).length > 0
        ? `${[data.historyContext, data.valuesContext, data.goalsContext].filter(Boolean).length} section(s) filled`
        : 'None',
      present: !!(data.historyContext || data.valuesContext || data.goalsContext),
    },
    {
      icon: <Target className="h-4 w-4 text-red-500" />,
      label: 'Competitors',
      detail: data.autoFindCompetitors ? 'Auto-find enabled' : (data.competitorInput ? 'Manual input' : 'None'),
      present: data.autoFindCompetitors || !!data.competitorInput,
    },
  ];
  const audioCount = [
    ...data.historyAudio, ...data.valuesAudio, ...data.uspsAudio,
    ...data.targetAudienceAudio, ...data.challengesAudio, ...data.goalsAudio, ...data.competitorAudio
  ].length;
  if (audioCount > 0) {
    items.push({
      icon: <MessageSquare className="h-4 w-4 text-indigo-500" />,
      label: 'Voice Notes',
      detail: `${audioCount} recording(s)`,
      present: true,
    });
  }
  return items;
}

export function WizardPage({ onSessionCreated }: WizardPageProps) {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [loadingDemo, setLoadingDemo] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showConfirm, setShowConfirm] = useState(false);
  const [pendingData, setPendingData] = useState<WizardFormData | null>(null);

  const handleLoadDemo = useCallback(async () => {
    setLoadingDemo(true);
    setError(null);
    try {
      const res = await fetch('/api/v1/demo/load');
      if (!res.ok) throw new Error('Demo data not available');
      const data = await res.json();
      const sessionId = data.session_id;
      if (!sessionId) throw new Error('No session returned');
      onSessionCreated?.(sessionId);
      router.push(`/analysis/${sessionId}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load demo');
      setLoadingDemo(false);
    }
  }, [router, onSessionCreated]);

  const handleRequestComplete = (data: WizardFormData) => {
    setPendingData(data);
    setShowConfirm(true);
  };

  const handleConfirmedComplete = async () => {
    if (!pendingData) return;
    setShowConfirm(false);
    await handleComplete(pendingData);
  };

  const handleComplete = async (data: WizardFormData) => {
    setIsSubmitting(true);
    setError(null);

    try {
      // Create FormData for file uploads
      const formData = new FormData();

      // Add location data
      formData.append('location', data.location);
      if (data.placeId) formData.append('place_id', data.placeId);
      if (data.businessName) formData.append('business_name', data.businessName);

      // Add files
      data.menuFiles.forEach((file) => formData.append('menu_files', file));
      data.salesFiles.forEach((file) => formData.append('sales_files', file));
      data.photoFiles.forEach((file) => formData.append('photo_files', file));
      data.videoFiles.forEach((file) => formData.append('video_files', file));
      data.competitorFiles.forEach((file) => formData.append('competitor_files', file));

      // Add context text
      const contextData = {
        history: data.historyContext,
        values: data.valuesContext,
        usps: data.uspsContext,
        target_audience: data.targetAudienceContext,
        challenges: data.challengesContext,
        goals: data.goalsContext,
        competitors: data.competitorInput,
        auto_find_competitors: data.autoFindCompetitors,
        social_media: {
          instagram: data.instagram,
          facebook: data.facebook,
          tiktok: data.tiktok,
          website: data.website,
        },
        // Enriched data from location selection
        enriched_profile: data.enrichedProfile || null,
        nearby_competitors: data.nearbyCompetitors || [],
        business_phone: data.businessPhone || null,
        business_website: data.businessWebsite || null,
        business_rating: data.businessRating || null,
        business_user_ratings_total: data.businessUserRatingsTotal || null,
      };
      formData.append('context', JSON.stringify(contextData));

      // Add audio blobs
      const audioBlobs = [
        ...data.historyAudio.map((b, i) => ({ blob: b, name: `history_audio_${i}.webm` })),
        ...data.valuesAudio.map((b, i) => ({ blob: b, name: `values_audio_${i}.webm` })),
        ...data.uspsAudio.map((b, i) => ({ blob: b, name: `usps_audio_${i}.webm` })),
        ...data.targetAudienceAudio.map((b, i) => ({ blob: b, name: `audience_audio_${i}.webm` })),
        ...data.challengesAudio.map((b, i) => ({ blob: b, name: `challenges_audio_${i}.webm` })),
        ...data.goalsAudio.map((b, i) => ({ blob: b, name: `goals_audio_${i}.webm` })),
        ...data.competitorAudio.map((b, i) => ({ blob: b, name: `competitor_audio_${i}.webm` })),
      ];

      audioBlobs.forEach(({ blob, name }) => {
        formData.append('audio_files', blob, name);
      });

      // Create session
      const response = await fetch(`/api/v1/business/setup-wizard`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to create session');
      }

      const result = await response.json();
      const sessionId = result.session_id;

      if (onSessionCreated) {
        onSessionCreated(sessionId);
      }

      // Auto-start full analysis pipeline
      try {
        await fetch(`/api/v1/marathon/start`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            task_type: 'full_analysis',
            session_id: sessionId,
            input_data: {},
            enable_checkpoints: true,
            checkpoint_interval_seconds: 60,
            max_retries_per_step: 3,
          }),
        });
      } catch (analysisErr) {
        console.warn('Auto-start analysis failed, user can start manually:', analysisErr);
      }

      // Navigate to analysis page (analysis already running)
      router.push(`/analysis/${sessionId}?autoStarted=true`);
    } catch (err: any) {
      const msg = err instanceof Error ? err.message : (err?.message || (typeof err === 'object' ? JSON.stringify(err, Object.getOwnPropertyNames(err || {})) : String(err)));
      console.error('Setup failed:', msg, err);
      setError(msg || 'Setup failed. Please try again.');
      setIsSubmitting(false);
    }
  };

  return (
    <div className="relative">
      {isSubmitting && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center">
          <div className="bg-white rounded-2xl p-8 max-w-md mx-4 text-center shadow-2xl">
            <div className="w-16 h-16 mx-auto mb-4 relative">
              <div className="absolute inset-0 border-4 border-purple-200 rounded-full animate-pulse" />
              <div className="absolute inset-0 border-4 border-purple-600 border-t-transparent rounded-full animate-spin" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">
              🚀 Starting Analysis
            </h3>
            <p className="text-gray-600">
              Gemini 3 is processing your information...
            </p>
          </div>
        </div>
      )}

      {error && (
        <div className="fixed top-4 left-1/2 -translate-x-1/2 z-50 bg-red-50 border border-red-200 text-red-800 px-6 py-3 rounded-lg shadow-lg">
          {error}
        </div>
      )}

      {/* Confirmation Dialog */}
      {pendingData && (
        <ConfirmDialog
          open={showConfirm}
          onOpenChange={setShowConfirm}
          title="Start AI Analysis?"
          description="Gemini 3 will analyze all your data using multimodal AI. This typically takes 2-5 minutes."
          confirmLabel="Start Analysis"
          cancelLabel="Review Data"
          onConfirm={handleConfirmedComplete}
          variant="ai"
          loading={isSubmitting}
        >
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {getDataSummary(pendingData).map((item, i) => (
              <div key={i} className="flex items-center gap-3 py-1.5">
                {item.icon}
                <span className="text-sm text-gray-700 font-medium flex-1">{item.label}</span>
                <span className={`text-sm ${item.present ? 'text-gray-900' : 'text-gray-400'}`}>
                  {item.present && <CheckCircle2 className="h-3.5 w-3.5 text-green-500 inline mr-1" />}
                  {item.detail}
                </span>
              </div>
            ))}
          </div>
          {!pendingData.menuFiles.length && !pendingData.salesFiles.length && (
            <div className="mt-3 p-2.5 bg-amber-50 rounded-lg border border-amber-200">
              <p className="text-xs text-amber-700">
                <strong>Note:</strong> Without menu or sales data, the analysis will be limited.
                Go back to add files for better results.
              </p>
            </div>
          )}
        </ConfirmDialog>
      )}

      {/* Hero Section — Redesigned for Hackathon Impact */}
      <div className="relative overflow-hidden bg-gradient-to-br from-slate-900 via-blue-950 to-purple-950">
        {/* Animated background grid */}
        <div className="absolute inset-0 opacity-[0.04]" style={{ backgroundImage: 'radial-gradient(circle at 1px 1px, white 1px, transparent 0)', backgroundSize: '40px 40px' }} />
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/20 via-transparent to-purple-600/20" />
        
        <div className="relative max-w-6xl mx-auto px-6 py-14 md:py-20">
          <div className="grid md:grid-cols-2 gap-10 items-center">
            {/* Left: Text Content */}
            <div className="text-white space-y-6">
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-sm rounded-full text-xs font-semibold text-blue-200 border border-white/10">
                <Sparkles className="h-3.5 w-3.5 text-amber-300" />
                Built with Gemini 3 Pro — Google DeepMind
              </div>
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-extrabold leading-[1.1] tracking-tight">
                Restaurant AI
                <span className="block bg-gradient-to-r from-amber-300 via-orange-300 to-rose-300 bg-clip-text text-transparent">
                  Powered by Gemini 3
                </span>
              </h1>
              <p className="text-blue-200/90 text-lg md:text-xl max-w-lg leading-relaxed">
                The first <strong className="text-white">multimodal restaurant intelligence platform</strong> — analyzing menus, photos, videos, voice, and sales data through a single AI pipeline.
              </p>

              {/* CTA Buttons — Demo is HUGE and primary */}
              <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 pt-3">
                <button
                  onClick={handleLoadDemo}
                  disabled={loadingDemo || isSubmitting}
                  className="group inline-flex items-center gap-3 px-8 py-4 text-base font-bold text-white bg-gradient-to-r from-amber-500 via-orange-500 to-rose-500 rounded-2xl hover:from-amber-600 hover:via-orange-600 hover:to-rose-600 transition-all shadow-xl shadow-orange-500/30 disabled:opacity-50 hover:scale-[1.02] active:scale-[0.98]"
                >
                  {loadingDemo ? (
                    <><Loader2 className="h-5 w-5 animate-spin" /> Loading Demo...</>
                  ) : (
                    <><Play className="h-5 w-5" /> See Live Demo <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" /></>
                  )}
                </button>
                <span className="text-sm text-blue-300/60 sm:ml-2">Instant — no signup required</span>
              </div>

              {/* Stats bar */}
              <div className="flex flex-wrap gap-6 pt-4 border-t border-white/10">
                <div className="text-center">
                  <div className="text-2xl font-bold text-white">6</div>
                  <div className="text-xs text-blue-300/70">AI Modalities</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-white">14</div>
                  <div className="text-xs text-blue-300/70">Pipeline Stages</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-white">3</div>
                  <div className="text-xs text-blue-300/70">AI Agents</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-white">Real-time</div>
                  <div className="text-xs text-blue-300/70">Thought Streaming</div>
                </div>
              </div>
            </div>

            {/* Right: Hero Image */}
            <div className="hidden md:block relative">
              <div className="relative rounded-2xl overflow-hidden shadow-2xl shadow-black/40 border border-white/10">
                <img
                  src="/images/hero-chef.png"
                  alt="Professional chef in modern kitchen"
                  className="w-full h-[380px] object-cover"
                  loading="eager"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-slate-900/70 via-transparent to-transparent" />
                {/* Overlay badge */}
                <div className="absolute bottom-4 left-4 right-4 bg-black/60 backdrop-blur-md rounded-xl p-3 border border-white/10">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center flex-shrink-0">
                      <Brain className="h-5 w-5 text-white" />
                    </div>
                    <div>
                      <div className="text-white text-sm font-semibold">Marathon Agent Running</div>
                      <div className="text-blue-200/70 text-xs">Autonomous 14-stage analysis pipeline</div>
                    </div>
                    <div className="ml-auto">
                      <span className="inline-flex items-center gap-1.5 text-xs text-green-300">
                        <span className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse" />
                        Live
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Gemini 3 Capabilities Showcase — The "WOW" section */}
      <div className="relative bg-white border-b border-gray-100">
        <div className="max-w-6xl mx-auto px-6 py-12">
          <div className="text-center mb-10">
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-blue-50 rounded-full text-xs font-semibold text-blue-700 mb-3">
              <Zap className="h-3 w-3" />
              Why Gemini 3 Changes Everything
            </div>
            <h2 className="text-2xl md:text-3xl font-bold text-gray-900">
              6 AI Modalities, One Unified Pipeline
            </h2>
            <p className="text-gray-500 mt-2 max-w-2xl mx-auto">
              No other AI model can natively process menus, photos, videos, voice notes, documents, and live web data in a single analysis flow.
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {[
              { icon: <Camera className="h-6 w-6" />, title: 'Vision Analysis', desc: 'Dish photos → quality scores, presentation analysis, Instagram appeal rating', color: 'from-blue-500 to-cyan-500', badge: 'Gemini 3 Vision' },
              { icon: <Video className="h-6 w-6" />, title: 'Native Video', desc: 'Restaurant ambience videos → atmosphere analysis, service flow insights', color: 'from-purple-500 to-pink-500', badge: 'Exclusive' },
              { icon: <Mic className="h-6 w-6" />, title: 'Voice Understanding', desc: 'Tell your story by voice — AI transcribes and extracts business intelligence', color: 'from-emerald-500 to-teal-500', badge: 'Multimodal' },
              { icon: <FileText className="h-6 w-6" />, title: 'Document Intelligence', desc: 'PDF menus → structured data with prices, categories, descriptions in seconds', color: 'from-orange-500 to-amber-500', badge: 'Gemini 3 Pro' },
              { icon: <Palette className="h-6 w-6" />, title: 'Image Generation', desc: 'AI-generated marketing campaigns with Imagen 3 — text in images, A/B variants', color: 'from-rose-500 to-pink-500', badge: 'Imagen 3' },
              { icon: <Search className="h-6 w-6" />, title: 'Search Grounding', desc: 'Competitive intelligence verified with Google Search — auto-cited real data', color: 'from-indigo-500 to-blue-500', badge: 'Grounded AI' },
            ].map((cap, i) => (
              <div key={i} className="group relative bg-gray-50 hover:bg-white rounded-2xl p-5 border border-gray-100 hover:border-gray-200 hover:shadow-lg transition-all duration-300">
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${cap.color} flex items-center justify-center text-white mb-3 group-hover:scale-110 transition-transform`}>
                  {cap.icon}
                </div>
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="font-bold text-gray-900 text-sm">{cap.title}</h3>
                  <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded-full bg-gradient-to-r from-blue-100 to-purple-100 text-blue-700">{cap.badge}</span>
                </div>
                <p className="text-xs text-gray-500 leading-relaxed">{cap.desc}</p>
              </div>
            ))}
          </div>

          {/* Agentic Architecture highlight */}
          <div className="mt-8 bg-gradient-to-r from-slate-900 to-blue-950 rounded-2xl p-6 md:p-8 text-white">
            <div className="grid md:grid-cols-3 gap-6">
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 rounded-lg bg-amber-500/20 flex items-center justify-center flex-shrink-0">
                  <Brain className="h-5 w-5 text-amber-400" />
                </div>
                <div>
                  <h4 className="font-bold text-sm">Marathon Agent</h4>
                  <p className="text-xs text-blue-200/70 mt-1">Autonomous 14-stage pipeline with checkpoints, retries, and real-time WebSocket streaming of AI reasoning</p>
                </div>
              </div>
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center flex-shrink-0">
                  <Palette className="h-5 w-5 text-purple-400" />
                </div>
                <div>
                  <h4 className="font-bold text-sm">Creative Autopilot</h4>
                  <p className="text-xs text-blue-200/70 mt-1">End-to-end campaign generation with Imagen 3, A/B variants, multi-language localization, impact estimation</p>
                </div>
              </div>
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 rounded-lg bg-green-500/20 flex items-center justify-center flex-shrink-0">
                  <CheckCircle2 className="h-5 w-5 text-green-400" />
                </div>
                <div>
                  <h4 className="font-bold text-sm">Vibe Engineering</h4>
                  <p className="text-xs text-blue-200/70 mt-1">Autonomous quality verification loops — the AI critiques itself and iterates until quality thresholds are met</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Section divider with "Set up your restaurant" */}
      <div className="max-w-6xl mx-auto px-6 pt-10 pb-4">
        <div className="flex items-center gap-4">
          <div className="h-px flex-1 bg-gradient-to-r from-transparent via-gray-200 to-transparent" />
          <span className="text-sm font-semibold text-gray-400 uppercase tracking-wider flex items-center gap-2">
            <Globe className="h-4 w-4" />
            Set Up Your Restaurant
          </span>
          <div className="h-px flex-1 bg-gradient-to-r from-transparent via-gray-200 to-transparent" />
        </div>
      </div>

      <SetupWizard onComplete={handleRequestComplete}>
        <WizardStepContent />
      </SetupWizard>
    </div>
  );
}

export default WizardPage;
