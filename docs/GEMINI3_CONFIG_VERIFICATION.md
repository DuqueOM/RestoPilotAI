# Verificación de Configuración Gemini 3

## ✅ Checklist de Configuración Correcta

Este documento verifica que MenuPilot esté usando **exclusivamente Gemini 3** y aprovechando todas sus capacidades multimodales.

---

## 1. Configuración Core (`backend/app/core/config.py`)

### ✅ Modelos Gemini 3 Configurados

```python
# CRÍTICO: Solo modelos de Gemini 3
gemini_model_primary: str = "gemini-3-flash-preview"      # ✅ Modelo principal
gemini_model_reasoning: str = "gemini-3-flash-preview"    # ✅ BCG, competitive intel
gemini_model_vision: str = "gemini-3-pro-preview"         # ✅ Multimodal (menús, platos)
gemini_model_image_gen: str = "gemini-3-pro-image-preview" # ✅ Creative Autopilot

# Backward compatibility
gemini_model: str = "gemini-3-flash-preview"              # ✅ Default
gemini_model_pro: str = "gemini-3-pro-preview"            # ✅ Pro variant
```

### ✅ Rate Limits Alineados con Free Tier

```python
gemini_rate_limit_rpm: int = 15                # ✅ Free tier: 15 requests/min
gemini_max_concurrent_requests: int = 3        # ✅ Evitar throttling
```

### ✅ Timeouts Optimizados para Marathon Agent

```python
gemini_timeout_seconds: int = 120              # ✅ Requests normales (2 min)
gemini_marathon_timeout_seconds: int = 600     # ✅ Tareas largas (10 min)
gemini_connection_timeout: int = 30            # ✅ Solo handshake
```

### ✅ Token Limits de Gemini 3

```python
gemini_max_input_tokens: int = 128000          # ✅ Context window completo
gemini_max_output_tokens: int = 8192           # ✅ Flash model limit
gemini_max_output_tokens_reasoning: int = 16384 # ✅ Análisis profundos
```

### ✅ Hackathon Features Flags

```python
enable_vibe_engineering: bool = True           # ✅ Track: Vibe Engineering
enable_marathon_agent: bool = True             # ✅ Track: Marathon Agent
enable_creative_autopilot: bool = True         # ✅ Activo para Hackathon
enable_grounding: bool = True                  # ✅ Google Search grounding
```

### ✅ Vibe Engineering Configuration

```python
vibe_quality_threshold: float = 0.85           # ✅ Score mínimo aceptable
vibe_max_iterations: int = 3                   # ✅ Máximo de ciclos de mejora
vibe_auto_improve_default: bool = True         # ✅ Auto-mejora por defecto
vibe_enable_thought_transparency: bool = True  # ✅ Mostrar razonamiento
```

### ✅ Marathon Agent Configuration

```python
marathon_checkpoint_interval: int = 60         # ✅ Guardar cada 60 segundos
marathon_max_retries_per_step: int = 3         # ✅ Reintentos por paso
marathon_enable_recovery: bool = True          # ✅ Recuperación habilitada
marathon_enable_checkpoints: bool = True       # ✅ Checkpoints habilitados
marathon_max_task_duration: int = 3600         # ✅ 1 hora máximo por tarea
```

### ✅ Thought Signatures Configuration

```python
# Niveles de razonamiento transparente
thinking_level_quick_temp: float = 0.3         # ✅ Quick: baja temperatura
thinking_level_quick_tokens: int = 2048        # ✅ Quick: 2K tokens

thinking_level_standard_temp: float = 0.5      # ✅ Standard: temperatura media
thinking_level_standard_tokens: int = 4096     # ✅ Standard: 4K tokens

thinking_level_deep_temp: float = 0.7          # ✅ Deep: alta temperatura
thinking_level_deep_tokens: int = 8192         # ✅ Deep: 8K tokens

thinking_level_exhaustive_temp: float = 0.8    # ✅ Exhaustive: muy alta temp
thinking_level_exhaustive_tokens: int = 16384  # ✅ Exhaustive: 16K tokens
```

### ✅ Grounding Configuration

```python
grounding_enabled_for_competitive: bool = True # ✅ Grounding para competidores
grounding_max_results: int = 5                 # ✅ Máximo de resultados
grounding_include_sources: bool = True         # ✅ Siempre citar fuentes
grounding_confidence_threshold: float = 0.7    # ✅ Mínimo de confianza
```

---

## 2. Base Agent (`backend/app/services/gemini/base_agent.py`)

### ✅ Enum de Modelos Corregido

```python
class GeminiModel(str, Enum):
    """Supported Gemini 3 models - CRÍTICO: Solo usar Gemini 3."""

    FLASH = "gemini-3-flash-preview"           # ✅ Modelo principal rápido
    PRO = "gemini-3-pro-preview"               # ✅ Modelo avanzado multimodal
    VISION = "gemini-3-pro-preview"            # ✅ Análisis de imágenes
    IMAGE_GEN = "gemini-3-pro-image-preview"   # ✅ Generación de imágenes
```

**❌ ANTES (INCORRECTO):**
```python
FLASH = "gemini-2.0-flash-exp"  # ❌ Modelo viejo
```

### ✅ Timeouts Dinámicos por Tipo de Tarea

```python
# Get timeout based on task type
is_long_task = thinking_level in ["EXHAUSTIVE", "DEEP"] or feature == "marathon"
timeout = settings.gemini_marathon_timeout_seconds if is_long_task else settings.gemini_timeout_seconds
```

**Beneficios:**
- Tareas rápidas (QUICK, STANDARD): 120 segundos
- Tareas largas (DEEP, EXHAUSTIVE, Marathon): 600 segundos
- Evita timeouts prematuros en análisis complejos

### ✅ Thinking Levels Configurables

```python
# Configure based on thinking level
if thinking_level == "QUICK":
    config_kwargs = {
        "temperature": settings.thinking_level_quick_temp,      # 0.3
        "max_output_tokens": settings.thinking_level_quick_tokens  # 2048
    }
elif thinking_level == "STANDARD":
    config_kwargs = {
        "temperature": settings.thinking_level_standard_temp,   # 0.5
        "max_output_tokens": settings.thinking_level_standard_tokens  # 4096
    }
# ... etc
```

**Beneficios:**
- Configuración centralizada en settings
- Fácil ajuste sin modificar código
- Diferentes niveles para diferentes casos de uso

### ✅ Helper para Selección de Modelo

```python
def get_model_for_task(self, task_type: str = "general") -> str:
    """Get appropriate Gemini 3 model based on task type."""
    if task_type == "vision" or task_type == "multimodal":
        return self.settings.gemini_model_vision
    elif task_type == "reasoning" or task_type == "analysis":
        return self.settings.gemini_model_reasoning
    elif task_type == "image_gen":
        return self.settings.gemini_model_image_gen
    else:
        return self.settings.gemini_model_primary
```

**Uso:**
```python
# Para análisis de imágenes de menú
model = agent.get_model_for_task("vision")

# Para análisis BCG
model = agent.get_model_for_task("reasoning")

# Para generación de imágenes (Creative Autopilot)
model = agent.get_model_for_task("image_gen")
```

---

## 3. Variables de Entorno (`.env`)

### ✅ Template Actualizado (`.env.example`)

```bash
# Gemini 3 Model Configuration (CRÍTICO: Solo usar Gemini 3)
GEMINI_MODEL_PRIMARY=gemini-3-flash-preview
GEMINI_MODEL_REASONING=gemini-3-flash-preview
GEMINI_MODEL_VISION=gemini-3-pro-preview
GEMINI_MODEL_IMAGE_GEN=gemini-3-pro-image-preview

# Gemini 3 Rate Limits (Free Tier)
GEMINI_RATE_LIMIT_RPM=15
GEMINI_MAX_CONCURRENT_REQUESTS=3

# Gemini 3 Timeouts
GEMINI_TIMEOUT_SECONDS=120
GEMINI_MARATHON_TIMEOUT_SECONDS=600
GEMINI_CONNECTION_TIMEOUT=30

# Gemini 3 Features
GEMINI_ENABLE_GROUNDING=true
GEMINI_ENABLE_STREAMING=true
GEMINI_CACHE_TTL_SECONDS=3600
```

---

## 4. Verificación de Integración

### ✅ Checklist de Verificación

- [x] **Config Core:** Todos los modelos son Gemini 3
- [x] **Base Agent:** Enum de modelos corregido
- [x] **Timeouts:** Dinámicos según tipo de tarea
- [x] **Thinking Levels:** Configurables desde settings
- [x] **Rate Limits:** Alineados con free tier (15 RPM)
- [x] **Token Limits:** Respetan límites de Gemini 3
- [x] **Hackathon Features:** Flags configurables
- [x] **Vibe Engineering:** Configuración completa
- [x] **Marathon Agent:** Configuración completa
- [x] **Grounding:** Configuración completa
- [x] **Thought Signatures:** 4 niveles configurables
- [x] **.env.example:** Actualizado con todas las variables

### 🔍 Comandos de Verificación

```bash
# Verificar que config.py compila
python -m py_compile backend/app/core/config.py

# Verificar que base_agent.py compila
python -m py_compile backend/app/services/gemini/base_agent.py

# Buscar referencias a modelos viejos
grep -r "gemini-2" backend/app/services/ || echo "✅ No old models found"
grep -r "gemini-1" backend/app/services/ || echo "✅ No old models found"

# Verificar que todos usan Gemini 3
grep -r "gemini-3" backend/app/services/ | wc -l
```

---

## 5. Casos de Uso por Modelo

### 📊 Gemini 3 Flash Preview (Primary/Reasoning)

**Uso:** Análisis rápidos, BCG, competitive intelligence, text processing

**Características:**
- Velocidad: ~1-2s por request
- Tokens: 8K output max
- Costo: Bajo (free tier)
- Casos: BCG analysis, sales predictions, campaign generation

**Ejemplo:**
```python
agent = GeminiBaseAgent()
result = await agent.generate_response(
    prompt="Analiza este menú y clasifica items según BCG matrix",
    thinking_level="STANDARD"  # 4K tokens, temp 0.5
)
```

### 🖼️ Gemini 3 Pro Preview (Vision/Multimodal)

**Uso:** Análisis de imágenes, menús, platos, fotos de competidores

**Características:**
- Velocidad: ~2-4s por request
- Tokens: 16K output max
- Multimodal: Texto + imágenes
- Casos: Menu extraction, dish analysis, competitor photos

**Ejemplo:**
```python
agent = GeminiBaseAgent(model_name=agent.get_model_for_task("vision"))
result = await agent.generate_response(
    prompt="Extrae todos los items de este menú",
    images=[menu_image_bytes],
    thinking_level="DEEP"  # 8K tokens, temp 0.7
)
```

### 🎨 Gemini 3 Pro Image Preview (Image Generation)

**Uso:** Creative Autopilot, generación de imágenes para campañas

**Características:**
- Velocidad: ~5-10s por imagen
- Output: Imagen generada
- Casos: Menu redesign, social media assets

**Ejemplo:**
```python
# TODO: Implementar cuando Creative Autopilot esté listo
agent = GeminiBaseAgent(model_name=agent.get_model_for_task("image_gen"))
image = await agent.generate_image(
    prompt="Diseña un menú moderno para restaurante mexicano"
)
```

---

## 6. Mejoras Implementadas

### ✅ Antes vs Después

| Aspecto | Antes | Después | Mejora |
|---------|-------|---------|--------|
| **Modelos** | Mezclados (2.0 + 3.0) | Solo Gemini 3 | ✅ Consistencia |
| **Timeouts** | Fijo 60s | Dinámico 120s-600s | ✅ Marathon Agent |
| **Thinking Levels** | Hardcoded | Configurables | ✅ Flexibilidad |
| **Rate Limits** | 60 RPM | 15 RPM (free tier) | ✅ Realista |
| **Token Limits** | Genérico | Por nivel | ✅ Optimizado |
| **Model Selection** | Manual | Helper method | ✅ Automático |
| **Hackathon Flags** | No existían | Configurables | ✅ Control |

---

## 7. Próximos Pasos

### 🚧 TODO: Creative Autopilot

```python
# Implementar generación de imágenes con Gemini 3 Pro Image Preview
# backend/app/services/creative/autopilot.py

async def generate_menu_design(prompt: str) -> bytes:
    """Generate menu design using Gemini 3 Image Generation."""
    agent = GeminiBaseAgent()
    model = agent.get_model_for_task("image_gen")
    # TODO: Implementar lógica de generación
    pass
```

### 🔄 Recomendaciones

1. **Monitoreo de Rate Limits:**
   - Implementar contador de requests por minuto
   - Alert cuando se acerque a 15 RPM
   - Queue para requests excedentes

2. **Optimización de Costos:**
   - Usar Flash para tareas simples
   - Usar Pro solo cuando sea necesario multimodal
   - Cachear respuestas agresivamente

3. **Testing:**
   - Probar cada thinking level
   - Verificar timeouts en Marathon Agent
   - Validar grounding en competitive analysis

---

## ✅ Resumen

**Estado:** Configuración de Gemini 3 completamente actualizada y optimizada

**Cambios Clave:**
1. ✅ Solo modelos Gemini 3 en toda la aplicación
2. ✅ Timeouts dinámicos para Marathon Agent
3. ✅ Thinking levels configurables desde settings
4. ✅ Rate limits realistas (15 RPM free tier)
5. ✅ Helper para selección automática de modelo
6. ✅ Flags para features del hackathon
7. ✅ Configuración completa de Vibe Engineering
8. ✅ Configuración completa de Marathon Agent
9. ✅ Template .env actualizado

**Integración:** Todos los cambios son backward-compatible y se integran correctamente con el workflow existente.

---

**Fecha:** 2026-02-02  
**Versión:** 2.0  
**Status:** ✅ Completado
