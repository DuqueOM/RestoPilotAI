# Multimodal Agent - Guía de Gemini 3 Vision

## 🎯 Capacidades Nativas de Gemini 3 Vision

El **Multimodal Agent** explota las capacidades nativas de visión de Gemini 3, eliminando la necesidad de OCR externo o procesamiento de imágenes adicional.

**DIFERENCIADOR HACKATHON:** Gemini 3 Vision procesa imágenes directamente con comprensión contextual profunda.

---

## 🚀 Mejoras Implementadas

### ✅ Uso de Gemini 3 Vision Nativo

**ANTES (❌ Incorrecto):**
```python
import pytesseract  # OCR externo - NO necesario
from PIL import Image

def extract_menu_from_image(self, image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)  # OCR básico
    return text
```

**AHORA (✅ Correcto):**
```python
# Sin OCR externo - Gemini 3 Vision procesa directamente
async def extract_menu_from_image(
    self,
    image_source: Union[str, bytes],
    additional_context: Optional[str] = None
) -> Dict[str, Any]:
    """Extrae menú usando Gemini 3 Vision NATIVO."""
    
    image_bytes = base64.b64decode(image_base64)
    
    response = await self.generate(
        prompt=prompt,
        images=[image_bytes],
        thinking_level="STANDARD",
        mime_type=mime_type,
        temperature=0.3,
        max_output_tokens=8192
    )
    
    return self._parse_json_response(response)
```

---

## 📊 Funcionalidades Principales

### 1. Extracción de Menú

**Método:** `extract_menu_from_image()`

**Capacidades:**
- Extrae TODOS los items visibles del menú
- Mantiene estructura original (categorías, secciones)
- Detecta precios en múltiples formatos ($, MXN, USD)
- Identifica tags especiales (🌱 vegetariano, 🌶️ picante, ⭐ popular)
- Extrae descripciones cuando están disponibles
- Maneja múltiples idiomas automáticamente

**Ejemplo de uso:**
```python
from app.services.gemini.multimodal import MultimodalAgent

agent = MultimodalAgent()

result = await agent.extract_menu_from_image(
    image_source=menu_image_bytes,
    additional_context="Restaurante mexicano en CDMX",
    language_hint="es"
)

# Resultado estructurado
{
    "items": [
        {
            "name": "Tacos al Pastor",
            "price": 85.00,
            "currency": "MXN",
            "description": "3 tacos con piña y cilantro",
            "category": "Tacos",
            "tags": ["popular", "spicy"],
            "sizes": [
                {"size": "regular", "price": 85.00},
                {"size": "orden grande", "price": 120.00}
            ]
        }
    ],
    "categories": [...],
    "metadata": {
        "language": "es",
        "currency_detected": "MXN",
        "estimated_items_visible": 25
    },
    "extraction_quality": {
        "confidence": 0.92,
        "items_clear": 22,
        "items_partial": 3
    }
}
```

---

### 2. Análisis Profesional de Platos

**Método:** `analyze_dish_professional()`

**CRÍTICO PARA HACKATHON:** "Food Porn AI" - Análisis de crítico gastronómico de clase mundial.

**Criterios de Evaluación (0-10):**

1. **Composición Visual**
   - Regla de tercios
   - Balance de elementos
   - Punto focal
   - Espacio negativo
   - Ángulo de fotografía

2. **Iluminación Profesional**
   - Dirección y calidad de luz
   - Sombras que añaden profundidad
   - Destacado de texturas
   - Color temperature

3. **Emplatado Profesional**
   - Precisión y limpieza
   - Altura y volumen
   - Uso del color
   - Garnish apropiado
   - Técnicas modernas

4. **Apetitosidad ("Food Porn Factor")**
   - Texturas visibles
   - Colores vibrantes
   - Frescura aparente
   - Factor "craveable"
   - Steam/moisture visible

5. **Instagramabilidad**
   - Aesthetic trending
   - Shareability
   - Visual storytelling
   - Elementos únicos
   - Wow factor

**Ejemplo de uso:**
```python
result = await agent.analyze_dish_professional(
    image_source=dish_photo_bytes,
    dish_name="Tacos al Pastor",
    dish_category="main_course"
)

# Resultado profesional
{
    "overall_score": 8.5,
    "scores": {
        "composition": 8.0,
        "lighting": 9.0,
        "plating": 8.5,
        "appetizing": 9.0,
        "instagramability": 8.0
    },
    "strengths": [
        "Iluminación natural perfecta que resalta texturas",
        "Colores vibrantes contrastan con fondo neutro"
    ],
    "weaknesses": [
        "Composición ligeramente descentrada"
    ],
    "specific_improvements": [
        {
            "issue": "Falta profundidad en el plato",
            "suggestion": "Agregar altura con técnica de stacking",
            "priority": "high",
            "expected_impact": "Aumentará percepción de valor en 20%"
        }
    ],
    "professional_assessment": "Plato bien ejecutado con potencial comercial alto...",
    "comparable_to": "Nivel de Pujol o Quintonil en presentación",
    "market_positioning": {
        "current_level": "upscale_casual",
        "potential_level": "fine_dining",
        "price_point_suggested": "$$$ (150-250 MXN)",
        "target_audience": "Millennials, foodies, Instagram influencers"
    },
    "technical_details": {
        "estimated_camera_angle": "45 degrees",
        "lighting_type": "natural_window",
        "color_palette": ["vibrant_green", "warm_brown", "white"],
        "plating_style": "modern_rustic"
    },
    "actionable_recommendations": [
        "Usar este estilo de iluminación consistentemente",
        "Invertir en platos de color neutro para mejor contraste"
    ],
    "instagram_optimization": {
        "hashtag_suggestions": ["#FoodPorn", "#MexicanCuisine"],
        "best_posting_time": "12:00-14:00, 19:00-21:00",
        "caption_angle": "Highlight freshness and traditional techniques"
    }
}
```

---

### 3. Análisis de Platos (Estándar)

**Método:** `analyze_dish_image()`

Análisis más rápido para casos de uso generales:

```python
result = await agent.analyze_dish_image(
    image_source=dish_photo_bytes,
    dish_name="Guacamole",
    menu_context=["Guacamole", "Tacos", "Quesadillas"]
)

# Resultado
{
    "dish_identification": {
        "name": "Guacamole",
        "confidence": 0.95,
        "matched_menu_item": "Guacamole",
        "cuisine_type": "Mexican"
    },
    "visual_scores": {
        "overall_attractiveness": 8.5,
        "color_appeal": 9.0,
        "composition": 7.5,
        "lighting_quality": 8.0
    },
    "presentation_analysis": {
        "plating_style": "Modern rustic",
        "plating_quality": 8.0,
        "portion_perception": "generous"
    },
    "marketability": {
        "instagram_worthiness": 8.5,
        "menu_photo_suitability": 9.0,
        "appetite_appeal": 8.5
    },
    "improvement_suggestions": [...]
}
```

---

### 4. Análisis de Competidores

**Método:** `extract_competitor_menu()`

Extrae información de menús de competidores para inteligencia competitiva:

```python
result = await agent.extract_competitor_menu(
    image_source=competitor_menu_bytes,
    competitor_name="Restaurante Competidor"
)

# Resultado
{
    "competitor_info": {
        "name": "Restaurante Competidor",
        "cuisine_type": "Mexican",
        "price_positioning": "mid-range",
        "brand_style": "Modern casual"
    },
    "items": [...],
    "pricing_analysis": {
        "price_range": {"min": 45, "max": 250},
        "average_price": 95,
        "price_tier": "mid-range"
    },
    "menu_analysis": {
        "total_items": 35,
        "categories": ["Appetizers", "Tacos", "Mains"],
        "unique_offerings": ["Specialty item 1"],
        "visual_quality": 7.5
    },
    "competitive_observations": [
        "Strong focus on traditional dishes",
        "Limited vegetarian options"
    ]
}
```

---

### 5. Análisis de Fotos de Clientes

**Método:** `analyze_customer_photos()`

Analiza fotos publicadas por clientes para insights de calidad:

```python
result = await agent.analyze_customer_photos(
    photos=[photo1_bytes, photo2_bytes, photo3_bytes],
    menu_items=["Tacos al Pastor", "Guacamole", "Quesadillas"]
)

# Resultado
{
    "photo_analyses": [
        {
            "photo_index": 0,
            "dish_identified": "Tacos al Pastor",
            "presentation_score": 7.5,
            "portion_perception": "adequate",
            "issues_noted": [],
            "positive_aspects": ["Good color", "Fresh looking"]
        }
    ],
    "aggregate_insights": {
        "dishes_most_photographed": ["Tacos al Pastor"],
        "average_presentation_score": 7.8,
        "common_issues": ["Inconsistent plating"],
        "overall_visual_sentiment": "positive"
    },
    "per_dish_summary": {
        "Tacos al Pastor": {
            "photo_count": 5,
            "avg_presentation": 8.0,
            "sentiment": "positive"
        }
    },
    "recommendations": [...]
}
```

---

## 🔧 Configuración

### Modelo por Defecto

El MultimodalAgent usa automáticamente `gemini-3-pro-preview` (modelo de visión):

```python
# backend/app/services/gemini/multimodal.py

def __init__(self, model: GeminiModel = GeminiModel.VISION, **kwargs):
    super().__init__(model_name=model, **kwargs)
    # Usa vision model de settings
    self.model_name = self.settings.gemini_model_vision
```

### Settings

```python
# backend/app/core/config.py

gemini_model_vision: str = "gemini-3-pro-preview"  # Multimodal
```

---

## 🎨 Integración en el Workflow

### BCG Analysis con Imágenes

```python
# Extraer menú de imagen
multimodal_agent = MultimodalAgent()
menu_data = await multimodal_agent.extract_menu_from_image(
    image_source=menu_image_bytes
)

# Analizar con BCG
from app.services.analysis.bcg import BCGAnalyzer
bcg = BCGAnalyzer()
classification = await bcg.classify(
    items=menu_data["items"],
    sales_data=sales_data
)
```

### Competitive Analysis con Visión

```python
# Extraer menú de competidor
competitor_data = await multimodal_agent.extract_competitor_menu(
    image_source=competitor_menu_bytes,
    competitor_name="Competidor XYZ"
)

# Comparar precios
our_avg_price = calculate_avg_price(our_menu)
their_avg_price = competitor_data["pricing_analysis"]["average_price"]

price_gap = (their_avg_price - our_avg_price) / our_avg_price * 100
```

### Campaign Generation con Análisis Visual

```python
# Analizar platos profesionalmente
dish_analyses = []
for dish_photo in dish_photos:
    analysis = await multimodal_agent.analyze_dish_professional(
        image_source=dish_photo,
        dish_name=dish["name"],
        dish_category=dish["category"]
    )
    dish_analyses.append(analysis)

# Seleccionar mejores platos para campaña
best_dishes = sorted(
    dish_analyses,
    key=lambda x: x["overall_score"],
    reverse=True
)[:5]

# Generar campaña con mejores platos
campaign = await campaign_agent.generate_instagram_campaign(
    featured_dishes=best_dishes,
    optimization_tips=[d["instagram_optimization"] for d in best_dishes]
)
```

---

## 📈 Ventajas sobre OCR Tradicional

### Gemini 3 Vision vs OCR Externo

| Aspecto | OCR Tradicional | Gemini 3 Vision |
|---------|----------------|-----------------|
| **Comprensión** | Solo texto | Contexto + texto + visual |
| **Estructura** | Pierde formato | Mantiene estructura |
| **Idiomas** | Requiere config | Automático |
| **Precios** | Parsing manual | Detecta automáticamente |
| **Categorías** | No detecta | Identifica lógicamente |
| **Calidad** | Depende de imagen | Robusto a calidad |
| **Setup** | Tesseract + deps | Solo Gemini API |
| **Mantenimiento** | Alto | Bajo |

---

## 🔍 Casos de Uso Avanzados

### 1. Menu Redesign Recommendations

```python
# Analizar menú actual
current_menu = await agent.extract_menu_from_image(current_menu_image)

# Analizar fotos de todos los platos
dish_analyses = []
for item in current_menu["items"]:
    if item["photo_available"]:
        analysis = await agent.analyze_dish_professional(
            image_source=item["photo"],
            dish_name=item["name"],
            dish_category=item["category"]
        )
        dish_analyses.append(analysis)

# Generar recomendaciones de rediseño
recommendations = {
    "items_to_highlight": [
        d for d in dish_analyses 
        if d["overall_score"] >= 8.5
    ],
    "items_needing_improvement": [
        d for d in dish_analyses 
        if d["overall_score"] < 6.0
    ],
    "photography_improvements": [
        d["actionable_recommendations"] 
        for d in dish_analyses
    ]
}
```

### 2. Quality Control Automation

```python
# Monitorear fotos de clientes en redes sociales
customer_photos = fetch_instagram_photos(restaurant_hashtag)

analysis = await agent.analyze_customer_photos(
    photos=customer_photos,
    menu_items=menu_item_names
)

# Alertar si hay problemas consistentes
if analysis["aggregate_insights"]["common_issues"]:
    send_alert_to_kitchen(
        issues=analysis["aggregate_insights"]["common_issues"]
    )
```

### 3. Competitive Pricing Intelligence

```python
# Analizar menús de 5 competidores
competitor_analyses = []
for competitor in competitors:
    menu_data = await agent.extract_competitor_menu(
        image_source=competitor["menu_image"],
        competitor_name=competitor["name"]
    )
    competitor_analyses.append(menu_data)

# Calcular posicionamiento de precios
market_analysis = calculate_market_position(
    our_prices=our_menu_prices,
    competitor_prices=[c["pricing_analysis"] for c in competitor_analyses]
)
```

---

## ✅ Checklist de Implementación

- [x] Usa `gemini-3-pro-preview` para visión
- [x] No requiere OCR externo (pytesseract, etc.)
- [x] Procesa imágenes directamente con Gemini API
- [x] Extracción estructurada de menús
- [x] Análisis profesional de platos con criterios gastronómicos
- [x] Análisis de competidores
- [x] Análisis de fotos de clientes
- [x] Integración con base_agent methods
- [x] Soporte para múltiples formatos de imagen
- [x] Manejo de errores robusto
- [ ] Tests unitarios
- [ ] Integración en API endpoints
- [ ] Documentación de API

---

## 🚀 Próximos Pasos

1. **API Endpoints:** Exponer funcionalidades vía REST API
2. **Batch Processing:** Optimizar para múltiples imágenes
3. **Caching:** Cachear resultados de análisis
4. **Frontend Integration:** Componentes para mostrar análisis
5. **Audio Support:** Agregar soporte para audio nativo (mp3, wav)

---

**Fecha:** 2026-02-02  
**Versión:** 2.0  
**Status:** ✅ Implementado con Gemini 3 Vision Nativo
