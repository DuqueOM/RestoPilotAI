import { CheckCircle, ChevronDown, ChevronUp, Trash2, Upload } from 'lucide-react';
import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { InfoTooltip } from './InfoTooltip';

interface FileUploadProps {
  label: string;
  accept: string;
  icon?: React.ReactNode;
  onChange: (files: File[]) => void;
  tooltip?: string;
  compact?: boolean;
  multiple?: boolean;
}

export function FileUpload({
  label,
  accept,
  icon,
  onChange,
  tooltip,
  compact = false,
  multiple = false
}: FileUploadProps) {
  const [files, setFiles] = useState<File[]>([]);
  const [isListExpanded, setIsListExpanded] = useState(false);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles = multiple ? [...files, ...acceptedFiles] : [acceptedFiles[0]];
    setFiles(newFiles);
    onChange(newFiles);
    // Auto-expand list when files are added
    if (newFiles.length > 0) setIsListExpanded(true);
  }, [files, multiple, onChange]);

  const removeFile = (e: React.MouseEvent, index: number) => {
    e.stopPropagation();
    const newFiles = files.filter((_, i) => i !== index);
    setFiles(newFiles);
    onChange(newFiles);
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: accept.split(',').reduce((acc, curr) => {
      if (curr.includes('image')) acc['image/*'] = [];
      else if (curr.includes('pdf')) acc['application/pdf'] = [];
      else if (curr.includes('csv')) acc['text/csv'] = [];
      else if (curr.includes('xlsx')) acc['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'] = [];
      else if (curr.includes('video')) acc['video/*'] = [];
      return acc;
    }, {} as Record<string, string[]>),
    multiple
  });

  return (
    <div className="w-full">
      <div className="flex items-center gap-2 mb-2">
        <label className="block text-sm font-medium text-gray-700">
          {label}
        </label>
        {tooltip && <InfoTooltip content={tooltip} />}
      </div>

      <div
        {...getRootProps()}
        className={`relative border-2 border-dashed rounded-lg transition-all cursor-pointer overflow-hidden ${
          isDragActive
            ? 'border-blue-500 bg-blue-50'
            : files.length > 0
            ? 'border-green-500 bg-green-50'
            : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
        } ${compact ? 'p-4' : 'p-6'}`}
      >
        <input {...getInputProps()} />

        {files.length === 0 ? (
          <div className="flex flex-col items-center justify-center text-gray-500">
            {icon || <Upload className="w-6 h-6 mb-2" />}
            <p className="text-xs text-center mt-1">
              {isDragActive ? 'Drop files here' : 'Click or drag to upload'}
            </p>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center">
             <div className="flex items-center gap-2 text-green-600 font-medium mb-1">
                <CheckCircle className="w-5 h-5" />
                <span>{files.length} file{files.length > 1 ? 's' : ''} selected</span>
             </div>
             <p className="text-xs text-gray-500">Click to add more</p>
          </div>
        )}
      </div>

      {/* Collapsible File List */}
      {files.length > 0 && (
        <div className="mt-2 border border-gray-200 rounded-lg overflow-hidden bg-white shadow-sm">
          <button
            type="button"
            onClick={() => setIsListExpanded(!isListExpanded)}
            className="w-full flex items-center justify-between p-2 bg-gray-50 hover:bg-gray-100 transition-colors text-xs font-medium text-gray-700"
          >
            <span>View Attached Files</span>
            {isListExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
          
          {isListExpanded && (
            <div className="max-h-48 overflow-y-auto p-2 space-y-1 bg-white">
              {files.map((file, idx) => (
                <div key={idx} className="flex items-center justify-between p-2 bg-gray-50 rounded hover:bg-gray-100 group transition-colors">
                  <div className="flex items-center gap-2 overflow-hidden">
                    <div className="w-1.5 h-1.5 rounded-full bg-blue-500 flex-shrink-0" />
                    <span className="text-xs text-gray-600 truncate max-w-[200px]" title={file.name}>
                      {file.name}
                    </span>
                    <span className="text-[10px] text-gray-400 flex-shrink-0">
                      ({(file.size / 1024).toFixed(0)} KB)
                    </span>
                  </div>
                  <button
                    onClick={(e) => removeFile(e, idx)}
                    className="p-1 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded transition-colors opacity-0 group-hover:opacity-100"
                    title="Remove file"
                  >
                    <Trash2 className="w-3 h-3" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
