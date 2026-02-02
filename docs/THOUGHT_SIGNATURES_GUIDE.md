# Thought Signatures - Guía de Implementación

## 🎯 Qué son las Thought Signatures

Las **Thought Signatures** son un patrón de transparencia de razonamiento que permite ver el proceso de pensamiento del modelo Gemini 3 paso a paso, antes de llegar a la respuesta final.

**CRÍTICO PARA HACKATHON:** Este es un diferenciador clave que muestra cómo el modelo "piensa" antes de responder.

---

## 🚀 Implementación en MenuPilot

### Estructura de una Thought Signature

```
[THOUGHT SIGNATURE - Level: STANDARD]

Expected Depth: Standard analysis, 3-5 reasoning steps

{prompt original}

IMPORTANT: Structure your response as follows:

<thinking>
Step 1: [Initial analysis]
Step 2: [Considerations]
Step 3: [Cross-checking]
Step 4: [Conclusion]
</thinking>

<answer>
[Final response]
</answer>
```

---

## 📊 Niveles de Pensamiento

### QUICK (Rápido)
- **Temperatura:** 0.3
- **Tokens:** 2,048
- **Pasos:** 1-2 reasoning steps
- **Uso:** Respuestas rápidas, validaciones simples

```python
result = await agent.generate_with_thought_signature(
    prompt="¿Este plato es vegetariano?",
    thinking_level="QUICK"
)
```

### STANDARD (Estándar)
- **Temperatura:** 0.5
- **Tokens:** 4,096
- **Pasos:** 3-5 reasoning steps
- **Uso:** Análisis normales, BCG classification

```python
result = await agent.generate_with_thought_signature(
    prompt="Clasifica este item según BCG matrix",
    thinking_level="STANDARD"
)
```

### DEEP (Profundo)
- **Temperatura:** 0.7
- **Tokens:** 8,192
- **Pasos:** 5-10 reasoning steps
- **Uso:** Análisis competitivo, estrategias complejas

```python
result = await agent.generate_with_thought_signature(
    prompt="Analiza la estrategia competitiva de estos 5 restaurantes",
    thinking_level="DEEP"
)
```

### EXHAUSTIVE (Exhaustivo)
- **Temperatura:** 0.8
- **Tokens:** 16,384
- **Pasos:** 10+ reasoning steps
- **Uso:** Marathon Agent, análisis comprehensivos

```python
result = await agent.generate_with_thought_signature(
    prompt="Genera un plan completo de optimización de menú",
    thinking_level="EXHAUSTIVE"
)
```

---

## 💻 Uso en el Código

### Método Principal: `generate_with_thought_signature()`

```python
from app.services.gemini.base_agent import GeminiBaseAgent

agent = GeminiBaseAgent()

result = await agent.generate_with_thought_signature(
    prompt="Analiza este menú y sugiere mejoras",
    images=[menu_image_bytes],  # Opcional
    thinking_level="STANDARD",
    include_thought_trace=True  # True por defecto
)

# Resultado
{
    "answer": "Basado en el análisis...",
    "thought_trace": "Step 1: Identifico 15 items...\nStep 2: Noto que...",
    "thinking_level": "STANDARD",
    "model_used": "gemini-3-flash-preview",
    "full_response": "..."
}
```

### Deshabilitar Thought Signatures

```python
# Para respuestas sin trace (más rápido)
result = await agent.generate_with_thought_signature(
    prompt="¿Cuál es el precio de este plato?",
    include_thought_trace=False
)

# Resultado
{
    "answer": "$15.99",
    "thought_trace": None,
    "thinking_level": "STANDARD",
    "model_used": "gemini-3-flash-preview"
}
```

---

## 🎨 Visualización en el Frontend

### Componente de Thought Trace

```typescript
// frontend/src/components/ThoughtTrace.tsx

interface ThoughtTraceProps {
  trace: string | null;
  thinkingLevel: string;
}

export function ThoughtTrace({ trace, thinkingLevel }: ThoughtTraceProps) {
  if (!trace) return null;
  
  return (
    <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
      <div className="flex items-center gap-2 mb-2">
        <Brain className="w-4 h-4 text-blue-600" />
        <span className="text-sm font-medium text-gray-700">
          Thought Process ({thinkingLevel})
        </span>
      </div>
      
      <div className="text-sm text-gray-600 whitespace-pre-wrap font-mono">
        {trace}
      </div>
    </div>
  );
}
```

### Uso en Análisis

```typescript
// En AnalysisPanel.tsx
const [analysisResult, setAnalysisResult] = useState<any>(null);

const runAnalysis = async () => {
  const response = await fetch('/api/v1/analysis/bcg', {
    method: 'POST',
    body: JSON.stringify({
      menu_items: items,
      include_thought_trace: true,
      thinking_level: 'DEEP'
    })
  });
  
  const result = await response.json();
  setAnalysisResult(result);
};

return (
  <div>
    {analysisResult?.thought_trace && (
      <ThoughtTrace 
        trace={analysisResult.thought_trace}
        thinkingLevel={analysisResult.thinking_level}
      />
    )}
    
    <div className="mt-4">
      {analysisResult?.answer}
    </div>
  </div>
);
```

---

## 🔧 Integración con Agentes

### Marathon Agent

```python
# backend/app/services/orchestrator.py

class AnalysisOrchestrator:
    async def run_step_with_thought_trace(
        self,
        step_name: str,
        prompt: str
    ) -> Dict[str, Any]:
        """Ejecuta un paso con thought signature."""
        
        agent = GeminiBaseAgent()
        
        result = await agent.generate_with_thought_signature(
            prompt=prompt,
            thinking_level="DEEP",  # Marathon usa DEEP o EXHAUSTIVE
            include_thought_trace=True
        )
        
        # Guardar thought trace en checkpoint
        await self.save_checkpoint(
            step_name=step_name,
            result=result["answer"],
            thought_trace=result["thought_trace"],
            thinking_level=result["thinking_level"]
        )
        
        return result
```

### Vibe Engineering

```python
# backend/app/services/verification/vibe_agent.py

class VibeEngineeringAgent:
    async def verify_with_reasoning(
        self,
        content: str,
        quality_threshold: float = 0.85
    ) -> Dict[str, Any]:
        """Verifica calidad con thought signature."""
        
        agent = GeminiBaseAgent()
        
        prompt = f"""
        Verifica la calidad de este contenido:
        
        {content}
        
        Evalúa:
        1. Claridad
        2. Precisión
        3. Utilidad
        4. Completitud
        
        Devuelve un score de 0-1 y explica tu razonamiento.
        """
        
        result = await agent.generate_with_thought_signature(
            prompt=prompt,
            thinking_level="STANDARD",
            include_thought_trace=True
        )
        
        # El thought trace muestra CÓMO llegó al score
        return {
            "score": self._extract_score(result["answer"]),
            "reasoning": result["thought_trace"],
            "passes": self._extract_score(result["answer"]) >= quality_threshold
        }
```

---

## 📈 Beneficios

### 1. Transparencia
- El usuario ve **cómo** el modelo llegó a la conclusión
- Aumenta confianza en las recomendaciones
- Facilita debugging de respuestas incorrectas

### 2. Calidad
- Forzar al modelo a "pensar en voz alta" mejora la calidad
- Reduce alucinaciones
- Mejora razonamiento paso a paso

### 3. Diferenciación Hackathon
- Muestra capacidades avanzadas de Gemini 3
- Demuestra pensamiento agentic
- Alineado con tracks de Marathon Agent y Vibe Engineering

---

## 🎯 Casos de Uso en MenuPilot

### 1. BCG Analysis
```python
result = await agent.generate_with_thought_signature(
    prompt=f"""
    Analiza estos items según BCG matrix:
    {json.dumps(menu_items)}
    
    Ventas: {json.dumps(sales_data)}
    """,
    thinking_level="DEEP"
)

# Thought trace muestra:
# - Cómo calculó market share
# - Por qué clasificó cada item
# - Qué métricas consideró
```

### 2. Competitive Analysis
```python
result = await agent.generate_with_grounding(
    prompt=f"""
    Analiza la estrategia de estos competidores:
    {json.dumps(competitors)}
    """,
    enable_grounding=True,
    thinking_level="DEEP"
)

# Thought trace + grounding metadata:
# - Fuentes de Google Search
# - Razonamiento sobre cada competidor
# - Conclusiones estratégicas
```

### 3. Campaign Generation
```python
result = await agent.generate_with_thought_signature(
    prompt=f"""
    Genera una campaña de Instagram para:
    Restaurante: {business_name}
    Target: {target_audience}
    """,
    thinking_level="STANDARD"
)

# Thought trace muestra:
# - Análisis del target
# - Estrategia de contenido
# - Justificación de cada elemento
```

---

## 🔍 Debugging con Thought Signatures

### Ver el Razonamiento

```python
# En desarrollo, siempre incluir thought trace
if settings.debug:
    result = await agent.generate_with_thought_signature(
        prompt=prompt,
        thinking_level="DEEP",
        include_thought_trace=True
    )
    
    logger.debug(f"Thought trace:\n{result['thought_trace']}")
    logger.debug(f"Answer: {result['answer']}")
```

### Logs Estructurados

```python
logger.info(
    "analysis_complete",
    thinking_level=result["thinking_level"],
    has_thought_trace=bool(result["thought_trace"]),
    answer_length=len(result["answer"]),
    model=result["model_used"]
)
```

---

## ⚙️ Configuración

### Settings

```python
# backend/app/core/config.py

# Thought Signatures habilitadas por defecto
vibe_enable_thought_transparency: bool = True

# Niveles configurables
thinking_level_quick_temp: float = 0.3
thinking_level_quick_tokens: int = 2048
thinking_level_standard_temp: float = 0.5
thinking_level_standard_tokens: int = 4096
thinking_level_deep_temp: float = 0.7
thinking_level_deep_tokens: int = 8192
thinking_level_exhaustive_temp: float = 0.8
thinking_level_exhaustive_tokens: int = 16384
```

### Deshabilitar Globalmente

```bash
# .env
VIBE_ENABLE_THOUGHT_TRANSPARENCY=false
```

---

## 📊 Métricas

### Tracking de Uso

```python
# Agregar a usage_stats
self.usage_stats["thought_signatures_used"] = 0
self.usage_stats["thinking_levels"] = {
    "QUICK": 0,
    "STANDARD": 0,
    "DEEP": 0,
    "EXHAUSTIVE": 0
}

# Incrementar en cada uso
self.usage_stats["thought_signatures_used"] += 1
self.usage_stats["thinking_levels"][thinking_level] += 1
```

---

## ✅ Checklist de Implementación

- [x] Método `_create_thought_signature()` implementado
- [x] Método `_extract_thought_trace()` implementado
- [x] Método `_extract_answer()` implementado
- [x] Método `generate_with_thought_signature()` implementado
- [x] Integración con thinking levels configurables
- [x] Soporte para imágenes multimodales
- [ ] Componente frontend `ThoughtTrace.tsx`
- [ ] Integración en Marathon Agent
- [ ] Integración en Vibe Engineering
- [ ] Tests unitarios
- [ ] Documentación de API

---

## 🚀 Próximos Pasos

1. **Frontend Component:** Crear `ThoughtTrace.tsx` para visualización
2. **Marathon Integration:** Usar en orchestrator para checkpoints
3. **Vibe Integration:** Usar en verification loops
4. **Analytics:** Trackear uso y efectividad
5. **UI Polish:** Animaciones para mostrar "pensamiento" en tiempo real

---

**Fecha:** 2026-02-02  
**Versión:** 1.0  
**Status:** ✅ Implementado en Backend
