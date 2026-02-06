'use client';

import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import {
    Camera,
    FileSpreadsheet,
    FileText,
    Film,
    Image,
    Upload,
    Video,
    X
} from 'lucide-react';
import { useCallback, useRef } from 'react';
import { useWizard } from './SetupWizard';

interface FileDropZoneProps {
  accept: string;
  multiple?: boolean;
  files: File[];
  onFilesChange: (files: File[]) => void;
  icon: React.ReactNode;
  title: string;
  description: string;
  hint?: string;
}

function FileDropZone({
  accept,
  multiple = true,
  files,
  onFilesChange,
  icon,
  title,
  description,
  hint,
}: FileDropZoneProps) {
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      const droppedFiles = Array.from(e.dataTransfer.files);
      if (multiple) {
        onFilesChange([...files, ...droppedFiles]);
      } else {
        onFilesChange(droppedFiles.slice(0, 1));
      }
    },
    [files, multiple, onFilesChange]
  );

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(e.target.files || []);
    if (multiple) {
      onFilesChange([...files, ...selectedFiles]);
    } else {
      onFilesChange(selectedFiles.slice(0, 1));
    }
  };

  const removeFile = (index: number) => {
    onFilesChange(files.filter((_, i) => i !== index));
  };

  return (
    <div className="space-y-3">
      <div
        className={cn(
          'border-2 border-dashed rounded-xl p-6 text-center transition-all cursor-pointer',
          'hover:border-purple-400 hover:bg-purple-50/50',
          files.length > 0 ? 'border-green-300 bg-green-50/30' : 'border-gray-300'
        )}
        onDrop={handleDrop}
        onDragOver={(e) => e.preventDefault()}
        onClick={() => inputRef.current?.click()}
      >
        <input
          ref={inputRef}
          type="file"
          accept={accept}
          multiple={multiple}
          onChange={handleChange}
          className="hidden"
        />
        <div className="flex flex-col items-center gap-2">
          <div className={cn(
            'p-3 rounded-full',
            files.length > 0 ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-500'
          )}>
            {icon}
          </div>
          <div>
            <p className="font-medium text-gray-900">{title}</p>
            <p className="text-sm text-gray-500">{description}</p>
          </div>
          <Button variant="outline" size="sm" type="button">
            <Upload className="h-4 w-4 mr-2" />
            Select files
          </Button>
          {hint && <p className="text-xs text-gray-400 mt-1">{hint}</p>}
        </div>
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="space-y-2">
          {files.map((file, index) => (
            <div
              key={`${file.name}-${index}`}
              className="flex items-center justify-between p-2 bg-gray-50 rounded-lg"
            >
              <div className="flex items-center gap-2 min-w-0">
                <FileText className="h-4 w-4 text-gray-400 flex-shrink-0" />
                <span className="text-sm text-gray-700 truncate">{file.name}</span>
                <span className="text-xs text-gray-400">
                  ({(file.size / 1024).toFixed(1)} KB)
                </span>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  removeFile(index);
                }}
                className="p-1 hover:bg-red-100 rounded text-gray-400 hover:text-red-600"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export function DataUploadStep() {
  const { formData, updateFormData } = useWizard();

  return (
    <div className="space-y-8">
      {/* Menu Files */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-3 flex items-center gap-2">
          <FileText className="h-5 w-5 text-orange-500" />
          Menu
        </h3>
        <FileDropZone
          accept=".pdf,.jpg,.jpeg,.png,.webp"
          files={formData.menuFiles}
          onFilesChange={(files) => updateFormData({ menuFiles: files })}
          icon={<FileText className="h-6 w-6" />}
          title="Upload your menu"
          description="PDF, images or photos of the menu"
          hint="Gemini 3 will automatically extract items, prices and categories"
        />
      </div>

      {/* Sales Files */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-3 flex items-center gap-2">
          <FileSpreadsheet className="h-5 w-5 text-green-500" />
          Sales Data
        </h3>
        <FileDropZone
          accept=".csv,.xlsx,.xls"
          files={formData.salesFiles}
          onFilesChange={(files) => updateFormData({ salesFiles: files })}
          icon={<FileSpreadsheet className="h-6 w-6" />}
          title="Upload your sales"
          description="Excel or CSV with sales history"
          hint="We'll use this for BCG analysis and predictions"
        />
      </div>

      {/* Photo Files */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-3 flex items-center gap-2">
          <Camera className="h-5 w-5 text-blue-500" />
          Dish Photos
        </h3>
        <FileDropZone
          accept=".jpg,.jpeg,.png,.webp"
          files={formData.photoFiles}
          onFilesChange={(files) => updateFormData({ photoFiles: files })}
          icon={<Image className="h-6 w-6" />}
          title="Upload photos of your dishes"
          description="High quality images of your products"
          hint="Visual analysis with Gemini 3 Vision"
        />
      </div>

      {/* Video Files */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-3 flex items-center gap-2">
          <Film className="h-5 w-5 text-purple-500" />
          Ambience Videos
        </h3>
        <FileDropZone
          accept=".mp4,.webm,.mov"
          files={formData.videoFiles}
          onFilesChange={(files) => updateFormData({ videoFiles: files })}
          icon={<Video className="h-6 w-6" />}
          title="Upload videos of the venue"
          description="Short videos of the ambience or kitchen"
          hint="Gemini 3 will analyze the atmosphere and service flow"
        />
      </div>

      {/* Info Card */}
      <div className="p-4 bg-blue-50 rounded-lg border border-blue-100">
        <h4 className="font-medium text-blue-900 mb-2">
          🤖 Multimodal Processing
        </h4>
        <p className="text-sm text-blue-800">
          Gemini 3 will analyze your files intelligently:
        </p>
        <ul className="text-sm text-blue-700 mt-2 space-y-1">
          <li>• <strong>Menus:</strong> Automatic extraction of items and prices</li>
          <li>• <strong>Sales:</strong> BCG analysis and demand predictions</li>
          <li>• <strong>Photos:</strong> Visual evaluation and presentation suggestions</li>
        </ul>
      </div>

      {/* No files warning */}
      {formData.menuFiles.length === 0 && 
       formData.salesFiles.length === 0 && 
       formData.photoFiles.length === 0 && (
        <div className="p-4 bg-amber-50 rounded-lg border border-amber-200">
          <p className="text-sm text-amber-800">
            <strong>💡 Tip:</strong> Without data, the analysis will be limited. 
            We recommend uploading at least your menu for better results.
          </p>
        </div>
      )}
    </div>
  );
}

export default DataUploadStep;
