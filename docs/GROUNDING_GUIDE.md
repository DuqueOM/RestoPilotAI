# Google Search Grounding - Guía de Implementación

## 🎯 Qué es Grounding

**Grounding** es una capacidad exclusiva de Gemini 3 que permite al modelo conectarse con Google Search en tiempo real para obtener información actualizada y verificable.

**DIFERENCIADOR HACKATHON:** Gemini 3 es el único modelo con grounding nativo de Google Search.

---

## 🚀 Implementación en MenuPilot

### Método Principal: `generate_with_grounding()`

```python
from app.services.gemini.base_agent import GeminiBaseAgent

agent = GeminiBaseAgent()

result = await agent.generate_with_grounding(
    prompt="¿Cuáles son las tendencias actuales en restaurantes mexicanos en 2026?",
    enable_grounding=True,
    thinking_level="STANDARD"
)

# Resultado
{
    "answer": "Las tendencias actuales incluyen...",
    "grounding_metadata": {
        "grounding_chunks": [
            {
                "uri": "https://example.com/restaurant-trends",
                "title": "Restaurant Trends 2026"
            }
        ],
        "search_queries": ["restaurant trends 2026 mexican"]
    },
    "grounded": True,
    "model_used": "gemini-3-flash-preview"
}
```

---

## 📊 Casos de Uso en MenuPilot

### 1. Competitive Intelligence

```python
# backend/app/services/analysis/competitive.py

async def analyze_competitor_with_grounding(
    competitor_name: str,
    location: str
) -> Dict[str, Any]:
    """Analiza competidor con información actualizada de Google Search."""
    
    agent = GeminiBaseAgent()
    
    prompt = f"""
    Analiza el restaurante "{competitor_name}" en {location}.
    
    Busca información sobre:
    1. Menú actual y precios
    2. Reviews recientes
    3. Estrategias de marketing
    4. Presencia en redes sociales
    5. Tendencias que están siguiendo
    
    Usa información actualizada de Google Search.
    """
    
    result = await agent.generate_with_grounding(
        prompt=prompt,
        enable_grounding=True,
        thinking_level="DEEP"
    )
    
    return {
        "analysis": result["answer"],
        "sources": result["grounding_metadata"]["grounding_chunks"],
        "search_queries": result["grounding_metadata"]["search_queries"],
        "timestamp": datetime.now().isoformat()
    }
```

### 2. Market Trends

```python
async def get_market_trends(
    cuisine_type: str,
    location: str
) -> Dict[str, Any]:
    """Obtiene tendencias de mercado actualizadas."""
    
    agent = GeminiBaseAgent()
    
    prompt = f"""
    ¿Cuáles son las tendencias actuales para restaurantes de {cuisine_type} 
    en {location}?
    
    Incluye:
    - Platos populares
    - Estrategias de precio
    - Marketing efectivo
    - Innovaciones recientes
    """
    
    result = await agent.generate_with_grounding(
        prompt=prompt,
        enable_grounding=True,
        thinking_level="STANDARD"
    )
    
    return result
```

### 3. Pricing Intelligence

```python
async def analyze_market_pricing(
    dish_name: str,
    location: str
) -> Dict[str, Any]:
    """Analiza precios de mercado para un plato."""
    
    agent = GeminiBaseAgent()
    
    prompt = f"""
    ¿Cuál es el rango de precios típico para {dish_name} en restaurantes 
    de {location}?
    
    Busca información actualizada sobre precios en la zona.
    """
    
    result = await agent.generate_with_grounding(
        prompt=prompt,
        enable_grounding=True,
        thinking_level="QUICK"
    )
    
    return result
```

---

## 🔧 Configuración

### Settings

```python
# backend/app/core/config.py

# Grounding habilitado por defecto
enable_grounding: bool = True

# Configuración específica
grounding_enabled_for_competitive: bool = True
grounding_max_results: int = 5
grounding_include_sources: bool = True
grounding_confidence_threshold: float = 0.7
```

### Variables de Entorno

```bash
# .env
ENABLE_GROUNDING=true
GROUNDING_ENABLED_FOR_COMPETITIVE=true
GROUNDING_MAX_RESULTS=5
GROUNDING_INCLUDE_SOURCES=true
GROUNDING_CONFIDENCE_THRESHOLD=0.7
```

---

## 🎨 Visualización en Frontend

### Componente de Sources

```typescript
// frontend/src/components/GroundingSources.tsx

interface GroundingSourcesProps {
  metadata: {
    grounding_chunks: Array<{
      uri: string;
      title: string;
    }>;
    search_queries: string[];
  } | null;
}

export function GroundingSources({ metadata }: GroundingSourcesProps) {
  if (!metadata || metadata.grounding_chunks.length === 0) {
    return null;
  }
  
  return (
    <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
      <div className="flex items-center gap-2 mb-3">
        <Search className="w-4 h-4 text-blue-600" />
        <span className="text-sm font-medium text-blue-900">
          Verified Sources
        </span>
      </div>
      
      <div className="space-y-2">
        {metadata.grounding_chunks.map((chunk, idx) => (
          <a
            key={idx}
            href={chunk.uri}
            target="_blank"
            rel="noopener noreferrer"
            className="block text-sm text-blue-700 hover:text-blue-900 
                       hover:underline"
          >
            <ExternalLink className="w-3 h-3 inline mr-1" />
            {chunk.title || chunk.uri}
          </a>
        ))}
      </div>
      
      {metadata.search_queries.length > 0 && (
        <div className="mt-3 pt-3 border-t border-blue-200">
          <span className="text-xs text-blue-600">
            Search: {metadata.search_queries.join(', ')}
          </span>
        </div>
      )}
    </div>
  );
}
```

---

## 📈 Beneficios

### 1. Información Actualizada
- Datos en tiempo real de Google Search
- No limitado al training data del modelo
- Información verificable con fuentes

### 2. Credibilidad
- Cita fuentes automáticamente
- Aumenta confianza del usuario
- Reduce alucinaciones

### 3. Competitive Advantage
- Análisis de competidores con datos reales
- Tendencias de mercado actualizadas
- Pricing intelligence preciso

---

## 🔍 Debugging

### Verificar Grounding Metadata

```python
result = await agent.generate_with_grounding(
    prompt="Test grounding",
    enable_grounding=True
)

logger.debug(f"Grounded: {result['grounded']}")
logger.debug(f"Sources: {result['grounding_metadata']}")

if not result['grounded']:
    logger.warning("Grounding no funcionó - verificar configuración")
```

---

## ⚠️ Limitaciones

1. **Rate Limits:** Grounding consume más recursos
2. **Latencia:** Búsquedas en Google agregan ~1-2s
3. **Disponibilidad:** Requiere Gemini 3 (no funciona en modelos anteriores)
4. **Idioma:** Mejores resultados en inglés

---

## ✅ Checklist

- [x] Método `generate_with_grounding()` implementado
- [x] Extracción de grounding metadata
- [x] Configuración en settings
- [ ] Componente frontend `GroundingSources.tsx`
- [ ] Integración en competitive analysis
- [ ] Tests de grounding
- [ ] Documentación de API

---

**Fecha:** 2026-02-02  
**Versión:** 1.0  
**Status:** ✅ Implementado en Backend
