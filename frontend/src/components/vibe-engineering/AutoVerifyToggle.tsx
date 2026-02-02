'use client';

import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { Switch } from '@/components/ui/switch';
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from '@/components/ui/tooltip';
import { Info, ShieldCheck, Sparkles } from 'lucide-react';

interface AutoVerifyToggleProps {
  autoVerify: boolean;
  autoImprove: boolean;
  qualityThreshold: number;
  maxIterations: number;
  onAutoVerifyChange: (value: boolean) => void;
  onAutoImproveChange: (value: boolean) => void;
  onQualityThresholdChange: (value: number) => void;
  onMaxIterationsChange: (value: number) => void;
  disabled?: boolean;
}

export function AutoVerifyToggle({
  autoVerify,
  autoImprove,
  qualityThreshold,
  maxIterations,
  onAutoVerifyChange,
  onAutoImproveChange,
  onQualityThresholdChange,
  onMaxIterationsChange,
  disabled = false,
}: AutoVerifyToggleProps) {
  return (
    <div className={`space-y-6 p-5 bg-white rounded-xl border transition-colors ${
        autoVerify ? 'border-blue-200 shadow-sm' : 'border-gray-200'
    }`}>
      {/* Header Section */}
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${autoVerify ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-500'}`}>
            <ShieldCheck className="h-5 w-5" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">Vibe Engineering</h3>
            <p className="text-xs text-gray-500">Autonomous Quality Assurance</p>
          </div>
        </div>
        {autoVerify && (
            <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
                Active
            </Badge>
        )}
      </div>

      <div className="space-y-5">
        {/* Auto Verify Toggle */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Label htmlFor="auto-verify" className="text-sm font-medium text-gray-700">
              Enable Auto-Verification
            </Label>
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger>
                  <Info className="h-4 w-4 text-gray-400 hover:text-blue-500 transition-colors" />
                </TooltipTrigger>
                <TooltipContent>
                  <p className="max-w-xs text-xs">
                    Gemini will act as a critic, auditing its own analysis for hallucinations and logical errors before showing results.
                  </p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
          <Switch
            id="auto-verify"
            checked={autoVerify}
            onCheckedChange={onAutoVerifyChange}
            disabled={disabled}
            className="data-[state=checked]:bg-blue-600"
          />
        </div>

        {/* Auto Improve Toggle */}
        <div className={`flex items-center justify-between transition-opacity ${!autoVerify ? 'opacity-50' : ''}`}>
          <div className="flex items-center gap-2">
            <Label htmlFor="auto-improve" className="text-sm font-medium text-gray-700">
              Auto-Improve Results
            </Label>
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger>
                  <Sparkles className={`h-4 w-4 ${autoImprove && autoVerify ? 'text-amber-500' : 'text-gray-400'}`} />
                </TooltipTrigger>
                <TooltipContent>
                  <p className="max-w-xs text-xs">
                    If quality checks fail, Gemini will autonomously regenerate and improve the analysis until thresholds are met.
                  </p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
          <Switch
            id="auto-improve"
            checked={autoImprove}
            onCheckedChange={onAutoImproveChange}
            disabled={disabled || !autoVerify}
            className="data-[state=checked]:bg-amber-500"
          />
        </div>
      </div>

      {/* Advanced Settings */}
      {autoVerify && (
        <div className="pt-4 border-t border-gray-100 space-y-5 animate-in fade-in slide-in-from-top-2 duration-300">
            {/* Quality Threshold Slider */}
            <div className="space-y-3">
                <div className="flex items-center justify-between">
                    <Label className="text-xs font-medium text-gray-600">Minimum Quality Score</Label>
                    <span className="text-xs font-bold bg-gray-100 px-2 py-1 rounded text-gray-700">
                    {(qualityThreshold * 100).toFixed(0)}%
                    </span>
                </div>
                <Slider
                    value={[qualityThreshold * 100]}
                    onValueChange={(values) => onQualityThresholdChange(values[0] / 100)}
                    min={70}
                    max={99}
                    step={1}
                    disabled={disabled || !autoImprove}
                    className="w-full"
                />
                <p className="text-[10px] text-gray-400">
                    Analysis below this score will trigger auto-improvement loops.
                </p>
            </div>

            {/* Max Iterations Slider */}
            {autoImprove && (
                <div className="space-y-3">
                    <div className="flex items-center justify-between">
                        <Label className="text-xs font-medium text-gray-600">Max Improvement Loops</Label>
                        <span className="text-xs font-bold bg-gray-100 px-2 py-1 rounded text-gray-700">
                            {maxIterations}
                        </span>
                    </div>
                    <Slider
                        value={[maxIterations]}
                        onValueChange={(values) => onMaxIterationsChange(values[0])}
                        min={1}
                        max={5}
                        step={1}
                        disabled={disabled}
                        className="w-full"
                    />
                    <p className="text-[10px] text-gray-400">
                        Safety limit to prevent infinite regeneration cycles.
                    </p>
                </div>
            )}
        </div>
      )}
    </div>
  );
}
