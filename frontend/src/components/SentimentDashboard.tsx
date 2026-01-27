'use client';

import React, { useState } from 'react';

interface ItemSentiment {
  itemName: string;
  bcgCategory?: 'star' | 'cash_cow' | 'question_mark' | 'dog';
  textSentiment: {
    score: number;
    mentionCount: number;
    commonDescriptors: string[];
  };
  visualSentiment: {
    appealScore?: number;
    presentationScore?: number;
    portionPerception?: 'very_small' | 'small' | 'adequate' | 'generous' | 'very_generous';
    portionScore?: number;
    photoCount: number;
  };
  overallSentiment: 'very_positive' | 'positive' | 'neutral' | 'negative' | 'very_negative';
  actionableInsight: string;
  priority: 'high' | 'medium' | 'low';
}

interface SentimentAnalysis {
  analysisId: string;
  overall: {
    sentimentScore: number;
    nps?: number;
    sentimentDistribution: {
      very_positive: number;
      positive: number;
      neutral: number;
      negative: number;
      very_negative: number;
    };
  };
  counts: {
    reviewsAnalyzed: number;
    photosAnalyzed: number;
    sourcesUsed: string[];
  };
  themes: {
    praises: string[];
    complaints: string[];
  };
  categorySentiments: {
    service?: number;
    foodQuality?: number;
    ambiance?: number;
    value?: number;
  };
  itemSentiments: ItemSentiment[];
  recommendations: Array<{
    priority: string;
    type: string;
    items?: string[];
    issue: string;
    action: string;
    expectedImpact: string;
  }>;
}

interface SentimentDashboardProps {
  analysis?: SentimentAnalysis;
  isLoading?: boolean;
}

export default function SentimentDashboard({ 
  analysis, 
  isLoading = false 
}: SentimentDashboardProps) {
  const [activeView, setActiveView] = useState<'overview' | 'items' | 'recommendations'>('overview');
  const [sortBy, setSortBy] = useState<'sentiment' | 'mentions' | 'priority'>('priority');

  if (isLoading) {
    return (
      <div className="animate-pulse space-y-4">
        <div className="h-8 bg-gray-200 rounded w-1/4"></div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-32 bg-gray-200 rounded-lg"></div>
          ))}
        </div>
        <div className="h-64 bg-gray-200 rounded-lg"></div>
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className="text-center py-12 bg-gray-50 rounded-lg">
        <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
        <h3 className="mt-2 text-sm font-medium text-gray-900">No sentiment data</h3>
        <p className="mt-1 text-sm text-gray-500">Connect review sources to see customer sentiment.</p>
      </div>
    );
  }

  const getSentimentColor = (score: number) => {
    if (score >= 0.5) return 'text-green-600 bg-green-100';
    if (score >= 0.2) return 'text-green-500 bg-green-50';
    if (score >= -0.2) return 'text-gray-600 bg-gray-100';
    if (score >= -0.5) return 'text-orange-600 bg-orange-100';
    return 'text-red-600 bg-red-100';
  };

  const getSentimentEmoji = (sentiment: string) => {
    switch (sentiment) {
      case 'very_positive': return '😍';
      case 'positive': return '😊';
      case 'neutral': return '😐';
      case 'negative': return '😕';
      case 'very_negative': return '😠';
      default: return '😐';
    }
  };

  const getPortionColor = (portion?: string) => {
    switch (portion) {
      case 'very_small':
      case 'small': return 'bg-red-100 text-red-800';
      case 'adequate': return 'bg-gray-100 text-gray-800';
      case 'generous':
      case 'very_generous': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-600';
    }
  };

  const getBcgBadge = (category?: string) => {
    switch (category) {
      case 'star': return { label: '⭐ Star', color: 'bg-yellow-100 text-yellow-800' };
      case 'cash_cow': return { label: '🐄 Cash Cow', color: 'bg-green-100 text-green-800' };
      case 'question_mark': return { label: '❓ Question', color: 'bg-blue-100 text-blue-800' };
      case 'dog': return { label: '🐕 Dog', color: 'bg-gray-100 text-gray-800' };
      default: return null;
    }
  };

  const sortedItems = [...(analysis.itemSentiments || [])].sort((a, b) => {
    switch (sortBy) {
      case 'sentiment':
        return b.textSentiment.score - a.textSentiment.score;
      case 'mentions':
        return b.textSentiment.mentionCount - a.textSentiment.mentionCount;
      case 'priority':
        const priorityOrder = { high: 0, medium: 1, low: 2 };
        return priorityOrder[a.priority] - priorityOrder[b.priority];
      default:
        return 0;
    }
  });

  const categoryLabels: Record<string, { label: string; emoji: string }> = {
    service: { label: 'Service', emoji: '👋' },
    foodQuality: { label: 'Food Quality', emoji: '🍽️' },
    ambiance: { label: 'Ambiance', emoji: '✨' },
    value: { label: 'Value', emoji: '💰' },
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">💬 Customer Sentiment</h2>
          <p className="mt-1 text-sm text-gray-500">
            Based on {analysis.counts.reviewsAnalyzed} reviews and {analysis.counts.photosAnalyzed} photos
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="text-center">
            <div className={`text-3xl font-bold ${analysis.overall.sentimentScore >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {analysis.overall.sentimentScore >= 0 ? '+' : ''}{(analysis.overall.sentimentScore * 100).toFixed(0)}
            </div>
            <div className="text-xs text-gray-500">Sentiment Score</div>
          </div>
          {analysis.overall.nps !== undefined && (
            <div className="text-center border-l pl-4">
              <div className={`text-3xl font-bold ${analysis.overall.nps >= 50 ? 'text-green-600' : analysis.overall.nps >= 0 ? 'text-yellow-600' : 'text-red-600'}`}>
                {analysis.overall.nps}
              </div>
              <div className="text-xs text-gray-500">NPS</div>
            </div>
          )}
        </div>
      </div>

      {/* View Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'overview', label: '📊 Overview' },
            { id: 'items', label: '🍽️ By Item' },
            { id: 'recommendations', label: '💡 Actions' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveView(tab.id as any)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeView === tab.id
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Overview Tab */}
      {activeView === 'overview' && (
        <div className="space-y-6">
          {/* Sentiment Distribution */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Sentiment Distribution</h3>
            <div className="flex items-center space-x-2">
              {Object.entries(analysis.overall.sentimentDistribution).map(([key, value]) => (
                <div key={key} className="flex-1">
                  <div 
                    className={`h-8 rounded ${
                      key === 'very_positive' ? 'bg-green-500' :
                      key === 'positive' ? 'bg-green-300' :
                      key === 'neutral' ? 'bg-gray-300' :
                      key === 'negative' ? 'bg-orange-300' :
                      'bg-red-400'
                    }`}
                    style={{ opacity: Math.max(0.3, value / 100) }}
                  >
                    <span className="text-xs text-white font-medium p-1">
                      {value}%
                    </span>
                  </div>
                  <div className="text-xs text-gray-500 mt-1 text-center capitalize">
                    {key.replace('_', ' ')}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Category Sentiments */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(analysis.categorySentiments).map(([key, value]) => {
              if (value === null || value === undefined) return null;
              const info = categoryLabels[key];
              return (
                <div key={key} className="bg-white rounded-lg shadow p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-2xl">{info?.emoji}</span>
                    <span className={`px-2 py-1 rounded-full text-sm font-medium ${getSentimentColor(value)}`}>
                      {value >= 0 ? '+' : ''}{(value * 100).toFixed(0)}
                    </span>
                  </div>
                  <h4 className="text-sm font-medium text-gray-900">{info?.label}</h4>
                  <div className="mt-2 h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div 
                      className={`h-full rounded-full ${value >= 0.5 ? 'bg-green-500' : value >= 0 ? 'bg-green-300' : value >= -0.5 ? 'bg-orange-300' : 'bg-red-400'}`}
                      style={{ width: `${Math.abs(value) * 100}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>

          {/* Themes */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Praises */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
                <span className="mr-2">👍</span> What Customers Love
              </h3>
              <ul className="space-y-2">
                {analysis.themes.praises.slice(0, 5).map((praise, idx) => (
                  <li key={idx} className="flex items-start p-2 bg-green-50 rounded-lg">
                    <span className="flex-shrink-0 text-green-500 mr-2">✓</span>
                    <span className="text-sm text-gray-700">{praise}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Complaints */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
                <span className="mr-2">👎</span> Common Complaints
              </h3>
              <ul className="space-y-2">
                {analysis.themes.complaints.slice(0, 5).map((complaint, idx) => (
                  <li key={idx} className="flex items-start p-2 bg-red-50 rounded-lg">
                    <span className="flex-shrink-0 text-red-500 mr-2">!</span>
                    <span className="text-sm text-gray-700">{complaint}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Items Tab */}
      {activeView === 'items' && (
        <div className="space-y-4">
          {/* Sort Controls */}
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-500">
              {analysis.itemSentiments.length} items analyzed
            </span>
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-500">Sort by:</span>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as any)}
                className="text-sm border-gray-300 rounded-md"
              >
                <option value="priority">Priority</option>
                <option value="sentiment">Sentiment</option>
                <option value="mentions">Mentions</option>
              </select>
            </div>
          </div>

          {/* Item Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {sortedItems.map((item, idx) => {
              const bcgBadge = getBcgBadge(item.bcgCategory);
              return (
                <div key={idx} className="bg-white rounded-lg shadow p-4 border-l-4 border-l-transparent hover:border-l-indigo-500 transition-colors">
                  {/* Header */}
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h4 className="font-medium text-gray-900">{item.itemName}</h4>
                      <div className="flex items-center space-x-2 mt-1">
                        {bcgBadge && (
                          <span className={`px-2 py-0.5 rounded text-xs font-medium ${bcgBadge.color}`}>
                            {bcgBadge.label}
                          </span>
                        )}
                        <span className="text-xs text-gray-500">
                          {item.textSentiment.mentionCount} mentions
                        </span>
                      </div>
                    </div>
                    <span className="text-2xl">{getSentimentEmoji(item.overallSentiment)}</span>
                  </div>

                  {/* Scores */}
                  <div className="grid grid-cols-2 gap-4 mb-3">
                    {/* Text Sentiment */}
                    <div>
                      <span className="text-xs text-gray-500">Review Sentiment</span>
                      <div className="flex items-center mt-1">
                        <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div 
                            className={`h-full ${item.textSentiment.score >= 0 ? 'bg-green-500' : 'bg-red-400'}`}
                            style={{ 
                              width: `${Math.abs(item.textSentiment.score) * 100}%`,
                              marginLeft: item.textSentiment.score < 0 ? 'auto' : 0
                            }}
                          />
                        </div>
                        <span className={`ml-2 text-sm font-medium ${item.textSentiment.score >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {item.textSentiment.score >= 0 ? '+' : ''}{(item.textSentiment.score * 100).toFixed(0)}
                        </span>
                      </div>
                    </div>

                    {/* Visual Appeal */}
                    {item.visualSentiment.appealScore !== undefined && (
                      <div>
                        <span className="text-xs text-gray-500">Photo Appeal</span>
                        <div className="flex items-center mt-1">
                          <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                            <div 
                              className="h-full bg-indigo-500"
                              style={{ width: `${item.visualSentiment.appealScore * 10}%` }}
                            />
                          </div>
                          <span className="ml-2 text-sm font-medium text-indigo-600">
                            {item.visualSentiment.appealScore.toFixed(1)}
                          </span>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Portion Perception */}
                  {item.visualSentiment.portionPerception && (
                    <div className="flex items-center space-x-2 mb-3">
                      <span className="text-xs text-gray-500">Portion:</span>
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${getPortionColor(item.visualSentiment.portionPerception)}`}>
                        {item.visualSentiment.portionPerception.replace('_', ' ')}
                      </span>
                    </div>
                  )}

                  {/* Descriptors */}
                  {item.textSentiment.commonDescriptors.length > 0 && (
                    <div className="mb-3">
                      <div className="flex flex-wrap gap-1">
                        {item.textSentiment.commonDescriptors.slice(0, 4).map((desc, i) => (
                          <span key={i} className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs">
                            {desc}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Insight */}
                  <div className={`p-2 rounded-lg text-sm ${
                    item.priority === 'high' ? 'bg-red-50 text-red-800' :
                    item.priority === 'medium' ? 'bg-yellow-50 text-yellow-800' :
                    'bg-blue-50 text-blue-800'
                  }`}>
                    {item.actionableInsight}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Recommendations Tab */}
      {activeView === 'recommendations' && (
        <div className="space-y-4">
          {analysis.recommendations.map((rec, idx) => (
            <div 
              key={idx} 
              className={`bg-white rounded-lg shadow p-6 border-l-4 ${
                rec.priority === 'high' ? 'border-l-red-500' :
                rec.priority === 'medium' ? 'border-l-yellow-500' :
                'border-l-blue-500'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <span className={`px-2 py-1 rounded text-xs font-medium uppercase ${
                      rec.priority === 'high' ? 'bg-red-100 text-red-800' :
                      rec.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      {rec.priority}
                    </span>
                    <span className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs">
                      {rec.type.replace('_', ' ')}
                    </span>
                  </div>
                  
                  <p className="text-sm text-gray-600 mb-2">
                    <span className="font-medium">Issue:</span> {rec.issue}
                  </p>
                  
                  <p className="text-sm font-medium text-gray-900 mb-2">
                    <span className="text-indigo-600">→</span> {rec.action}
                  </p>
                  
                  <p className="text-sm text-green-600">
                    <span className="font-medium">Expected Impact:</span> {rec.expectedImpact}
                  </p>
                  
                  {rec.items && rec.items.length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-1">
                      {rec.items.map((item, i) => (
                        <span key={i} className="px-2 py-1 bg-indigo-50 text-indigo-700 rounded text-xs">
                          {item}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
