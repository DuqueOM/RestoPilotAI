'use client';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import {
    AlertTriangle,
    CheckCircle2,
    ChevronDown,
    ChevronUp,
    Edit3,
    FileText,
    Loader2,
    Sparkles,
    X,
} from 'lucide-react';
import { useCallback, useEffect, useState } from 'react';

interface ExtractedItem {
  name: string;
  price: number | null;
  description?: string;
  category?: string;
  confidence?: number;
  tags?: string[];
  has_image?: boolean;
  image_description?: string;
}

interface ExtractionResult {
  items: ExtractedItem[];
  categories?: string[];
  item_count?: number;
  extraction_confidence?: number;
  warnings?: string[];
}

interface MenuExtractionPreviewProps {
  file: File;
  onItemsExtracted?: (items: ExtractedItem[]) => void;
  onRemove?: () => void;
  compact?: boolean;
  /** Delay in ms before starting extraction (to stagger parallel requests) */
  extractionDelay?: number;
}

export function MenuExtractionPreview({
  file,
  onItemsExtracted,
  onRemove,
  compact = false,
  extractionDelay = 0,
}: MenuExtractionPreviewProps) {
  const [preview, setPreview] = useState<string | null>(null);
  const [extracting, setExtracting] = useState(false);
  const [result, setResult] = useState<ExtractionResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [editedItems, setEditedItems] = useState<ExtractedItem[]>([]);
  const [expanded, setExpanded] = useState(!compact);

  // Generate image preview
  useEffect(() => {
    if (file.type.startsWith('image/')) {
      const url = URL.createObjectURL(file);
      setPreview(url);
      return () => URL.revokeObjectURL(url);
    }
  }, [file]);

  // Auto-extract on mount (with optional stagger delay)
  useEffect(() => {
    const timer = setTimeout(() => extractMenu(), extractionDelay);
    return () => clearTimeout(timer);
  }, [file]);

  const extractMenu = useCallback(async (retryCount = 0) => {
    setExtracting(true);
    setError(null);

    const MAX_RETRIES = 2;

    try {
      const formData = new FormData();
      formData.append('files', file);

      const response = await fetch('/api/v1/ingest/menu', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        // Retry on 500/503 (Gemini rate limit / server overload)
        if ((response.status === 500 || response.status === 503) && retryCount < MAX_RETRIES) {
          const backoff = (retryCount + 1) * 3000; // 3s, 6s
          console.warn(`[MenuExtraction] ${file.name} failed (${response.status}), retrying in ${backoff}ms (attempt ${retryCount + 1}/${MAX_RETRIES})`);
          await new Promise(r => setTimeout(r, backoff));
          return extractMenu(retryCount + 1);
        }
        throw new Error(`Extraction failed: ${response.status}`);
      }

      const data = await response.json();
      const extractedItems = data.items || [];
      
      setResult({
        items: extractedItems,
        categories: data.categories || [],
        item_count: extractedItems.length,
        extraction_confidence: data.thought_process?.confidence || 0.85,
        warnings: [],
      });
      setEditedItems(extractedItems);
      onItemsExtracted?.(extractedItems);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Extraction failed');
    } finally {
      setExtracting(false);
    }
  }, [file, onItemsExtracted]);

  const handleItemEdit = (index: number, field: keyof ExtractedItem, value: any) => {
    setEditedItems(prev => {
      const updated = [...prev];
      updated[index] = { ...updated[index], [field]: value };
      return updated;
    });
  };

  const handleSaveEdit = () => {
    setEditingIndex(null);
    onItemsExtracted?.(editedItems);
  };

  const handleRemoveItem = (index: number) => {
    setEditedItems(prev => prev.filter((_, i) => i !== index));
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600 bg-green-50';
    if (confidence >= 0.6) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  // Group items by category
  const groupedItems = editedItems.reduce((acc, item) => {
    const cat = item.category || 'Other';
    if (!acc[cat]) acc[cat] = [];
    acc[cat].push(item);
    return acc;
  }, {} as Record<string, ExtractedItem[]>);

  return (
    <div className="rounded-xl border border-gray-200 overflow-hidden bg-white">
      {/* Header */}
      <div
        className="flex items-center gap-3 p-4 bg-gradient-to-r from-purple-50 to-blue-50 border-b cursor-pointer"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="p-2 bg-white rounded-lg shadow-sm">
          <Sparkles className="h-4 w-4 text-purple-600" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-gray-900 truncate">{file.name}</p>
          <p className="text-xs text-gray-500">
            {extracting
              ? 'Gemini 3 is extracting menu items...'
              : result
              ? `${editedItems.length} items extracted across ${Object.keys(groupedItems).length} categories`
              : error
              ? 'Extraction failed'
              : 'Ready to extract'}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {extracting && <Loader2 className="h-4 w-4 animate-spin text-purple-600" />}
          {result && !extracting && (
            <Badge className={cn('text-xs', getConfidenceColor(result.extraction_confidence || 0.85))}>
              {Math.round((result.extraction_confidence || 0.85) * 100)}% confidence
            </Badge>
          )}
          {error && <AlertTriangle className="h-4 w-4 text-red-500" />}
          {expanded ? <ChevronUp className="h-4 w-4 text-gray-400" /> : <ChevronDown className="h-4 w-4 text-gray-400" />}
        </div>
      </div>

      {/* Content */}
      {expanded && (
        <div className="flex flex-col md:flex-row">
          {/* Left: Image Preview */}
          {preview && (
            <div className="md:w-1/3 border-r border-gray-100 p-3">
              <div className="relative rounded-lg overflow-hidden bg-gray-50">
                <img
                  src={preview}
                  alt="Menu"
                  className="w-full h-auto max-h-[400px] object-contain"
                />
                {extracting && (
                  <div className="absolute inset-0 bg-purple-600/10 flex items-center justify-center">
                    <div className="bg-white/90 rounded-xl px-4 py-3 shadow-lg flex items-center gap-2">
                      <Loader2 className="h-4 w-4 animate-spin text-purple-600" />
                      <span className="text-sm font-medium text-purple-700">Analyzing with Gemini 3...</span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Right: Extracted Items */}
          <div className={cn('flex-1 p-3', !preview && 'w-full')}>
            {extracting && !result && (
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <div className="relative mb-4">
                  <div className="w-12 h-12 border-3 border-purple-200 rounded-full animate-pulse" />
                  <div className="absolute inset-0 w-12 h-12 border-3 border-purple-600 border-t-transparent rounded-full animate-spin" />
                </div>
                <p className="text-sm font-medium text-gray-700">Extracting menu items...</p>
                <p className="text-xs text-gray-500 mt-1">Gemini 3 is reading items, prices, and categories</p>
              </div>
            )}

            {error && (
              <div className="p-4 bg-red-50 rounded-lg border border-red-200">
                <p className="text-sm text-red-700 font-medium">Extraction Error</p>
                <p className="text-xs text-red-600 mt-1">{error}</p>
                <Button size="sm" variant="outline" onClick={extractMenu} className="mt-3">
                  Retry
                </Button>
              </div>
            )}

            {result && editedItems.length > 0 && (
              <div className="space-y-3 max-h-[400px] overflow-y-auto">
                {Object.entries(groupedItems).map(([category, items]) => (
                  <div key={category}>
                    <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1.5 sticky top-0 bg-white py-1">
                      {category} ({items.length})
                    </h4>
                    <div className="space-y-1">
                      {items.map((item, idx) => {
                        const globalIdx = editedItems.indexOf(item);
                        const isEditing = editingIndex === globalIdx;

                        return (
                          <div
                            key={`${item.name}-${idx}`}
                            className={cn(
                              'flex items-center gap-2 p-2 rounded-lg transition-colors group',
                              isEditing ? 'bg-purple-50 border border-purple-200' : 'hover:bg-gray-50'
                            )}
                          >
                            {isEditing ? (
                              <>
                                <input
                                  value={item.name}
                                  onChange={(e) => handleItemEdit(globalIdx, 'name', e.target.value)}
                                  className="flex-1 text-sm border rounded px-2 py-1 focus:ring-1 focus:ring-purple-500"
                                />
                                <input
                                  value={item.price ?? ''}
                                  onChange={(e) => handleItemEdit(globalIdx, 'price', parseFloat(e.target.value) || null)}
                                  className="w-20 text-sm border rounded px-2 py-1 text-right focus:ring-1 focus:ring-purple-500"
                                  type="number"
                                  step="0.01"
                                />
                                <Button size="sm" variant="ghost" onClick={handleSaveEdit}>
                                  <CheckCircle2 className="h-3.5 w-3.5 text-green-600" />
                                </Button>
                              </>
                            ) : (
                              <>
                                <span className="flex-1 text-sm text-gray-800 truncate">{item.name}</span>
                                {item.price != null && (
                                  <span className="text-sm font-medium text-gray-900 tabular-nums">
                                    ${item.price.toFixed(2)}
                                  </span>
                                )}
                                {item.confidence != null && item.confidence < 0.7 && (
                                  <AlertTriangle className="h-3 w-3 text-amber-500 flex-shrink-0" />
                                )}
                                <button
                                  onClick={() => setEditingIndex(globalIdx)}
                                  className="p-1 opacity-0 group-hover:opacity-100 hover:bg-gray-200 rounded transition-all"
                                >
                                  <Edit3 className="h-3 w-3 text-gray-500" />
                                </button>
                                <button
                                  onClick={() => handleRemoveItem(globalIdx)}
                                  className="p-1 opacity-0 group-hover:opacity-100 hover:bg-red-100 rounded transition-all"
                                >
                                  <X className="h-3 w-3 text-gray-400 hover:text-red-500" />
                                </button>
                              </>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {result && editedItems.length === 0 && (
              <div className="text-center py-8">
                <FileText className="h-8 w-8 text-gray-300 mx-auto mb-2" />
                <p className="text-sm text-gray-500">No items could be extracted</p>
                <Button size="sm" variant="outline" onClick={extractMenu} className="mt-3">
                  Try Again
                </Button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Footer */}
      {expanded && result && editedItems.length > 0 && (
        <div className="flex items-center justify-between px-4 py-2.5 bg-gray-50 border-t text-xs text-gray-500">
          <span>{editedItems.length} items &middot; {Object.keys(groupedItems).length} categories</span>
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1 text-purple-600">
              <Sparkles className="h-3 w-3" />
              Extracted by Gemini 3
            </span>
            {onRemove && (
              <button onClick={onRemove} className="text-gray-400 hover:text-red-500 transition-colors">
                Remove
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default MenuExtractionPreview;
