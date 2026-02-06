# RestoPilotAI — Exhaustive UX/UI Audit & Action Plan

> **Author**: Staff UX/UI Engineer Analysis  
> **Date**: February 2026  
> **Scope**: Full-stack UX audit focused on Gemini 3 multimodal exploitation, agentic patterns, and end-user experience  
> **Goal**: Transform RestoPilotAI into a world-class, production-ready product that maximizes Gemini 3's unique capabilities through a fluid, intuitive, and visually stunning interface

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Architecture Audit](#2-architecture-audit)
3. [Current UX Heuristic Evaluation](#3-current-ux-heuristic-evaluation)
4. [Gemini 3 Capability Gap Analysis](#4-gemini-3-capability-gap-analysis)
5. [Action Plan — Phase 1: Foundation & Polish](#5-phase-1-foundation--polish)
6. [Action Plan — Phase 2: Multimodal Experience Revolution](#6-phase-2-multimodal-experience-revolution)
7. [Action Plan — Phase 3: Agentic Intelligence Layer](#7-phase-3-agentic-intelligence-layer)
8. [Action Plan — Phase 4: Creative Studio & Delight](#8-phase-4-creative-studio--delight)
9. [Component Architecture Recommendations](#9-component-architecture-recommendations)
10. [Implementation Priority Matrix](#10-implementation-priority-matrix)

---

## 1. Executive Summary

RestoPilotAI has an **exceptionally strong backend** — a 2,000-line orchestrator, 15+ Gemini 3 service modules, Marathon Agent pattern with checkpoints, multi-agent debates, vibe engineering loops, native video/audio/PDF processing, image generation via Imagen 3, and Google Search grounding. This is genuinely a top-tier AI backend.

**The critical gap is that the frontend exposes roughly 30% of this capability.** The user experience is functional but does not match the sophistication of the AI engine behind it. The setup wizard collects data effectively but provides no feedback loop. The analysis dashboard displays results statically with no interactivity. The creative tools exist in isolation. Real-time AI transparency (thought streams, debates) is present but under-leveraged.

### Key Findings

| Area | Current State | Target State | Gap |
|------|--------------|--------------|-----|
| **Setup Wizard** | 4-step form, basic uploads | Intelligent guided experience with live AI preview | High |
| **Analysis Dashboard** | Static data display, 5 tabs | Interactive, explorable, actionable intelligence hub | High |
| **Multimodal Input** | File upload zones, basic transcription | Live camera capture, drag-drop anywhere, voice commands | Critical |
| **AI Transparency** | ThoughtBubbleStream exists but passive | Interactive reasoning explorer with drill-down | Medium |
| **Creative Studio** | Form-based generation, isolated | Integrated visual workspace with real-time preview | High |
| **Real-time Feedback** | WebSocket + SSE infrastructure exists | Smooth progressive disclosure during long analysis | Medium |
| **Mobile Experience** | Basic responsive | Touch-optimized, camera-first mobile flow | High |
| **Microinteractions** | Minimal animations | Purposeful motion design communicating AI state | Medium |

---

## 2. Architecture Audit

### 2.1 Backend Capabilities (What Exists)

```
Backend Service Map:
├── Orchestrator (orchestrator.py — 2022 lines)
│   ├── 17-stage pipeline with checkpoints
│   ├── Marathon Agent pattern (long-running tasks)
│   ├── Automatic recovery & retry
│   └── WebSocket progress broadcasting
│
├── Gemini Services (15 modules)
│   ├── base_agent.py — Core agent with rate limiting, caching, retry
│   ├── advanced_multimodal.py — Video, batch images, PDF, audio
│   ├── reasoning_agent.py — Multi-level thinking (QUICK→EXHAUSTIVE)
│   ├── creative_autopilot.py — Full campaign generation + Imagen 3
│   ├── vibe_engineering.py — Auto-verification loops
│   ├── marathon_agent.py — Checkpoint-based long tasks
│   ├── streaming_reasoning.py — SSE thought streaming
│   ├── grounded_intelligence.py — Google Search grounding
│   ├── verification.py — Quality validation
│   └── enhanced_agent.py — Structured outputs (Pydantic)
│
├── Intelligence Services
│   ├── competitor_finder.py (ScoutAgent)
│   ├── data_enrichment.py — Business profile enrichment
│   ├── social_aesthetics.py — Visual quality scoring
│   ├── neighborhood.py — Local market analysis
│   └── geocoding.py — Location services
│
├── Analysis Services
│   ├── bcg.py — BCG Matrix classification
│   ├── sentiment.py — Multi-source sentiment
│   ├── pricing.py — Competitive pricing intelligence
│   ├── menu_analyzer.py — Menu extraction from images
│   ├── menu_engineering.py — Full menu engineering
│   ├── sales_predictor.py — Demand forecasting
│   └── neural_predictor.py — ML-based predictions
│
└── API Routes (13 route files)
    ├── marathon.py — WebSocket + SSE + REST
    ├── creative.py — Image generation, menu transform
    ├── video.py — Native video analysis (Gemini exclusive)
    ├── streaming.py — Real-time thought visualization
    └── business.py — Session management, enrichment
```

### 2.2 Frontend Structure (What Exists)

```
Frontend Component Map:
├── Setup Wizard Flow
│   ├── WizardPage.tsx — Orchestrates wizard + submission
│   ├── SetupWizard.tsx — Step management, context, localStorage
│   ├── LocationStep.tsx — Google Maps + enrichment
│   ├── DataUploadStep.tsx — 4 file drop zones
│   ├── StoryStep.tsx — 5 context sections + voice input
│   └── CompetitorsStep.tsx — Auto-find + manual + voice
│
├── Analysis Dashboard
│   ├── layout.tsx — 5-tab navigation + session context
│   ├── page.tsx (Overview) — Summary cards + pipeline progress
│   ├── bcg/page.tsx — BCG matrix + menu engineering
│   ├── competitors/page.tsx — Competitor analysis
│   ├── sentiment/page.tsx — Review analysis
│   └── campaigns/page.tsx — Marketing + creative autopilot
│
├── AI Components
│   ├── ThoughtBubbleStream.tsx — Real-time AI thinking
│   ├── MultiAgentDebatePanel.tsx — Agent perspectives
│   ├── ConfidenceIndicator.tsx — Trust signals
│   └── VerifiedSourceBadge.tsx — Grounding indicators
│
├── Creative Components
│   ├── CreativeAutopilot.tsx — Campaign generation
│   ├── ABTestingPanel.tsx — Variant testing
│   ├── CampaignPreviewGallery.tsx — Asset preview
│   └── MenuTransformation.tsx — Style transfer
│
├── Multimodal Components
│   ├── LiveTranscriptionBox.tsx — Voice recording + transcription
│   ├── VideoAnalysisZone.tsx — Video upload + analysis
│   └── MenuPreviewCard.tsx — Extracted menu preview
│
└── Hooks
    ├── useThinkingStream.ts — WebSocket thought stream
    ├── useMarathonAgent.ts — Task state management
    ├── useWebSocket.ts — Generic WebSocket
    └── useVibeEngineering.ts — Auto-verification
```

### 2.3 Integration Assessment

| Integration Point | Status | Issue |
|---|---|---|
| WebSocket (thoughts) | ✅ Connected | Passive display only, no user interaction |
| WebSocket (marathon) | ✅ Connected | Progress shows but no granular step detail |
| SSE (streaming analysis) | ✅ Backend ready | ❌ Not consumed by any frontend page |
| Video analysis API | ✅ Backend ready | ⚠️ VideoAnalyzer component exists but NOT integrated into wizard or dashboard |
| Audio processing | ✅ Backend ready | ⚠️ LiveTranscriptionBox works but audio NOT sent to Gemini for native processing |
| Image generation | ✅ Backend ready | ⚠️ CreativeAutopilot exists but UX is form-heavy, not visual |
| Menu transform | ✅ Backend ready | ⚠️ Accessible from BCG page but hidden in collapsible |
| Grounding sources | ✅ Backend ready | ⚠️ GroundedSources component exists but rarely shown |
| Multi-agent debates | ✅ Backend ready | ⚠️ Only shown on overview, not on relevant analysis pages |
| Vibe engineering | ✅ Backend ready | ❌ useVibeEngineering hook exists but NO UI triggers it |

---

## 3. Current UX Heuristic Evaluation

### 3.1 Nielsen's 10 Heuristics Assessment

| # | Heuristic | Score | Issues |
|---|-----------|-------|--------|
| 1 | **Visibility of system status** | 5/10 | Pipeline progress exists but gives no ETAs. No per-stage progress bars. User doesn't know what's happening during 2-5 min analysis. |
| 2 | **Match between system and real world** | 7/10 | BCG terminology (Stars, Dogs) is good. But "Marathon Agent" and "Vibe Engineering" are developer terms leaked to UI. |
| 3 | **User control and freedom** | 4/10 | No way to re-run individual analyses. No way to edit inputs after submission. No undo for any action. |
| 4 | **Consistency and standards** | 6/10 | Tab navigation is consistent. But card styles, spacing, and color usage vary across pages. |
| 5 | **Error prevention** | 5/10 | File type validation exists. But no preview before submission. No confirmation dialog before starting analysis. |
| 6 | **Recognition over recall** | 6/10 | Good labels on wizard steps. But analysis pages don't remind user what data was provided. |
| 7 | **Flexibility and efficiency** | 4/10 | "Quick Start" button exists. But no keyboard shortcuts, no bulk actions, no expert mode. |
| 8 | **Aesthetic and minimalist design** | 6/10 | Clean layout. But too much white space in some areas, too dense in others. Inconsistent card hierarchy. |
| 9 | **Help users recognize, diagnose, recover from errors** | 4/10 | Generic error messages. No recovery suggestions. Failed analysis gives no actionable guidance. |
| 10 | **Help and documentation** | 2/10 | No onboarding. No tooltips explaining AI concepts. No "what does this mean?" for BCG categories. |

**Overall Score: 49/100** — Functional but not production-ready.

### 3.2 Critical User Journey Pain Points

```
JOURNEY: Restaurant Owner → Setup → Analysis → Action

Pain Point 1: "WHAT'S HAPPENING?" (Setup → Analysis transition)
┌─────────────────────────────────────────────────────┐
│ User clicks "Analyze My Business"                    │
│ → Sees spinning loader for 3-5 seconds              │
│ → Redirected to analysis page                       │
│ → Sees mostly empty cards with "Processing..."      │
│ → Waits 2-5 minutes with minimal feedback           │
│ → Has no idea which step is running or why           │
│                                                      │
│ FIX: Progressive reveal with rich AI storytelling    │
└─────────────────────────────────────────────────────┘

Pain Point 2: "WHAT DO I DO WITH THIS?" (Analysis → Action gap)
┌─────────────────────────────────────────────────────┐
│ User sees BCG matrix with categories                 │
│ → Doesn't understand "Plowhorse" means               │
│ → Sees strategic recommendations as text blocks      │
│ → No "Apply this" or "Generate campaign for this"   │
│ → No connection between analysis and creative tools  │
│                                                      │
│ FIX: Actionable insights with one-click follow-ups   │
└─────────────────────────────────────────────────────┘

Pain Point 3: "I UPLOADED A VIDEO BUT NOTHING HAPPENED"
┌─────────────────────────────────────────────────────┐
│ User uploads video in DataUploadStep                 │
│ → Video is sent to backend with FormData             │
│ → Backend has video analysis capability              │
│ → BUT no video analysis results shown anywhere       │
│ → User never sees Gemini's video insights            │
│                                                      │
│ FIX: Dedicated video insights section in dashboard   │
└─────────────────────────────────────────────────────┘

Pain Point 4: "THE VOICE THING DIDN'T DO ANYTHING"
┌─────────────────────────────────────────────────────┐
│ User records voice note in StoryStep                 │
│ → LiveTranscriptionBox captures audio                │
│ → Audio blob is stored in formData                   │
│ → Sent to backend as audio_files                     │
│ → BUT transcription is simulated (placeholder)      │
│ → User sees no transcribed text appear               │
│                                                      │
│ FIX: Real Gemini audio → text in real-time           │
└─────────────────────────────────────────────────────┘
```

---

## 4. Gemini 3 Capability Gap Analysis

### What Gemini 3 Can Do vs. What the UI Exposes

| Gemini 3 Capability | Backend Ready? | Frontend Exposes? | UX Quality | Priority to Fix |
|---|---|---|---|---|
| **Menu extraction from photo** | ✅ Yes | ⚠️ Partial — upload only, no live preview | Low | P0 |
| **Native video analysis** | ✅ Yes | ❌ VideoAnalyzer exists but disconnected | None | P0 |
| **Native audio processing** | ✅ Yes | ❌ Transcription is simulated/placeholder | None | P0 |
| **Image generation (Imagen 3)** | ✅ Yes | ⚠️ CreativeAutopilot form only | Low | P1 |
| **Menu style transfer** | ✅ Yes | ⚠️ Hidden in BCG collapsible | Low | P1 |
| **Google Search grounding** | ✅ Yes | ⚠️ GroundedSources component rarely shown | Low | P1 |
| **Multi-agent debates** | ✅ Yes | ⚠️ Only on overview page | Medium | P2 |
| **Streaming thought visualization** | ✅ Yes (SSE) | ⚠️ ThoughtBubbleStream exists but passive | Medium | P1 |
| **Vibe engineering (auto-improve)** | ✅ Yes | ❌ Hook exists, no UI trigger | None | P2 |
| **Batch image processing** | ✅ Yes | ❌ No batch photo review UI | None | P2 |
| **PDF understanding** | ✅ Yes | ⚠️ PDF upload works, no specific feedback | Low | P2 |
| **Competitive intelligence grounding** | ✅ Yes | ⚠️ Data exists but visual comparison poor | Low | P1 |
| **Instagram engagement prediction** | ✅ Yes | ⚠️ InstagramPredictor exists but isolated | Medium | P2 |
| **Dish photo quality scoring** | ✅ Yes | ❌ Backend scores photos, no visual gallery | None | P1 |

### Multimodal "WOW Moments" — Currently Missing

These are the moments that would make a judge/investor/user say "wow":

1. **Live Menu Scan** — Point phone camera → see menu items extracted in real-time with prices
2. **Dish Photo Scorecard** — Upload photo → instant visual quality assessment with improvement suggestions overlay
3. **Video Insights Timeline** — Upload video → interactive timeline with key moments, quality scores, platform recommendations
4. **Voice-to-Strategy** — Speak about your business → see Gemini synthesize it into a strategic profile in real-time
5. **Before/After Menu Design** — Side-by-side menu transformation with Imagen 3
6. **AI Agent Debate Live** — Watch agents debate a strategic decision in real-time as analysis runs
7. **Campaign Visual Preview** — See generated campaign assets rendered as Instagram/TikTok mockups
8. **Competitive Landscape Map** — Interactive map showing your restaurant vs. competitors with data overlays

---

## 5. Phase 1: Foundation & Polish (Week 1-2)

> **Goal**: Fix structural UX issues, establish design system consistency, and create the foundation for multimodal features.

### 5.1 Design System Standardization

**Files to modify**: All component files

```
Design Tokens to Establish:
├── Colors
│   ├── Primary: Purple-600 (AI/Gemini brand)
│   ├── Secondary: Blue-600 (data/analysis)
│   ├── Success: Green-600 (completed/positive)
│   ├── Warning: Amber-500 (in progress/attention)
│   ├── Danger: Red-600 (errors/negative)
│   └── Neutral: Gray scale (backgrounds/text)
│
├── Spacing Scale: 4px base (4, 8, 12, 16, 24, 32, 48, 64)
├── Border Radius: sm(6px), md(8px), lg(12px), xl(16px), 2xl(24px)
├── Shadows: sm, md, lg (consistent elevation system)
└── Typography: Inter for UI, JetBrains Mono for data/code
```

**Action Items**:

| # | Task | File(s) | Impact |
|---|------|---------|--------|
| 1.1 | Create `design-tokens.css` with CSS custom properties | `globals.css` | Foundation |
| 1.2 | Standardize card component variants (elevated, flat, interactive) | `components/ui/card.tsx` | Visual consistency |
| 1.3 | Create `StatusBadge` component for pipeline states | New: `components/ui/StatusBadge.tsx` | Reusability |
| 1.4 | Normalize spacing in all analysis pages | `analysis/*/page.tsx` | Visual rhythm |
| 1.5 | Add consistent loading skeletons to all data sections | All analysis pages | Perceived performance |

### 5.2 Setup Wizard UX Overhaul

**Current issues**:
- No visual preview of uploaded files (images/PDFs)
- No file size/count limits communicated
- Voice recording has no real transcription feedback
- "Quick Start" button doesn't explain consequences of skipping

**Action Items**:

| # | Task | File(s) | Impact |
|---|------|---------|--------|
| 1.6 | Add image thumbnail previews to DataUploadStep | `DataUploadStep.tsx` | Trust + delight |
| 1.7 | Add PDF page count display for menu uploads | `DataUploadStep.tsx` | Feedback |
| 1.8 | Show "What you'll get" comparison for Quick Start vs. Full Setup | `SetupWizard.tsx` | Informed decisions |
| 1.9 | Add confirmation modal before "Analyze My Business" with data summary | `WizardPage.tsx` | Error prevention |
| 1.10 | Persist uploaded file names (not blobs) to show returning user what was uploaded | `SetupWizard.tsx` | Context recovery |

### 5.3 Analysis Dashboard Structure

**Current issues**:
- Overview page is passive — shows data but no actions
- Tabs don't indicate completion status
- No "Suggested next action" flow
- No export/share functionality

**Action Items**:

| # | Task | File(s) | Impact |
|---|------|---------|--------|
| 1.11 | Add completion badges to tab navigation | `layout.tsx` | Status visibility |
| 1.12 | Create "Quick Actions" bar at top of overview | `analysis/page.tsx` | Actionability |
| 1.13 | Add "Export Report" button (PDF generation) | New: `components/common/ExportButton.tsx` | Business value |
| 1.14 | Add "Re-run Analysis" option per section | All analysis pages | User control |
| 1.15 | Create "What's Next" CTA at bottom of each analysis page | All analysis pages | Flow guidance |

---

## 6. Phase 2: Multimodal Experience Revolution (Week 2-4)

> **Goal**: Connect ALL Gemini 3 multimodal capabilities to the frontend with rich, interactive UX.

### 6.1 Live Menu Extraction Preview

**The killer feature**: User uploads menu image → sees items extracted in real-time with a split-view.

**Implementation**:

```
┌──────────────────────────────────────────────────┐
│  Menu Upload                                      │
│  ┌─────────────────┐  ┌─────────────────────────┐│
│  │                  │  │ Extracted Items          ││
│  │  [Menu Image]    │  │ ┌─────────────────────┐ ││
│  │                  │  │ │ Tacos al Pastor  $12 │ ││
│  │  (with bounding  │  │ │ Guacamole        $8  │ ││
│  │   box overlays)  │  │ │ Agua Fresca      $4  │ ││
│  │                  │  │ └─────────────────────┘ ││
│  └─────────────────┘  │ 12 items · 3 categories ││
│                        │ Confidence: 94%          ││
│                        └─────────────────────────┘│
└──────────────────────────────────────────────────┘
```

| # | Task | File(s) | Impact |
|---|------|---------|--------|
| 2.1 | Create `MenuExtractionPreview` component with split view | New: `components/multimodal/MenuExtractionPreview.tsx` | WOW factor |
| 2.2 | Add real-time extraction API call on image upload in DataUploadStep | `DataUploadStep.tsx` | Immediate value |
| 2.3 | Allow inline editing of extracted items before submission | `MenuPreviewCard.tsx` | User control |
| 2.4 | Show extraction confidence per item with color coding | `MenuExtractionPreview.tsx` | Trust |

### 6.2 Native Video Analysis Integration

**The differentiator**: This is what GPT-4V and Claude CANNOT do. Must be prominently featured.

```
┌──────────────────────────────────────────────────┐
│  🎥 Video Intelligence (Gemini 3 Exclusive)       │
│  ┌─────────────────────────────────────────────┐ │
│  │ [Video Player with Timeline]                 │ │
│  │ ──●────────────●───────●──────────           │ │
│  │   0:05         0:32    0:48                  │ │
│  │   "Chef prep"  "Plating" "Service"           │ │
│  └─────────────────────────────────────────────┘ │
│                                                    │
│  Quality Scores    Platform Suitability             │
│  ┌──────────┐     ┌───────────────────────┐       │
│  │ Visual 8.5│     │ Instagram Reels  9.2  │       │
│  │ Audio  7.0│     │ TikTok           8.8  │       │
│  │ Overall 7.8│    │ YouTube Shorts   7.5  │       │
│  └──────────┘     └───────────────────────┘       │
│                                                    │
│  📋 Recommended Cuts                               │
│  • Trim intro to start at 0:03 for better hook    │
│  • Best thumbnail at 0:32 (plating shot)          │
│  • Add text overlay at 0:15 for engagement        │
└──────────────────────────────────────────────────┘
```

| # | Task | File(s) | Impact |
|---|------|---------|--------|
| 2.5 | Create `VideoInsightsPanel` with interactive timeline | New: `components/multimodal/VideoInsightsPanel.tsx` | WOW factor |
| 2.6 | Integrate VideoAnalyzer into DataUploadStep (auto-analyze on upload) | `DataUploadStep.tsx`, `VideoAnalyzer.tsx` | Multimodal showcase |
| 2.7 | Add video analysis results section to Analysis Overview | `analysis/page.tsx` | Visibility |
| 2.8 | Create platform mockup previews (Instagram/TikTok frame overlays) | New: `components/creative/PlatformMockup.tsx` | Delight |
| 2.9 | Add "Gemini 3 Exclusive" badge to video features | Global | Competitive positioning |

### 6.3 Native Audio → Gemini Integration

**Current gap**: `LiveTranscriptionBox` records audio but `simulateLiveTranscription()` is a placeholder.

| # | Task | File(s) | Impact |
|---|------|---------|--------|
| 2.10 | Implement real audio streaming to backend Gemini endpoint | `LiveTranscriptionBox.tsx`, New backend route | Core feature |
| 2.11 | Show real-time transcription with word-by-word animation | `LiveTranscriptionBox.tsx` | Delight |
| 2.12 | Add emotional tone detection badge from audio analysis | `LiveTranscriptionBox.tsx` | AI showcase |
| 2.13 | Display detected themes/values as tags after recording completes | `StoryStep.tsx` | Immediate value |

### 6.4 Dish Photo Gallery with AI Scoring

**Backend has**: `SocialAestheticsAnalyzer`, `DishAnalysisSchema` with presentation/lighting/composition/Instagram scores.

```
┌──────────────────────────────────────────────────┐
│  📸 Dish Photo Intelligence                       │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │ [Photo] │ │ [Photo] │ │ [Photo] │           │
│  │ Tacos   │ │ Guac    │ │ Pozole  │           │
│  │ ⭐ 8.5  │ │ ⭐ 6.2  │ │ ⭐ 9.1  │           │
│  │ IG: 8.8 │ │ IG: 5.5 │ │ IG: 9.4 │           │
│  └─────────┘ └─────────┘ └─────────┘           │
│                                                    │
│  🔍 Selected: Guacamole (Score: 6.2/10)          │
│  ├── Lighting: 5/10 — "Too dark, add fill light" │
│  ├── Composition: 7/10 — "Good angle"            │
│  ├── Presentation: 6/10 — "Add garnish"          │
│  └── Quick Fix: "Retake with natural light + lime│
│       garnish for estimated 40% engagement boost" │
└──────────────────────────────────────────────────┘
```

| # | Task | File(s) | Impact |
|---|------|---------|--------|
| 2.14 | Create `DishPhotoGallery` with scoring cards | New: `components/multimodal/DishPhotoGallery.tsx` | Visual showcase |
| 2.15 | Add photo analysis results to Analysis Overview | `analysis/page.tsx` | Visibility |
| 2.16 | Create photo detail modal with improvement suggestions | New: `components/multimodal/PhotoDetailModal.tsx` | Actionability |
| 2.17 | Add "Retake Suggestion" CTA with specific improvement tips | `DishPhotoGallery.tsx` | Practical value |

---

## 7. Phase 3: Agentic Intelligence Layer (Week 4-6)

> **Goal**: Make the AI reasoning visible, interactive, and actionable throughout the application.

### 7.1 Enhanced Analysis Pipeline Experience

**Replace the passive "Processing..." with an engaging, educational AI storytelling experience.**

```
┌──────────────────────────────────────────────────┐
│  🧠 Gemini is Analyzing Your Business              │
│                                                    │
│  Stage 3 of 12: Competitor Discovery               │
│  ████████████░░░░░░░░░░░░░░░░░░░░ 25%             │
│  ⏱ ~3 min remaining                                │
│                                                    │
│  💭 "I found 8 restaurants within 1 mile.          │
│      Now analyzing their menus and reviews          │
│      to understand your competitive position..."    │
│                                                    │
│  Recent discoveries:                                │
│  ✅ Menu extracted: 47 items across 6 categories   │
│  ✅ 3 direct competitors identified                │
│  🔄 Analyzing competitor pricing...                │
│  ⏳ Sentiment analysis queued                       │
│                                                    │
│  [See AI Reasoning ▾]  [Pause]  [Skip to Results] │
└──────────────────────────────────────────────────┘
```

| # | Task | File(s) | Impact |
|---|------|---------|--------|
| 3.1 | Create `AnalysisPipelineExperience` — full-page analysis storytelling | New: `components/analysis/PipelineExperience.tsx` | WOW factor |
| 3.2 | Add ETA estimation based on data volume | Backend: `orchestrator.py`, Frontend: `PipelineExperience.tsx` | User expectation |
| 3.3 | Show progressive "discoveries" as each stage completes | `PipelineExperience.tsx` | Engagement |
| 3.4 | Add "AI Reasoning" expandable panel showing ThoughtTraces | `PipelineExperience.tsx` | Transparency |
| 3.5 | Implement "Skip to Results" for impatient users | `PipelineExperience.tsx` | User control |

### 7.2 Multi-Agent Debate Integration

**Move debates from overview-only to contextual placement throughout the app.**

| # | Task | File(s) | Impact |
|---|------|---------|--------|
| 3.6 | Add debate triggers on BCG page for controversial items | `bcg/page.tsx` | Depth |
| 3.7 | Add competitor debate panel on competitors page | `competitors/page.tsx` | Multiple perspectives |
| 3.8 | Add "Ask the AI Agents" button on any recommendation | All analysis pages | Interactivity |
| 3.9 | Animate debate panels to show agents "thinking" sequentially | `MultiAgentDebatePanel.tsx` | Engagement |

### 7.3 Vibe Engineering UI

**The backend has a complete auto-verification and improvement loop — expose it.**

| # | Task | File(s) | Impact |
|---|------|---------|--------|
| 3.10 | Create `QualityAssurancePanel` showing verification history | New: `components/ai/QualityAssurancePanel.tsx` | Trust |
| 3.11 | Add "Improve this analysis" button that triggers vibe loop | All analysis pages | Interactivity |
| 3.12 | Show quality score evolution chart (iteration 1 → 2 → 3) | `QualityAssurancePanel.tsx` | Transparency |
| 3.13 | Add confidence indicators to every AI-generated insight | All analysis components | Trust calibration |

### 7.4 Grounding & Source Attribution

**Make grounded insights feel trustworthy with clear source attribution.**

| # | Task | File(s) | Impact |
|---|------|---------|--------|
| 3.14 | Show grounding sources inline with every analysis section | All analysis pages | Trust |
| 3.15 | Add "Verified by Google Search" badges to grounded data | `GroundedSources.tsx` | Credibility |
| 3.16 | Create source detail modal with snippets and relevance scores | New: `components/common/SourceDetailModal.tsx` | Deep dive |

---

## 8. Phase 4: Creative Studio & Delight (Week 6-8)

> **Goal**: Create an integrated creative workspace that turns analysis into action.

### 8.1 Unified Creative Studio

**Merge all creative tools into one visual workspace.**

```
┌──────────────────────────────────────────────────┐
│  🎨 Creative Studio                               │
│  ┌─────────────────────────────────────────────┐ │
│  │ [Sidebar]          [Canvas]                  │ │
│  │                                              │ │
│  │ 📋 Menu Items      ┌─────────────────────┐  │ │
│  │  ⭐ Tacos (Star)   │                     │  │ │
│  │  🐴 Pozole         │  [Generated Asset]  │  │ │
│  │  🧩 Enchiladas     │                     │  │ │
│  │                    │  Instagram Post      │  │ │
│  │ 🎯 Strategy        │  for "Tacos al      │  │ │
│  │  Promote Stars     │  Pastor"             │  │ │
│  │  Boost Puzzles     │                     │  │ │
│  │                    └─────────────────────┘  │ │
│  │ 🖼️ Style           A/B Variants:           │ │
│  │  ○ Minimalist      [Var A] [Var B] [Var C] │ │
│  │  ● Rustic                                   │ │
│  │  ○ Luxury          Platforms:               │ │
│  │                    [IG] [TikTok] [FB] [Web] │ │
│  └─────────────────────────────────────────────┘ │
│                                                    │
│  [Generate Campaign]  [A/B Test]  [Export All]    │
└──────────────────────────────────────────────────┘
```

| # | Task | File(s) | Impact |
|---|------|---------|--------|
| 4.1 | Create `CreativeStudio` unified workspace layout | New: `components/creative/CreativeStudio.tsx` | Product differentiator |
| 4.2 | Add dish selector sidebar with BCG category filters | `CreativeStudio.tsx` | Context |
| 4.3 | Create platform-specific preview frames (IG Story, Post, Reel, TikTok, Web Banner) | New: `components/creative/PlatformPreview.tsx` | Professional quality |
| 4.4 | Integrate A/B variant generation with side-by-side comparison | `ABTestingPanel.tsx` | Decision support |
| 4.5 | Add one-click export per platform (correct aspect ratios + text overlays) | `CreativeStudio.tsx` | Practical value |

### 8.2 Menu Transformation Experience

**Make Imagen 3 menu style transfer a visual, interactive experience.**

| # | Task | File(s) | Impact |
|---|------|---------|--------|
| 4.6 | Create before/after slider for menu transformations | New: `components/creative/BeforeAfterSlider.tsx` | WOW factor |
| 4.7 | Add style gallery with visual previews (not just text labels) | `MenuTransformation.tsx` | Discoverability |
| 4.8 | Show transformation progress with Gemini thinking animation | `MenuTransformation.tsx` | Engagement |

### 8.3 Microinteractions & Motion Design

| # | Task | File(s) | Impact |
|---|------|---------|--------|
| 4.9 | Add Framer Motion for page transitions between analysis tabs | `layout.tsx` | Polish |
| 4.10 | Create number count-up animations for KPI cards | All analysis pages | Delight |
| 4.11 | Add staggered card entrance animations for analysis results | All analysis pages | Professional feel |
| 4.12 | Create pulsing "AI thinking" indicator for active processes | New: `components/ui/AIThinkingIndicator.tsx` | Status visibility |
| 4.13 | Add confetti/celebration animation when analysis completes | `analysis/page.tsx` | Emotional reward |

---

## 9. Component Architecture Recommendations

### 9.1 New Component Tree

```
components/
├── ui/                          # Primitive design system
│   ├── StatusBadge.tsx          # NEW: Pipeline status badges
│   ├── AIThinkingIndicator.tsx  # NEW: Pulsing AI activity dot
│   ├── ScoreRing.tsx            # NEW: Circular score indicator
│   ├── BeforeAfterSlider.tsx    # NEW: Image comparison slider
│   └── ConfirmDialog.tsx        # NEW: Action confirmation
│
├── multimodal/                  # Gemini 3 multimodal features
│   ├── MenuExtractionPreview.tsx    # NEW: Live extraction split-view
│   ├── VideoInsightsPanel.tsx       # NEW: Video timeline + scores
│   ├── DishPhotoGallery.tsx         # NEW: Photo scoring gallery
│   ├── PhotoDetailModal.tsx         # NEW: Photo improvement detail
│   ├── LiveTranscriptionBox.tsx     # ENHANCE: Real Gemini transcription
│   └── AudioInsightsCard.tsx        # NEW: Transcription themes/values
│
├── analysis/                    # Analysis result displays
│   ├── PipelineExperience.tsx       # NEW: Engaging analysis progress
│   ├── InsightActionCard.tsx        # NEW: Insight → Action CTA
│   ├── CompetitorMap.tsx            # NEW: Geographic competitor view
│   └── SentimentTimeline.tsx        # NEW: Review sentiment over time
│
├── ai/                          # AI transparency layer
│   ├── QualityAssurancePanel.tsx    # NEW: Vibe engineering UI
│   ├── ReasoningExplorer.tsx        # NEW: Interactive thought drill-down
│   └── AgentDebateTrigger.tsx       # NEW: "Ask AI Agents" button
│
├── creative/                    # Creative generation tools
│   ├── CreativeStudio.tsx           # NEW: Unified workspace
│   ├── PlatformPreview.tsx          # NEW: Platform-specific frames
│   └── CampaignExportPanel.tsx      # NEW: Multi-format export
│
└── common/                      # Shared components
    ├── ExportButton.tsx             # NEW: PDF/CSV export
    ├── SourceDetailModal.tsx        # NEW: Grounding source detail
    ├── OnboardingTooltip.tsx        # NEW: Feature education
    └── EmptyState.tsx               # NEW: Consistent empty states
```

### 9.2 State Management Recommendations

```
Current: Props drilling + Context (SessionContext)
Recommendation: Keep Context pattern but add:

1. useAnalysisStore (Zustand) — Cross-tab analysis state
   - bcgData, sentimentData, competitorData, campaignData
   - Avoids re-fetching when switching tabs
   
2. useMultimodalStore — Upload state + analysis results
   - menuImages, dishPhotos, videos, audioRecordings
   - extractionResults, photoScores, videoAnalysis
   
3. useCreativeStore — Creative studio state
   - selectedDish, selectedPlatform, generatedAssets
   - abTestVariants, exportQueue
```

---

## 10. Implementation Priority Matrix

### Impact vs. Effort Grid

```
HIGH IMPACT
    │
    │  ★ 2.1 Menu Extraction    ★ 3.1 Pipeline Experience
    │    Preview (P0)              (P0)
    │
    │  ★ 2.5 Video Insights     ★ 4.1 Creative Studio
    │    Panel (P0)                (P1)
    │
    │  ★ 2.10 Real Audio        ★ 2.14 Photo Gallery
    │    Transcription (P0)        (P1)
    │
    │  ★ 1.11 Tab Badges        ★ 3.10 QA Panel
    │    (P1)                      (P2)
    │
    │  ★ 1.6 Image Previews     ★ 4.9 Page Transitions
    │    (P1)                      (P2)
    │
LOW ├──────────────────────────────────────── HIGH EFFORT
    │
    │  1.1 Design Tokens (P1)   4.6 Before/After Slider (P2)
    │  1.9 Confirm Dialog (P1)  3.8 Ask AI Agents (P2)
    │
LOW IMPACT
```

### Sprint Breakdown

**Sprint 1 (Week 1-2): Foundation**
- [ ] 1.1–1.5: Design system standardization
- [ ] 1.6–1.10: Wizard UX improvements
- [ ] 1.11–1.15: Dashboard structure improvements

**Sprint 2 (Week 2-3): Multimodal Core**
- [ ] 2.1–2.4: Live menu extraction preview
- [ ] 2.5–2.9: Video analysis integration
- [ ] 2.10–2.13: Real audio processing

**Sprint 3 (Week 3-5): Intelligence Layer**
- [ ] 2.14–2.17: Photo gallery + scoring
- [ ] 3.1–3.5: Pipeline experience
- [ ] 3.6–3.9: Contextual debates

**Sprint 4 (Week 5-7): Creative & Polish**
- [ ] 3.10–3.16: Vibe engineering + grounding UI
- [ ] 4.1–4.8: Creative studio
- [ ] 4.9–4.13: Microinteractions

---

## Appendix A: Key Metrics to Track

| Metric | Current (Est.) | Target | How to Measure |
|--------|---------------|--------|----------------|
| Setup completion rate | ~40% | 80% | Wizard step funnel analytics |
| Time to first insight | 3-5 min | <2 min (progressive) | Time from submit to first card populated |
| Feature discovery rate | ~30% | 75% | % of users who interact with video/voice/creative |
| Analysis page bounce rate | High (Est.) | <20% | Users who leave without exploring tabs |
| Creative asset generation | <5% of sessions | 40% of sessions | API call tracking |
| User confidence in AI results | Unknown | >80% (survey) | Post-analysis NPS |

## Appendix B: Technical Dependencies

```
New packages needed:
├── framer-motion — Page transitions + microinteractions
├── zustand — Lightweight cross-component state management  
├── react-compare-slider — Before/after image comparison
├── @tanstack/react-query — Server state management + caching
├── recharts (already present?) — Data visualization
├── html2canvas + jsPDF — Client-side PDF export
└── canvas-confetti — Celebration animation
```

---

*This document should be treated as a living plan. Each phase should be validated with user testing before proceeding to the next. The priority order is designed to maximize "wow factor" for the Gemini 3 Hackathon while building toward a production-ready product.*
