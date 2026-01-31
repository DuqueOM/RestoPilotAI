import { HelpCircle } from 'lucide-react';
import { useState } from 'react';

interface InfoTooltipProps {
  content: string;
  position?: 'top' | 'bottom' | 'left' | 'right';
}

export function InfoTooltip({ content, position = 'top' }: InfoTooltipProps) {
  const [visible, setVisible] = useState(false);
  
  const positions = {
    top: 'bottom-full left-1/2 -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 -translate-x-1/2 mt-2',
    left: 'right-full top-1/2 -translate-y-1/2 mr-2',
    right: 'left-full top-1/2 -translate-y-1/2 ml-2',
  };
  
  return (
    <div className="relative inline-block">
      <button
        type="button"
        className="text-gray-400 hover:text-gray-600 transition-colors"
        onMouseEnter={() => setVisible(true)}
        onMouseLeave={() => setVisible(false)}
        onClick={() => setVisible(!visible)}
      >
        <HelpCircle className="w-5 h-5" />
      </button>
      
      {visible && (
        <div
          className={`absolute z-50 ${positions[position]} w-64 px-4 py-3 bg-gray-900 text-white text-sm rounded-lg shadow-xl`}
        >
          <div className="relative">
            {content}
            <div className={`absolute w-3 h-3 bg-gray-900 transform rotate-45 ${
              position === 'top' ? 'top-full left-1/2 -translate-x-1/2 -mt-1.5' :
              position === 'bottom' ? 'bottom-full left-1/2 -translate-x-1/2 -mb-1.5' :
              position === 'left' ? 'left-full top-1/2 -translate-y-1/2 -ml-1.5' :
              'right-full top-1/2 -translate-y-1/2 -mr-1.5'
            }`} />
          </div>
        </div>
      )}
    </div>
  );
}
