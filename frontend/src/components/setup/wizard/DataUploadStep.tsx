'use client';

import { DishPhotoGallery } from '@/components/multimodal/DishPhotoGallery';
import { MenuExtractionPreview } from '@/components/multimodal/MenuExtractionPreview';
import { VideoInsightsPanel } from '@/components/multimodal/VideoInsightsPanel';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import {
    Camera,
    FileImage,
    FileSpreadsheet,
    FileText,
    Film,
    Image,
    Upload,
    Video,
    X
} from 'lucide-react';
import { useCallback, useEffect, useRef, useState } from 'react';
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
  showThumbnails?: boolean;
  fileType?: 'image' | 'pdf' | 'spreadsheet' | 'video';
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function FileThumbnail({ file, fileType, onRemove }: { file: File; fileType?: string; onRemove: () => void }) {
  const [preview, setPreview] = useState<string | null>(null);
  const [pdfPages, setPdfPages] = useState<number | null>(null);
  const [videoDuration, setVideoDuration] = useState<string | null>(null);

  useEffect(() => {
    if (fileType === 'image' || file.type.startsWith('image/')) {
      const url = URL.createObjectURL(file);
      setPreview(url);
      return () => URL.revokeObjectURL(url);
    }
    if (fileType === 'video' || file.type.startsWith('video/')) {
      const url = URL.createObjectURL(file);
      setPreview(url);
      const video = document.createElement('video');
      video.preload = 'metadata';
      video.onloadedmetadata = () => {
        const mins = Math.floor(video.duration / 60);
        const secs = Math.floor(video.duration % 60);
        setVideoDuration(`${mins}:${secs.toString().padStart(2, '0')}`);
        URL.revokeObjectURL(video.src);
      };
      video.src = url;
      return () => URL.revokeObjectURL(url);
    }
    if (fileType === 'pdf' || file.type === 'application/pdf') {
      // Estimate PDF pages from file size (rough: ~50KB per page)
      const estimatedPages = Math.max(1, Math.round(file.size / 50000));
      setPdfPages(estimatedPages);
    }
  }, [file, fileType]);

  const isImage = fileType === 'image' || file.type.startsWith('image/');
  const isVideo = fileType === 'video' || file.type.startsWith('video/');
  const isPdf = fileType === 'pdf' || file.type === 'application/pdf';

  return (
    <div className="group relative rounded-lg border border-gray-200 overflow-hidden bg-white hover:border-purple-300 transition-colors">
      {/* Thumbnail area */}
      <div className="aspect-square w-full bg-gray-50 flex items-center justify-center relative overflow-hidden">
        {isImage && preview ? (
          <img src={preview} alt={file.name} className="w-full h-full object-cover" />
        ) : isVideo && preview ? (
          <div className="relative w-full h-full">
            <video src={preview} className="w-full h-full object-cover" muted />
            <div className="absolute inset-0 flex items-center justify-center bg-black/20">
              <Film className="h-8 w-8 text-white" />
            </div>
            {videoDuration && (
              <span className="absolute bottom-1 right-1 bg-black/70 text-white text-xs px-1.5 py-0.5 rounded">
                {videoDuration}
              </span>
            )}
          </div>
        ) : isPdf ? (
          <div className="text-center p-2">
            <FileText className="h-8 w-8 text-red-500 mx-auto mb-1" />
            {pdfPages && (
              <span className="text-xs text-gray-500">~{pdfPages} {pdfPages === 1 ? 'page' : 'pages'}</span>
            )}
          </div>
        ) : (
          <FileSpreadsheet className="h-8 w-8 text-green-500" />
        )}
      </div>

      {/* File info */}
      <div className="p-2">
        <p className="text-xs font-medium text-gray-700 truncate" title={file.name}>{file.name}</p>
        <p className="text-xs text-gray-400">{formatFileSize(file.size)}</p>
      </div>

      {/* Remove button */}
      <button
        onClick={(e) => { e.stopPropagation(); onRemove(); }}
        className="absolute top-1 right-1 p-1 bg-white/90 hover:bg-red-100 rounded-full text-gray-400 hover:text-red-600 opacity-0 group-hover:opacity-100 transition-all shadow-sm"
      >
        <X className="h-3.5 w-3.5" />
      </button>
    </div>
  );
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
  showThumbnails = false,
  fileType,
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

      {/* File List - Thumbnails or List view */}
      {files.length > 0 && showThumbnails ? (
        <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-2">
          {files.map((file, index) => (
            <FileThumbnail
              key={`${file.name}-${index}`}
              file={file}
              fileType={fileType}
              onRemove={() => removeFile(index)}
            />
          ))}
        </div>
      ) : files.length > 0 ? (
        <div className="space-y-2">
          {files.map((file, index) => (
            <div
              key={`${file.name}-${index}`}
              className="flex items-center justify-between p-2.5 bg-gray-50 rounded-lg border border-gray-100 hover:border-gray-200 transition-colors"
            >
              <div className="flex items-center gap-2 min-w-0">
                {file.type.startsWith('image/') ? (
                  <FileImage className="h-4 w-4 text-blue-500 flex-shrink-0" />
                ) : file.type === 'application/pdf' ? (
                  <FileText className="h-4 w-4 text-red-500 flex-shrink-0" />
                ) : (
                  <FileSpreadsheet className="h-4 w-4 text-green-500 flex-shrink-0" />
                )}
                <span className="text-sm text-gray-700 truncate">{file.name}</span>
                <span className="text-xs text-gray-400 flex-shrink-0">
                  {formatFileSize(file.size)}
                </span>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  removeFile(index);
                }}
                className="p-1 hover:bg-red-100 rounded text-gray-400 hover:text-red-600 transition-colors"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          ))}
        </div>
      ) : null}
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
          showThumbnails={true}
          fileType="pdf"
        />
        {/* Live Menu Extraction Previews */}
        {formData.menuFiles.length > 0 && (
          <div className="space-y-3 mt-3">
            {formData.menuFiles.map((file, index) => (
              <MenuExtractionPreview
                key={`${file.name}-${index}`}
                file={file}
                compact={formData.menuFiles.length > 1}
                onRemove={() => {
                  updateFormData({
                    menuFiles: formData.menuFiles.filter((_, i) => i !== index),
                  });
                }}
              />
            ))}
          </div>
        )}
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
          hint="Gemini 3 will score presentation, lighting, and Instagram appeal"
          showThumbnails={false}
          fileType="image"
        />
        {/* AI-Powered Photo Gallery */}
        {formData.photoFiles.length > 0 && (
          <DishPhotoGallery
            files={formData.photoFiles}
            onRemoveFile={(index) => {
              updateFormData({
                photoFiles: formData.photoFiles.filter((_, i) => i !== index),
              });
            }}
          />
        )}
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
          hint="Gemini 3 Exclusive: Native video analysis (no other AI can do this)"
          showThumbnails={true}
          fileType="video"
        />
        {/* Live Video Analysis Previews */}
        {formData.videoFiles.length > 0 && (
          <div className="space-y-3 mt-3">
            {formData.videoFiles.map((file, index) => (
              <VideoInsightsPanel
                key={`${file.name}-${index}`}
                file={file}
                autoAnalyze={false}
                compact={formData.videoFiles.length > 1}
                onRemove={() => {
                  updateFormData({
                    videoFiles: formData.videoFiles.filter((_, i) => i !== index),
                  });
                }}
              />
            ))}
          </div>
        )}
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
          <li>• <strong>Menus:</strong> Automatic extraction of items and prices from images/PDF</li>
          <li>• <strong>Sales:</strong> BCG matrix analysis and demand forecasting</li>
          <li>• <strong>Photos:</strong> Visual quality scoring, presentation & Instagram appeal</li>
          <li>• <strong>Videos:</strong> Native video analysis — atmosphere, service flow, key moments <span className="inline-flex items-center bg-purple-100 text-purple-700 text-xs px-1.5 py-0.5 rounded-full ml-1">Gemini 3 Exclusive</span></li>
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
