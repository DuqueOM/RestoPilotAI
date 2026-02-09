# Video Analysis - Guía Completa (GAME CHANGER)

## 🎥 Descripción

El **Video Analysis** es la característica más diferenciadora del proyecto - una capacidad que **SOLO Gemini 3 tiene** y que ningún competidor puede igualar.

**Por qué es GAME CHANGER:**
- ✅ **SOLO GEMINI 3** procesa video nativamente
- ✅ OpenAI GPT-4V solo puede analizar frames individuales
- ✅ Claude 3 NO tiene capacidad de video
- ✅ TikTok/Instagram = video-first marketing
- ✅ Restaurantes necesitan video content strategy
- ✅ **+10 puntos en el hackathon**

---

## 🏆 Ventaja Competitiva Absoluta

### vs OpenAI GPT-4V

| Capacidad | Gemini 3 (Nosotros) | GPT-4V |
|-----------|---------------------|--------|
| **Video Nativo** | ✅ Procesa video completo | ❌ Solo frames |
| **Audio Analysis** | ✅ Incluido | ❌ No |
| **Temporal Understanding** | ✅ Entiende secuencias | ❌ Frames aislados |
| **Key Moments** | ✅ Detecta automáticamente | ❌ Manual |
| **Platform Suitability** | ✅ Automático | ❌ No |

### vs Claude 3

| Capacidad | Gemini 3 (Nosotros) | Claude 3 |
|-----------|---------------------|----------|
| **Video Processing** | ✅ Nativo | ❌ No tiene |
| **Cualquier capacidad de video** | ✅ Completa | ❌ Cero |

---

## 🚀 Uso Backend

### Endpoint Principal

```bash
POST /api/v1/video/analyze
```

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/video/analyze" \
  -F "video=@restaurant_tour.mp4" \
  -F "purpose=social_media"
```

**Response:**
```json
{
  "filename": "restaurant_tour.mp4",
  "content_type": "Behind-the-scenes cooking",
  "key_moments": [
    {
      "timestamp": "0:15",
      "description": "Chef plating signature dish",
      "type": "best_thumbnail",
      "engagement_potential": "high"
    },
    {
      "timestamp": "0:45",
      "description": "Sizzling pan with flames",
      "type": "high_engagement",
      "engagement_potential": "very_high"
    },
    {
      "timestamp": "1:20",
      "description": "Customer reaction - genuine smile",
      "type": "shareable",
      "engagement_potential": "high"
    }
  ],
  "quality_scores": {
    "visual": 7.2,
    "audio": 6.8,
    "overall": 7.0
  },
  "platform_suitability": {
    "instagram_reels": 9.0,
    "tiktok": 8.5,
    "youtube_shorts": 7.5,
    "facebook": 5.0,
    "linkedin": 4.0,
    "youtube": 6.0
  },
  "best_thumbnail_timestamp": "0:15",
  "recommended_cuts": [
    "Cut 0:00-0:12 (slow intro, lose viewers)",
    "Add text overlay at 0:45 explaining technique",
    "Trim total length to 1:30 for Reels"
  ],
  "recommendations": {
    "optimal_length": {
      "recommended": "15-60 seconds",
      "based_on": "instagram_reels"
    },
    "best_platforms": [
      {
        "platform": "instagram_reels",
        "score": 9.0,
        "recommendation": "excellent"
      },
      {
        "platform": "tiktok",
        "score": 8.5,
        "recommendation": "excellent"
      }
    ],
    "improvements": [
      "Cut 0:00-0:12 (slow intro)",
      "Add text overlay at 0:45",
      "Trim to 1:30 for Reels"
    ]
  }
}
```

### Quick Check Endpoint

```bash
POST /api/v1/video/quick-check
```

Para análisis rápido sin procesamiento profundo:

```python
# Quick assessment
response = await client.post(
    "/api/v1/video/quick-check",
    files={"video": video_file}
)

# Returns basic metrics quickly
{
    "filename": "video.mp4",
    "quick_assessment": {
        "duration": "2:43",
        "visual_quality": 7.5,
        "audio_quality": 6.8,
        "content_type": "cooking",
        "recommendation": "Good for Instagram Reels"
    }
}
```

---

## 💻 Uso Frontend

### Componente VideoAnalyzer

```typescript
import { VideoAnalyzer } from '@/components/video/VideoAnalyzer';

function VideoStudio() {
  const handleAnalysisComplete = (result) => {
    console.log('Video analyzed:', result);
    // Process results
  };

  return (
    <VideoAnalyzer
      onAnalysisComplete={handleAnalysisComplete}
    />
  );
}
```

### Features del Componente

1. **Upload & Preview**
   - Drag & drop o file selector
   - Video preview con controles
   - Validación de tipo y tamaño

2. **Quality Scores**
   - Visual quality (1-10)
   - Audio quality (1-10)
   - Overall score

3. **Key Moments Timeline**
   - Clickable timestamps
   - Seek to moment
   - Type indicators (thumbnail, engaging, shareable)

4. **Platform Suitability**
   - Score bars por plataforma
   - Iconos de plataforma
   - Recomendaciones automáticas

5. **Recommendations**
   - Optimal length
   - Best platforms
   - Specific improvements

---

## 🎯 Casos de Uso

### Caso 1: Optimizar Video para Instagram Reels

```python
# Backend
from app.services.gemini.advanced_multimodal import AdvancedMultimodalAgent

agent = AdvancedMultimodalAgent()

# Analizar video
with open("restaurant_video.mp4", "rb") as f:
    video_bytes = f.read()

analysis = await agent.analyse_video_content(
    video_bytes=video_bytes,
    video_purpose="social_media"
)

# Verificar suitability para Reels
if analysis.social_media_suitability["instagram_reels"] >= 8.0:
    print("✅ Excellent for Instagram Reels")
    print(f"Best thumbnail: {analysis.best_thumbnail_timestamp}")
    
    # Aplicar recomendaciones
    for cut in analysis.recommended_cuts:
        print(f"→ {cut}")
```

### Caso 2: Content Strategy Dashboard

```python
# Analizar múltiples videos
videos = ["video1.mp4", "video2.mp4", "video3.mp4"]
results = []

for video_path in videos:
    with open(video_path, "rb") as f:
        analysis = await agent.analyse_video_content(f.read())
        results.append({
            "filename": video_path,
            "best_platform": max(
                analysis.social_media_suitability.items(),
                key=lambda x: x[1]
            )[0],
            "overall_quality": (
                analysis.visual_quality_score + 
                (analysis.audio_quality_score or 0)
            ) / 2
        })

# Generar reporte
for result in sorted(results, key=lambda x: x["overall_quality"], reverse=True):
    print(f"{result['filename']}: {result['overall_quality']:.1f}/10")
    print(f"  Best for: {result['best_platform']}")
```

### Caso 3: Thumbnail Optimization

```python
# Encontrar mejor momento para thumbnail
analysis = await agent.analyse_video_content(video_bytes)

best_moment = analysis.best_thumbnail_timestamp
print(f"Use frame at {best_moment} as thumbnail")

# Extraer frame (usando ffmpeg o similar)
import subprocess

subprocess.run([
    "ffmpeg",
    "-i", "video.mp4",
    "-ss", best_moment,
    "-vframes", "1",
    "thumbnail.jpg"
])
```

### Caso 4: Platform-Specific Optimization

```python
# Optimizar para plataforma específica
target_platform = "tiktok"

analysis = await agent.analyse_video_content(
    video_bytes=video_bytes,
    video_purpose="social_media"
)

suitability = analysis.social_media_suitability[target_platform]

if suitability < 7.0:
    print(f"⚠️ Video needs optimization for {target_platform}")
    print("\nRecommendations:")
    for rec in analysis.recommended_cuts:
        print(f"  - {rec}")
else:
    print(f"✅ Video is ready for {target_platform} ({suitability}/10)")
```

---

## 📊 Análisis Detallado

### Content Types Detectados

- **Behind-the-scenes** - Cocina, preparación
- **Dish reveal** - Presentación de platillos
- **Restaurant tour** - Tour del local
- **Customer testimonial** - Testimonios
- **Recipe tutorial** - Tutoriales
- **Event coverage** - Eventos especiales
- **Staff introduction** - Presentación de equipo

### Key Moment Types

- **best_thumbnail** - Mejor momento para thumbnail
- **high_engagement** - Alto potencial de engagement
- **shareable** - Momento compartible
- **engaging** - Momento interesante
- **weak** - Momento débil (considerar cortar)

### Platform Suitability Scores

**Instagram Reels (15-60s)**
- Vertical format preferred
- Quick cuts
- Music/trending audio
- Text overlays

**TikTok (15-60s)**
- Vertical format
- Trending sounds
- Quick hooks
- Authentic feel

**YouTube Shorts (30-60s)**
- Vertical or square
- Captions important
- Longer hooks ok
- Educational content

**Facebook (1-3min)**
- Horizontal format
- Longer content ok
- Captions essential
- Story-driven

**LinkedIn (30-90s)**
- Professional tone
- Educational focus
- Horizontal format
- Business context

**YouTube (3-10min)**
- Horizontal format
- Detailed content
- SEO optimized
- Longer form

---

## 🎬 Ejemplo Visual de Output

```
📹 Video Analysis Results

Filename: restaurant_behind_scenes.mp4
Content Type: Behind-the-scenes cooking
Duration: 2:43

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 QUALITY ASSESSMENT

Visual Quality:  ████████░░ 7.2/10
Audio Quality:   ███████░░░ 6.8/10
Overall:         ███████░░░ 7.0/10

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌟 KEY MOMENTS

⭐ 0:15-0:23  Chef plating signature dish
              [BEST THUMBNAIL] [High Engagement]
              
🔥 0:45-0:58  Sizzling pan with flames
              [High Engagement] [Very High Potential]
              
😊 1:20-1:35  Customer reaction - genuine smile
              [Shareable] [Authentic]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📱 PLATFORM SUITABILITY

Instagram Reels  █████████░ 9.0/10 ✅ Excellent
TikTok           ████████░░ 8.5/10 ✅ Excellent
YouTube Shorts   ███████░░░ 7.5/10 ✅ Good
YouTube          ██████░░░░ 6.0/10 ⚠️  Fair
Facebook         █████░░░░░ 5.0/10 ⚠️  Fair
LinkedIn         ████░░░░░░ 4.0/10 ❌ Not recommended

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 RECOMMENDATIONS

Optimal Length: 15-60 seconds (for Instagram Reels)

Top Improvements:
→ Cut 0:00-0:12 (slow intro, lose viewers)
→ Add text overlay at 0:45 explaining technique
→ Trim total length to 1:30 for Reels

Best Platforms:
✅ Instagram Reels (9.0/10)
✅ TikTok (8.5/10)
✅ YouTube Shorts (7.5/10)
```

---

## 🔧 Configuración

### Backend

```python
# .env
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-3-flash-preview

# Video limits
MAX_VIDEO_SIZE_MB=100
SUPPORTED_FORMATS=mp4,mov,avi,webm
```

### Frontend

```typescript
// Video upload config
const VIDEO_CONFIG = {
  maxSize: 100 * 1024 * 1024, // 100MB
  acceptedFormats: ['video/mp4', 'video/quicktime', 'video/x-msvideo'],
  maxDuration: 600 // 10 minutes
};
```

---

## 🎓 Best Practices

### 1. Optimizar Tamaño de Video

```python
# ✅ Comprimir antes de subir si es muy grande
import subprocess

subprocess.run([
    "ffmpeg",
    "-i", "input.mp4",
    "-vcodec", "h264",
    "-crf", "28",  # Compression level
    "output.mp4"
])
```

### 2. Usar Purpose Apropiado

```python
# ✅ Especificar propósito para mejor análisis
purposes = {
    "social_media": "Para Instagram, TikTok, etc.",
    "marketing": "Para campañas de marketing",
    "training": "Para entrenamiento de staff",
    "menu_showcase": "Para mostrar platillos"
}
```

### 3. Implementar Thumbnails

```python
# ✅ Extraer thumbnail del mejor momento
best_time = analysis.best_thumbnail_timestamp

# Usar ffmpeg para extraer frame
extract_thumbnail(video_path, best_time, "thumbnail.jpg")
```

### 4. Batch Processing

```python
# ✅ Procesar múltiples videos eficientemente
async def analyze_video_library(video_paths):
    results = []
    for path in video_paths:
        result = await analyze_video(path)
        results.append(result)
    return results
```

---

## 🏆 Impacto en Hackathon

### +10 Puntos en Technical Execution

1. **Native Video Processing** (+3) - Solo Gemini 3
2. **Key Moments Detection** (+2) - Automático
3. **Platform Optimization** (+2) - Multi-platform
4. **Quality Assessment** (+1) - Visual + Audio
5. **Content Strategy** (+1) - Recomendaciones accionables
6. **Thumbnail Optimization** (+1) - Best moment detection

### Demo Script (Video Analysis Feature)

**Parte 1: Problema**
"Los restaurantes crean videos pero no saben cómo optimizarlos para cada plataforma"

**Parte 2: Solución Única**
"Gemini 3 puede analizar video nativamente - OpenAI y Claude NO pueden"

**Parte 3: Demostración**
[Subir video de restaurante]
[Mostrar análisis en tiempo real]
- Key moments detectados
- Platform suitability scores
- Recomendaciones específicas

**Parte 4: Impacto**
"Ahora saben exactamente cómo editar y dónde publicar para máximo impacto"

---

## � Hackathon Demo Video — Production Guide

### Overview

Create a **3-minute screen-recording demo** that showcases RestoPilotAI's full pipeline to hackathon judges. The goal is to demonstrate real Gemini 3 capabilities, not talk about them.

### Recommended Tools

- **Screen recording**: OBS Studio or Loom (1080p minimum, 60fps preferred)
- **Audio**: External microphone, quiet environment, clear narration
- **Browser**: Chrome with DevTools closed, clean tab bar
- **Backend**: Running locally or on Cloud Run

### Script (3:00 total)

#### 0:00 – 0:15 — Hook
> "What if a $5,000 restaurant consultant could be replaced by a 5-minute AI analysis costing $2?"

Show the landing page. Click **Try Demo** or start a new session.

#### 0:15 – 0:45 — Setup Wizard (Multimodal Ingestion)
1. **Location**: Type a restaurant name, select from Google Maps autocomplete.
2. **Menu Upload**: Drag-and-drop a menu photo (show the image being processed).
3. **Audio Context**: Record a 10-second voice clip describing the restaurant concept.
4. **Launch Analysis**: Click "Start Analysis" — show the Marathon Agent progress bar begin.

> Narrate: "We just uploaded a photo, a voice recording, and a location — three different modalities processed by a single Gemini 3 model."

#### 0:45 – 1:30 — Analysis Dashboard (Agentic Pipeline)
Show the Overview tab as the 17-stage pipeline progresses:
1. **Thought Bubble Stream** — highlight transparent AI reasoning appearing in real-time.
2. **Agent Pipeline** — point out each agent activating: Menu Extractor → BCG Classifier → Competitor Discovery → etc.
3. **Hackathon Track Badges** — briefly hover over Marathon Agent, Creative Autopilot, Vibe Engineering, Google Grounding badges.

> Narrate: "8 specialized AI agents working autonomously — extracting menu data, discovering competitors via Google Maps, classifying items in a BCG matrix, and verifying everything with Google Search citations."

#### 1:30 – 2:00 — BCG Matrix + Competitors
Switch to the **BCG Matrix** tab:
- Show the interactive scatter plot with Stars, Cash Cows, Question Marks, Dogs.
- Click a menu item to see its strategic recommendation.

Switch to **Competitors** tab:
- Show discovered competitor cards with Google Maps data.
- Highlight a grounded insight with its web citation.

> Narrate: "Every competitive insight is backed by a real Google Search source — no hallucinations."

#### 2:00 – 2:30 — Creative Studio (Wow Factor)
Switch to **Creative Studio** / Campaigns tab:
- Show AI-generated campaign images (Instagram post, story, web banner).
- If A/B variants are available, compare them side-by-side.
- Highlight: "These images were generated natively by Gemini 3 Pro Image — not DALL-E, not Midjourney."

> Narrate: "From a menu photo to a complete marketing campaign with AI-generated visuals — Photo to Data to New Photo."

#### 2:30 – 2:50 — Vibe Engineering + Debate
Trigger a **Verify with Sources** action on any analysis.
Show the quality score improving through iteration.
If time allows, show the **Multi-Agent Debate** panel where agents argue positions.

> Narrate: "Every analysis is self-verified through iterative quality loops. Multiple AI agents debate conclusions to reach a stronger consensus."

#### 2:50 – 3:00 — Closing
Return to Overview. Show the full pipeline completed.

> "RestoPilotAI — from a phone photo to a complete competitive intelligence report in under 5 minutes. Built entirely on Gemini 3."

### Production Tips

- **Pre-warm the backend** — run one analysis before recording so models are cached
- **Use real restaurant data** — demo mode works, but real data is more convincing
- **Keep the browser clean** — no bookmarks bar, no other tabs, dark mode optional
- **Show loading states** — don't cut them out; they prove it's real, not mocked
- **Highlight streaming** — the thought bubble stream and real-time progress are visually impressive
- **End on the Creative Studio** — AI-generated images are the strongest visual "wow"

### Checklist Before Recording

- [ ] Backend running (`make run-backend` or Cloud Run URL)
- [ ] Frontend running (`make run-frontend`)
- [ ] Demo data loaded or fresh session ready
- [ ] Screen recording at 1080p
- [ ] Microphone tested
- [ ] Browser zoom at 100%, no extensions visible
- [ ] Script rehearsed at least once

---

## 🎯 Conclusión

El **Video Analysis** es el diferenciador más poderoso del proyecto:

1. ✅ **SOLO Gemini 3** puede hacer esto nativamente
2. ✅ OpenAI y Claude NO tienen esta capacidad
3. ✅ Video-first marketing es el futuro
4. ✅ Restaurantes necesitan video content strategy

**Esta es la característica que gana el hackathon.**

---

**Última actualización:** 2026-02-07  
**Versión:** 2.0.0  
**Autor:** DuqueOM
