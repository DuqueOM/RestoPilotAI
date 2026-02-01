'use client';

import React from 'react';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { Info } from 'lucide-react';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';

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
    <div className="space-y-6 p-4 bg-white rounded-lg border border-gray-200">
      <div className="space-y-4">
        {/* Auto Verify Toggle */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Label htmlFor="auto-verify" className="text-sm font-medium">
              Auto-Verify Analysis
            </Label>
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger>
                  <Info className="h-4 w-4 text-gray-400" />
                </TooltipTrigger>
                <TooltipContent>
                  <p className="max-w-xs text-xs">
                    Automatically check the quality of AI analysis using autonomous verification
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
          />
        </div>

        {/* Auto Improve Toggle */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Label htmlFor="auto-improve" className="text-sm font-medium">
              Auto-Improve Results
            </Label>
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger>
                  <Info className="h-4 w-4 text-gray-400" />
                </TooltipTrigger>
                <TooltipContent>
                  <p className="max-w-xs text-xs">
                    Let the AI autonomously improve its analysis until quality threshold is met
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
          />
        </div>
      </div>

      {/* Quality Threshold Slider */}
      {autoVerify && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label className="text-sm font-medium">Quality Threshold</Label>
            <span className="text-sm font-semibold text-gray-900">
              {(qualityThreshold * 100).toFixed(0)}%
            </span>
          </div>
          <Slider
            value={[qualityThreshold * 100]}
            onValueChange={(values) => onQualityThresholdChange(values[0] / 100)}
            min={70}
            max={95}
            step={5}
            disabled={disabled || !autoImprove}
            className="w-full"
          />
          <p className="text-xs text-gray-600">
            AI will improve analysis until this quality level is reached
          </p>
        </div>
      )}

      {/* Max Iterations Slider */}
      {autoVerify && autoImprove && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label className="text-sm font-medium">Max Iterations</Label>
            <span className="text-sm font-semibold text-gray-900">{maxIterations}</span>
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
          <p className="text-xs text-gray-600">
            Maximum number of improvement cycles to prevent infinite loops
          </p>
        </div>
      )}
    </div>
  );
}
