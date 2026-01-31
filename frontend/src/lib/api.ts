/**
 * RestoPilotAI API Client
 * Centralized API communication for the frontend
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface MenuItem {
  name: string;
  price: number;
  description?: string;
  category?: string;
}

export interface MenuExtractionResult {
  session_id: string;
  items: MenuItem[];
  categories: string[];
  raw_text?: string;
}

export interface MenuEngineeringItem {
  name: string;
  category: string;
  units_sold: number;
  price: number;
  cost: number;
  cm_unitario: number;
  popularity_pct: number;
  total_contribution: number;
  margin_pct: number;
  total_revenue: number;
  category_label: string;
  high_popularity: boolean;
  high_cm: boolean;
  strategy: {
    action: string;
    priority: string;
    recommendations: string[];
    pricing: string;
    menu_position: string;
    cm_gap?: number;
  };
}

export interface MenuEngineeringThresholds {
  popularity_threshold: number;
  cm_threshold: number;
  cm_average_simple: number;
  expected_popularity: number;
  n_items: number;
  total_units: number;
}

export interface CategorySummary {
  category: string;
  label: string;
  count: number;
  pct_items: number;
  total_revenue: number;
  pct_revenue: number;
  total_contribution: number;
  pct_contribution: number;
  units_sold: number;
  pct_units: number;
}

export interface MenuEngineeringSummary {
  total_items: number;
  total_revenue: number;
  total_contribution: number;
  total_units: number;
  avg_cm: number;
  categories: CategorySummary[];
  top_by_contribution: { name: string; contribution: number }[];
  top_by_popularity: { name: string; popularity_pct: number }[];
  attention_needed: number;
  dogs_list: string[];
}

export interface BCGAnalysisResult {
  session_id: string;
  status: string;
  methodology: string;
  period: string;
  date_range: { start: string | null; end: string | null };
  total_records: number;
  items_analyzed: number;
  thresholds: MenuEngineeringThresholds;
  summary: MenuEngineeringSummary;
  items: MenuEngineeringItem[];
}

// Legacy types for backwards compatibility
export interface BCGItem {
  name: string;
  price: number;
  category: 'STAR' | 'CASH_COW' | 'QUESTION_MARK' | 'DOG';
  growth: number;
  share: number;
  revenue?: number;
}

export interface SalesPrediction {
  date: string;
  predicted: number;
  actual?: number;
  confidence_lower: number;
  confidence_upper: number;
}

export interface PredictionResult {
  session_id: string;
  predictions: SalesPrediction[];
  metrics: {
    mape: number;
    rmse: number;
    r2: number;
  };
  insights: string[];
}

export interface Campaign {
  title: string;
  objective: string;
  target_category: string;
  target_audience: string;
  copy: {
    social_media: string;
    email_subject: string;
    email_body: string;
  };
  timing: string;
  expected_impact: string;
  rationale: string;
}

export interface CampaignResult {
  session_id: string;
  campaigns: Campaign[];
  thought_process?: string;
}

export interface AnalysisSession {
  session_id: string;
  status: string;
  created_at: string;
  menu?: MenuExtractionResult;
  bcg?: BCGAnalysisResult;
  predictions?: PredictionResult;
  campaigns?: CampaignResult;
}

export interface ThoughtSignature {
  level: 'QUICK' | 'STANDARD' | 'DEEP' | 'EXHAUSTIVE';
  reasoning: string;
  confidence: number;
  steps: string[];
}

class RestoPilotAIAPI {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`API Error: ${response.status} - ${error}`);
    }

    return response.json();
  }

  // ==================== Ingest Endpoints ====================

  async uploadMenu(file: File): Promise<MenuExtractionResult> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${this.baseUrl}/api/v1/ingest/menu`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Failed to upload menu');
    }

    return response.json();
  }

  async uploadDishes(files: File[], sessionId: string): Promise<{ count: number }> {
    const formData = new FormData();
    files.forEach((file) => formData.append('files', file));
    formData.append('session_id', sessionId);

    const response = await fetch(`${this.baseUrl}/api/v1/ingest/dishes`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Failed to upload dishes');
    }

    return response.json();
  }

  async uploadSalesData(file: File, sessionId: string): Promise<{ rows: number }> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('session_id', sessionId);

    const response = await fetch(`${this.baseUrl}/api/v1/ingest/sales`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Failed to upload sales data');
    }

    return response.json();
  }

  // ==================== Analysis Endpoints ====================

  async analyzeBCG(sessionId: string): Promise<BCGAnalysisResult> {
    return this.request<BCGAnalysisResult>(`/api/v1/analyze/bcg?session_id=${sessionId}`, {
      method: 'POST',
    });
  }

  async predictSales(sessionId: string): Promise<PredictionResult> {
    return this.request<PredictionResult>(`/api/v1/predict/sales?session_id=${sessionId}`, {
      method: 'POST',
    });
  }

  async generateCampaigns(sessionId: string): Promise<CampaignResult> {
    return this.request<CampaignResult>(`/api/v1/campaigns/generate?session_id=${sessionId}`, {
      method: 'POST',
    });
  }

  // ==================== Session Endpoints ====================

  async getSession(sessionId: string): Promise<AnalysisSession> {
    return this.request<AnalysisSession>(`/api/v1/session/${sessionId}`);
  }

  async exportSession(sessionId: string): Promise<Blob> {
    const response = await fetch(
      `${this.baseUrl}/api/v1/session/${sessionId}/export`
    );

    if (!response.ok) {
      throw new Error('Failed to export session');
    }

    return response.blob();
  }

  // ==================== Orchestrator Endpoints ====================

  async runFullAnalysis(sessionId: string): Promise<{ status: string }> {
    return this.request<{ status: string }>('/api/v1/orchestrator/run', {
      method: 'POST',
      body: JSON.stringify({ session_id: sessionId }),
    });
  }

  async resumeOrchestratorSession(
    sessionId: string,
    options?: { thinking_level?: string; auto_verify?: boolean }
  ): Promise<{ status: string }> {
    const formData = new FormData();
    if (options?.thinking_level) formData.append('thinking_level', options.thinking_level);
    if (options?.auto_verify !== undefined) formData.append('auto_verify', String(options.auto_verify));

    return this.request<{ status: string }>(`/api/v1/orchestrator/resume/${sessionId}`, {
      method: 'POST',
      body: formData,
      headers: {}, // FormData handles boundary
    });
  }

  async getAnalysisStatus(sessionId: string): Promise<{
    status: string;
    progress: number;
    current_stage: string;
  }> {
    return this.request(`/api/v1/orchestrator/status/${sessionId}`);
  }

  // ==================== Verification Endpoints ====================

  async verifyAnalysis(sessionId: string): Promise<{
    verified: boolean;
    issues: string[];
    suggestions: string[];
  }> {
    return this.request('/api/v1/verify/analysis', {
      method: 'POST',
      body: JSON.stringify({ session_id: sessionId }),
    });
  }

  // ==================== Model Info ====================

  async getModelsInfo(): Promise<{
    sales_predictor: { version: string; accuracy: number };
    neural_predictor: { version: string; type: string };
  }> {
    return this.request('/api/v1/models/info');
  }

  // ==================== Health Check ====================

  async healthCheck(): Promise<{ status: string; version: string }> {
    return this.request('/health');
  }

  // ==================== Demo Endpoints ====================

  async getDemoSession(): Promise<AnalysisSession> {
    return this.request<AnalysisSession>('/api/v1/demo/session');
  }

  async loadDemo(): Promise<{ session_id: string; status: string; items_count: number }> {
    return this.request('/api/v1/demo/load');
  }

  // ==================== Advanced Analytics Endpoints ====================

  async analyzeCapabilities(sessionId: string): Promise<DataCapabilityReport> {
    const formData = new FormData();
    formData.append('session_id', sessionId);
    
    return this.request<DataCapabilityReport>('/api/v1/analyze/capabilities', {
      method: 'POST',
      body: formData,
      headers: {}, // Let browser set content-type for FormData
    });
  }

  async runMenuOptimization(sessionId: string): Promise<MenuOptimizationResult> {
    const formData = new FormData();
    formData.append('session_id', sessionId);
    
    return this.request<MenuOptimizationResult>('/api/v1/analyze/menu-optimization', {
      method: 'POST',
      body: formData,
      headers: {},
    });
  }

  async runAdvancedAnalytics(
    sessionId: string, 
    capabilities?: string[]
  ): Promise<AdvancedAnalyticsResult> {
    const formData = new FormData();
    formData.append('session_id', sessionId);
    if (capabilities) {
      formData.append('capabilities', capabilities.join(','));
    }
    
    return this.request<AdvancedAnalyticsResult>('/api/v1/analyze/advanced', {
      method: 'POST',
      body: formData,
      headers: {},
    });
  }
}

// ==================== Advanced Analytics Types ====================

export interface DataCapabilityReport {
  session_id: string;
  available_capabilities: string[];
  missing_for_advanced: Record<string, string[]>;
  data_quality_score: number;
  row_count: number;
  date_range_days: number | null;
  unique_items: number;
  unique_categories: number;
  recommendations: string[];
  detected_at: string;
}

export interface ItemOptimization {
  item_name: string;
  current_price: number;
  suggested_price: number | null;
  current_margin: number | null;
  action: 'increase_price' | 'decrease_price' | 'promote' | 'remove' | 'bundle' | 'reposition' | 'maintain';
  priority: 'critical' | 'high' | 'medium' | 'low';
  reasoning: string;
  expected_impact: string;
  rotation_score: number;
  margin_score: number;
  combined_score: number;
  bcg_category: string | null;
}

export interface CategorySummary {
  category: string;
  item_count: number;
  avg_margin: number;
  avg_rotation: number;
  total_revenue: number;
  recommendations: string[];
}

export interface MenuOptimizationResult {
  session_id: string;
  generated_at: string;
  item_optimizations: ItemOptimization[];
  category_summaries: CategorySummary[];
  quick_wins: Array<{
    type: string;
    item?: string;
    items?: string[];
    action: string;
    impact: string;
    difficulty: string;
  }>;
  revenue_opportunity: number;
  margin_improvement_potential: number;
  items_to_promote: string[];
  items_to_review: string[];
  items_to_remove: string[];
  price_adjustments: Array<{
    item: string;
    current: number;
    suggested: number;
    change_pct: number;
  }>;
  ai_insights: string[];
  thought_process: string;
}

export interface HourlyPattern {
  hour: number;
  avg_quantity: number;
  avg_revenue: number;
  peak_indicator: boolean;
  staffing_recommendation: string;
}

export interface DailyPattern {
  day_of_week: number;
  day_name: string;
  avg_quantity: number;
  avg_revenue: number;
  avg_tickets: number | null;
  is_peak_day: boolean;
}

export interface SeasonalTrend {
  season_type: string;
  pattern_description: string;
  peak_periods: string[];
  low_periods: string[];
  variance_pct: number;
}

export interface ProductAnalytic {
  item_name: string;
  total_quantity: number;
  total_revenue: number;
  avg_daily_sales: number;
  sales_trend: 'increasing' | 'decreasing' | 'stable';
  trend_pct: number;
  category: string | null;
}

export interface CategoryAnalytic {
  category: string;
  item_count: number;
  total_revenue: number;
  revenue_share: number;
  top_performer: string;
  worst_performer: string;
}

export interface DemandForecast {
  period: string;
  predicted_quantity: number;
  predicted_revenue: number;
  confidence_lower: number;
  confidence_upper: number;
  factors: string[];
}

export interface AdvancedAnalyticsResult {
  session_id: string;
  generated_at: string;
  capabilities_used: string[];
  hourly_patterns: HourlyPattern[];
  daily_patterns: DailyPattern[];
  seasonal_trends: SeasonalTrend[];
  product_analytics: ProductAnalytic[];
  category_analytics: CategoryAnalytic[];
  demand_forecast: DemandForecast[];
  key_insights: string[];
  recommendations: string[];
  data_quality_notes: string[];
}

// Singleton instance
export const api = new RestoPilotAIAPI();

// Export class for custom instances
export { RestoPilotAIAPI };
