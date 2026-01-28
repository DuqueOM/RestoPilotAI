/**
 * MenuPilot API Client
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

export interface BCGItem {
  name: string;
  price: number;
  category: 'STAR' | 'CASH_COW' | 'QUESTION_MARK' | 'DOG';
  growth: number;
  share: number;
  revenue?: number;
}

export interface BCGAnalysisResult {
  session_id: string;
  items: BCGItem[];
  insights: Record<string, string>;
  summary: string;
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

class MenuPilotAPI {
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
}

// Singleton instance
export const api = new MenuPilotAPI();

// Export class for custom instances
export { MenuPilotAPI };
