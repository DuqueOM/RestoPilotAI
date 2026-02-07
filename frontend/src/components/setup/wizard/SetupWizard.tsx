'use client';

import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';
import {
    ArrowLeft,
    ArrowRight,
    Check,
    CheckCircle2,
    FileText,
    MapPin,
    Mic,
    MinusCircle,
    Sparkles,
    Target,
    Zap
} from 'lucide-react';
import { createContext, useCallback, useContext, useEffect, useState } from 'react';

export interface WizardFormData {
  // Step 1: Location
  location: string;
  placeId?: string;
  businessName?: string;
  
  // Step 2: Data Upload
  menuFiles: File[];
  salesFiles: File[];
  photoFiles: File[];
  videoFiles: File[]; // New for video analysis
  
  // Step 3: Your Story
  historyContext: string;
  historyAudio: Blob[];
  valuesContext: string;
  valuesAudio: Blob[];
  uspsContext: string;
  uspsAudio: Blob[];
  targetAudienceContext: string;
  targetAudienceAudio: Blob[];
  challengesContext: string;
  challengesAudio: Blob[];
  goalsContext: string;
  goalsAudio: Blob[];
  
  // Step 4: Competitors
  competitorInput: string;
  autoFindCompetitors: boolean;
  competitorFiles: File[];
  competitorAudio: Blob[];
  
  // Social Media (optional)
  instagram?: string;
  facebook?: string;
  tiktok?: string;
  website?: string;
  deliveryPlatforms?: { name: string; icon: string; url: string | null }[];

  // Enriched data (auto-populated from location selection)
  enrichedProfile?: Record<string, any>;
  nearbyCompetitors?: Record<string, any>[];
  businessPhone?: string;
  businessWebsite?: string;
  businessRating?: number;
  businessUserRatingsTotal?: number;
}

export interface WizardStep {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  isRequired: boolean;
  isComplete: (data: WizardFormData) => boolean;
}

interface WizardContextType {
  currentStep: number;
  totalSteps: number;
  formData: WizardFormData;
  updateFormData: (updates: Partial<WizardFormData>) => void;
  nextStep: () => void;
  prevStep: () => void;
  goToStep: (step: number) => void;
  canProceed: boolean;
  isLastStep: boolean;
  isFirstStep: boolean;
}

const WizardContext = createContext<WizardContextType | null>(null);

export function useWizard() {
  const context = useContext(WizardContext);
  if (!context) {
    throw new Error('useWizard must be used within SetupWizard');
  }
  return context;
}

const STORAGE_KEY = 'restopilot_setup_wizard';

const defaultFormData: WizardFormData = {
  location: '',
  placeId: '',
  businessName: '',
  menuFiles: [],
  salesFiles: [],
  photoFiles: [],
  videoFiles: [], // Initialize empty
  historyContext: '',
  historyAudio: [],
  valuesContext: '',
  valuesAudio: [],
  uspsContext: '',
  uspsAudio: [],
  targetAudienceContext: '',
  targetAudienceAudio: [],
  challengesContext: '',
  challengesAudio: [],
  goalsContext: '',
  goalsAudio: [],
  competitorInput: '',
  autoFindCompetitors: true,
  competitorFiles: [],
  competitorAudio: [],
  instagram: '',
  facebook: '',
  tiktok: '',
  website: '',
  enrichedProfile: undefined,
  nearbyCompetitors: [],
  businessPhone: '',
  businessWebsite: '',
  businessRating: undefined,
  businessUserRatingsTotal: undefined,
};

const WIZARD_STEPS: WizardStep[] = [
  {
    id: 'location',
    title: '📍 Location',
    description: 'Where is your restaurant?',
    icon: <MapPin className="h-5 w-5" />,
    isRequired: true,
    isComplete: (data) => !!data.location,
  },
  {
    id: 'data',
    title: '📁 Your Data',
    description: 'Menu, sales, and photos',
    icon: <FileText className="h-5 w-5" />,
    isRequired: false,
    isComplete: (data) => 
      data.menuFiles.length > 0 || 
      data.salesFiles.length > 0 || 
      data.photoFiles.length > 0,
  },
  {
    id: 'competitors',
    title: '� Competitors',
    description: 'Who competes with you?',
    icon: <Target className="h-5 w-5" />,
    isRequired: false,
    isComplete: (data) => 
      !!data.competitorInput || 
      data.autoFindCompetitors ||
      data.competitorFiles.length > 0,
  },
  {
    id: 'story',
    title: '� Your Story',
    description: 'Tell us about your business',
    icon: <Mic className="h-5 w-5" />,
    isRequired: false,
    isComplete: (data) => 
      !!data.historyContext || 
      !!data.valuesContext || 
      !!data.goalsContext ||
      data.historyAudio.length > 0,
  },
];

interface SetupWizardProps {
  onComplete: (data: WizardFormData) => void;
  initialData?: Partial<WizardFormData>;
  children: React.ReactNode;
}

export function SetupWizard({ onComplete, initialData, children }: SetupWizardProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [isLoaded, setIsLoaded] = useState(false);
  const [formData, setFormData] = useState<WizardFormData>({ 
    ...defaultFormData, 
    ...initialData 
  });

  // Load from localStorage on mount
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        try {
          const parsed = JSON.parse(saved);
          setFormData(_prev => ({
            ...defaultFormData,
            ...parsed,
            // Files and Blobs can't be serialized, so we reset them
            menuFiles: [],
            salesFiles: [],
            photoFiles: [],
            videoFiles: [], 
            competitorFiles: [],
            historyAudio: [],
            valuesAudio: [],
            uspsAudio: [],
            targetAudienceAudio: [],
            challengesAudio: [],
            goalsAudio: [],
            competitorAudio: [],
            ...initialData,
          }));
        } catch {
          // Invalid JSON, use defaults
        }
      }
    }
    setIsLoaded(true);
  }, []); // Run once on mount

  // Save to localStorage on change (excluding files/blobs, but save file metadata)
  useEffect(() => {
    if (!isLoaded) return;

    const fileMetadata = (files: File[]) => files.map(f => ({ name: f.name, size: f.size, type: f.type }));

    const toSave = {
      location: formData.location,
      placeId: formData.placeId,
      businessName: formData.businessName,
      historyContext: formData.historyContext,
      valuesContext: formData.valuesContext,
      uspsContext: formData.uspsContext,
      targetAudienceContext: formData.targetAudienceContext,
      challengesContext: formData.challengesContext,
      goalsContext: formData.goalsContext,
      competitorInput: formData.competitorInput,
      autoFindCompetitors: formData.autoFindCompetitors,
      instagram: formData.instagram,
      facebook: formData.facebook,
      tiktok: formData.tiktok,
      website: formData.website,
      enrichedProfile: formData.enrichedProfile,
      nearbyCompetitors: formData.nearbyCompetitors,
      businessPhone: formData.businessPhone,
      businessWebsite: formData.businessWebsite,
      businessRating: formData.businessRating,
      businessUserRatingsTotal: formData.businessUserRatingsTotal,
      // Persist file metadata for returning users
      _fileMeta: {
        menuFiles: fileMetadata(formData.menuFiles),
        salesFiles: fileMetadata(formData.salesFiles),
        photoFiles: fileMetadata(formData.photoFiles),
        videoFiles: fileMetadata(formData.videoFiles),
        competitorFiles: fileMetadata(formData.competitorFiles),
      },
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(toSave));
  }, [formData]);

  const updateFormData = useCallback((updates: Partial<WizardFormData>) => {
    setFormData(prev => ({ ...prev, ...updates }));
  }, []);

  const nextStep = useCallback(() => {
    if (currentStep < WIZARD_STEPS.length - 1) {
      setCurrentStep(prev => prev + 1);
    }
  }, [currentStep]);

  const prevStep = useCallback(() => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1);
    }
  }, [currentStep]);

  const goToStep = useCallback((step: number) => {
    if (step >= 0 && step < WIZARD_STEPS.length) {
      setCurrentStep(step);
    }
  }, []);

  const currentStepConfig = WIZARD_STEPS[currentStep];
  const canProceed = !currentStepConfig.isRequired || currentStepConfig.isComplete(formData);
  const isLastStep = currentStep === WIZARD_STEPS.length - 1;
  const isFirstStep = currentStep === 0;

  const contextValue: WizardContextType = {
    currentStep,
    totalSteps: WIZARD_STEPS.length,
    formData,
    updateFormData,
    nextStep,
    prevStep,
    goToStep,
    canProceed,
    isLastStep,
    isFirstStep,
  };

  const handleComplete = () => {
    // Clear localStorage on complete
    localStorage.removeItem(STORAGE_KEY);
    onComplete(formData);
  };

  const progress = ((currentStep + 1) / WIZARD_STEPS.length) * 100;

  return (
    <WizardContext.Provider value={contextValue}>
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
        <div className="max-w-4xl mx-auto px-4 py-8">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-purple-100 text-purple-700 rounded-full text-sm font-medium mb-4">
              <Sparkles className="h-4 w-4" />
              Powered by Gemini 3 Multimodal
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Setup Your Analysis
            </h1>
            <p className="text-gray-600">
              Complete the steps to get personalized insights
            </p>
          </div>

          {/* Progress Bar */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600">
                Step {currentStep + 1} of {WIZARD_STEPS.length}
              </span>
              <span className="text-sm font-medium text-purple-600">
                {Math.round(progress)}% completed
              </span>
            </div>
            <Progress value={progress} className="h-2" />
          </div>

          {/* Step Indicators */}
          <div className="flex items-center justify-center gap-2 mb-8">
            {WIZARD_STEPS.map((step, index) => {
              const isActive = index === currentStep;
              const isCompleted = index < currentStep || step.isComplete(formData);
              const isPast = index < currentStep;

              return (
                <button
                  key={step.id}
                  onClick={() => goToStep(index)}
                  disabled={index > currentStep && !canProceed}
                  className={cn(
                    'flex items-center gap-2 px-4 py-2 rounded-full transition-all',
                    isActive && 'bg-purple-600 text-white shadow-lg scale-105',
                    !isActive && isCompleted && 'bg-green-100 text-green-700',
                    !isActive && !isCompleted && 'bg-gray-100 text-gray-500',
                    index > currentStep && !canProceed && 'opacity-50 cursor-not-allowed'
                  )}
                >
                  {isPast && isCompleted ? (
                    <Check className="h-4 w-4" />
                  ) : (
                    step.icon
                  )}
                  <span className="hidden sm:inline text-sm font-medium">
                    {step.title}
                  </span>
                </button>
              );
            })}
          </div>

          {/* Step Content */}
          <div className="bg-white rounded-2xl shadow-xl p-6 md:p-8 mb-6">
            <div className="mb-6">
              <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                {WIZARD_STEPS[currentStep].icon}
                {WIZARD_STEPS[currentStep].title}
              </h2>
              <p className="text-gray-600 mt-1">
                {WIZARD_STEPS[currentStep].description}
              </p>
              {!WIZARD_STEPS[currentStep].isRequired && (
                <span className="inline-block mt-2 text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                  Optional - you can skip this step
                </span>
              )}
            </div>

            {/* Dynamic Step Content */}
            {children}
          </div>

          {/* Navigation Buttons */}
          <div className="flex items-center justify-between">
            <Button
              variant="outline"
              onClick={prevStep}
              disabled={isFirstStep}
              className={cn(isFirstStep && 'invisible')}
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Previous
            </Button>

            <div className="flex items-center gap-3">
              {/* Quick Start Button with tooltip */}
              {!isLastStep && (
                <div className="relative group">
                  <Button
                    variant="outline"
                    onClick={handleComplete}
                    className="border-purple-300 text-purple-700 hover:bg-purple-50"
                  >
                    <Zap className="h-4 w-4 mr-2" />
                    Quick Start
                  </Button>
                  {/* Quick Start info tooltip */}
                  <div className="absolute bottom-full right-0 mb-2 w-72 bg-white rounded-xl shadow-xl border border-gray-200 p-4 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-50">
                    <p className="text-xs font-semibold text-gray-900 mb-2">Quick Start vs Full Setup</p>
                    <div className="space-y-1.5 text-xs">
                      <div className="flex items-center gap-2">
                        <CheckCircle2 className="h-3.5 w-3.5 text-green-500 flex-shrink-0" />
                        <span className="text-gray-700">Location-based competitor discovery</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <CheckCircle2 className="h-3.5 w-3.5 text-green-500 flex-shrink-0" />
                        <span className="text-gray-700">Google Maps reviews & sentiment</span>
                      </div>
                      <div className="flex items-center gap-2">
                        {formData.menuFiles.length > 0
                          ? <CheckCircle2 className="h-3.5 w-3.5 text-green-500 flex-shrink-0" />
                          : <MinusCircle className="h-3.5 w-3.5 text-gray-300 flex-shrink-0" />}
                        <span className={formData.menuFiles.length > 0 ? 'text-gray-700' : 'text-gray-400'}>Menu extraction & BCG analysis</span>
                      </div>
                      <div className="flex items-center gap-2">
                        {formData.salesFiles.length > 0
                          ? <CheckCircle2 className="h-3.5 w-3.5 text-green-500 flex-shrink-0" />
                          : <MinusCircle className="h-3.5 w-3.5 text-gray-300 flex-shrink-0" />}
                        <span className={formData.salesFiles.length > 0 ? 'text-gray-700' : 'text-gray-400'}>Sales forecasting & predictions</span>
                      </div>
                      <div className="flex items-center gap-2">
                        {formData.photoFiles.length > 0
                          ? <CheckCircle2 className="h-3.5 w-3.5 text-green-500 flex-shrink-0" />
                          : <MinusCircle className="h-3.5 w-3.5 text-gray-300 flex-shrink-0" />}
                        <span className={formData.photoFiles.length > 0 ? 'text-gray-700' : 'text-gray-400'}>Photo quality & visual scoring</span>
                      </div>
                      <div className="flex items-center gap-2">
                        {formData.videoFiles.length > 0
                          ? <CheckCircle2 className="h-3.5 w-3.5 text-green-500 flex-shrink-0" />
                          : <MinusCircle className="h-3.5 w-3.5 text-gray-300 flex-shrink-0" />}
                        <span className={formData.videoFiles.length > 0 ? 'text-gray-700' : 'text-gray-400'}>Video analysis (Gemini 3 exclusive)</span>
                      </div>
                    </div>
                    <div className="mt-2 pt-2 border-t text-xs text-gray-500">
                      Skipped steps can limit analysis depth
                    </div>
                  </div>
                </div>
              )}

              {isLastStep ? (
                <Button
                  onClick={handleComplete}
                  disabled={!canProceed}
                  className="bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700"
                >
                  <Sparkles className="h-4 w-4 mr-2" />
                  Analyze My Business
                </Button>
              ) : (
                <Button
                  onClick={nextStep}
                  disabled={!canProceed && WIZARD_STEPS[currentStep].isRequired}
                >
                  {canProceed || !WIZARD_STEPS[currentStep].isRequired ? 'Next' : 'Complete this step'}
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>
    </WizardContext.Provider>
  );
}

export { WIZARD_STEPS };
export default SetupWizard;
