# Enhanced Gemini 3 Agent - Guía de Uso

## 📚 Descripción

El `EnhancedGeminiAgent` es una versión mejorada del agente base que aprovecha al máximo las capacidades multimodales de Gemini 3, incluyendo:

- ✅ **Streaming** - Generación en tiempo real para mejor UX
- ✅ **Grounding** - Google Search integrado para mayor precisión
- ✅ **Caching** - Reducción de costos y latencia
- ✅ **Validation** - Salidas estructuradas con Pydantic
- ✅ **Thought Traces** - Razonamiento transparente con metadata

---

## 🚀 Uso Básico

### Inicialización

```python
from app.services.gemini.enhanced_agent import EnhancedGeminiAgent, ThinkingLevel

# Inicializar con todas las features habilitadas
agent = EnhancedGeminiAgent(
    enable_streaming=True,
    enable_grounding=True,
    enable_cache=True
)
```

### Generación Simple

```python
# Generación básica
result = await agent.generate(
    prompt="Analiza las tendencias de menú en restaurantes mexicanos",
    thinking_level=ThinkingLevel.STANDARD
)

print(result["data"])  # Respuesta del modelo
print(result["usage"])  # Estadísticas de tokens y costo
print(result["thought_trace"])  # Proceso de razonamiento
```

### Generación con Grounding

```python
# Usar Google Search para información actualizada
result = await agent.generate(
    prompt="¿Cuáles son las tendencias de comida vegana en 2026?",
    thinking_level=ThinkingLevel.DEEP,
    enable_grounding=True
)

# Ver fuentes de información
for source in result["grounding_sources"]:
    print(f"- {source['title']}: {source['uri']}")
```

### Generación con Imágenes (Multimodal)

```python
# Analizar imagen de menú
with open("menu.jpg", "rb") as f:
    menu_image = f.read()

result = await agent.generate(
    prompt="Extrae todos los platillos y precios de este menú",
    images=[menu_image],
    thinking_level=ThinkingLevel.STANDARD
)
```

### Salida Estructurada con Pydantic

```python
from pydantic import BaseModel
from typing import List

class MenuItem(BaseModel):
    name: str
    price: float
    category: str
    description: str

class MenuAnalysis(BaseModel):
    items: List[MenuItem]
    total_items: int
    avg_price: float

# Generar con validación automática
result = await agent.generate(
    prompt="Extrae los platillos de este menú en formato JSON",
    images=[menu_image],
    response_schema=MenuAnalysis,
    thinking_level=ThinkingLevel.STANDARD
)

# result["data"] ya está validado como MenuAnalysis
menu_data = result["data"]
print(f"Total items: {menu_data['total_items']}")
```

---

## 🌊 Streaming

### Generación en Tiempo Real

```python
# Streaming para mejor UX
async for chunk in agent.generate_stream(
    prompt="Genera una campaña de marketing para un restaurante italiano",
    thinking_level=ThinkingLevel.STANDARD
):
    print(chunk, end="", flush=True)
```

### Streaming con WebSocket (Frontend)

```python
from fastapi import WebSocket

@router.websocket("/ws/generate")
async def websocket_generate(websocket: WebSocket):
    await websocket.accept()
    
    # Recibir prompt del cliente
    data = await websocket.receive_json()
    prompt = data["prompt"]
    
    # Stream respuesta
    async for chunk in agent.generate_stream(prompt):
        await websocket.send_text(chunk)
    
    await websocket.close()
```

---

## 💾 Caching

### Uso Automático

```python
# Primera llamada - genera y cachea
result1 = await agent.generate(
    prompt="Analiza este menú",
    images=[menu_image]
)
print(result1["cached"])  # False

# Segunda llamada - usa cache
result2 = await agent.generate(
    prompt="Analiza este menú",
    images=[menu_image]
)
print(result2["cached"])  # True
print(result2["usage"]["cost_usd"])  # 0.0
```

### Bypass Cache

```python
# Forzar regeneración
result = await agent.generate(
    prompt="Analiza este menú",
    images=[menu_image],
    bypass_cache=True
)
```

### Limpiar Cache

```python
# Limpiar cache manualmente
agent.clear_cache()
```

---

## 🧠 Thinking Levels

### Niveles Disponibles

```python
from app.services.gemini.enhanced_agent import ThinkingLevel

# QUICK - Respuestas rápidas (temp=0.3, tokens=2048)
result = await agent.generate(
    prompt="¿Cuál es el precio promedio?",
    thinking_level=ThinkingLevel.QUICK
)

# STANDARD - Análisis estándar (temp=0.7, tokens=4096)
result = await agent.generate(
    prompt="Analiza las tendencias de ventas",
    thinking_level=ThinkingLevel.STANDARD
)

# DEEP - Análisis profundo (temp=0.9, tokens=8192)
result = await agent.generate(
    prompt="Genera estrategia competitiva completa",
    thinking_level=ThinkingLevel.DEEP
)

# EXHAUSTIVE - Análisis exhaustivo (temp=1.0, tokens=16384)
result = await agent.generate(
    prompt="Análisis completo de mercado con múltiples escenarios",
    thinking_level=ThinkingLevel.EXHAUSTIVE
)
```

---

## 📊 Thought Traces

### Razonamiento Transparente

```python
result = await agent.generate(
    prompt="¿Por qué este platillo es un 'Star' en BCG?",
    thinking_level=ThinkingLevel.DEEP,
    enable_thought_trace=True
)

# Ver proceso de razonamiento
trace = result["thought_trace"]
print(f"Nivel de pensamiento: {trace['thinking_level']}")
print(f"Confianza: {trace['confidence_score']}")
print(f"Grounded: {trace['grounded']}")

print("\nPasos de razonamiento:")
for step in trace["reasoning_steps"]:
    print(f"- {step}")

print("\nFuentes de datos:")
for source in trace["data_sources"]:
    print(f"- {source}")
```

---

## 📈 Estadísticas y Monitoreo

### Estadísticas de Sesión

```python
# Obtener estadísticas
stats = agent.get_session_stats()

print(f"Total requests: {stats['total_requests']}")
print(f"Total tokens: {stats['total_tokens']}")
print(f"Total cost: ${stats['total_cost_usd']}")
print(f"Avg cost/request: ${stats['avg_cost_per_request']}")
print(f"Cache hit rate: {stats['cache_hit_rate']}")
print(f"Cache size: {stats['cache_size']}")
```

---

## 🎯 Casos de Uso Específicos

### 1. Extracción de Menú con Validación

```python
from pydantic import BaseModel
from typing import List

class MenuItem(BaseModel):
    name: str
    price: float
    category: str

class MenuExtraction(BaseModel):
    items: List[MenuItem]

# Leer imagen
with open("menu.jpg", "rb") as f:
    menu_image = f.read()

# Extraer con validación
result = await agent.generate(
    prompt="""
    Extrae todos los platillos del menú en formato JSON.
    Para cada platillo incluye: name, price, category.
    """,
    images=[menu_image],
    response_schema=MenuExtraction,
    thinking_level=ThinkingLevel.STANDARD
)

# Datos ya validados
menu = result["data"]
for item in menu["items"]:
    print(f"{item['name']}: ${item['price']}")
```

### 2. Análisis Competitivo con Grounding

```python
result = await agent.generate(
    prompt="""
    Analiza las tendencias actuales de precios en restaurantes 
    de comida italiana en Ciudad de México. Incluye:
    - Rango de precios promedio
    - Platillos más populares
    - Estrategias de pricing
    """,
    thinking_level=ThinkingLevel.DEEP,
    enable_grounding=True
)

# Ver fuentes verificadas
print("Fuentes consultadas:")
for source in result["grounding_sources"]:
    print(f"- {source['title']}")
    print(f"  {source['uri']}")
```

### 3. Generación de Campaña con Streaming

```python
# Generar campaña en tiempo real
campaign_chunks = []

async for chunk in agent.generate_stream(
    prompt="""
    Genera una campaña de marketing completa para un 
    restaurante mexicano nuevo. Incluye:
    - Slogan
    - Propuesta de valor
    - Canales de marketing
    - Presupuesto sugerido
    """,
    thinking_level=ThinkingLevel.DEEP
):
    campaign_chunks.append(chunk)
    print(chunk, end="", flush=True)

full_campaign = "".join(campaign_chunks)
```

### 4. Análisis BCG con Thought Trace

```python
result = await agent.generate(
    prompt="""
    Analiza estos datos de ventas y clasifica cada platillo 
    según la matriz BCG (Star, Cash Cow, Question Mark, Dog).
    
    Datos: {sales_data}
    """,
    thinking_level=ThinkingLevel.DEEP,
    enable_thought_trace=True
)

# Ver razonamiento completo
trace = result["thought_trace"]
print(f"Confianza del análisis: {trace['confidence_score']:.2%}")
print("\nProceso de razonamiento:")
for i, step in enumerate(trace["reasoning_steps"], 1):
    print(f"{i}. {step}")
```

---

## ⚙️ Configuración Avanzada

### Personalizar Modelo

```python
from app.core.config import GeminiModel

# Usar modelo específico
agent = EnhancedGeminiAgent(
    model=GeminiModel.PRO_PREVIEW,  # Modelo más capaz
    enable_grounding=True
)
```

### Deshabilitar Features Selectivamente

```python
# Solo caching, sin streaming ni grounding
agent = EnhancedGeminiAgent(
    enable_streaming=False,
    enable_grounding=False,
    enable_cache=True
)
```

---

## 🔧 Integración con Servicios Existentes

### Uso en Reasoning Agent

```python
from app.services.gemini.enhanced_agent import EnhancedGeminiAgent

class ReasoningAgent:
    def __init__(self):
        self.agent = EnhancedGeminiAgent(
            enable_grounding=True,
            enable_cache=True
        )
    
    async def analyze_bcg(self, sales_data):
        result = await self.agent.generate(
            prompt=f"Analiza BCG: {sales_data}",
            thinking_level=ThinkingLevel.DEEP,
            enable_thought_trace=True
        )
        return result
```

### Uso en Creative Autopilot

```python
class CreativeAutopilotAgent:
    def __init__(self):
        self.agent = EnhancedGeminiAgent(
            model=GeminiModel.PRO_IMAGE,
            enable_streaming=True
        )
    
    async def generate_campaign_stream(self, brief):
        async for chunk in self.agent.generate_stream(
            prompt=brief,
            thinking_level=ThinkingLevel.STANDARD
        ):
            yield chunk
```

---

## 📝 Best Practices

### 1. Usar Thinking Level Apropiado

```python
# ✅ QUICK para respuestas simples
await agent.generate("¿Cuántos platillos hay?", ThinkingLevel.QUICK)

# ✅ STANDARD para análisis normales
await agent.generate("Analiza ventas", ThinkingLevel.STANDARD)

# ✅ DEEP para decisiones estratégicas
await agent.generate("Estrategia competitiva", ThinkingLevel.DEEP)

# ❌ NO usar EXHAUSTIVE innecesariamente (caro)
```

### 2. Aprovechar Cache

```python
# ✅ Reutilizar prompts similares
for menu in menus:
    result = await agent.generate(
        prompt="Extrae platillos",
        images=[menu]
    )  # Cache por imagen
```

### 3. Usar Grounding Solo Cuando Necesario

```python
# ✅ Grounding para info actualizada
await agent.generate(
    "Tendencias 2026",
    enable_grounding=True
)

# ❌ NO usar grounding para análisis interno
await agent.generate(
    "Analiza estos datos",
    enable_grounding=False  # Datos ya proporcionados
)
```

### 4. Validar Salidas Críticas

```python
# ✅ Usar Pydantic para datos estructurados
result = await agent.generate(
    prompt="Extrae menú",
    response_schema=MenuExtraction
)

# ✅ Verificar confidence score
if result["thought_trace"]["confidence_score"] < 0.7:
    logger.warning("Low confidence result")
```

---

## 🎓 Diferencias con Base Agent

| Feature | Base Agent | Enhanced Agent |
|---------|-----------|----------------|
| Streaming | ❌ | ✅ |
| Grounding | ⚠️ Parcial | ✅ Completo |
| Caching | ❌ | ✅ |
| Validation | ❌ | ✅ Pydantic |
| Thought Traces | ✅ Básico | ✅ Mejorado |
| Rate Limiting | ⚠️ Manual | ✅ Automático |
| Fallback | ❌ | ✅ Automático |
| Cost Tracking | ⚠️ Básico | ✅ Detallado |

---

## 🚀 Migración desde Base Agent

```python
# Antes (Base Agent)
from app.services.gemini.base_agent import GeminiBaseAgent

agent = GeminiBaseAgent()
result = await agent.generate(prompt="Test")

# Después (Enhanced Agent)
from app.services.gemini.enhanced_agent import EnhancedGeminiAgent, ThinkingLevel

agent = EnhancedGeminiAgent()
result = await agent.generate(
    prompt="Test",
    thinking_level=ThinkingLevel.STANDARD
)

# Acceder a datos
text = result["data"]["text"]  # En lugar de result directamente
```

---

**Última actualización:** 2026-02-03  
**Versión:** 1.0.0  
**Autor:** MenuPilot Team
