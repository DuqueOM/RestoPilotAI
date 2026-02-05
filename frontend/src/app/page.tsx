'use client';

import { ContextInput } from '@/components/setup/ContextInput';
import { FileUpload } from '@/components/setup/FileUpload';
import { InfoTooltip } from '@/components/setup/InfoTooltip';
import { ProgressBar } from '@/components/setup/ProgressBar';
import { TemplateSelector } from '@/components/setup/TemplateSelector';
import { api } from '@/lib/api';
import {
  CheckCircle2,
  FileText,
  Instagram,
  Loader2,
  MapPin,
  Mic,
  Play,
  Sparkles,
  Target,
  Upload
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import { lazy, Suspense, useEffect, useState } from 'react';
import { toast } from 'sonner';

// Lazy load heavy components
const GeminiChat = lazy(() => import('@/components/chat/GeminiChat').then(mod => ({ default: mod.GeminiChat })));
const LocationInput = lazy(() => import('@/components/setup/LocationInput').then(mod => ({ default: mod.LocationInput })));

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '';

export default function SetupPage() {
  const router = useRouter();
  const [completionScore, setCompletionScore] = useState(0);
  const [loadingState, setLoadingState] = useState<{
    type: 'demo' | 'analysis' | null;
    stage: 'idle' | 'loading' | 'success';
  }>({ type: null, stage: 'idle' });
  const [loadingMessage, setLoadingMessage] = useState('Initializing...');
  
  // New states for analysis configuration
  const [autoVerify, setAutoVerify] = useState(true);
  const [autoImprove, setAutoImprove] = useState(true);

  // Rotating loading messages
  useEffect(() => {
    if (loadingState.stage !== 'loading') return;

    const demoMessages = [
      "Spinning up your demo environment...",
      "Loading sample data...",
      "Configuring dashboard widgets...",
      "Preparing your experience..."
    ];

    const analysisMessages = [
      "Analyzing your business data...",
      "Identifying market trends...",
      "Comparing with local competitors...",
      "Generating strategic insights...",
      "Building your growth plan..."
    ];

    const messages = loadingState.type === 'demo' ? demoMessages : analysisMessages;
    setLoadingMessage(messages[0]);

    let i = 0;
    const interval = setInterval(() => {
      i = (i + 1) % messages.length;
      setLoadingMessage(messages[i]);
    }, 3000);

    return () => clearInterval(interval);
  }, [loadingState.stage, loadingState.type]);
  
  const [formData, setFormData] = useState({
    // Location (most important - shown first)
    location: '',
    
    // Business basics
    businessName: '',
    instagram: '',
    facebook: '',
    tiktok: '',
    website: '',
    
    // Files
    menuFiles: [] as File[],
    salesFiles: [] as File[],
    photoFiles: [] as File[],
    
    // Context (text)
    historyContext: '',
    valuesContext: '',
    uspsContext: '',
    targetAudienceContext: '',
    challengesContext: '',
    goalsContext: '',
    
    // Context (audio)
    historyAudio: [] as Blob[],
    valuesAudio: [] as Blob[],
    uspsAudio: [] as Blob[],
    targetAudienceAudio: [] as Blob[],
    challengesAudio: [] as Blob[],
    goalsAudio: [] as Blob[],
    
    // Competitor info
    competitorInput: '', 
    competitorAudio: [] as Blob[], // New for competitor audio
    competitorFiles: [] as File[], 
    autoFindCompetitors: true,
  });
  
  // Calculate completion score
  useEffect(() => {
    const fields = [
      formData.location ? 25 : 0,
      formData.businessName ? 5 : 0,
      formData.instagram || formData.facebook || formData.tiktok || formData.website ? 5 : 0,
      formData.menuFiles.length > 0 ? 10 : 0,
      formData.salesFiles.length > 0 ? 10 : 0,
      formData.photoFiles.length > 0 ? 10 : 0,
      formData.historyContext ? 5 : 0,
      formData.valuesContext ? 5 : 0,
      formData.uspsContext ? 5 : 0,
      formData.targetAudienceContext ? 5 : 0,
      formData.challengesContext ? 5 : 0,
      formData.goalsContext ? 5 : 0,
      (formData.competitorInput || formData.competitorAudio.length > 0 || formData.competitorFiles.length > 0) ? 5 : 0,
    ];
    
    setCompletionScore(Math.min(100, fields.reduce((a, b) => a + b, 0)));
  }, [formData]);
  
  const handleDemoClick = async () => {
    try {
      setLoadingState({ type: 'demo', stage: 'loading' });
      
      const result = await api.loadDemo();
      
      setLoadingState({ type: 'demo', stage: 'success' });
      
      // Small delay to show success state before redirecting
      setTimeout(() => {
        router.push(`/analysis/${result.session_id}`);
      }, 1500);
    } catch (error) {
      console.error('Failed to load demo:', error);
      toast.error('Failed to load demo experience. Is the backend running?');
      setLoadingState({ type: null, stage: 'idle' });
    }
  };

  const handleBusinessEnriched = (profile: any) => {
    console.log("Enriched profile received:", profile);
    
    // Extract social media
    let instagram = '';
    let facebook = '';
    let tiktok = '';
    
    if (profile.social_media) {
      profile.social_media.forEach((p: any) => {
        if (p.platform === 'instagram') instagram = p.handle ? `@${p.handle}` : p.url;
        if (p.platform === 'facebook') facebook = p.url;
        if (p.platform === 'tiktok') tiktok = p.handle ? `@${p.handle}` : p.url;
      });
    }

    setFormData(prev => ({
      ...prev,
      businessName: profile.name || prev.businessName,
      website: profile.website || prev.website,
      instagram: instagram || prev.instagram,
      facebook: facebook || prev.facebook,
      tiktok: tiktok || prev.tiktok,
    }));
    
    toast.success('Business details found and applied!');
  };

  const handleSubmit = async () => {
    if (!formData.location) return;
    
    setLoadingState({ type: 'analysis', stage: 'loading' });
    try {
      const data = new FormData();
      
      // Basic info
      data.append('location', formData.location);
      if (formData.businessName) data.append('businessName', formData.businessName);
      if (formData.instagram) data.append('instagram', formData.instagram);
      if (formData.facebook) data.append('facebook', formData.facebook);
      if (formData.tiktok) data.append('tiktok', formData.tiktok);
      if (formData.website) data.append('website', formData.website);
      
      // Analysis configuration
      data.append('auto_verify', autoVerify.toString());
      data.append('auto_improve', autoImprove.toString());
      
      // Context
      if (formData.historyContext) data.append('historyContext', formData.historyContext);
      if (formData.valuesContext) data.append('valuesContext', formData.valuesContext);
      if (formData.uspsContext) data.append('uspsContext', formData.uspsContext);
      if (formData.targetAudienceContext) data.append('targetAudienceContext', formData.targetAudienceContext);
      if (formData.challengesContext) data.append('challengesContext', formData.challengesContext);
      if (formData.goalsContext) data.append('goalsContext', formData.goalsContext);
      
      // Competitors
      if (formData.competitorInput) data.append('competitorInput', formData.competitorInput);
      data.append('autoFindCompetitors', formData.autoFindCompetitors.toString());
      
      // Files
      formData.menuFiles.forEach(file => data.append('menuFiles', file));
      formData.salesFiles.forEach(file => data.append('salesFiles', file));
      formData.photoFiles.forEach(file => data.append('photoFiles', file));
      formData.competitorFiles.forEach(file => data.append('competitorFiles', file));
      
      // Audio (Handling arrays)
      const appendAudio = (blobs: Blob[], fieldName: string) => {
        blobs.forEach((blob, idx) => {
          data.append(fieldName, blob, `${fieldName}_${idx}.webm`);
        });
      };

      appendAudio(formData.historyAudio, 'historyAudio');
      appendAudio(formData.valuesAudio, 'valuesAudio');
      appendAudio(formData.uspsAudio, 'uspsAudio');
      appendAudio(formData.targetAudienceAudio, 'targetAudienceAudio');
      appendAudio(formData.challengesAudio, 'challengesAudio');
      appendAudio(formData.goalsAudio, 'goalsAudio');
      
      // Append competitor audio as generic competitor files if API doesn't support specific field yet, 
      // OR update API. Current API takes competitorFiles. We can treat these blobs as files.
      formData.competitorAudio.forEach((blob, idx) => {
        data.append('competitorFiles', blob, `competitor_audio_${idx}.webm`);
      });
      
      // Start analysis
      const response = await fetch(`${API_BASE}/api/v1/analysis/start`, {
        method: 'POST',
        body: data,
      });
      
      if (!response.ok) {
        throw new Error('Failed to start analysis');
      }
      
      const { analysis_id } = await response.json();
      
      // AUTO-START MARATHON AGENT (full analysis)
      try {
        await fetch(`${API_BASE}/api/v1/marathon/start`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            task_type: 'full_analysis',
            session_id: analysis_id,
            enable_checkpoints: true,
            auto_verify: autoVerify,
            auto_improve: autoImprove,
          }),
        });
      } catch (marathonErr) {
        console.warn('Marathon Agent auto-start failed:', marathonErr);
        // Continue anyway
      }
      
      setLoadingState({ type: 'analysis', stage: 'success' });
      
      setTimeout(() => {
        router.push(`/analysis/${analysis_id}`);
      }, 1500);
      
    } catch (error) {
      console.error('Error starting analysis:', error);
      toast.error('Failed to start analysis. Please try again.');
      setLoadingState({ type: null, stage: 'idle' });
    }
  };
  
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header - Matching Analysis Layout */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-600 rounded-lg">
                <FileText className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">RestoPilotAI</h1>
                <p className="text-xs text-gray-500">AI-Powered Restaurant Optimization</p>
              </div>
            </div>
            <div className="flex items-center gap-6 w-1/3 justify-end">
              <div className="flex-1 max-w-xs">
                 <ProgressBar 
                  value={completionScore} 
                  label={`${completionScore}% Ready`}
                />
              </div>
            </div>
          </div>
        </div>
      </header>
      
      <main className="max-w-5xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {/* Hero Section */}
        <div className="text-center mb-10 space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-blue-50 border border-blue-100 rounded-full">
            <Sparkles className="w-3.5 h-3.5 text-blue-600" />
            <span className="text-xs font-medium text-blue-700">
              Powered by Gemini 3 Multimodal AI
            </span>
          </div>
          
          <h2 className="text-3xl font-bold text-gray-900 tracking-tight sm:text-4xl">
            Discover Your Competitive Edge
          </h2>
          
          <p className="text-lg text-gray-600 max-w-2xl mx-auto leading-relaxed">
            Just tell us where you are. We'll find your competitors, analyze your market,
            and create a winning strategy.
          </p>

          {/* Live Demo CTA */}
          <div className="flex justify-center mt-6">
            <button
              onClick={handleDemoClick}
              disabled={loadingState.stage !== 'idle'}
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-white text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 hover:text-gray-900 transition-all shadow-sm font-medium text-sm disabled:opacity-50"
            >
              {loadingState.type === 'demo' && loadingState.stage === 'loading' ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Play className="w-4 h-4 fill-gray-500" />
              )}
              View Live Demo
            </button>
          </div>
        </div>
        
        {/* Form Sections - Progressive Disclosure */}
        <div className="space-y-6">
          
          {/* SECTION 1: Location */}
          <section className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 transition-all hover:shadow-md">
            <div className="flex items-start gap-4 mb-6">
              <div className="p-2 bg-blue-50 rounded-lg shrink-0">
                <MapPin className="w-6 h-6 text-blue-600" />
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900">
                  Where is your restaurant?
                </h3>
                <p className="text-sm text-gray-500 mt-1">
                  This is all we need to get started. Everything else is optional.
                </p>
              </div>
              <InfoTooltip content="We'll use this to find competitors, analyze your neighborhood, and understand local market dynamics." />
            </div>
            
            <Suspense fallback={
              <div className="flex items-center justify-center py-8">
                <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
              </div>
            }>
              <LocationInput
                value={formData.location}
                onChange={(value) => setFormData({...formData, location: value})}
                onBusinessEnriched={handleBusinessEnriched}
                placeholder="123 Main St, New York, NY 10001"
                autoFocus
              />
            </Suspense>
          </section>
          
          {/* SECTION 2: Basic Info */}
          <section className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 transition-all hover:shadow-md">
            <div className="flex items-start gap-4 mb-6">
              <div className="p-2 bg-gray-50 rounded-lg shrink-0">
                <FileText className="w-6 h-6 text-gray-600" />
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900">
                  Basic Information
                </h3>
                <p className="text-sm text-gray-500 mt-1">
                  Add your social media to help us analyze your current presence.
                </p>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="col-span-1 md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1.5">
                  Business Name
                </label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all text-sm"
                  placeholder="Taqueria El Sabor"
                  value={formData.businessName}
                  onChange={(e) => setFormData({...formData, businessName: e.target.value})}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5 flex items-center gap-2">
                  <Instagram className="w-4 h-4" />
                  Instagram
                </label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all text-sm"
                  placeholder="@yourbusiness"
                  value={formData.instagram}
                  onChange={(e) => setFormData({...formData, instagram: e.target.value})}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5 flex items-center gap-2">
                   Facebook
                </label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all text-sm"
                  placeholder="facebook.com/yourbusiness"
                  value={formData.facebook}
                  onChange={(e) => setFormData({...formData, facebook: e.target.value})}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5 flex items-center gap-2">
                   TikTok
                </label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all text-sm"
                  placeholder="@yourbusiness"
                  value={formData.tiktok}
                  onChange={(e) => setFormData({...formData, tiktok: e.target.value})}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5 flex items-center gap-2">
                   Website
                </label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all text-sm"
                  placeholder="www.yourrestaurant.com"
                  value={formData.website}
                  onChange={(e) => setFormData({...formData, website: e.target.value})}
                />
              </div>
            </div>
          </section>
          
          {/* SECTION 3: Upload Files */}
          <section className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 transition-all hover:shadow-md">
            <div className="flex items-start gap-4 mb-6">
              <div className="p-2 bg-gray-50 rounded-lg shrink-0">
                <Upload className="w-6 h-6 text-gray-600" />
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900">
                  Your Data
                </h3>
                <p className="text-sm text-gray-500 mt-1">
                  Upload what you have. We'll work with anything you provide.
                </p>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <FileUpload
                label="Menu"
                accept=".pdf,image/*"
                icon={<FileText className="w-5 h-5 text-gray-400" />}
                onChange={(files) => setFormData({...formData, menuFiles: files})}
                tooltip="Photo of your menu, or PDF."
                compact
                multiple
              />
              
              <FileUpload
                label="Sales Data"
                accept=".csv,.xlsx"
                icon={<FileText className="w-5 h-5 text-gray-400" />}
                onChange={(files) => setFormData({...formData, salesFiles: files})}
                tooltip="CSV or Excel with sales history."
                compact
              />
              
              <FileUpload
                label="Visual Context"
                accept="image/*,video/*"
                multiple
                icon={<Upload className="w-5 h-5 text-gray-400" />}
                onChange={(files) => setFormData({...formData, photoFiles: files})}
                tooltip="Dish photos, ambiance videos, social screenshots."
                compact
              />
            </div>
          </section>
          
          {/* SECTION 4: Business Context */}
          <section className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 transition-all hover:shadow-md">
            <div className="flex items-start gap-4 mb-6">
              <div className="p-2 bg-gray-50 rounded-lg shrink-0">
                <Mic className="w-6 h-6 text-gray-600" />
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900">
                  Tell Us Your Story
                </h3>
                <p className="text-sm text-gray-500 mt-1">
                  The more context you provide, the more personalized your strategy.
                </p>
              </div>
            </div>
            
            <div className="mb-6">
              <TemplateSelector
                onSelect={(templateContext) => {
                  setFormData(prev => ({
                    ...prev,
                    ...templateContext
                  }));
                }}
              />
            </div>
            
            <div className="space-y-4">
              <ContextInput
                label="Your History & Story"
                placeholder="Example: We've been serving authentic Oaxacan cuisine for 3 generations..."
                value={formData.historyContext}
                onChange={(value) => setFormData({...formData, historyContext: value})}
                allowAudio
                onAudioChange={(audios) => setFormData({...formData, historyAudio: audios})}
                template="How did you start? What's the story behind your recipes?"
                detailedTemplate="Our restaurant was founded in 1985 by my grandmother, bringing authentic recipes from Oaxaca..."
              />
              
              <ContextInput
                label="Your Values & Mission"
                placeholder="Example: We prioritize organic, locally-sourced ingredients..."
                value={formData.valuesContext}
                onChange={(value) => setFormData({...formData, valuesContext: value})}
                allowAudio
                onAudioChange={(audios) => setFormData({...formData, valuesAudio: audios})}
                template="What do you stand for? Sustainability? Community?"
                detailedTemplate="We believe in 'Farm to Table' integrity..."
              />
              
              <ContextInput
                label="Target Customers"
                placeholder="Example: Health-conscious millennials who value sustainability..."
                value={formData.targetAudienceContext}
                onChange={(value) => setFormData({...formData, targetAudienceContext: value})}
                allowAudio
                onAudioChange={(audios) => setFormData({...formData, targetAudienceAudio: audios})}
                template="Who comes to your restaurant? Who do you WANT to come?"
                detailedTemplate="Our core customers are young professionals (25-35)..."
              />
              
              <ContextInput
                label="Current Challenges"
                placeholder="Example: Struggling to attract dinner crowd..."
                value={formData.challengesContext}
                onChange={(value) => setFormData({...formData, challengesContext: value})}
                allowAudio
                onAudioChange={(audios) => setFormData({...formData, challengesAudio: audios})}
                template="What keeps you up at night? Low traffic? Staffing?"
                detailedTemplate="Our biggest challenge is the dinner service..."
              />
              
              <ContextInput
                label="Goals & Ambitions"
                placeholder="Example: Expand to 3 locations in next 2 years..."
                value={formData.goalsContext}
                onChange={(value) => setFormData({...formData, goalsContext: value})}
                allowAudio
                onAudioChange={(audios) => setFormData({...formData, goalsAudio: audios})}
                template="Where do you see the business in 1-2 years?"
                detailedTemplate="We want to open a second location in the downtown area..."
              />
            </div>
          </section>
          
          {/* SECTION 5: Competitors */}
          <section className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 transition-all hover:shadow-md">
            <div className="flex items-start gap-4 mb-6">
              <div className="p-2 bg-gray-50 rounded-lg shrink-0">
                <Target className="w-6 h-6 text-gray-600" />
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900">
                  Competitors (Optional)
                </h3>
                <p className="text-sm text-gray-500 mt-1">
                  Leave blank and we'll find them automatically based on your location.
                </p>
              </div>
            </div>
            
            <div className="space-y-4">
              <ContextInput
                label="Competitor Notes & Links"
                placeholder="Paste Instagram links or record audio notes..."
                value={formData.competitorInput}
                onChange={(value) => setFormData({...formData, competitorInput: value})}
                allowAudio
                onAudioChange={(audios) => setFormData({...formData, competitorAudio: audios})}
                template="Mention specific competitors by name, or paste their URLs."
                detailedTemplate="Our main competitor is 'Taco King' across the street..."
              />
              
              <FileUpload
                label="Competitor Menus & Photos"
                accept=".pdf,image/*,video/*"
                multiple
                icon={<Upload className="w-5 h-5 text-gray-400" />}
                onChange={(files) => setFormData({...formData, competitorFiles: files})}
                tooltip="Upload menus, food photos of competitors."
                compact
              />
            </div>
          </section>
          
        </div>
        
        {/* CTA Section */}
        <div className="mt-10 sticky bottom-6 z-40">
           <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-4 sm:px-6 max-w-5xl mx-auto">
             {/* Configuration Toggles */}
             <div className="flex flex-wrap items-center gap-4 mb-4 pb-4 border-b">
               <div className="flex items-center gap-2">
                 <input
                   type="checkbox"
                   id="autoVerify"
                   checked={autoVerify}
                   onChange={(e) => setAutoVerify(e.target.checked)}
                   className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
                 />
                 <label htmlFor="autoVerify" className="text-sm font-medium text-gray-700 cursor-pointer">
                   ✓ Enable Auto-Verification
                 </label>
               </div>
               
               <div className="flex items-center gap-2">
                 <input
                   type="checkbox"
                   id="autoImprove"
                   checked={autoImprove}
                   onChange={(e) => setAutoImprove(e.target.checked)}
                   className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
                 />
                 <label htmlFor="autoImprove" className="text-sm font-medium text-gray-700 cursor-pointer">
                   🚀 Auto-Improve Results
                 </label>
               </div>
               
               <div className="text-xs text-gray-500 ml-auto">
                 Powered by Gemini 3 Multimodal AI
               </div>
             </div>
             
             {/* Main Button and Data Quality */}
             <div className="flex items-center justify-between">
               <div>
                <div className="text-sm font-medium text-gray-900">
                  Data Quality: <span className={completionScore < 30 ? 'text-red-600' : completionScore < 60 ? 'text-yellow-600' : 'text-green-600'}>
                    {completionScore < 30 ? 'Minimal' : completionScore < 60 ? 'Good' : 'Excellent'}
                  </span>
                </div>
                <div className="text-xs text-gray-500 mt-0.5">
                  {completionScore < 30 && "Add more info for better insights"}
                  {completionScore >= 30 && completionScore < 60 && "Great start! Add context for personalization"}
                  {completionScore >= 60 && "Perfect! You'll get highly personalized insights"}
                </div>
              </div>
              
              <button
                onClick={handleSubmit}
                disabled={!formData.location || loadingState.stage !== 'idle'}
                className={`px-6 py-2.5 rounded-lg font-medium text-white transition-all flex items-center gap-2 shadow-sm ${
                  formData.location && loadingState.stage === 'idle'
                    ? 'bg-blue-600 hover:bg-blue-700 hover:shadow-md'
                    : 'bg-gray-300 cursor-not-allowed'
                }`}
              >
                {loadingState.type === 'analysis' && loadingState.stage === 'loading' ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Starting...
                  </>
                ) : (
                  <>
                    {formData.location ? 'Analyze My Business' : 'Add Location First'}
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
        
      </main>
      
      <Suspense fallback={null}>
        <GeminiChat />
      </Suspense>

      {/* Loading Overlay */}
      {loadingState.stage !== 'idle' && (
        <div className="fixed inset-0 bg-white/80 backdrop-blur-sm z-[100] flex items-center justify-center transition-all duration-300">
          <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8 max-w-sm w-full mx-4 text-center transform transition-all duration-300 scale-100 animate-in fade-in zoom-in-95">
            {loadingState.stage === 'loading' ? (
              <div className="space-y-4">
                <div className="relative w-20 h-20 mx-auto">
                  <div className="w-full h-full border-4 border-blue-100 border-t-blue-600 rounded-full animate-spin"></div>
                  <div className="absolute inset-0 flex items-center justify-center">
                    {loadingState.type === 'demo' ? (
                      <Sparkles className="w-8 h-8 text-blue-600 animate-pulse" />
                    ) : (
                      <Target className="w-8 h-8 text-blue-600 animate-pulse" />
                    )}
                  </div>
                </div>
                <div>
                  <h3 className="text-xl font-bold text-gray-900">
                    {loadingState.type === 'demo' ? 'Loading Demo' : 'Analyzing Business'}
                  </h3>
                  <p className="text-sm text-gray-500 mt-2 min-h-[1.25rem] transition-all duration-300">
                    {loadingMessage}
                  </p>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto animate-in zoom-in duration-300">
                  <CheckCircle2 className="w-10 h-10 text-green-600" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-gray-900">Ready!</h3>
                  <p className="text-sm text-gray-500 mt-2">
                    {loadingState.type === 'demo'
                      ? 'Demo loaded successfully'
                      : 'Analysis complete. Taking you there...'}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
