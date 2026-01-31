import { motion } from 'framer-motion';

interface ProgressBarProps {
  value: number;  // 0-100
  label?: string;
  showPercentage?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

export function ProgressBar({ 
  value, 
  label, 
  showPercentage = false,
  size = 'md' 
}: ProgressBarProps) {
  const heights = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3'
  };
  
  const getColor = (val: number) => {
    if (val < 30) return 'from-red-400 to-orange-400';
    if (val < 60) return 'from-yellow-400 to-orange-400';
    return 'from-green-400 to-blue-500';
  };
  
  return (
    <div className="w-full">
      {(label || showPercentage) && (
        <div className="flex justify-between items-center mb-2">
          {label && <span className="text-sm font-medium text-gray-700">{label}</span>}
          {showPercentage && (
            <span className="text-sm font-semibold text-gray-900">{value}%</span>
          )}
        </div>
      )}
      
      <div className={`w-full bg-gray-200 rounded-full ${heights[size]} overflow-hidden`}>
        <motion.div
          className={`${heights[size]} bg-gradient-to-r ${getColor(value)} rounded-full`}
          initial={{ width: 0 }}
          animate={{ width: `${value}%` }}
          transition={{ duration: 0.5, ease: "easeOut" }}
        />
      </div>
    </div>
  );
}
