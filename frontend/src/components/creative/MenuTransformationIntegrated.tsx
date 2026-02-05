'use client';

import { Button } from '@/components/ui/button';
import { Loader2 } from 'lucide-react';
import { useEffect, useState } from 'react';

interface MenuTransformationIntegratedProps {
  sessionId: string;
}

const STYLES = [
  { value: 'minimalist', label: 'Minimalist', emoji: '⚪' },
  { value: 'vintage', label: 'Vintage', emoji: '📜' },
  { value: 'modern', label: 'Modern', emoji: '✨' },
  { value: 'rustic', label: 'Rustic', emoji: '🌾' },
  { value: 'elegant', label: 'Elegant', emoji: '💎' },
];

export function MenuTransformationIntegrated({ sessionId }: MenuTransformationIntegratedProps) {
  const [menuImages, setMenuImages] = useState<any[]>([]);
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [selectedStyle, setSelectedStyle] = useState('minimalist');
  const [isTransforming, setIsTransforming] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  // Load menu images from session
  useEffect(() => {
    const fetchMenuImages = async () => {
      try {
        const response = await fetch(`/api/v1/session/${sessionId}/files`);
        if (!response.ok) throw new Error('Failed to load files');
        
        const files = await response.json();
        setMenuImages(files.menu || []);
        if (files.menu && files.menu.length > 0) {
          setSelectedImage(files.menu[0].path);
        }
      } catch (err) {
        console.error('Failed to load menu images:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchMenuImages();
  }, [sessionId]);

  const handleTransform = async () => {
    if (!selectedImage) return;
    
    setIsTransforming(true);
    setResult(null);
    
    try {
      const formData = new FormData();
      formData.append('session_id', sessionId);
      formData.append('image_path', selectedImage);
      formData.append('target_style', selectedStyle);
      
      const response = await fetch('/api/v1/creative/menu-transform-from-session', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) throw new Error('Transformation failed');
      
      const data = await response.json();
      setResult(data);
    } catch (err) {
      console.error('Transform error:', err);
    } finally {
      setIsTransforming(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
      </div>
    );
  }

  if (menuImages.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p className="text-3xl mb-2">📷</p>
        <p>No menu images found in this session.</p>
        <p className="text-sm mt-1">Upload menu images in the setup page.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Selector de imagen */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Select Menu Image:
        </label>
        <div className="grid grid-cols-3 gap-3">
          {menuImages.map((img, idx) => (
            <button
              key={idx}
              onClick={() => setSelectedImage(img.path)}
              className={`relative rounded-lg overflow-hidden border-2 transition-all ${
                selectedImage === img.path
                  ? 'border-purple-500 ring-2 ring-purple-200'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <img
                src={`/api/v1/files/${sessionId}/${img.path}`}
                alt={img.name}
                className="w-full h-32 object-cover"
              />
              <div className="absolute bottom-0 left-0 right-0 bg-black/50 text-white text-xs p-1 truncate">
                {img.name}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Selector de estilo */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Target Style:
        </label>
        <div className="flex flex-wrap gap-2">
          {STYLES.map((style) => (
            <button
              key={style.value}
              onClick={() => setSelectedStyle(style.value)}
              className={`px-4 py-2 rounded-lg border-2 transition-all ${
                selectedStyle === style.value
                  ? 'border-purple-500 bg-purple-50 text-purple-700'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <span className="mr-2">{style.emoji}</span>
              {style.label}
            </button>
          ))}
        </div>
      </div>

      {/* Transform button */}
      <Button
        onClick={handleTransform}
        disabled={!selectedImage || isTransforming}
        className="w-full"
      >
        {isTransforming ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Transforming with Gemini 3...
          </>
        ) : (
          '🎨 Transform Menu Style'
        )}
      </Button>

      {/* Resultado */}
      {result && (
        <div className="border-t pt-6">
          <h4 className="text-lg font-semibold mb-4">Before / After</h4>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600 mb-2">Original</p>
              <img
                src={`/api/v1/files/${sessionId}/${result.original_path}`}
                alt="Original"
                className="w-full rounded-lg border"
              />
            </div>
            <div>
              <p className="text-sm text-gray-600 mb-2">Transformed ({selectedStyle})</p>
              <img
                src={result.url}
                alt="Transformed"
                className="w-full rounded-lg border"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
