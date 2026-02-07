'use client';

import { Brain, Eye, Globe, Image, Mic, Search, Shield, Sparkles, Video, Wand2, Zap } from 'lucide-react';
import { ReactNode } from 'react';

export type GeminiCapability =
  | 'pro'
  | 'flash'
  | 'vision'
  | 'image-gen'
  | 'video'
  | 'audio'
  | 'grounding'
  | 'thinking'
  | 'vibe'
  | 'creative-autopilot'
  | 'marathon'
  | 'debate'
  | 'context-cache';

interface CapabilityConfig {
  label: string;
  icon: ReactNode;
  gradient: string;
  description: string;
}

const CAPABILITY_MAP: Record<GeminiCapability, CapabilityConfig> = {
  pro: {
    label: 'Gemini 3 Pro',
    icon: <Sparkles className="h-3 w-3" />,
    gradient: 'from-blue-500/20 to-indigo-500/20 text-blue-700 border-blue-300/50',
    description: 'Deep reasoning & analysis',
  },
  flash: {
    label: 'Gemini 3 Flash',
    icon: <Zap className="h-3 w-3" />,
    gradient: 'from-amber-500/20 to-yellow-500/20 text-amber-700 border-amber-300/50',
    description: 'Fast & efficient processing',
  },
  vision: {
    label: 'Vision Analysis',
    icon: <Eye className="h-3 w-3" />,
    gradient: 'from-cyan-500/20 to-teal-500/20 text-cyan-700 border-cyan-300/50',
    description: 'Image understanding & extraction',
  },
  'image-gen': {
    label: 'Imagen 3',
    icon: <Image className="h-3 w-3" />,
    gradient: 'from-purple-500/20 to-pink-500/20 text-purple-700 border-purple-300/50',
    description: 'AI image generation',
  },
  video: {
    label: 'Native Video',
    icon: <Video className="h-3 w-3" />,
    gradient: 'from-pink-500/20 to-rose-500/20 text-pink-700 border-pink-300/50',
    description: 'Video understanding & analysis',
  },
  audio: {
    label: 'Voice Understanding',
    icon: <Mic className="h-3 w-3" />,
    gradient: 'from-emerald-500/20 to-green-500/20 text-emerald-700 border-emerald-300/50',
    description: 'Audio transcription & analysis',
  },
  grounding: {
    label: 'Search Grounding',
    icon: <Search className="h-3 w-3" />,
    gradient: 'from-amber-500/20 to-orange-500/20 text-amber-700 border-amber-300/50',
    description: 'Real-time web intelligence',
  },
  thinking: {
    label: 'Deep Thinking',
    icon: <Brain className="h-3 w-3" />,
    gradient: 'from-violet-500/20 to-purple-500/20 text-violet-700 border-violet-300/50',
    description: 'Multi-step reasoning with thought signatures',
  },
  vibe: {
    label: 'Vibe Engineering',
    icon: <Shield className="h-3 w-3" />,
    gradient: 'from-emerald-500/20 to-teal-500/20 text-emerald-700 border-emerald-300/50',
    description: 'Self-improving quality assurance',
  },
  'creative-autopilot': {
    label: 'Creative Autopilot',
    icon: <Wand2 className="h-3 w-3" />,
    gradient: 'from-fuchsia-500/20 to-pink-500/20 text-fuchsia-700 border-fuchsia-300/50',
    description: 'AI-powered creative generation',
  },
  marathon: {
    label: 'Marathon Agent',
    icon: <Zap className="h-3 w-3" />,
    gradient: 'from-indigo-500/20 to-blue-500/20 text-indigo-700 border-indigo-300/50',
    description: 'Autonomous multi-stage pipeline',
  },
  debate: {
    label: 'Multi-Agent Debate',
    icon: <Brain className="h-3 w-3" />,
    gradient: 'from-orange-500/20 to-red-500/20 text-orange-700 border-orange-300/50',
    description: 'Adversarial reasoning for better decisions',
  },
  'context-cache': {
    label: 'Context Caching',
    icon: <Globe className="h-3 w-3" />,
    gradient: 'from-slate-500/20 to-gray-500/20 text-slate-700 border-slate-300/50',
    description: 'Efficient token reuse',
  },
};

interface GeminiCapabilityBadgeProps {
  capabilities: GeminiCapability[];
  size?: 'xs' | 'sm' | 'md';
  showDescription?: boolean;
  layout?: 'inline' | 'stack';
}

export function GeminiCapabilityBadge({
  capabilities,
  size = 'xs',
  showDescription: _showDescription = false,
  layout = 'inline',
}: GeminiCapabilityBadgeProps) {
  const sizeClasses = {
    xs: 'px-1.5 py-0.5 text-[9px] gap-0.5',
    sm: 'px-2 py-0.5 text-[10px] gap-1',
    md: 'px-2.5 py-1 text-xs gap-1.5',
  };

  return (
    <div className={`flex ${layout === 'stack' ? 'flex-col' : 'flex-wrap'} gap-1`}>
      {capabilities.map((cap) => {
        const config = CAPABILITY_MAP[cap];
        if (!config) return null;
        return (
          <span
            key={cap}
            title={config.description}
            className={`inline-flex items-center ${sizeClasses[size]} bg-gradient-to-r ${config.gradient} border rounded-full font-semibold whitespace-nowrap`}
          >
            {config.icon}
            {config.label}
          </span>
        );
      })}
    </div>
  );
}

interface GeminiPoweredHeaderProps {
  title: string;
  subtitle?: string;
  capabilities: GeminiCapability[];
  icon?: ReactNode;
}

export function GeminiPoweredHeader({
  title,
  subtitle,
  capabilities,
  icon,
}: GeminiPoweredHeaderProps) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4">
      <div className="flex items-center gap-2 flex-1">
        {icon}
        <div>
          <h2 className="text-lg font-bold text-gray-900">{title}</h2>
          {subtitle && <p className="text-sm text-gray-500">{subtitle}</p>}
        </div>
      </div>
      <GeminiCapabilityBadge capabilities={capabilities} size="sm" />
    </div>
  );
}
