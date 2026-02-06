# RestoPilotAI — Plan de Acción UX/UI para Gemini 3 Hackathon

> **Análisis Staff UX/UI** | Febrero 2026  
> **Objetivo**: Maximizar puntuación en las 4 dimensiones del hackathon  
> **Criterios de Evaluación Oficiales (de gemini3.devpost.com)**:

| Criterio | Peso | Qué Evalúan |
|----------|------|-------------|
| **Technical Execution** | **40%** | ¿Demuestra desarrollo de calidad? ¿Aprovecha Gemini 3? ¿Código funcional? |
| **Innovation / Wow Factor** | **30%** | ¿Idea original? ¿Solución única? ¿Aborda problema significativo? |
| **Potential Impact** | **20%** | ¿Impacto real? ¿Útil para amplio mercado? ¿Resuelve eficientemente? |
| **Presentation / Demo** | **10%** | ¿Problema claro? ¿Demo efectiva? ¿Explican uso de Gemini 3? ¿Documentación? |

> **IMPORTANTE**: NO hay tracks específicos. Es abierto. Los jueces ven: demo video (≤3min), screenshots, texto (~200 palabras), link público, código público.

---

## 1. DIAGNÓSTICO ACTUAL

### 1.1 Lo que Tenemos (Fortalezas)

**Backend Excepcional** — 15+ módulos Gemini 3, pipeline de 17 etapas:
- `creative_autopilot.py` — Generación de campañas + Imagen 3 real
- `vibe_engineering.py` — Loops autónomos de verificación/mejora  
- `grounded_intelligence.py` — Google Search grounding con auto-citación
- `marathon_agent.py` — Tareas de larga duración con checkpoints
- `advanced_multimodal.py` — Video, audio, PDF, imágenes nativas
- `streaming_reasoning.py` — Thought streaming en tiempo real
- Todos los modelos en PRO (máxima calidad)

**Frontend Funcional** — Next.js 15, Tailwind, shadcn/ui:
- Wizard de 4 pasos (Location, Data, Story, Competitors)
- Dashboard con 5 tabs (Overview, BCG, Competitors, Sentiment, Campaigns)
- Componentes multimodales (DishPhotoGallery, VideoInsightsPanel, MenuExtractionPreview)
- WebSocket streaming, ThoughtBubbleStream, multi-agent debates

**Demo Data Configurada** — Margarita Pinta (Pasto, Colombia):
- 139 items de menú, ventas sintéticas 2023-2025 (57K registros)
- 44+ fotos del restaurante, 4 screenshots redes sociales
- 2 PDFs de menú, 1 video, logo
- `session.json` ya con datos BCG y campañas pre-calculados

### 1.2 Brechas Críticas para el Hackathon

| Problema | Impacto en Puntuación | Prioridad |
|----------|----------------------|-----------|
| **Landing page genérica** — No comunica inmediatamente qué hace Gemini 3 | Innovation -30%, Demo -10% | 🔴 CRÍTICA |
| **Demo no funciona de un click** — Jueces necesitan acceso sin login/paywall | Technical -40%, Demo -10% | 🔴 CRÍTICA |
| **Frontend expone ~30% del backend** — Capacidades invisibles para jueces | Technical -40%, Innovation -30% | 🔴 CRÍTICA |
| **No hay "wow moment" visual** — Nada espectacular en los primeros 10 segundos | Innovation -30% | 🔴 CRÍTICA |
| **Interfaz en inglés** — El negocio demo es colombiano, inconsistencia | Demo -10% | 🟡 ALTA |
| **Generación de imágenes no se demuestra visualmente** — Imagen 3 es diferenciador clave | Technical -40%, Innovation -30% | 🔴 CRÍTICA |
| **Resultados de análisis estáticos** — No muestran el proceso de razonamiento | Innovation -30% | 🟡 ALTA |

---

## 2. PLAN DE ACCIÓN — Priorizado por Impacto en Puntuación

### FASE 1: Landing Page que Impacte (Technical 40% + Innovation 30%)

**Problema**: La landing actual es un wizard genérico. Los jueces tienen 3 minutos máximo de video y un link. Necesitan ver en ≤5 segundos qué hace el producto y por qué Gemini 3 es esencial.

**Acciones**:

1. **Reestructurar Hero Section** — Antes del wizard, mostrar:
   - Headline potente: "Transform Restaurant Intelligence with Gemini 3"
   - Subtítulo que mencione las 5 capacidades multimodales
   - **Botón "See Live Demo" ENORME y prominente** (lo primero que debe ver el juez)
   - Botón "Start Your Own Analysis" secundario
   - Estadísticas de impacto: "17-stage AI pipeline", "5 modalities", "Real-time reasoning"

2. **Gemini 3 Capability Showcase** — Cards interactivas ANTES del wizard:
   - 🎨 **Image Generation** — "Native Imagen 3 for campaign visuals"
   - 🎥 **Video Analysis** — "Understand restaurant ambience from video"
   - 🎤 **Audio Understanding** — "Voice notes → business intelligence"  
   - 📄 **Document Intelligence** — "Menu PDFs → structured data in seconds"
   - 🔍 **Search Grounding** — "Auto-verified competitive intelligence"
   - 🧠 **Agentic Reasoning** — "17-stage autonomous analysis pipeline"

3. **Live Demo Preview** — Mostrar screenshots/preview del dashboard con datos reales de Margarita Pinta como "teaser" antes de entrar

### FASE 2: Demo de Un Click Impecable (Technical 40% + Demo 10%)

**Problema**: Los jueces NO están obligados a testear el proyecto. Pueden juzgar solo por video/texto/imágenes. Pero si lo prueban, debe ser impecable.

**Acciones**:

1. **Demo autocontenido** — El botón "Try Demo" debe:
   - Cargar instantáneamente (datos pre-calculados)
   - Mostrar dashboard COMPLETO con todos los análisis ya hechos
   - Incluir: BCG Matrix, Competitor Analysis, Sentiment, Campaigns, Creative Studio
   - Incluir datos de Margarita Pinta con fotos reales del restaurante

2. **Demo data completa** — Asegurar que `session.json` incluya:
   - `competitor_analysis` con datos de Google Search grounding
   - `sentiment_analysis` con reviews reales
   - `campaigns` con imágenes generadas
   - `sales_data` para predicciones
   - `restaurant_info` con rating, reviews, fotos

3. **Guided Tour opcional** — Tooltips que expliquen qué Gemini 3 feature se usó en cada sección

### FASE 3: Dashboard que Demuestre Gemini 3 (Technical 40% + Innovation 30%)

**Problema**: El dashboard muestra datos pero no demuestra visualmente QUÉ hizo Gemini 3 ni POR QUÉ es especial.

**Acciones**:

1. **Badges de "Powered by"** en cada sección:
   - BCG Matrix → "Analyzed by Gemini 3 Pro • Exhaustive Reasoning"
   - Competitors → "Grounded with Google Search • Auto-cited sources"
   - Sentiment → "Multi-source sentiment • Gemini 3 Vision for review images"
   - Campaigns → "Generated by Imagen 3 • Native text-in-image"
   - Overview → "17-stage Marathon Agent Pipeline"

2. **Thought Transparency Panel** — En cada sección, un toggle "See AI Reasoning":
   - Muestra el chain-of-thought de Gemini
   - Muestra las fuentes grounding usadas
   - Muestra los quality scores de Vibe Engineering

3. **Real-time Indicators** — Animaciones que muestren actividad AI:
   - WebSocket connection indicator (✅ ya implementado)
   - Thinking indicators cuando se ejecutan análisis
   - Progress bars para pipeline stages
   - Contadores de tokens/modelos usados

### FASE 4: Creative Studio Espectacular (Innovation 30%)

**Problema**: La generación de imágenes con Imagen 3 es el diferenciador más visual, pero está enterrada en un tab.

**Acciones**:

1. **Galería visual prominente** — Mostrar assets generados en grid grande
2. **A/B Variant comparador** — Side-by-side de variantes
3. **Localización visual** — Mostrar el mismo asset en ES/EN/FR lado a lado
4. **Download all como ZIP** — Para que jueces puedan descargar assets
5. **Estadísticas de impacto estimado** visualmente atractivas

### FASE 5: Presentación/Documentación (Demo 10%)

**Acciones**:

1. **README.md** completo con:
   - Arquitectura diagram clara
   - Quick Start (ya implementado ✅)
   - Gemini 3 features list con explicación técnica
   - Screenshots del dashboard con datos reales

2. **Texto de integración Gemini** (~200 palabras) preparado para Devpost:
   - Qué features de Gemini 3 se usan
   - Cómo son centrales a la aplicación
   - Qué no sería posible sin Gemini 3

---

## 3. PRIORIZACIÓN DE IMPLEMENTACIÓN

| # | Acción | Impacto | Esfuerzo | Criterio Principal |
|---|--------|---------|----------|-------------------|
| 1 | Reestructurar landing con Gemini 3 showcase | 🔴 Muy Alto | Medio | Innovation 30% + Demo 10% |
| 2 | Asegurar demo de un click funcional | 🔴 Muy Alto | Bajo | Technical 40% + Demo 10% |
| 3 | Badges "Powered by Gemini 3" en dashboard | 🟠 Alto | Bajo | Technical 40% |
| 4 | AI Reasoning toggle en secciones | 🟠 Alto | Medio | Innovation 30% |
| 5 | Creative Studio visual enhancement | 🟠 Alto | Medio | Innovation 30% |
| 6 | Demo data completa con Margarita Pinta | 🟠 Alto | Medio | Technical 40% |
| 7 | Interacciones pulidas (animaciones, loading) | 🟡 Medio | Bajo | Demo 10% |
| 8 | Documentación final | 🟡 Medio | Bajo | Demo 10% |

---

## 4. DEMO: MARGARITA PINTA

### Datos Disponibles
- **Restaurante**: Margarita Pinta, Cl 20 #40A-10, Pasto, Nariño, Colombia
- **Redes**: Instagram @margaritapintapasto, Facebook /MargaritaPintaRestauranteBar
- **Menú**: 139 productos (cocteles, licores, carnes, entradas, postres)
- **Ventas**: 57,283 registros, 9,696 tickets, 2023-2025
- **Fotos**: 44+ imágenes de platos, ambiente, cocteles
- **Video**: 1 video del establecimiento
- **Logo**: Logo.jpg

### Pipeline de Análisis Esperado
1. Gemini 3 Vision → Extracción de menú de PDFs
2. Gemini 3 Pro → BCG Matrix con ventas
3. Gemini 3 Pro + Google Search → Competitive Intelligence (Pasto, Nariño)
4. Gemini 3 Pro → Sentiment Analysis de reviews
5. Imagen 3 → Campaña visual para el plato estrella
6. Vibe Engineering → Verificación de calidad
7. Marathon Agent → Orquestación completa

---

## 5. MÉTRICAS DE ÉXITO

| Métrica | Objetivo |
|---------|----------|
| Tiempo de carga demo | < 2 segundos |
| Funcionalidades Gemini 3 visibles | 6+ (vision, audio, video, image gen, grounding, reasoning) |
| Secciones con badge "Powered by" | 100% |
| Build exitoso | 0 errores |
| Demo data completa | Todas las secciones con datos |
| Screenshots listos para Devpost | 5+ |
