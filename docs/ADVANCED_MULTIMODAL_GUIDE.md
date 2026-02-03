# Advanced Multimodal Agent - Guía Completa

## 🌟 Descripción

El `AdvancedMultimodalAgent` es la implementación TOP 1% que maximiza las capacidades únicas de Gemini 3, incluyendo funcionalidades que **ningún competidor puede igualar**:

- ✅ **Video Analysis** - ÚNICO en Gemini 3 (GPT-4V no puede)
- ✅ **Batch Processing** - Análisis eficiente de múltiples imágenes
- ✅ **Comparative Vision** - Análisis competitivo side-by-side
- ✅ **Native Audio** - Sin necesidad de Whisper/STT externo
- ✅ **PDF Understanding** - Procesamiento nativo de documentos
- ✅ **Structured Outputs** - Validación con Pydantic

---

## 🎯 Capacidades Únicas vs Competencia

| Capacidad | Gemini 3 (Nosotros) | GPT-4V | Claude 3 |
|-----------|---------------------|---------|----------|
| Video Analysis | ✅ Nativo | ❌ No | ❌ No |
| Batch Images | ✅ Eficiente | ⚠️ Múltiples calls | ⚠️ Múltiples calls |
| Audio Nativo | ✅ Sin STT | ❌ Necesita Whisper | ❌ Necesita STT |
| PDF Nativo | ✅ Directo | ⚠️ Requiere parsing | ⚠️ Requiere parsing |
| Grounding | ✅ Google Search | ❌ No | ❌ No |
| Image Generation | ✅ Imagen 3 | ✅ DALL-E | ❌ No |

---

## 🚀 Uso Básico

### Inicialización

```python
from app.services.gemini.advanced_multimodal import AdvancedMultimodalAgent

# Inicializar agente
agent = AdvancedMultimodalAgent()
```

---

## 📋 Extracción de Menús

### Desde Imagen

```python
# Leer imagen de menú
with open("menu.jpg", "rb") as f:
    menu_image = f.read()

# Extraer con estructura garantizada
menu_data = await agent.extract_menu_from_image(
    image=menu_image,
    language="es",  # español, "auto" para detectar
    additional_context="Restaurante mexicano en CDMX"
)

# Datos estructurados y validados
print(f"Restaurante: {menu_data.restaurant_name}")
print(f"Total items: {menu_data.total_items}")
print(f"Rango de precios: ${menu_data.price_range['min']} - ${menu_data.price_range['max']}")

# Iterar por secciones
for section in menu_data.menu_sections:
    print(f"\n{section['name']}:")
    for item in section['items']:
        print(f"  - {item['name']}: ${item['price']}")
```

### Desde PDF

```python
# Procesar menú en PDF
with open("menu.pdf", "rb") as f:
    pdf_bytes = f.read()

menu_data = await agent.extract_menu_from_pdf(pdf_bytes)
# Misma estructura que extract_menu_from_image
```

---

## 🍽️ Análisis de Platillos (Food Porn AI)

### Análisis Individual

```python
# Analizar foto de platillo
with open("dish.jpg", "rb") as f:
    dish_image = f.read()

analysis = await agent.analyse_dish_image(
    image=dish_image,
    dish_name="Tacos al Pastor",
    context="Restaurante casual, target Instagram"
)

# Scores detallados
print(f"Overall: {analysis.overall_score}/10")
print(f"Presentation: {analysis.presentation_score}/10")
print(f"Lighting: {analysis.lighting_score}/10")
print(f"Composition: {analysis.composition_score}/10")
print(f"Instagram-ability: {analysis.instagram_score}/10")

# Feedback profesional
print(f"\nFeedback: {analysis.detailed_feedback}")

# Mejoras específicas y accionables
print("\nMejoras rápidas:")
for improvement in analysis.quick_improvements:
    print(f"  - {improvement}")

print(f"\nImpacto estimado: {analysis.estimated_engagement_boost}")
```

### Batch Processing (Múltiples Platillos)

```python
# Analizar todo el menú de una vez
dish_images = []
dish_names = []

for dish_file in ["taco.jpg", "burrito.jpg", "quesadilla.jpg"]:
    with open(dish_file, "rb") as f:
        dish_images.append(f.read())
        dish_names.append(dish_file.replace(".jpg", ""))

# Un solo API call para todos
analyses = await agent.analyse_dish_batch(
    images=dish_images,
    dish_names=dish_names
)

# Resultados para cada platillo
for analysis in analyses:
    print(f"{analysis.dish_name}: {analysis.overall_score}/10")
    print(f"  Mejora principal: {analysis.quick_improvements[0]}")
```

---

## 🔥 Análisis Competitivo

### Comparación Visual vs Competencia

```python
# Tu platillo
with open("our_taco.jpg", "rb") as f:
    our_dish = f.read()

# Platillos de competidores
competitor_images = []
for comp in ["comp1_taco.jpg", "comp2_taco.jpg", "comp3_taco.jpg"]:
    with open(comp, "rb") as f:
        competitor_images.append(f.read())

# Análisis competitivo completo
comparison = await agent.comparative_dish_analysis(
    your_dish=our_dish,
    competitor_dishes=competitor_images,
    dish_name="Tacos al Pastor"
)

# Ver posición competitiva
print(f"Tu ranking: {comparison['your_rank']} de {len(competitor_images) + 1}")
print(f"Tu score: {comparison['your_score']}/10")
print(f"Promedio competencia: {comparison['competitor_avg_score']}/10")
print(f"Gap a cerrar: {comparison['gap_to_best']} puntos")

# Fortalezas
print("\nTus fortalezas:")
for strength in comparison['strengths']:
    print(f"  ✅ {strength}")

# Debilidades
print("\nTus debilidades:")
for weakness in comparison['weaknesses']:
    print(f"  ❌ {weakness}")

# Ideas para robar
print("\nIdeas para implementar:")
for idea in comparison['steal_these_ideas']:
    print(f"  💡 De competidor #{idea['from_competitor']}: {idea['element']}")
    print(f"     Cómo: {idea['how_to_implement']}")
    print(f"     Dificultad: {idea['difficulty']}, Impacto: {idea['impact']}")
```

### Expectativa vs Realidad

```python
# Fotos oficiales del restaurante
official_photos = []
for photo in ["official1.jpg", "official2.jpg"]:
    with open(photo, "rb") as f:
        official_photos.append(f.read())

# Fotos de clientes (de redes sociales)
customer_photos = []
for photo in ["customer1.jpg", "customer2.jpg", "customer3.jpg"]:
    with open(photo, "rb") as f:
        customer_photos.append(f.read())

# Análisis de consistencia
consistency = await agent.analyse_customer_photos(
    customer_photos=customer_photos,
    official_photos=official_photos,
    dish_name="Tacos al Pastor"
)

print(f"Consistency score: {consistency['consistency_score']}/10")
print(f"Sentiment: {consistency['customer_sentiment']}")
print(f"Gap: {consistency['overall_gap']}")

print("\nDiscrepancias detectadas:")
for disc in consistency['discrepancies']:
    print(f"  - {disc['aspect']} ({disc['severity']}): {disc['description']}")

print("\nRecomendaciones:")
for rec in consistency['recommendations']:
    print(f"  - [{rec['priority']}] {rec['area']}: {rec['action']}")
```

---

## 🎥 Video Analysis (ÚNICO EN GEMINI 3)

```python
# Analizar video de restaurante
with open("restaurant_tour.mp4", "rb") as f:
    video_bytes = f.read()

video_analysis = await agent.analyse_video_content(
    video_bytes=video_bytes,
    video_purpose="social_media"
)

print(f"Tipo de contenido: {video_analysis.content_type}")
print(f"Calidad visual: {video_analysis.visual_quality_score}/10")
print(f"Calidad audio: {video_analysis.audio_quality_score}/10")

# Momentos clave
print("\nMomentos clave:")
for moment in video_analysis.key_moments:
    print(f"  [{moment['timestamp']}] {moment['description']} ({moment['type']})")

# Mejor momento para thumbnail
print(f"\nMejor thumbnail: {video_analysis.best_thumbnail_timestamp}")

# Suitability por plataforma
print("\nSuitability por plataforma:")
for platform, score in video_analysis.social_media_suitability.items():
    print(f"  {platform}: {score}/10")

# Recomendaciones de edición
print("\nRecomendaciones de corte:")
for cut in video_analysis.recommended_cuts:
    print(f"  - {cut}")
```

---

## 🎤 Audio Analysis (Nativo)

```python
# Procesar audio del dueño contando su historia
with open("owner_story.mp3", "rb") as f:
    audio_bytes = f.read()

insights = await agent.transcribe_and_analyze_audio(
    audio_bytes=audio_bytes,
    audio_format="mp3",
    context="business_story"
)

# Transcripción completa
print("Transcripción:")
print(insights.transcription)

# Insights extraídos
print(f"\nTono emocional: {insights.emotional_tone}")

print("\nTemas clave:")
for theme in insights.key_themes:
    print(f"  - {theme}")

print("\nValores detectados:")
for value in insights.values_detected:
    print(f"  - {value}")

print("\nUSPs identificados:")
for usp in insights.unique_selling_points:
    print(f"  - {usp}")

# Ángulos de campaña sugeridos
print("\nÁngulos de campaña:")
for angle in insights.campaign_angles:
    print(f"\n  📢 {angle['angle']}")
    print(f"     Rationale: {angle['rationale']}")
    print(f"     Hook emocional: {angle['emotional_hook']}")
    print(f"     Mensaje: {angle['suggested_message']}")
```

---

## 🎯 Casos de Uso Completos

### Caso 1: Auditoría Completa de Menú Visual

```python
async def audit_menu_photos(menu_folder: str):
    """Auditar todas las fotos del menú."""
    
    agent = AdvancedMultimodalAgent()
    
    # Recopilar todas las imágenes
    images = []
    names = []
    
    for img_file in Path(menu_folder).glob("*.jpg"):
        with open(img_file, "rb") as f:
            images.append(f.read())
            names.append(img_file.stem)
    
    # Análisis batch
    analyses = await agent.analyse_dish_batch(images, names)
    
    # Generar reporte
    report = {
        "total_dishes": len(analyses),
        "avg_score": sum(a.overall_score for a in analyses) / len(analyses),
        "top_performers": [],
        "needs_improvement": [],
        "quick_wins": []
    }
    
    for analysis in analyses:
        if analysis.overall_score >= 8.0:
            report["top_performers"].append(analysis.dish_name)
        elif analysis.overall_score < 6.0:
            report["needs_improvement"].append({
                "dish": analysis.dish_name,
                "score": analysis.overall_score,
                "fix": analysis.quick_improvements[0]
            })
    
    return report
```

### Caso 2: Benchmark Competitivo Completo

```python
async def competitive_benchmark(dish_name: str, our_photo: str, competitor_folder: str):
    """Benchmark completo vs competencia."""
    
    agent = AdvancedMultimodalAgent()
    
    # Cargar nuestra foto
    with open(our_photo, "rb") as f:
        our_dish = f.read()
    
    # Cargar fotos de competidores
    competitor_images = []
    for comp_file in Path(competitor_folder).glob("*.jpg"):
        with open(comp_file, "rb") as f:
            competitor_images.append(f.read())
    
    # Análisis comparativo
    comparison = await agent.comparative_dish_analysis(
        your_dish=our_dish,
        competitor_dishes=competitor_images,
        dish_name=dish_name
    )
    
    # Generar plan de acción
    action_plan = []
    
    # Priorizar cambios por impacto/dificultad
    for change in comparison['recommended_changes']:
        if change['impact'] == 'high' and change['difficulty'] in ['easy', 'medium']:
            action_plan.append({
                "priority": "HIGH",
                "action": change['change'],
                "difficulty": change['difficulty']
            })
    
    return {
        "current_position": comparison['your_rank'],
        "gap_to_close": comparison['gap_to_best'],
        "action_plan": action_plan,
        "ideas_to_steal": comparison['steal_these_ideas'][:3]  # Top 3
    }
```

### Caso 3: Optimización de Contenido Social

```python
async def optimize_social_content(video_path: str, dish_photos: List[str]):
    """Optimizar contenido para redes sociales."""
    
    agent = AdvancedMultimodalAgent()
    
    # Analizar video
    with open(video_path, "rb") as f:
        video_bytes = f.read()
    
    video_analysis = await agent.analyse_video_content(
        video_bytes=video_bytes,
        video_purpose="social_media"
    )
    
    # Analizar fotos
    images = []
    names = []
    for photo in dish_photos:
        with open(photo, "rb") as f:
            images.append(f.read())
            names.append(Path(photo).stem)
    
    photo_analyses = await agent.analyse_dish_batch(images, names)
    
    # Generar recomendaciones
    recommendations = {
        "video": {
            "best_platform": max(
                video_analysis.social_media_suitability.items(),
                key=lambda x: x[1]
            )[0],
            "thumbnail_time": video_analysis.best_thumbnail_timestamp,
            "key_moments": [m for m in video_analysis.key_moments if m['type'] == 'engaging']
        },
        "photos": {
            "instagram_ready": [
                a.dish_name for a in photo_analyses 
                if a.instagram_score >= 8.0
            ],
            "needs_work": [
                {
                    "dish": a.dish_name,
                    "fix": a.quick_improvements[0]
                }
                for a in photo_analyses if a.instagram_score < 7.0
            ]
        }
    }
    
    return recommendations
```

---

## 📊 Schemas de Respuesta

### MenuExtractionSchema

```python
{
    "restaurant_name": "La Taquería",
    "menu_sections": [
        {
            "name": "Tacos",
            "items": [
                {
                    "name": "Tacos al Pastor",
                    "description": "Con piña y cilantro",
                    "price": 45.0,
                    "currency": "MXN",
                    "dietary_labels": [],
                    "spice_level": 2,
                    "allergens": [],
                    "special_markers": ["popular"]
                }
            ]
        }
    ],
    "total_items": 15,
    "price_range": {
        "min": 35.0,
        "max": 150.0,
        "average": 75.0,
        "currency": "MXN"
    },
    "cuisines": ["Mexican"],
    "special_dietary": ["vegetarian"],
    "confidence_score": 0.95
}
```

### DishAnalysisSchema

```python
{
    "overall_score": 7.5,
    "presentation_score": 8.0,
    "lighting_score": 6.5,
    "composition_score": 7.0,
    "instagram_score": 7.5,
    "detailed_feedback": "Good plating but lighting needs improvement...",
    "quick_improvements": [
        "Shoot near window between 10am-2pm for soft natural light",
        "Add microgreens to top-right for color contrast",
        "Shoot from 45° angle, 6 inches higher"
    ],
    "estimated_engagement_boost": "+30-40% if all improvements applied"
}
```

---

## 🎓 Best Practices

### 1. Usar Batch Processing Cuando Sea Posible

```python
# ❌ Ineficiente - múltiples API calls
for image in images:
    analysis = await agent.analyse_dish_image(image, name)

# ✅ Eficiente - un solo API call
analyses = await agent.analyse_dish_batch(images, names)
```

### 2. Aprovechar Video Analysis

```python
# ✅ Analizar videos de redes sociales
# ✅ Optimizar contenido antes de publicar
# ✅ Identificar mejores momentos para clips
```

### 3. Usar Audio Nativo

```python
# ❌ No usar Whisper externo
# ✅ Dejar que Gemini procese audio directamente
insights = await agent.transcribe_and_analyze_audio(audio_bytes)
```

### 4. Validar Outputs Estructurados

```python
# ✅ Todos los schemas usan Pydantic
# ✅ Validación automática
# ✅ Type safety garantizada
```

---

## 🚀 Ventajas Competitivas

### vs GPT-4V

| Feature | Nosotros (Gemini 3) | GPT-4V |
|---------|---------------------|--------|
| Video | ✅ Nativo | ❌ No soporta |
| Batch | ✅ 1 call | ❌ N calls |
| Audio | ✅ Nativo | ❌ Necesita Whisper |
| Grounding | ✅ Google Search | ❌ No |
| Costo | ✅ Más barato | ❌ Más caro |

### vs Claude 3

| Feature | Nosotros (Gemini 3) | Claude 3 |
|---------|---------------------|----------|
| Video | ✅ Nativo | ❌ No soporta |
| PDF | ✅ Nativo | ⚠️ Limitado |
| Grounding | ✅ Google Search | ❌ No |
| Batch | ✅ Eficiente | ⚠️ Limitado |

---

## 📝 Integración con Workflow

### En AnalysisOrchestrator

```python
from app.services.gemini.advanced_multimodal import AdvancedMultimodalAgent

class AnalysisOrchestrator:
    def __init__(self):
        self.multimodal = AdvancedMultimodalAgent()
    
    async def process_menu_images(self, images):
        # Usar batch processing
        return await self.multimodal.analyse_dish_batch(images, names)
    
    async def analyze_competitor_videos(self, videos):
        # Analizar videos de competencia
        analyses = []
        for video in videos:
            analysis = await self.multimodal.analyse_video_content(video)
            analyses.append(analysis)
        return analyses
```

---

**Última actualización:** 2026-02-03  
**Versión:** 1.0.0  
**Autor:** MenuPilot Team
