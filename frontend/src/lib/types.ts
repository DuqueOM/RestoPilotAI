/**
 * Shared TypeScript types for MenuPilot
 */

export type BCGCategory = 'STAR' | 'CASH_COW' | 'QUESTION_MARK' | 'DOG';

export type AnalysisStatus = 
  | 'pending'
  | 'extracting'
  | 'analyzing'
  | 'predicting'
  | 'generating'
  | 'completed'
  | 'error';

export type ThinkingLevel = 'QUICK' | 'STANDARD' | 'DEEP' | 'EXHAUSTIVE';

export interface ApiError {
  message: string;
  code?: string;
  details?: Record<string, unknown>;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
}
