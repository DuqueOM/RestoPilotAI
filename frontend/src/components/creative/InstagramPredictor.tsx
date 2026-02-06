'use client';

import { FileUpload } from '@/components/setup/FileUpload';
import { AlertCircle, Instagram, Loader2, TrendingUp, Upload } from 'lucide-react';
import { useState } from 'react';
import { toast } from 'sonner';

export function InstagramPredictor() {
  const [file, setFile] = useState<File | null>(null);
  const [category, setCategory] = useState('General');
  const [postingTime, setPostingTime] = useState(new Date().toISOString().slice(0, 16)); // Default to now
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [prediction, setPrediction] = useState<any | null>(null);

  const handlePredict = async () => {
    if (!file) {
      toast.error("Please upload an image first.");
      return;
    }

    setIsAnalyzing(true);
    const formData = new FormData();
    formData.append('image', file);
    formData.append('restaurant_category', category);
    formData.append('posting_time_iso', new Date(postingTime).toISOString());

    try {
      const response = await fetch(`/api/v1/creative/instagram-prediction`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Prediction failed');

      const data = await response.json();
      setPrediction(data);
      toast.success("Engagement prediction complete!");
    } catch (error) {
      console.error('Error predicting performance:', error);
      toast.error('Failed to analyze image. Please try again.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 8) return 'text-green-600 bg-green-50 ring-green-200';
    if (score >= 5) return 'text-yellow-600 bg-yellow-50 ring-yellow-200';
    return 'text-red-600 bg-red-50 ring-red-200';
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
      <div className="flex items-center gap-2 mb-6">
        <Instagram className="w-6 h-6 text-pink-600" />
        <h2 className="text-2xl font-bold bg-gradient-to-r from-pink-600 to-purple-600 bg-clip-text text-transparent">
          Instagram Performance Predictor
        </h2>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Controls */}
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              1. Upload Dish Photo
            </label>
            <FileUpload
              label="Dish Photo"
              accept="image/*"
              icon={<Upload className="w-5 h-5 text-gray-400" />}
              onChange={(files) => setFile(files[0])}
              tooltip="Upload a photo you plan to post."
              compact
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                2. Category
              </label>
              <select
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
              >
                <option value="General">General</option>
                <option value="Mexican">Mexican</option>
                <option value="Italian">Italian</option>
                <option value="Japanese">Japanese</option>
                <option value="Fast Food">Fast Food</option>
                <option value="Fine Dining">Fine Dining</option>
                <option value="Desserts">Desserts</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                3. Posting Time
              </label>
              <input
                type="datetime-local"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500"
                value={postingTime}
                onChange={(e) => setPostingTime(e.target.value)}
              />
            </div>
          </div>

          <button
            onClick={handlePredict}
            disabled={!file || isAnalyzing}
            className={`w-full py-3 rounded-xl font-semibold text-white transition-all flex items-center justify-center gap-2 ${
              file && !isAnalyzing
                ? 'bg-gradient-to-r from-pink-600 to-purple-600 hover:shadow-lg hover:scale-[1.02]'
                : 'bg-gray-300 cursor-not-allowed'
            }`}
          >
            {isAnalyzing ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Analyzing with Gemini Vision...
              </>
            ) : (
              <>
                <TrendingUp className="w-5 h-5" />
                Predict Engagement
              </>
            )}
          </button>
        </div>

        {/* Results */}
        <div className="bg-gray-50 rounded-2xl border-2 border-dashed border-gray-200 min-h-[400px]">
          {!prediction ? (
            <div className="flex flex-col items-center justify-center h-full p-6 text-center">
              <div className="w-16 h-16 bg-white rounded-full shadow-sm flex items-center justify-center mb-4">
                <TrendingUp className="w-8 h-8 text-gray-300" />
              </div>
              <h3 className="text-gray-900 font-medium mb-1">Waiting for Analysis</h3>
              <p className="text-gray-500 text-sm max-w-xs">
                Upload a photo to see how it will perform on Instagram.
              </p>
            </div>
          ) : (
            <div className="p-6 space-y-6">
              {/* Prediction Header */}
              <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100 flex items-center justify-between">
                <div>
                  <div className="text-sm text-gray-500">Estimated Likes</div>
                  <div className="text-2xl font-bold text-gray-900">
                    {prediction.predicted_performance.likes_estimate}
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm text-gray-500">Engagement Rate</div>
                  <div className="text-2xl font-bold text-pink-600">
                    {prediction.predicted_performance.engagement_rate}
                  </div>
                </div>
              </div>

              {/* Scores Grid */}
              <div className="grid grid-cols-2 gap-3">
                {Object.entries(prediction.scores).map(([key, score]: [string, any]) => (
                  <div key={key} className={`p-3 rounded-lg border ring-1 ${getScoreColor(score)}`}>
                    <div className="text-xs uppercase font-semibold opacity-70 mb-1">
                      {key.replace('_', ' ')}
                    </div>
                    <div className="text-xl font-bold">{score}/10</div>
                  </div>
                ))}
              </div>

              {/* Improvements */}
              {prediction.improvements && prediction.improvements.length > 0 && (
                <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
                  <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 text-orange-500" />
                    Improvements
                  </h4>
                  <div className="space-y-3">
                    {prediction.improvements.map((imp: any, idx: number) => (
                      <div key={idx} className="text-sm">
                        <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium mr-2 ${
                          imp.impact === 'high' ? 'bg-red-100 text-red-700' : 
                          imp.impact === 'medium' ? 'bg-orange-100 text-orange-700' : 
                          'bg-blue-100 text-blue-700'
                        }`}>
                          {imp.impact.toUpperCase()}
                        </span>
                        <span className="text-gray-700">{imp.suggestion}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Trends */}
              <div className="text-xs text-gray-500 bg-white p-3 rounded-lg border border-gray-100">
                 <strong>Trend Check:</strong> {prediction.comparison_to_trends}
                 <div className="mt-1 text-blue-600">
                   {prediction.trending_hashtags?.join(' ')}
                 </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
