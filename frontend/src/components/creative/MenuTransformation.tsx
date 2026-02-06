'use client';

import { FileUpload } from '@/components/setup/FileUpload';
import { ArrowLeftRight, Download, Loader2, Sparkles, Upload } from 'lucide-react';
import Image from 'next/image';
import { useEffect, useRef, useState } from 'react';
import { toast } from 'sonner';

const STYLES = [
  { id: 'modern_minimalist', name: 'Modern Minimalist', description: 'Clean, sans-serif, whitespace' },
  { id: 'rustic_vintage', name: 'Rustic Vintage', description: 'Serif, textured, warm tones' },
  { id: 'luxury_fine_dining', name: 'Luxury Fine Dining', description: 'Elegant, black & gold, sophisticated' },
];

export function MenuTransformation() {
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [selectedStyle, setSelectedStyle] = useState(STYLES[0].id);
  const [isTransforming, setIsTransforming] = useState(false);
  const [resultImage, setResultImage] = useState<string | null>(null);
  const [sliderPosition, setSliderPosition] = useState(50);
  const [isResizing, setIsResizing] = useState(false);

  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (file) {
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
      return () => URL.revokeObjectURL(url);
    } else {
      setPreviewUrl(null);
    }
  }, [file]);

  useEffect(() => {
    const handleMove = (e: MouseEvent | TouchEvent) => {
      if (!isResizing || !containerRef.current) return;
      
      let clientX;
      if ('touches' in e) {
        clientX = e.touches[0].clientX;
      } else {
        clientX = (e as MouseEvent).clientX;
      }

      const rect = containerRef.current.getBoundingClientRect();
      const x = Math.max(0, Math.min(clientX - rect.left, rect.width));
      const percentage = (x / rect.width) * 100;
      setSliderPosition(percentage);
    };

    const handleUp = () => {
      setIsResizing(false);
    };

    if (isResizing) {
      window.addEventListener('mousemove', handleMove);
      window.addEventListener('mouseup', handleUp);
      window.addEventListener('touchmove', handleMove);
      window.addEventListener('touchend', handleUp);
    }

    return () => {
      window.removeEventListener('mousemove', handleMove);
      window.removeEventListener('mouseup', handleUp);
      window.removeEventListener('touchmove', handleMove);
      window.removeEventListener('touchend', handleUp);
    };
  }, [isResizing]);

  const handleTransform = async () => {
    if (!file) return;

    setIsTransforming(true);
    const formData = new FormData();
    formData.append('image', file);
    formData.append('target_style', selectedStyle);

    try {
      const response = await fetch(`/api/v1/creative/menu-transform`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Transformation failed');

      const data = await response.json();
      if (data.transformed_menu_base64) {
        setResultImage(`data:image/jpeg;base64,${data.transformed_menu_base64}`);
      }
    } catch (error) {
      console.error('Error transforming menu:', error);
      toast.error('Failed to transform menu. Please try again.');
    } finally {
      setIsTransforming(false);
    }
  };

  const handleMouseDown = () => setIsResizing(true);
  const handleTouchStart = () => setIsResizing(true);

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
      <div className="flex items-center gap-2 mb-6">
        <Sparkles className="w-6 h-6 text-purple-600" />
        <h2 className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
          Menu Transformation Studio
        </h2>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Controls */}
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              1. Upload Current Menu
            </label>
            <FileUpload
              label="Menu Image"
              accept="image/*"
              icon={<Upload className="w-5 h-5 text-gray-400" />}
              onChange={(files) => setFile(files[0])}
              tooltip="Upload a photo or screenshot of your current menu."
              compact
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              2. Select Target Style
            </label>
            <div className="grid grid-cols-1 gap-3">
              {STYLES.map((style) => (
                <button
                  key={style.id}
                  onClick={() => setSelectedStyle(style.id)}
                  className={`p-4 rounded-xl border text-left transition-all ${
                    selectedStyle === style.id
                      ? 'border-purple-500 bg-purple-50 ring-2 ring-purple-200'
                      : 'border-gray-200 hover:border-purple-200 hover:bg-gray-50'
                  }`}
                >
                  <div className="font-semibold text-gray-900">{style.name}</div>
                  <div className="text-sm text-gray-500">{style.description}</div>
                </button>
              ))}
            </div>
          </div>

          <button
            onClick={handleTransform}
            disabled={!file || isTransforming}
            className={`w-full py-3 rounded-xl font-semibold text-white transition-all flex items-center justify-center gap-2 ${
              file && !isTransforming
                ? 'bg-gradient-to-r from-purple-600 to-blue-600 hover:shadow-lg hover:scale-[1.02]'
                : 'bg-gray-300 cursor-not-allowed'
            }`}
          >
            {isTransforming ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Transforming with Nano Banana Pro...
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5" />
                Transform Menu Style
              </>
            )}
          </button>
        </div>

        {/* Preview / Comparison */}
        <div className="bg-gray-50 rounded-2xl border-2 border-dashed border-gray-200 flex items-center justify-center min-h-[500px] relative overflow-hidden">
          
          {!file && !resultImage && (
            <div className="text-center p-6">
              <div className="w-16 h-16 bg-white rounded-full shadow-sm flex items-center justify-center mx-auto mb-4">
                <Sparkles className="w-8 h-8 text-gray-300" />
              </div>
              <h3 className="text-gray-900 font-medium mb-1">Ready to Redesign</h3>
              <p className="text-gray-500 text-sm max-w-xs mx-auto">
                Upload your menu and select a style to see the AI transformation here.
              </p>
            </div>
          )}

          {file && !resultImage && !isTransforming && previewUrl && (
             <div className="relative w-full h-full p-4 flex flex-col items-center">
                <Image src={previewUrl} alt="Original" width={800} height={450} className="max-h-[450px] object-contain rounded-lg shadow-sm opacity-50" unoptimized />
                <p className="mt-4 text-gray-500 text-sm">Original Image Preview</p>
             </div>
          )}

          {isTransforming && (
             <div className="flex flex-col items-center justify-center">
                <Loader2 className="w-12 h-12 text-purple-600 animate-spin mb-4" />
                <p className="text-purple-700 font-medium animate-pulse">Generating new design...</p>
                <p className="text-gray-400 text-sm mt-2">Preserving menu items & prices</p>
             </div>
          )}

          {resultImage && previewUrl && (
            <div 
              ref={containerRef}
              className="relative w-full h-full select-none"
            >
              <div className="absolute inset-0 w-full h-full p-4 flex items-center justify-center bg-gray-100">
                 {/* Background: Result (After) */}
                 <Image 
                    src={resultImage} 
                    alt="After" 
                    width={1200}
                    height={800}
                    className="max-h-full max-w-full object-contain shadow-xl rounded-lg" 
                    style={{ maxHeight: '100%', maxWidth: '100%' }}
                    unoptimized
                 />
              </div>

              {/* Foreground: Original (Before) - Clipped */}
              <div 
                className="absolute inset-0 w-full h-full p-4 flex items-center justify-center bg-gray-100 overflow-hidden"
                style={{ clipPath: `inset(0 ${100 - sliderPosition}% 0 0)` }}
              >
                 <Image 
                    src={previewUrl} 
                    alt="Before" 
                    width={1200}
                    height={800}
                    className="max-h-full max-w-full object-contain shadow-xl rounded-lg"
                    style={{ maxHeight: '100%', maxWidth: '100%' }}
                    unoptimized
                 />
                 <div className="absolute top-6 left-6 bg-black/50 text-white px-3 py-1 rounded-full text-xs font-bold backdrop-blur-sm">
                    BEFORE
                 </div>
              </div>

              <div className="absolute top-6 right-6 bg-purple-600/80 text-white px-3 py-1 rounded-full text-xs font-bold backdrop-blur-sm z-10">
                 AFTER
              </div>

              {/* Slider Handle */}
              <div 
                className="absolute inset-y-0 w-1 bg-white cursor-ew-resize z-20 shadow-[0_0_10px_rgba(0,0,0,0.5)] flex items-center justify-center"
                style={{ left: `${sliderPosition}%` }}
                onMouseDown={handleMouseDown}
                onTouchStart={handleTouchStart}
              >
                <div className="w-8 h-8 bg-white rounded-full shadow-lg flex items-center justify-center -ml-[14px]">
                  <ArrowLeftRight className="w-4 h-4 text-purple-600" />
                </div>
              </div>

              {/* Download Button */}
              <div className="absolute bottom-6 right-6 z-30">
                 <a
                  href={resultImage}
                  download={`menu-${selectedStyle}.jpg`}
                  className="bg-white hover:bg-gray-50 text-gray-800 px-4 py-2 rounded-lg shadow-lg flex items-center gap-2 font-medium transition-colors"
                >
                  <Download className="w-4 h-4" />
                  Download Result
                </a>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
