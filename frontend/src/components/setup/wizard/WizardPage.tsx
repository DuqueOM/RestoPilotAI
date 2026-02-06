'use client';

import { useRouter } from 'next/navigation';
import { useState } from 'react';
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

export function WizardPage({ onSessionCreated }: WizardPageProps) {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

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

      <SetupWizard onComplete={handleComplete}>
        <WizardStepContent />
      </SetupWizard>
    </div>
  );
}

export default WizardPage;
