'use client';

import { ChefHat, Sparkles, TrendingUp, DollarSign, Users, Zap, ArrowRight, Play, Brain, BarChart3 } from 'lucide-react';

interface LandingHeroProps {
  onGetStarted: () => void;
  onTryDemo: () => void;
  isDemoLoading?: boolean;
}

export default function LandingHero({ onGetStarted, onTryDemo, isDemoLoading }: LandingHeroProps) {
  const impactMetrics = [
    { icon: DollarSign, value: '+15%', label: 'Revenue Increase', color: 'text-green-500' },
    { icon: TrendingUp, value: '+23%', label: 'Menu Optimization', color: 'text-blue-500' },
    { icon: Users, value: '10K+', label: 'Items Analyzed', color: 'text-purple-500' },
    { icon: Zap, value: '<5min', label: 'Analysis Time', color: 'text-orange-500' },
  ];

  const features = [
    {
      icon: Brain,
      title: 'AI-Powered Analysis',
      description: 'Gemini 3 multimodal AI extracts menu items from images, analyzes sales data, and provides actionable insights.',
    },
    {
      icon: BarChart3,
      title: 'BCG Matrix Classification',
      description: 'Automatically classify products as Stars, Cash Cows, Question Marks, or Dogs based on performance metrics.',
    },
    {
      icon: TrendingUp,
      title: 'Demand Prediction',
      description: 'Forecast daily and hourly demand patterns to optimize staffing and inventory.',
    },
  ];

  return (
    <div className="relative overflow-hidden">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary-50 via-white to-indigo-50" />
      
      {/* Hero Section */}
      <div className="relative max-w-7xl mx-auto px-4 py-16 sm:px-6 lg:px-8">
        <div className="text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary-100 text-primary-700 rounded-full text-sm font-medium mb-6">
            <Sparkles className="w-4 h-4" />
            Powered by Google Gemini 3
          </div>

          {/* Main Title */}
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
            Transform Your Restaurant
            <br />
            <span className="bg-gradient-to-r from-primary-600 to-indigo-600 bg-clip-text text-transparent">
              with AI Intelligence
            </span>
          </h1>

          {/* Subtitle */}
          <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-8">
            Upload your menu, sales data, or restaurant images. Get instant AI-powered insights, 
            BCG classification, demand predictions, and marketing campaigns.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-12">
            <button
              onClick={onGetStarted}
              className="px-8 py-4 bg-gradient-to-r from-primary-600 to-indigo-600 text-white font-semibold rounded-xl hover:shadow-lg hover:scale-105 transition-all flex items-center gap-2"
            >
              Get Started Free
              <ArrowRight className="w-5 h-5" />
            </button>
            <button
              onClick={onTryDemo}
              disabled={isDemoLoading}
              className="px-8 py-4 bg-white text-gray-700 font-semibold rounded-xl border-2 border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-all flex items-center gap-2 disabled:opacity-50"
            >
              {isDemoLoading ? (
                <>
                  <div className="animate-spin h-5 w-5 border-2 border-primary-500 border-t-transparent rounded-full" />
                  Loading...
                </>
              ) : (
                <>
                  <Play className="w-5 h-5" />
                  Try Demo
                </>
              )}
            </button>
          </div>

          {/* Impact Metrics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-3xl mx-auto mb-16">
            {impactMetrics.map((metric, idx) => (
              <div key={idx} className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
                <metric.icon className={`w-8 h-8 ${metric.color} mx-auto mb-2`} />
                <div className="text-2xl font-bold text-gray-900">{metric.value}</div>
                <div className="text-sm text-gray-500">{metric.label}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-6 mt-8">
          {features.map((feature, idx) => (
            <div key={idx} className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
              <div className="p-3 bg-primary-100 rounded-lg w-fit mb-4">
                <feature.icon className="w-6 h-6 text-primary-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">{feature.title}</h3>
              <p className="text-gray-600 text-sm">{feature.description}</p>
            </div>
          ))}
        </div>

        {/* Gemini Features */}
        <div className="mt-16 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl p-8 text-white">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold mb-2">Built with Gemini 3 Capabilities</h2>
            <p className="text-indigo-100">Leveraging the full power of Google&apos;s most advanced AI</p>
          </div>
          <div className="grid md:grid-cols-5 gap-4">
            {[
              { title: '1M Tokens', desc: 'Long context memory' },
              { title: 'Multimodal', desc: 'Images, audio, text' },
              { title: 'Function Calling', desc: 'Structured actions' },
              { title: 'Reasoning', desc: 'Multi-step thinking' },
              { title: 'Real-time Chat', desc: 'Interactive AI' },
            ].map((cap, idx) => (
              <div key={idx} className="bg-white/10 backdrop-blur-sm rounded-lg p-4 text-center">
                <div className="font-semibold">{cap.title}</div>
                <div className="text-xs text-indigo-200">{cap.desc}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Trust Badge */}
        <div className="mt-12 text-center">
          <p className="text-sm text-gray-500">
            🏆 Built for Google Gemini 3 Hackathon • Open Source • Privacy First
          </p>
        </div>
      </div>
    </div>
  );
}
