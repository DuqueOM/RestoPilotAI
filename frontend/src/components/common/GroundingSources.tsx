'use client';
 
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { GroundingSource } from '@/lib/api';
import { CheckCircle2, ExternalLink, Globe } from 'lucide-react';

interface GroundingSourcesProps {
  sources: GroundingSource[];
  isGrounded: boolean;
  className?: string;
}

export function GroundingSources({ sources, isGrounded, className }: GroundingSourcesProps) {
  if (!sources || sources.length === 0) return null;
 
  return (
    <Card className={`border-green-100 bg-green-50/30 ${className || ''}`}>
      <CardHeader className="pb-2">
        <div className="flex items-center gap-2">
          <Globe className="w-4 h-4 text-green-600" />
          <CardTitle className="text-sm font-medium">
            Verifiable Sources (Google Search Grounding)
          </CardTitle>
          {isGrounded && (
            <Badge variant="outline" className="ml-auto text-green-600 border-green-600">
              <CheckCircle2 className="w-3 h-3 mr-1" />
              Verified
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <ul className="space-y-2">
          {sources.map((source, idx) => (
            <li key={idx} className="flex items-start gap-2 text-sm">
              <ExternalLink className="w-4 h-4 mt-0.5 text-blue-500 flex-shrink-0" />
              <a 
                href={source.uri} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline break-all"
              >
                {source.title || source.uri}
              </a>
            </li>
          ))}
        </ul>
        <p className="text-xs text-muted-foreground mt-3">
          Analysis enriched with real-time data from Google Search.
        </p>
      </CardContent>
    </Card>
  );
}
