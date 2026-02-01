'use client';

import { useState } from 'react';
import { MenuTransformation } from '@/components/creative/MenuTransformation';
import { InstagramPredictor } from '@/components/creative/InstagramPredictor';
import { Palette, TrendingUp, Sparkles } from 'lucide-react';

export function CreativeStudio() {
  const [activeTab, setActiveTab] = useState<'transform' | 'predict'>('transform');

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-100 to-blue-100 rounded-3xl p-8 border border-white/50 shadow-sm">
        <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-3">
          <Sparkles className="w-8 h-8 text-purple-600" />
          Creative Studio
        </h1>
        <p className="text-lg text-gray-600 max-w-2xl">
          Use Gemini 3's multimodal capabilities to reimagine your menu and predict social media success before you post.
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-4 border-b border-gray-200">
        <button
          onClick={() => setActiveTab('transform')}
          className={`pb-4 px-2 flex items-center gap-2 font-medium transition-colors relative ${
            activeTab === 'transform'
              ? 'text-purple-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          <Palette className="w-5 h-5" />
          Menu Transformation
          {activeTab === 'transform' && (
            <div className="absolute bottom-0 left-0 w-full h-0.5 bg-purple-600 rounded-t-full" />
          )}
        </button>

        <button
          onClick={() => setActiveTab('predict')}
          className={`pb-4 px-2 flex items-center gap-2 font-medium transition-colors relative ${
            activeTab === 'predict'
              ? 'text-pink-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          <TrendingUp className="w-5 h-5" />
          Instagram Predictor
          {activeTab === 'predict' && (
            <div className="absolute bottom-0 left-0 w-full h-0.5 bg-pink-600 rounded-t-full" />
          )}
        </button>
      </div>

      {/* Content */}
      <div className="min-h-[600px]">
        {activeTab === 'transform' ? (
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
            <MenuTransformation />
          </div>
        ) : (
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
            <InstagramPredictor />
          </div>
        )}
      </div>
    </div>
  );
}
