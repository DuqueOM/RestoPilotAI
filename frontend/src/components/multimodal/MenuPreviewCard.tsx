'use client';

import { ConfidenceIndicator } from '@/components/ai/ConfidenceIndicator';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import {
  AlertTriangle,
  Check,
  ChevronDown,
  ChevronUp,
  DollarSign,
  Edit3,
  FileImage,
  Loader2,
  Sparkles,
  Tag,
  Trash2,
  X,
} from 'lucide-react';
import { useState } from 'react';

export interface ExtractedMenuItem {
  id: string;
  name: string;
  description?: string;
  price?: number;
  category?: string;
  imageUrl?: string;
  confidence: number;
  isVerified: boolean;
  warnings?: string[];
  suggestions?: string[];
}

interface MenuPreviewCardProps {
  items: ExtractedMenuItem[];
  sourceFileName?: string;
  sourceImageUrl?: string;
  isProcessing?: boolean;
  onItemEdit?: (id: string, updates: Partial<ExtractedMenuItem>) => void;
  onItemDelete?: (id: string) => void;
  onItemVerify?: (id: string) => void;
  onVerifyAll?: () => void;
  className?: string;
}

function MenuItemRow({
  item,
  onEdit,
  onDelete,
  onVerify,
}: {
  item: ExtractedMenuItem;
  onEdit?: (updates: Partial<ExtractedMenuItem>) => void;
  onDelete?: () => void;
  onVerify?: () => void;
}) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editedName, setEditedName] = useState(item.name);
  const [editedPrice, setEditedPrice] = useState(item.price?.toString() || '');
  const [editedCategory, setEditedCategory] = useState(item.category || '');

  const handleSave = () => {
    onEdit?.({
      name: editedName,
      price: editedPrice ? parseFloat(editedPrice) : undefined,
      category: editedCategory || undefined,
    });
    setIsEditing(false);
  };

  const hasWarnings = item.warnings && item.warnings.length > 0;
  const hasSuggestions = item.suggestions && item.suggestions.length > 0;

  return (
    <div
      className={cn(
        'border rounded-lg overflow-hidden transition-all',
        item.isVerified ? 'border-green-200 bg-green-50/30' : 'border-gray-200',
        hasWarnings && !item.isVerified && 'border-amber-200 bg-amber-50/30'
      )}
    >
      {/* Main Row */}
      <div className="p-3 flex items-center gap-3">
        {/* Thumbnail */}
        {item.imageUrl ? (
          <img
            src={item.imageUrl}
            alt={item.name}
            className="w-12 h-12 rounded object-cover flex-shrink-0"
          />
        ) : (
          <div className="w-12 h-12 rounded bg-gray-100 flex items-center justify-center flex-shrink-0">
            <FileImage className="h-5 w-5 text-gray-400" />
          </div>
        )}

        {/* Content */}
        <div className="flex-1 min-w-0">
          {isEditing ? (
            <div className="space-y-2">
              <input
                type="text"
                value={editedName}
                onChange={(e) => setEditedName(e.target.value)}
                className="w-full px-2 py-1 border rounded text-sm"
                placeholder="Item name"
              />
              <div className="flex gap-2">
                <input
                  type="text"
                  value={editedPrice}
                  onChange={(e) => setEditedPrice(e.target.value)}
                  className="w-24 px-2 py-1 border rounded text-sm"
                  placeholder="Price"
                />
                <input
                  type="text"
                  value={editedCategory}
                  onChange={(e) => setEditedCategory(e.target.value)}
                  className="flex-1 px-2 py-1 border rounded text-sm"
                  placeholder="Category"
                />
              </div>
            </div>
          ) : (
            <>
              <div className="flex items-center gap-2">
                <p className="font-medium text-gray-900 truncate">{item.name}</p>
                {item.isVerified && (
                  <Check className="h-4 w-4 text-green-600 flex-shrink-0" />
                )}
                {hasWarnings && !item.isVerified && (
                  <AlertTriangle className="h-4 w-4 text-amber-500 flex-shrink-0" />
                )}
              </div>
              <div className="flex items-center gap-2 mt-0.5">
                {item.price !== undefined && (
                  <span className="text-sm font-medium text-green-700 flex items-center">
                    <DollarSign className="h-3 w-3" />
                    {item.price.toFixed(2)}
                  </span>
                )}
                {item.category && (
                  <Badge variant="secondary" className="text-xs">
                    {item.category}
                  </Badge>
                )}
              </div>
            </>
          )}
        </div>

        {/* Confidence */}
        <div className="flex-shrink-0">
          <ConfidenceIndicator value={item.confidence} variant="minimal" size="xs" />
        </div>

        {/* Actions */}
        <div className="flex items-center gap-1 flex-shrink-0">
          {isEditing ? (
            <>
              <Button size="sm" variant="ghost" onClick={handleSave}>
                <Check className="h-4 w-4 text-green-600" />
              </Button>
              <Button size="sm" variant="ghost" onClick={() => setIsEditing(false)}>
                <X className="h-4 w-4 text-gray-500" />
              </Button>
            </>
          ) : (
            <>
              {!item.isVerified && onVerify && (
                <Button size="sm" variant="ghost" onClick={onVerify} title="Verify">
                  <Check className="h-4 w-4 text-gray-500 hover:text-green-600" />
                </Button>
              )}
              <Button size="sm" variant="ghost" onClick={() => setIsEditing(true)} title="Edit">
                <Edit3 className="h-4 w-4 text-gray-500" />
              </Button>
              {onDelete && (
                <Button size="sm" variant="ghost" onClick={onDelete} title="Delete">
                  <Trash2 className="h-4 w-4 text-gray-500 hover:text-red-600" />
                </Button>
              )}
              {(hasWarnings || hasSuggestions || item.description) && (
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => setIsExpanded(!isExpanded)}
                >
                  {isExpanded ? (
                    <ChevronUp className="h-4 w-4 text-gray-500" />
                  ) : (
                    <ChevronDown className="h-4 w-4 text-gray-500" />
                  )}
                </Button>
              )}
            </>
          )}
        </div>
      </div>

      {/* Expanded Details */}
      {isExpanded && !isEditing && (
        <div className="px-3 pb-3 pt-0 space-y-2 border-t bg-gray-50/50">
          {item.description && (
            <p className="text-sm text-gray-600 mt-2">{item.description}</p>
          )}
          
          {hasWarnings && (
            <div className="p-2 bg-amber-50 rounded border border-amber-200">
              <p className="text-xs font-medium text-amber-800 mb-1">⚠️ Warnings:</p>
              <ul className="text-xs text-amber-700 space-y-0.5">
                {item.warnings!.map((w, i) => (
                  <li key={i}>• {w}</li>
                ))}
              </ul>
            </div>
          )}
          
          {hasSuggestions && (
            <div className="p-2 bg-blue-50 rounded border border-blue-200">
              <p className="text-xs font-medium text-blue-800 mb-1">💡 Suggestions:</p>
              <ul className="text-xs text-blue-700 space-y-0.5">
                {item.suggestions!.map((s, i) => (
                  <li key={i}>• {s}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export function MenuPreviewCard({
  items,
  sourceFileName,
  sourceImageUrl,
  isProcessing = false,
  onItemEdit,
  onItemDelete,
  onItemVerify,
  onVerifyAll,
  className,
}: MenuPreviewCardProps) {
  const [showAllItems, setShowAllItems] = useState(false);

  const verifiedCount = items.filter(i => i.isVerified).length;
  const warningsCount = items.filter(i => i.warnings && i.warnings.length > 0 && !i.isVerified).length;
  const avgConfidence = items.length > 0
    ? items.reduce((sum, i) => sum + i.confidence, 0) / items.length
    : 0;

  const displayedItems = showAllItems ? items : items.slice(0, 5);
  const hasMoreItems = items.length > 5;

  // Group by category
  const categories = [...new Set(items.map(i => i.category || 'Uncategorized'))];

  return (
    <div className={cn('rounded-xl border bg-white overflow-hidden', className)}>
      {/* Header */}
      <div className="p-4 bg-gradient-to-r from-orange-50 to-amber-50 border-b">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-orange-100 rounded-lg">
              <Tag className="h-5 w-5 text-orange-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">
                Extracted Menu
                {isProcessing && (
                  <Loader2 className="inline h-4 w-4 ml-2 animate-spin text-orange-600" />
                )}
              </h3>
              <p className="text-sm text-gray-600">
                {items.length} items detected
                {sourceFileName && ` from ${sourceFileName}`}
              </p>
            </div>
          </div>
          
          {/* Stats */}
          <div className="text-right">
            <ConfidenceIndicator value={avgConfidence} variant="badge" size="sm" />
            <p className="text-xs text-gray-500 mt-1">
              {verifiedCount}/{items.length} verified
            </p>
          </div>
        </div>

        {/* Category Pills */}
        {categories.length > 1 && (
          <div className="flex flex-wrap gap-2 mt-3">
            {categories.map((cat) => {
              const count = items.filter(i => (i.category || 'Uncategorized') === cat).length;
              return (
                <Badge key={cat} variant="outline" className="text-xs">
                  {cat} ({count})
                </Badge>
              );
            })}
          </div>
        )}

        {/* Warnings Summary */}
        {warningsCount > 0 && (
          <div className="mt-3 p-2 bg-amber-100 rounded flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-amber-600" />
            <span className="text-sm text-amber-800">
              {warningsCount} item{warningsCount !== 1 ? 's' : ''} with warnings
            </span>
          </div>
        )}
      </div>

      {/* Source Image Preview */}
      {sourceImageUrl && (
        <div className="p-3 bg-gray-50 border-b">
          <img
            src={sourceImageUrl}
            alt="Original Menu"
            className="w-full max-h-40 object-contain rounded border"
          />
        </div>
      )}

      {/* Items List */}
      <div className="p-4 space-y-2">
        {isProcessing && items.length === 0 && (
          <div className="py-8 text-center">
            <Loader2 className="h-8 w-8 animate-spin text-orange-600 mx-auto mb-3" />
            <p className="text-gray-600">Extracting menu items...</p>
            <p className="text-sm text-gray-500 mt-1">
              Gemini 3 Vision is analyzing the document
            </p>
          </div>
        )}

        {!isProcessing && items.length === 0 && (
          <div className="py-8 text-center text-gray-500">
            No items detected in menu
          </div>
        )}

        {displayedItems.map((item) => (
          <MenuItemRow
            key={item.id}
            item={item}
            onEdit={onItemEdit ? (updates) => onItemEdit(item.id, updates) : undefined}
            onDelete={onItemDelete ? () => onItemDelete(item.id) : undefined}
            onVerify={onItemVerify ? () => onItemVerify(item.id) : undefined}
          />
        ))}

        {/* Show More */}
        {hasMoreItems && (
          <Button
            variant="ghost"
            className="w-full"
            onClick={() => setShowAllItems(!showAllItems)}
          >
            {showAllItems ? (
              <>
                <ChevronUp className="h-4 w-4 mr-2" />
                Show less
              </>
            ) : (
              <>
                <ChevronDown className="h-4 w-4 mr-2" />
                View {items.length - 5} more items
              </>
            )}
          </Button>
        )}
      </div>

      {/* Footer Actions */}
      {items.length > 0 && onVerifyAll && (
        <div className="p-4 bg-gray-50 border-t flex justify-between items-center">
          <p className="text-sm text-gray-600">
            {verifiedCount === items.length ? (
              <span className="text-green-600 flex items-center gap-1">
                <Check className="h-4 w-4" />
                All items verified
              </span>
            ) : (
              `${items.length - verifiedCount} items pending verification`
            )}
          </p>
          {verifiedCount < items.length && (
            <Button onClick={onVerifyAll} size="sm">
              <Sparkles className="h-4 w-4 mr-2" />
              Verify all
            </Button>
          )}
        </div>
      )}
    </div>
  );
}

export default MenuPreviewCard;
