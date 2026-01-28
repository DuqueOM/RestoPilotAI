/**
 * Shared TypeScript types for MenuPilot
 * Centralized type definitions for the frontend
 */

// ==================== Enums & Constants ====================

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

export type Step = 'upload' | 'analysis' | 'results';

export type ResultsTab = 
  | 'overview' 
  | 'agents' 
  | 'bcg' 
  | 'competitors' 
  | 'sentiment' 
  | 'predictions' 
  | 'campaigns';

// ==================== Menu & Items ====================

export interface MenuItem {
  name: string;
  price: number;
  description?: string;
  category?: string;
  cost?: number;
  image_score?: number;
}

export interface BCGClassification {
  name: string;
  bcg_class: BCGCategory;
  label: string;
  market_share: number;
  growth_rate: number;
  margin: number;
  gross_profit: number;
  strategy: string;
  priority: string;
}

// ==================== Analysis Results ====================

export interface BCGAnalysis {
  classifications: BCGClassification[];
  summary: {
    stars: number;
    cash_cows: number;
    question_marks: number;
    dogs: number;
    total_items: number;
  };
  thresholds: {
    high_share_threshold: number;
    high_growth_threshold: number;
  };
  ai_insights: string;
  analysis_timestamp: string;
}

export interface SalesPrediction {
  item_name: string;
  scenario: string;
  predictions: Array<{
    date: string;
    predicted_units: number;
    confidence_lower?: number;
    confidence_upper?: number;
  }>;
}

export interface Campaign {
  id: number;
  title: string;
  objective: string;
  target_audience: string;
  target_items: string[];
  start_date: string;
  end_date: string;
  channels: string[];
  copy: {
    social_media?: string;
    email_subject?: string;
    email_body?: string;
    in_store?: string;
  };
  expected_roi: number;
  budget_suggestion: string;
}

// ==================== Session & State ====================

export interface SessionData {
  session_id: string;
  created_at: string;
  menu_items: MenuItem[];
  sales_data: unknown[];
  bcg_analysis?: BCGAnalysis;
  predictions?: SalesPrediction[];
  campaigns?: Campaign[];
  thought_signature?: ThoughtSignatureData;
}

export interface ThoughtSignatureData {
  task: string;
  context: Record<string, unknown>;
  reasoning_steps: string[];
  verification_status: string;
  confidence: number;
  timestamp: string;
}

// ==================== API Responses ====================

export interface ApiError {
  message: string;
  code?: string;
  details?: Record<string, unknown>;
}

export interface ApiResponse<T> {
  data: T;
  status: 'success' | 'error';
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
}

// ==================== Component Props ====================

export interface FileUploadProps {
  onSessionCreated: (id: string, data: SessionData) => void;
  onComplete: () => void;
  sessionId: string | null;
}

export interface AnalysisPanelProps {
  sessionId: string;
  sessionData: SessionData;
  onComplete: (data: Partial<SessionData>) => void;
}

export interface BCGResultsPanelProps {
  classifications: BCGClassification[];
  summary: BCGAnalysis['summary'];
  insights?: string;
}

export interface CampaignCardsProps {
  campaigns: Campaign[];
}

export interface ThoughtSignatureProps {
  signature: ThoughtSignatureData;
}
