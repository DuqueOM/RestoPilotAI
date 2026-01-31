import { CheckCircle, Upload, X } from 'lucide-react';
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

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles = multiple ? [...files, ...acceptedFiles] : [acceptedFiles[0]];
    setFiles(newFiles);
    onChange(newFiles);
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
          <div className="space-y-2">
            <div className="flex items-center justify-center mb-2">
              <CheckCircle className="w-6 h-6 text-green-500" />
            </div>
            {files.map((file, idx) => (
              <div key={idx} className="flex items-center justify-between bg-white/50 rounded p-1.5 text-xs">
                <span className="truncate max-w-[80%]">{file.name}</span>
                <button
                  onClick={(e) => removeFile(e, idx)}
                  className="p-1 hover:bg-red-100 rounded-full text-gray-500 hover:text-red-500"
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
