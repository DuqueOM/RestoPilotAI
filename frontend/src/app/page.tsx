'use client';

import { GeminiChat } from '@/components/chat/GeminiChat';
import { ContextInput } from '@/components/setup/ContextInput';
import { FileUpload } from '@/components/setup/FileUpload';
import { InfoTooltip } from '@/components/setup/InfoTooltip';
import { LocationInput } from '@/components/setup/LocationInput';
import { ProgressBar } from '@/components/setup/ProgressBar';
import { TemplateSelector } from '@/components/setup/TemplateSelector';
import {
    FileText,
    Instagram,
    Loader2,
    MapPin,
    Mic,
    Sparkles,
    Upload
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function SetupPage() {
  const router = useRouter();
  const [completionScore, setCompletionScore] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
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
  
  const handleSubmit = async () => {
    if (!formData.location) return;
    
    setIsSubmitting(true);
    try {
      const data = new FormData();
      
      // Basic info
      data.append('location', formData.location);
      if (formData.businessName) data.append('businessName', formData.businessName);
      if (formData.instagram) data.append('instagram', formData.instagram);
      if (formData.facebook) data.append('facebook', formData.facebook);
      if (formData.tiktok) data.append('tiktok', formData.tiktok);
      if (formData.website) data.append('website', formData.website);
      
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
      router.push(`/analysis/${analysis_id}`);
    } catch (error) {
      console.error('Error starting analysis:', error);
      toast.error('Failed to start analysis. Please try again.');
      setIsSubmitting(false);
    }
  };
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-white to-blue-50">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold bg-gradient-to-r from-orange-500 to-blue-600 bg-clip-text text-transparent">
              🍽️ RestoPilotAI
            </h1>
            <div className="flex items-center gap-4 w-1/3">
              <ProgressBar 
                value={completionScore} 
                label={`${completionScore}% Complete`}
              />
            </div>
          </div>
        </div>
      </header>
      
      <main className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Hero Section */}
        <div className="text-center mb-8 space-y-4">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-orange-100 to-blue-100 rounded-full">
            <Sparkles className="w-4 h-4 text-orange-600" />
            <span className="text-sm font-medium text-gray-700">
              Powered by Gemini 3 Multimodal AI
            </span>
          </div>
          
          <h2 className="text-4xl font-bold text-gray-900">
            Discover Your Competitive Edge
          </h2>
          
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Just tell us where you are. We'll find your competitors, analyze your market,
            and create a winning strategy. All in 5 minutes.
          </p>
        </div>
        
        {/* Form Sections - Progressive Disclosure */}
        <div className="space-y-6">
          
          {/* SECTION 1: Location (MOST IMPORTANT - Always visible) */}
          <section className="bg-white rounded-2xl shadow-lg p-6 border-2 border-orange-200">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-full bg-orange-100 flex items-center justify-center">
                <MapPin className="w-5 h-5 text-orange-600" />
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900">
                  Where is your restaurant?
                </h3>
                <p className="text-sm text-gray-600">
                  This is all we need to get started. Everything else is optional but helps.
                </p>
              </div>
              <InfoTooltip content="We'll use this to find competitors, analyze your neighborhood, and understand local market dynamics. The more specific, the better!" />
            </div>
            
            <LocationInput
              value={formData.location}
              onChange={(value) => setFormData({...formData, location: value})}
              placeholder="123 Main St, New York, NY 10001"
              autoFocus
            />
          </section>
          
          {/* SECTION 2: Basic Info (Compact) */}
          <section className="bg-white rounded-2xl shadow-lg p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
                <FileText className="w-5 h-5 text-blue-600" />
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900">
                  Basic Information
                </h3>
                <p className="text-sm text-gray-600">
                  Add your social media to help us analyze your current presence.
                </p>
              </div>
              <InfoTooltip content="This helps us find your existing social media and online presence automatically." />
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="col-span-1 md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Business Name
                </label>
                <input
                  type="text"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Taquería El Sabor"
                  value={formData.businessName}
                  onChange={(e) => setFormData({...formData, businessName: e.target.value})}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                  <Instagram className="w-4 h-4" />
                  Instagram
                </label>
                <input
                  type="text"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="@yourbusiness"
                  value={formData.instagram}
                  onChange={(e) => setFormData({...formData, instagram: e.target.value})}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                   Facebook
                </label>
                <input
                  type="text"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="facebook.com/yourbusiness"
                  value={formData.facebook}
                  onChange={(e) => setFormData({...formData, facebook: e.target.value})}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                   TikTok
                </label>
                <input
                  type="text"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="@yourbusiness"
                  value={formData.tiktok}
                  onChange={(e) => setFormData({...formData, tiktok: e.target.value})}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                   Website
                </label>
                <input
                  type="text"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="www.yourrestaurant.com"
                  value={formData.website}
                  onChange={(e) => setFormData({...formData, website: e.target.value})}
                />
              </div>
            </div>
          </section>
          
          {/* SECTION 3: Upload Files (Optimized spacing) */}
          <section className="bg-white rounded-2xl shadow-lg p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-full bg-purple-100 flex items-center justify-center">
                <Upload className="w-5 h-5 text-purple-600" />
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900">
                  Your Data
                </h3>
                <p className="text-sm text-gray-600">
                  Upload what you have. We'll work with anything you provide.
                </p>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <FileUpload
                label="Menu"
                accept=".pdf,image/*"
                icon={<FileText className="w-6 h-6 text-gray-400" />}
                onChange={(files) => setFormData({...formData, menuFiles: files})}
                tooltip="Photo of your menu, or PDF. We'll extract all items and prices automatically."
                compact
                multiple
              />
              
              <FileUpload
                label="Sales Data"
                accept=".csv,.xlsx"
                icon={<FileText className="w-6 h-6 text-gray-400" />}
                onChange={(files) => setFormData({...formData, salesFiles: files})}
                tooltip="CSV or Excel with sales history. Helps us predict trends and do BCG analysis."
                compact
              />
              
              <FileUpload
                label="Visual Context"
                accept="image/*,video/*"
                multiple
                icon={<Upload className="w-6 h-6 text-gray-400" />}
                onChange={(files) => setFormData({...formData, photoFiles: files})}
                tooltip="Upload ANY visual content: Dish photos, videos of the ambiance, screenshots of your social media, decor, or anything else. Gemini 3 will analyze it all for suggestions!"
                compact
              />
            </div>
          </section>
          
          {/* SECTION 4: Business Context (Collapsible with Templates) */}
          <section className="bg-white rounded-2xl shadow-lg p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center">
                <Mic className="w-5 h-5 text-green-600" />
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900">
                  Tell Us Your Story
                </h3>
                <p className="text-sm text-gray-600">
                  The more context you provide, the more personalized your strategy
                </p>
              </div>
              <InfoTooltip content="This context makes our AI understand YOUR unique situation. Campaigns will reference your authentic story, not generic templates." />
            </div>
            
            <TemplateSelector
              onSelect={(templateContext) => {
                // Pre-fill with template examples
                setFormData(prev => ({
                  ...prev,
                  ...templateContext
                }));
              }}
            />
            
            <div className="space-y-4 mt-4">
              <ContextInput
                label="Your History & Story"
                placeholder="Example: We've been serving authentic Oaxacan cuisine for 3 generations..."
                value={formData.historyContext}
                onChange={(value) => setFormData({...formData, historyContext: value})}
                allowAudio
                onAudioChange={(audios) => setFormData({...formData, historyAudio: audios})}
                template="How did you start? What's the story behind your recipes? Any family traditions?"
                detailedTemplate="Our restaurant was founded in 1985 by my grandmother, bringing authentic recipes from Oaxaca. We started as a small street cart and grew into a family gathering spot. Our signature mole sauce takes 3 days to prepare and has been in the family for 4 generations. We want to preserve this tradition while adapting to modern times."
              />
              
              <ContextInput
                label="Your Values & Mission"
                placeholder="Example: We prioritize organic, locally-sourced ingredients..."
                value={formData.valuesContext}
                onChange={(value) => setFormData({...formData, valuesContext: value})}
                allowAudio
                onAudioChange={(audios) => setFormData({...formData, valuesAudio: audios})}
                template="What do you stand for? Sustainability? Community? Authenticity?"
                detailedTemplate="We believe in 'Farm to Table' integrity. We source 80% of our ingredients from local farmers within 50 miles. We prioritize fair wages for our staff and zero-waste cooking practices. Our mission is to show that fast food can be healthy, sustainable, and deeply connected to the community."
              />
              
              <ContextInput
                label="Target Customers"
                placeholder="Example: Health-conscious millennials who value sustainability..."
                value={formData.targetAudienceContext}
                onChange={(value) => setFormData({...formData, targetAudienceContext: value})}
                allowAudio
                onAudioChange={(audios) => setFormData({...formData, targetAudienceAudio: audios})}
                template="Who comes to your restaurant? Who do you WANT to come?"
                detailedTemplate="Our core customers are young professionals (25-35) looking for quick but high-quality lunch options. We also attract health-conscious families on weekends. We are trying to reach more of the Gen Z crowd who value aesthetic food for social media, but we struggle to connect with them digitally."
              />
              
              <ContextInput
                label="Current Challenges"
                placeholder="Example: Struggling to attract dinner crowd, mostly lunch customers..."
                value={formData.challengesContext}
                onChange={(value) => setFormData({...formData, challengesContext: value})}
                allowAudio
                onAudioChange={(audios) => setFormData({...formData, challengesAudio: audios})}
                template="What keeps you up at night? Low traffic? High costs? Staffing?"
                detailedTemplate="Our biggest challenge is the dinner service on weekdays (Mon-Thu), which is very slow compared to lunch. Food costs have risen 15% this year, squeezing our margins. We also find it hard to retain kitchen staff. We need marketing that drives evening traffic specifically."
              />
              
              <ContextInput
                label="Goals & Ambitions"
                placeholder="Example: Expand to 3 locations in next 2 years..."
                value={formData.goalsContext}
                onChange={(value) => setFormData({...formData, goalsContext: value})}
                allowAudio
                onAudioChange={(audios) => setFormData({...formData, goalsAudio: audios})}
                template="Where do you see the business in 1-2 years?"
                detailedTemplate="We want to open a second location in the downtown area next year. To do that, we need to increase our monthly revenue by 20% and stabilize our operations manual. We also want to launch a packaged version of our signature hot sauce for retail sale."
              />
            </div>
          </section>
          
          {/* SECTION 5: Competitors (Optional) */}
          <section className="bg-white rounded-2xl shadow-lg p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900">
                  Know Your Competitors?
                </h3>
                <p className="text-sm text-gray-600">
                  Leave blank and we'll find them automatically based on your location
                </p>
              </div>
              <InfoTooltip content="We'll automatically find 5-10 competitors near you. But if you know specific ones you want to track, add them here." />
            </div>
            
            <div className="space-y-4">
              <div className="p-4 bg-blue-50 rounded-lg border border-blue-100 text-sm text-blue-800">
                <strong>New:</strong> You can now upload competitor menus, photos, or paste mixed links and notes!
              </div>

              <ContextInput
                label="Competitor Notes & Links"
                placeholder="Paste Instagram links, website URLs, or record audio notes about your competitors..."
                value={formData.competitorInput}
                onChange={(value) => setFormData({...formData, competitorInput: value})}
                allowAudio
                onAudioChange={(audios) => setFormData({...formData, competitorAudio: audios})}
                template="Mention specific competitors by name, their strengths/weaknesses, or paste their URLs."
                detailedTemplate="Our main competitor is 'Taco King' across the street. They have cheaper prices ($2 tacos) but lower quality. Another one is 'Mezcal Bar' which steals our Friday night crowd because they have live music. I want to know how to position against these two specifically."
              />
              
              <FileUpload
                label="Competitor Menus & Photos"
                accept=".pdf,image/*,video/*"
                multiple
                icon={<Upload className="w-6 h-6 text-gray-400" />}
                onChange={(files) => setFormData({...formData, competitorFiles: files})}
                tooltip="Upload menus, food photos, or videos of your competitors. We'll extract the data."
                compact
              />
            </div>
          </section>
          
        </div>
        
        {/* CTA Section */}
        <div className="mt-8 sticky bottom-0 bg-white/90 backdrop-blur-md border-t p-6 -mx-4">
          <div className="max-w-4xl mx-auto flex items-center justify-between">
            <div>
              <div className="text-sm text-gray-600">
                Data Quality: {completionScore < 30 ? '⚠️ Minimal' : completionScore < 60 ? '✅ Good' : '🚀 Excellent'}
              </div>
              <div className="text-xs text-gray-500 mt-1">
                {completionScore < 30 && "Add more info for better insights"}
                {completionScore >= 30 && completionScore < 60 && "Great start! Add context for personalization"}
                {completionScore >= 60 && "Perfect! You'll get highly personalized insights"}
              </div>
            </div>
            
            <button
              onClick={handleSubmit}
              disabled={!formData.location || isSubmitting}
              className={`px-8 py-3 rounded-lg font-semibold text-white transition-all flex items-center gap-2 ${
                formData.location && !isSubmitting
                  ? 'bg-gradient-to-r from-orange-500 to-blue-600 hover:shadow-lg hover:scale-105'
                  : 'bg-gray-300 cursor-not-allowed'
              }`}
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Starting Analysis...
                </>
              ) : (
                <>
                  {formData.location ? '🚀 Analyze My Business' : '📍 Add Location First'}
                </>
              )}
            </button>
          </div>
        </div>
        
      </main>
      
      <GeminiChat />
    </div>
  );
}
