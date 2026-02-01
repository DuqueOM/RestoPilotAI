# MenuPilot - Hackathon Demo Script & Architecture

## 🎥 DEMO VIDEO (3 minutes exactos)

**Estructura recomendada:**

### SEGUNDO 0-15: HOOK EMOCIONAL
- **Escena**: Dueño de restaurante frustrado viendo su menú
- **Narración**: "María lleva 5 años con su restaurante. Trabaja 12 horas diarias pero no entiende por qué algunos platos no se venden..."

### SEGUNDO 15-45: EL PROBLEMA
- **Estadística impactante**: "El 70% de los restaurantes pequeños cierran en los primeros 3 años"
- **Visual**: Gráfica de quiebras de restaurantes
- **Narración**: "El problema: decisiones basadas en intuición, no en datos"

### SEGUNDO 45-120: LA SOLUCIÓN (DEMO REAL)
*[DEMOSTRACIÓN EN VIVO - PASO A PASO]*

1.  **Upload de menú (5 seg)**:
    -   Arrastra imagen de menú físico
    -   Gemini Vision + OCR lo extrae automáticamente

2.  **Análisis BCG con Thought Signatures (15 seg)**:
    -   Muestra el "pensamiento" del modelo en streaming
    -   Clasifica cada plato en tiempo real
    -   Muestra Thought Trace: "Este plato es Question Mark porque..."

3.  **Creative Autopilot (20 seg)**:
    -   Click en "Generar campaña para plato estrella"
    -   Nano Banana Pro genera 4 assets en 10 segundos:
        *   Post Instagram con texto en español
        *   Story vertical
        *   Banner web
        *   Flyer imprimible
    -   Show de localización: "Traducir a inglés" → texto dentro de imagen se traduce manteniendo diseño

4.  **Vibe Engineering en acción (15 seg)**:
    -   Muestra auto-verificación
    -   "Calidad inicial: 72% → Mejorando automáticamente..."
    -   "Calidad final: 89% ✓"

5.  **Competitive Intelligence con Grounding (15 seg)**:
    -   "Comparar con competidores cercanos"
    -   Gemini busca en Google en tiempo real
    -   Muestra insights: "Tus competidores cobran 15% más por platos similares"

### SEGUNDO 120-150: IMPACTO
-   **Narración**: "María implementó las recomendaciones"
-   **Visual**: Gráfica de ventas subiendo
-   **Testimonial simulado**: "En 2 meses aumenté mis ventas 40%"

### SEGUNDO 150-180: DIFERENCIADORES TÉCNICOS
*[VELOCIDAD RÁPIDA - ESTILO TECH DEMO]*
-   "¿Por qué Gemini 3?"
    ✓ Única IA que genera imágenes 4K con texto legible
    ✓ Grounding con Google Search para datos actualizados
    ✓ Auto-verificación autónoma (Vibe Engineering)
    ✓ Thought Signatures para transparencia total
-   "Construido 100% con Gemini 3 API"
-   Logo de Google DeepMind
-   **CTA**: "Prueba MenuPilot hoy"

---

## 🏗️ Architecture Diagram

```mermaid
graph TD
    Client[Frontend Next.js] --> API[FastAPI Backend]
    
    subgraph "Gemini 3 Multi-Agent System"
        API --> Orchestrator[Analysis Orchestrator]
        
        Orchestrator --> Vision[Multimodal Agent (Vision)]
        Vision --> |Menu & Dish Analysis| Gemini[Gemini 3 Flash]
        
        Orchestrator --> Creative[Creative Autopilot]
        Creative --> |Image Gen + Text| NanoBanana[Gemini 3 Pro Image]
        
        Orchestrator --> Vibe[Vibe Engineering Agent]
        Vibe --> |Auto-Verification Loop| Gemini
        
        Orchestrator --> Reasoning[Reasoning Agent]
        Reasoning --> |Strategy & Grounding| GoogleSearch[Google Search Tool]
        
        Orchestrator --> Marathon[Marathon Agent]
        Marathon --> |Long-running Tasks| DB[(PostgreSQL)]
    end
    
    Orchestrator --> DB
```

## 🚀 New "WOW" Features

### 1. Menu Transformation Studio
Transforma el diseño visual de un menú manteniendo el contenido exacto.
- **Endpoint**: `POST /api/v1/creative/menu-transform`
- **Model**: Gemini 3 Pro Image Preview
- **Features**: Preserva texto y precios, cambia estilo (Minimalista, Vintage, Luxury).

### 2. Instagram Performance Predictor
Predice el engagement de fotos de comida antes de publicar.
- **Endpoint**: `POST /api/v1/creative/instagram-prediction`
- **Model**: Gemini 3 Flash Preview + Vision + Grounding
- **Features**: Analiza composición, iluminación, tendencias actuales en Instagram vía Google Search.
