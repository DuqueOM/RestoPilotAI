# 🎯 Sistema Avanzado de Inteligencia Competitiva

## Resumen Ejecutivo

MenuPilot ahora cuenta con un **sistema completo de inteligencia competitiva** que aprovecha:

- ✅ **Google Maps API** (Place Details) para metadatos exhaustivos
- ✅ **Cross-referencing inteligente** con búsqueda web
- ✅ **Identificación automática** de redes sociales
- ✅ **Análisis multimodal** con Gemini Vision
- ✅ **Consolidación de perfiles** desde múltiples fuentes
- ✅ **Extracción de menús** de websites, fotos y WhatsApp Business

---

## 🚀 Capacidades Implementadas

### 1. **Identificación Precisa del Negocio Propio**

**Endpoint**: `POST /api/v1/location/identify-business`

Permite al usuario **buscar y seleccionar su propio negocio** en Google Maps con precisión.

**Parámetros**:
```json
{
  "query": "La Parrilla de Pepe, Bogotá",
  "lat": 4.6097,  // Opcional: bias hacia ubicación
  "lng": -74.0817
}
```

**Respuesta**:
```json
{
  "status": "success",
  "candidates": [
    {
      "name": "La Parrilla de Pepe",
      "address": "Calle 123 #45-67, Bogotá",
      "placeId": "ChIJ...",
      "lat": 4.6097,
      "lng": -74.0817,
      "rating": 4.5,
      "userRatingsTotal": 235,
      "types": ["restaurant", "food"],
      "photos": ["photo_ref_1", "photo_ref_2"]
    }
  ],
  "total_found": 3
}
```

**Flujo**:
1. Usuario busca su restaurante por nombre
2. Sistema devuelve **candidatos con fotos**
3. Usuario **selecciona el correcto** del mapa
4. Sistema establece ubicación precisa

---

### 2. **Establecer Negocio Propio con Enriquecimiento**

**Endpoint**: `POST /api/v1/location/set-business`

Establece el negocio seleccionado y **enriquece su perfil** para auto-análisis.

**Parámetros**:
```json
{
  "session_id": "abc123",
  "place_id": "ChIJ...",
  "enrich_profile": true
}
```

**Datos Extraídos**:
- ✅ Información de contacto completa
- ✅ Calificaciones y reseñas
- ✅ Horarios de atención
- ✅ Fotos del negocio
- ✅ Redes sociales propias
- ✅ Menú desde website/fotos

---

### 3. **Búsqueda de Competidores Cercanos**

**Endpoint**: `POST /api/v1/location/nearby-restaurants`

Busca competidores en radio de 1.5km y **opcionalmente enriquece perfiles**.

**Parámetros**:
```json
{
  "lat": 4.6097,
  "lng": -74.0817,
  "radius": 1500,
  "address": "Calle 123, Bogotá",
  "enrich": true  // 🆕 Enriquecimiento automático
}
```

**Con `enrich=false` (básico)**:
```json
{
  "restaurants": [
    {
      "name": "Competidor A",
      "address": "Calle 100",
      "rating": 4.2,
      "placeId": "ChIJ..."
    }
  ],
  "source": "google_places",
  "enriched": false
}
```

**Con `enrich=true` (completo)**:
```json
{
  "restaurants": [
    {
      "competitor_id": "uuid",
      "name": "Competidor A",
      "location": {...},
      "contact": {
        "phone": "+57 300 1234567",
        "website": "https://...",
        "whatsapp_business": "+573001234567"
      },
      "google_maps": {
        "rating": 4.2,
        "user_ratings_total": 450,
        "price_level": 2,
        "opening_hours": {...},
        "reviews_summary": "Análisis de reseñas...",
        "photos_count": 45
      },
      "social_media": [
        {
          "platform": "facebook",
          "url": "https://facebook.com/...",
          "followers": 5200
        },
        {
          "platform": "instagram",
          "url": "https://instagram.com/...",
          "handle": "@competidora"
        },
        {
          "platform": "whatsapp_business",
          "url": "https://wa.me/573001234567"
        }
      ],
      "menu": {
        "items": [...],
        "sources": ["website", "google_photos"],
        "item_count": 45
      },
      "competitive_intelligence": {
        "cuisine_types": ["Colombiana", "Parrilla"],
        "specialties": ["Arepas", "Bandeja Paisa"],
        "unique_offerings": ["Menú vegano completo"],
        "target_audience": "Familias de clase media",
        "brand_positioning": "Tradicional premium"
      },
      "metadata": {
        "data_sources": [
          "google_maps_place_details",
          "web_search",
          "facebook",
          "instagram",
          "whatsapp_business",
          "google_photos_vision_analysis"
        ],
        "confidence_score": 0.92
      }
    }
  ],
  "source": "google_places_enriched",
  "enriched": true
}
```

---

### 4. **Enriquecimiento Individual de Competidor**

**Endpoint**: `POST /api/v1/location/enrich-competitor`

Enriquece el perfil completo de **un competidor específico**.

**Parámetros**:
```json
{
  "place_id": "ChIJ...",
  "session_id": "abc123"  // Opcional: guardar en sesión
}
```

**Pipeline de Enriquecimiento**:

```
1. Google Maps Place Details API
   ↓
   - Nombre, dirección, coordenadas
   - Teléfono, website
   - Rating, reseñas (primeras 10)
   - Horarios de atención
   - Fotos (hasta 20)
   - Price level

2. Cross-Referencing Web (Gemini + Google Search)
   ↓
   - Búsqueda: "Nombre + Teléfono + Dirección"
   - Identificación de redes sociales
   - Links a delivery platforms
   - Menú o precios públicos

3. Identificación de Redes Sociales
   ↓
   - Facebook (fanpage)
   - Instagram (perfil + handle)
   - TikTok
   - WhatsApp Business

4. Validación por Coincidencia
   ↓
   ¿Coincide nombre + teléfono + dirección?
   → SÍ: Consolidar datos
   → NO: Marcar como "baja confianza"

5. Extracción de WhatsApp Business
   ↓
   - Número identificado
   - Catálogo (requiere API)
   - Menú disponible

6. Análisis de Fotos (Gemini Vision)
   ↓
   - Ambiente del restaurante
   - Platos visibles
   - Nivel de precio aparente
   - Calidad de presentación

7. Análisis de Reseñas (Gemini)
   ↓
   - Fortalezas mencionadas
   - Quejas comunes
   - Platos más elogiados

8. Extracción de Menú (Múltiples Fuentes)
   ↓
   - Website (scraping + Gemini)
   - Fotos de Google Maps
   - WhatsApp Business catalog
   - Consolidación inteligente

9. Consolidación Final (Gemini)
   ↓
   - Cuisine types
   - Specialties
   - Unique offerings
   - Target audience
   - Brand positioning
   - Competitive strengths/weaknesses
```

---

## 📊 Estructura de Datos

### **CompetitorProfile** (Completo)

```python
{
  "competitor_id": "uuid",
  "name": "Nombre del Restaurante",
  
  # Ubicación
  "location": {
    "address": "Dirección completa",
    "coordinates": {"lat": 4.6097, "lng": -74.0817},
    "place_id": "ChIJ..."
  },
  
  # Contacto
  "contact": {
    "phone": "+57 300 1234567",
    "website": "https://...",
    "whatsapp_business": "+573001234567"
  },
  
  # Google Maps
  "google_maps": {
    "rating": 4.2,
    "user_ratings_total": 450,
    "price_level": 2,  # 1=$ 2=$$ 3=$$$ 4=$$$$
    "opening_hours": {
      "open_now": true,
      "periods": [...]
    },
    "reviews_count": 10,
    "reviews_summary": "Texto generado por Gemini",
    "photos_count": 45
  },
  
  # Redes Sociales
  "social_media": [
    {
      "platform": "facebook",
      "url": "https://facebook.com/...",
      "handle": "restaurantepro",
      "followers": 5200,
      "verified": true
    },
    {
      "platform": "instagram",
      "url": "https://instagram.com/...",
      "handle": "@restaurantepro",
      "followers": 8500
    },
    {
      "platform": "whatsapp_business",
      "url": "https://wa.me/573001234567",
      "handle": "+573001234567"
    }
  ],
  
  # Menú
  "menu": {
    "items": [
      {
        "name": "Bandeja Paisa",
        "price": 28000,
        "category": "Platos Fuertes",
        "source": "website",
        "confidence": 0.95
      }
    ],
    "sources": ["website", "google_photos", "whatsapp_business"],
    "item_count": 45
  },
  
  # WhatsApp Business
  "whatsapp_business_data": {
    "number": "+573001234567",
    "has_menu": true,
    "catalog_items": 30
  },
  
  # Inteligencia Competitiva
  "competitive_intelligence": {
    "cuisine_types": ["Colombiana", "Parrilla"],
    "specialties": ["Arepas artesanales", "Bandeja Paisa premium"],
    "unique_offerings": ["Menú vegano", "Delivery 24/7"],
    "price_range": {"min": 15000, "max": 45000, "avg": 28500},
    "target_audience": "Familias de clase media-alta",
    "brand_positioning": "Tradicional con toque moderno"
  },
  
  # Metadata
  "metadata": {
    "data_sources": [
      "google_maps_place_details",
      "web_search",
      "facebook",
      "instagram",
      "whatsapp_business",
      "google_photos_vision_analysis",
      "google_reviews"
    ],
    "confidence_score": 0.92,
    "last_updated": "2026-01-30T06:00:00Z",
    "enrichment_notes": [
      "Cross-validated phone from Maps and Facebook",
      "Menu extracted from website with 95% confidence"
    ]
  }
}
```

---

## 🔄 Cross-Referencing Inteligente

### **Validación por Coincidencia**

El sistema valida que los datos de diferentes fuentes correspondan al **mismo negocio**:

```python
# Ejemplo de validación
Maps: "La Parrilla de Pepe" | +57 300 1234567 | Calle 123
Web:  "La Parrilla de Pepe" | +57 300 1234567 | Calle 123
        ✅ MATCH: 100% - Es el mismo negocio

Facebook: "Parrilla Pepe"    | +57 300 1234567 | Calle 123
          ⚠️  MATCH: 80% - Probablemente el mismo (nombre similar)

Instagram: "@parrilladejuan"  | +57 300 9999999 | Otra calle
          ❌ NO MATCH: Diferente negocio
```

**Criterios de Validación**:
1. **Nombre**: Fuzzy matching (>70% similitud)
2. **Teléfono**: Match exacto (ignorar formato)
3. **Dirección**: Misma calle o coordenadas cercanas (<50m)

**Confidence Score**:
- 3 coincidencias = **1.0** (muy alta confianza)
- 2 coincidencias = **0.8** (alta confianza)
- 1 coincidencia = **0.5** (media confianza)
- 0 coincidencias = **0.2** (baja confianza)

---

## 🎯 Casos de Uso

### **Caso 1: Usuario Busca Su Negocio**

```
1. Usuario: "La Parrilla de Pepe, Bogotá"
2. Sistema: Busca en Google Maps Text Search
3. Sistema: Devuelve 3 candidatos con fotos
4. Usuario: Selecciona el correcto en el mapa
5. Sistema: Establece place_id y enriquece perfil
   - Extrae rating: 4.5 (235 reseñas)
   - Identifica Instagram: @parrillapepe
   - Identifica Facebook: facebook.com/parrillapepe
   - WhatsApp: +57 300 1234567
   - Valida que coinciden (mismo teléfono)
6. Resultado: Perfil propio completo para auto-análisis
```

### **Caso 2: Análisis de Competencia Cercana**

```
1. Usuario establece su ubicación: (4.6097, -74.0817)
2. Sistema: Busca competidores en 1.5km radio
3. Sistema: Encuentra 8 restaurantes
4. Usuario: Solicita enriquecimiento (enrich=true)
5. Sistema: Para cada competidor:
   a. Extrae Google Maps details
   b. Busca en web: Facebook, Instagram
   c. Valida coincidencias (nombre + teléfono)
   d. Analiza fotos con Gemini Vision
   e. Extrae menú de website
   f. Consolida con Gemini
6. Resultado: 8 perfiles completos listos para análisis
```

### **Caso 3: Deep Dive en Competidor Específico**

```
1. Usuario ve competidor interesante: "Restaurante X"
2. Usuario solicita enriquecimiento individual
3. Sistema ejecuta pipeline completo:
   - Google Maps: 4.8 rating, 520 reseñas
   - Web search encuentra:
     * Instagram: @restaurantex (12K followers)
     * Facebook: RestauranteXOficial
     * WhatsApp: +57 301 9876543
   - Valida: Mismo teléfono en todos los perfiles ✅
   - Extrae menú de Instagram (fotos de platos)
   - Analiza 10 reseñas top con Gemini:
     "Fortaleza: Atención rápida, platos abundantes"
     "Debilidad: Estacionamiento limitado"
4. Resultado: Perfil ultra-completo con 0.95 confidence
```

---

## 🔧 Configuración Requerida

### **Variables de Entorno**

```bash
# backend/.env
GOOGLE_MAPS_API_KEY=AIza...  # REQUERIDO para Place Details API
GEMINI_API_KEY=AIza...       # REQUERIDO para análisis multimodal
```

### **APIs Habilitadas en Google Cloud**

1. **Places API** (Place Details, Text Search, Nearby Search)
2. **Maps JavaScript API** (para visualización en frontend)

### **Opcional** (para funcionalidad completa):

- **WhatsApp Business API** (para extraer catálogos)
- **Facebook Graph API** (para estadísticas de fanpages)
- **Instagram Basic Display API** (para posts y engagement)

---

## 📈 Beneficios del Sistema

### **Para el Negocio Propio**

✅ **Auto-conocimiento**:
- Ver cómo te ven en Google Maps
- Tus propias calificaciones y reseñas
- Tu presencia en redes sociales
- Tu menú consolidado

### **Para Análisis de Competencia**

✅ **Perfiles Completos**:
- Datos de 5-10 fuentes consolidados
- Validación por cross-referencing
- Confianza medible (confidence score)

✅ **Inteligencia Accionable**:
- Qué ofrecen que tú no
- Cómo están posicionados
- Sus fortalezas según reseñas
- Sus debilidades explotables

✅ **Menús Comparables**:
- Precios de competidores
- Platos que tienen y tú no
- Gaps de mercado

---

## 🚀 Próximos Pasos

### **Frontend** (Pendiente)

1. **Mejorar LocationPicker**:
   - Mostrar candidatos con fotos
   - Permitir selección visual
   - Preview del perfil antes de confirmar

2. **Vista de Competidores Enriquecidos**:
   - Cards con todos los datos
   - Tabs: Menú, Reseñas, Redes Sociales
   - Comparación lado a lado

3. **Dashboard de Inteligencia**:
   - Mapa con competidores
   - Click para ver perfil completo
   - Análisis comparativo

### **Backend** (Mejoras Futuras)

1. **Cache de Perfiles**:
   - Guardar perfiles enriquecidos
   - TTL de 24 horas
   - Re-enriquecimiento bajo demanda

2. **Scraping Avanzado**:
   - Instagram posts (con API)
   - Facebook reviews
   - TripAdvisor si está disponible

3. **Análisis de Tendencias**:
   - Monitorear cambios en ratings
   - Nuevos posts en redes sociales
   - Cambios en menú

---

## 💡 Ejemplos de Uso

### **Enriquecer Competencia Cercana**

```bash
curl -X POST http://localhost:8000/api/v1/location/nearby-restaurants \
  -F "lat=4.6097" \
  -F "lng=-74.0817" \
  -F "radius=1500" \
  -F "enrich=true"
```

### **Identificar Mi Negocio**

```bash
curl -X POST http://localhost:8000/api/v1/location/identify-business \
  -F "query=La Parrilla de Pepe, Bogotá" \
  -F "lat=4.6097" \
  -F "lng=-74.0817"
```

### **Establecer Mi Negocio**

```bash
curl -X POST http://localhost:8000/api/v1/location/set-business \
  -F "session_id=abc123" \
  -F "place_id=ChIJ..." \
  -F "enrich_profile=true"
```

### **Enriquecer Competidor Individual**

```bash
curl -X POST http://localhost:8000/api/v1/location/enrich-competitor \
  -F "place_id=ChIJ..." \
  -F "session_id=abc123"
```

---

**¡El sistema más completo de inteligencia competitiva para restaurantes con Gemini 3 y Google Maps! 🎉**
