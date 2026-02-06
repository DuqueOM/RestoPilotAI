# RestoPilotAI — Frontend

> Next.js 15 dashboard for AI-powered restaurant intelligence, built with React 18, TailwindCSS, Radix UI, and Recharts.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Framework** | Next.js 15.1 (App Router, standalone output) |
| **Language** | TypeScript 5.3 |
| **Styling** | TailwindCSS 3.4 + tailwindcss-animate |
| **Components** | Radix UI primitives (Tabs, Tooltip, Select, Popover, etc.) |
| **Icons** | Lucide React |
| **Charts** | Recharts 2.15 |
| **Animations** | Framer Motion 12 |
| **HTTP** | Native Fetch (via API client class) |
| **Maps** | @react-google-maps/api |
| **Notifications** | Sonner (toast notifications) |
| **File Upload** | react-dropzone |

---

## Project Structure

```
frontend/
├── public/
│   └── images/                  # Professional restaurant imagery
│       ├── hero-chef.png        # Landing page hero image
│       ├── hero-dish.png        # Floating accent dish
│       ├── pattern-food.png     # Repeating background pattern
│       ├── dashboard-header.png # Analysis overview header
│       ├── bcg-matrix-accent.png    # BCG page accent
│       ├── campaign-studio.png      # Campaigns page accent
│       ├── sentiment-reviews.png    # Sentiment page accent
│       ├── competitors-market.png   # Competitors page accent
│       └── empty-state-plate.png    # Empty state placeholder
├── src/
│   ├── app/
│   │   ├── layout.tsx           # Root layout (fonts, metadata)
│   │   ├── page.tsx             # Entry → WizardPage
│   │   ├── globals.css          # Global styles, Tailwind directives
│   │   ├── error.tsx            # Global error boundary
│   │   ├── not-found.tsx        # 404 page
│   │   ├── api/
│   │   │   └── setup-wizard/    # Server-side API proxy route
│   │   └── analysis/
│   │       └── [sessionId]/
│   │           ├── layout.tsx       # Tab navigation + SessionContext
│   │           ├── page.tsx         # Overview dashboard
│   │           ├── bcg/page.tsx     # BCG matrix analysis
│   │           ├── campaigns/page.tsx   # Creative studio & campaigns
│   │           ├── competitors/page.tsx # Competitor analysis
│   │           └── sentiment/page.tsx   # Sentiment analysis
│   ├── components/
│   │   ├── ai/                  # AI Transparency components
│   │   │   ├── ThoughtBubbleStream.tsx   # Real-time AI reasoning display
│   │   │   ├── ConfidenceIndicator.tsx   # Trust score visualization
│   │   │   ├── VerifiedSourceBadge.tsx   # Grounding source badges
│   │   │   ├── AgentDebateTrigger.tsx    # Multi-agent debate trigger
│   │   │   ├── MultiAgentDebatePanel.tsx # Debate visualization
│   │   │   └── QualityAssurancePanel.tsx # Vibe Engineering QA
│   │   ├── analysis/            # Analysis visualization
│   │   │   ├── AdvancedAnalytics.tsx     # Advanced patterns & trends
│   │   │   ├── AgentDashboard.tsx        # AI agent activity dashboard
│   │   │   ├── AnalysisPanel.tsx         # Analysis trigger panel
│   │   │   ├── BCGChart.tsx              # BCG quadrant scatter chart
│   │   │   ├── BCGMatrix.tsx             # Full BCG matrix component
│   │   │   ├── Campaigns.tsx             # Campaign card display
│   │   │   ├── CompetitorDashboard.tsx   # Competitor comparison
│   │   │   ├── FeedbackSummary.tsx       # AI feedback chat panel
│   │   │   ├── MenuItemsTable.tsx        # Menu items data table
│   │   │   ├── SentimentDashboard.tsx    # Sentiment analysis visuals
│   │   │   └── StreamingAnalysis.tsx     # Real-time streaming analysis
│   │   ├── creative/            # Creative Studio
│   │   │   ├── CreativeAutopilot.tsx     # Full campaign generation
│   │   │   ├── CampaignPreviewGallery.tsx # Image gallery & preview
│   │   │   ├── ABTestingPanel.tsx        # A/B variant comparison
│   │   │   ├── InstagramPredictor.tsx    # IG engagement predictor
│   │   │   ├── MenuTransformation.tsx    # Menu style transformation
│   │   │   └── MenuTransformationIntegrated.tsx # Integrated variant
│   │   ├── multimodal/          # Multimodal data handling
│   │   │   ├── MenuExtractionPreview.tsx # OCR extraction preview
│   │   │   ├── MenuPreviewCard.tsx       # Menu card display
│   │   │   ├── DishPhotoGallery.tsx      # Dish photo upload & display
│   │   │   ├── VideoAnalysisZone.tsx     # Video upload & analysis
│   │   │   ├── VideoInsightsPanel.tsx    # Video analysis results
│   │   │   └── LiveTranscriptionBox.tsx  # Audio transcription
│   │   ├── marathon-agent/      # Marathon Agent UI
│   │   │   ├── PipelineProgress.tsx      # Pipeline stage progress bar
│   │   │   ├── StepTimeline.tsx          # Step-by-step timeline
│   │   │   ├── TaskMonitor.tsx           # Active task monitor
│   │   │   ├── CheckpointViewer.tsx      # Checkpoint inspection
│   │   │   └── RecoveryPanel.tsx         # Crash recovery panel
│   │   ├── setup/               # Setup wizard components
│   │   │   ├── wizard/
│   │   │   │   └── WizardPage.tsx        # Main wizard orchestrator
│   │   │   ├── LandingHero.tsx           # Hero section
│   │   │   ├── LocationInput.tsx         # Google Maps location picker
│   │   │   ├── FileUpload.tsx            # Drag-and-drop file upload
│   │   │   ├── ContextInput.tsx          # Business context input
│   │   │   ├── TemplateSelector.tsx      # Analysis template chooser
│   │   │   ├── ProgressBar.tsx           # Setup progress indicator
│   │   │   └── InfoTooltip.tsx           # Help tooltips
│   │   ├── vibe-engineering/    # Vibe Engineering UI
│   │   │   ├── VerificationPanel.tsx     # Quality verification panel
│   │   │   ├── AutoVerifyToggle.tsx      # Auto-verify toggle switch
│   │   │   ├── QualityMetrics.tsx        # Quality score display
│   │   │   └── ImprovementHistory.tsx    # Improvement iteration log
│   │   ├── grounding/           # Grounding components
│   │   ├── reasoning/           # Reasoning trace display
│   │   ├── video/               # Video analysis components
│   │   ├── dashboard/           # Dashboard-level components
│   │   ├── shared/              # Shared utility components
│   │   ├── chat/                # Chat interface
│   │   ├── common/              # Common UI patterns
│   │   └── ui/                  # Base UI primitives (shadcn/ui)
│   │       ├── button.tsx, card.tsx, badge.tsx
│   │       ├── tabs.tsx, tooltip.tsx, select.tsx
│   │       ├── progress.tsx, slider.tsx, switch.tsx
│   │       └── collapsible.tsx, label.tsx, popover.tsx
│   ├── hooks/
│   │   ├── useApi.ts                # Generic API request hook
│   │   ├── useAvailablePeriods.ts   # Date period options
│   │   ├── useMarathonAgent.ts      # Marathon Agent state management
│   │   ├── useRealTimeProgress.ts   # Progress bar hook
│   │   ├── useThinkingStream.ts     # AI thought stream hook
│   │   ├── useVibeEngineering.ts    # Vibe Engineering hook
│   │   └── useWebSocket.ts         # WebSocket connection hook
│   ├── lib/
│   │   ├── api/
│   │   │   └── index.ts            # RestoPilotAIAPI client (760+ lines)
│   │   ├── types.ts                # Shared TypeScript types
│   │   ├── utils.ts                # cn() utility
│   │   └── utils/                  # Utility functions
│   ├── types/                       # Additional type definitions
│   └── styles/                      # Additional styles
├── next.config.js               # API proxy rewrites, webpack config
├── tailwind.config.js           # TailwindCSS configuration
├── tsconfig.json                # TypeScript configuration
├── .eslintrc.json               # ESLint rules
├── components.json              # shadcn/ui config
├── Dockerfile                   # Production container
└── netlify.toml                 # Netlify deployment config
```

---

## Pages & Routing

### `/` — Setup Wizard
The landing page (`WizardPage.tsx`) provides a guided multi-step setup:
1. **Hero Section** — Professional hero with background pattern, chef image, and demo button
2. **Location** — Google Maps place search + competitor discovery
3. **Menu Upload** — Drag-and-drop for menu images/PDFs with OCR preview
4. **Sales Data** — CSV/XLSX upload with validation
5. **Context** — Business context, audio recording, competitor info
6. **Template** — Analysis profile selection
7. **Launch** — Start the full analysis pipeline

### `/analysis/[sessionId]` — Analysis Dashboard
Tab-based dashboard with shared `SessionContext`:

| Tab | Route | Key Components |
|-----|-------|---------------|
| **Overview** | `/analysis/[id]` | Business info header with bg image, progress bars, analysis cards, export |
| **BCG Matrix** | `/analysis/[id]/bcg` | Interactive BCG chart, menu engineering table, pricing benchmarks, period selector |
| **Competitors** | `/analysis/[id]/competitors` | Competitor cards, Google Maps data, enrichment panels |
| **Sentiment** | `/analysis/[id]/sentiment` | Sentiment scores, review analysis, NPS, recommendation cards |
| **Campaigns** | `/analysis/[id]/campaigns` | Campaign gallery, Creative Autopilot, A/B testing, Instagram predictor |

---

## API Client

The `RestoPilotAIAPI` class (`src/lib/api/index.ts`) provides a typed API client with **50+ methods** covering:

- **Ingestion** — `uploadMenu()`, `uploadDishes()`, `uploadSalesData()`
- **Analysis** — `analyzeBCG()`, `predictSales()`, `generateCampaigns()`
- **Session** — `getSession()`, `exportSession()`, `getDemoSession()`
- **Orchestrator** — `runFullAnalysis()`, `resumeOrchestratorSession()`, `getAnalysisStatus()`
- **Creative** — `transformMenuStyle()`, `predictInstagramEngagement()`, `generateCreativeAssets()`
- **Advanced** — `analyzeCapabilities()`, `runMenuOptimization()`, `runAdvancedAnalytics()`
- **Verification** — `verifyAnalysis()`
- **Health** — `healthCheck()`, `getModelsInfo()`

All API calls use **relative URLs** (`/api/v1/...`) proxied through Next.js `rewrites` in `next.config.js` to avoid CORS issues.

---

## Custom Hooks

| Hook | Purpose |
|------|---------|
| `useApi` | Generic async request with loading/error states |
| `useWebSocket` | WebSocket connection management with auto-reconnect |
| `useThinkingStream` | Stream AI thought traces in real-time |
| `useMarathonAgent` | Marathon Agent task lifecycle (start/monitor/recover) |
| `useVibeEngineering` | Vibe Engineering quality loop state |
| `useRealTimeProgress` | Pipeline progress percentage tracking |
| `useAvailablePeriods` | Generate date period options for analysis filtering |

---

## Key Architecture Decisions

- **App Router** — Next.js 15 App Router with server components where possible
- **SessionContext** — Single fetch in layout, shared across all tab pages via React Context
- **Proxy Pattern** — Next.js `rewrites` proxy all `/api/*` requests to backend `localhost:8000`
- **Standalone Output** — `output: 'standalone'` for Docker deployment
- **Bundle Optimization** — Recharts and vendors in separate chunks; tree-shaking for Lucide icons
- **Security Headers** — X-Frame-Options, X-Content-Type-Options, Referrer-Policy

---

## Running

```bash
# Development
cd frontend
npm install
npm run dev          # http://localhost:3000

# Build
npm run build        # Production build
npm run start        # Serve production build

# Quality
npm run lint         # ESLint
npm run typecheck    # TypeScript type checking
npm run build:analyze # Bundle size analysis
```

---

## Environment Variables

```bash
# .env.development (default)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

The `NEXT_PUBLIC_API_URL` is used only by `next.config.js` for rewrites configuration. Frontend code uses relative paths exclusively.
