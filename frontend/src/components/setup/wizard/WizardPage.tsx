'use client';

import { ConfirmDialog } from '@/components/ui/ConfirmDialog';
import { CheckCircle2, FileText, Image, Loader2, MapPin, MessageSquare, Play, Target, Video } from 'lucide-react';
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
      return <StoryStep />;
    case 3:
      return <CompetitorsStep />;
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
      const response = await fetch(`/api/setup-wizard`, {
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

      {/* Demo Mode Button */}
      <div className="max-w-3xl mx-auto px-4 pt-4 flex justify-end">
        <button
          onClick={handleLoadDemo}
          disabled={loadingDemo || isSubmitting}
          className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-purple-700 bg-purple-50 border border-purple-200 rounded-lg hover:bg-purple-100 transition-colors disabled:opacity-50"
        >
          {loadingDemo ? (
            <><Loader2 className="h-4 w-4 animate-spin" /> Loading Demo...</>
          ) : (
            <><Play className="h-4 w-4" /> Try Demo</>
          )}
        </button>
      </div>

      <SetupWizard onComplete={handleRequestComplete}>
        <WizardStepContent />
      </SetupWizard>
    </div>
  );
}

export default WizardPage;
