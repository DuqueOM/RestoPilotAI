# Marathon Agent - Guía de Ejecución de Tareas Largas

## 🎯 Qué es Marathon Agent

**Marathon Agent** es un patrón de IA agentic que permite ejecutar tareas de larga duración (multi-hora) con capacidades de checkpoint, recovery y progreso en tiempo real.

**TRACK DEL HACKATHON:** Este es uno de los tracks principales de Gemini 3 Hackathon que demuestra ejecución resiliente de tareas complejas.

---

## 🚀 Implementación en MenuPilot

### Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    MARATHON AGENT SYSTEM                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. TASK INITIALIZATION                                      │
│     └─> Check for existing checkpoint                       │
│     └─> Load state or start fresh                           │
│                                                              │
│  2. PIPELINE EXECUTION                                       │
│     ├─> Execute step with retry logic                       │
│     ├─> Save checkpoint after each step                     │
│     ├─> Send progress via WebSocket                         │
│     └─> Handle errors gracefully                            │
│                                                              │
│  3. CHECKPOINT MANAGEMENT                                    │
│     ├─> Redis: Persistent storage (preferred)               │
│     ├─> Fallback: In-memory storage                         │
│     ├─> TTL: 1 hora                                         │
│     └─> State snapshot for debugging                        │
│                                                              │
│  4. RECOVERY SYSTEM                                          │
│     ├─> Detect failures                                     │
│     ├─> Load last checkpoint                                │
│     ├─> Resume from failed step                             │
│     └─> Exponential backoff retry                           │
│                                                              │
│  5. REAL-TIME UPDATES                                        │
│     └─> WebSocket: /ws/marathon/{task_id}                   │
│     └─> Progress, status, errors                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Uso del Marathon Agent

### 1. Ejecución de Tarea Larga

**Método:** `execute_long_running_task()`

```python
from app.services.gemini.marathon_agent import MarathonAgent

# Inicializar agente
marathon_agent = MarathonAgent()

# Definir pipeline de pasos
task_config = {
    "steps": [
        {
            "name": "extract_menu",
            "function": extract_menu_async,
            "timeout": 120,
            "retryable": True
        },
        {
            "name": "analyze_bcg",
            "function": analyze_bcg_async,
            "timeout": 180,
            "retryable": True
        },
        {
            "name": "competitive_intel",
            "function": competitive_intel_async,
            "timeout": 300,
            "retryable": True
        },
        {
            "name": "generate_campaigns",
            "function": generate_campaigns_async,
            "timeout": 240,
            "retryable": True
        }
    ]
}

# Ejecutar con checkpoints
result = await marathon_agent.execute_long_running_task(
    task_id="analysis_123",
    task_config=task_config,
    progress_callback=my_progress_handler
)

# Resultado
{
    "task_id": "analysis_123",
    "status": "completed",
    "results": {
        "extract_menu": {...},
        "analyze_bcg": {...},
        "competitive_intel": {...},
        "generate_campaigns": {...}
    },
    "total_steps": 4
}
```

---

## 🔄 Checkpoints Persistentes

### Redis Storage (Recomendado)

**Configuración:**
```python
# backend/app/core/config.py
redis_url: str = "redis://localhost:6379"

# Marathon Agent detecta Redis automáticamente
marathon_agent = MarathonAgent()
# storage_backend: "redis"
```

**Estructura del Checkpoint:**
```json
{
    "task_id": "analysis_123",
    "step": 2,
    "results": {
        "extract_menu": {...},
        "analyze_bcg": {...}
    },
    "timestamp": "2026-02-02T18:30:00Z",
    "state_snapshot": {
        "storage_backend": "redis",
        "checkpoint_interval": 60,
        "max_retries": 3,
        "enable_recovery": true
    }
}
```

**TTL:** 1 hora (3600 segundos)

### Fallback: In-Memory Storage

Si Redis no está disponible, usa almacenamiento en memoria:
```python
# Automático si Redis falla
marathon_agent = MarathonAgent()
# storage_backend: "memory"
# ⚠️ Checkpoints se pierden si el proceso se reinicia
```

---

## 🔧 Recovery de Fallos

### Detección Automática

El Marathon Agent detecta fallos y guarda el estado de error:

```python
# Error guardado automáticamente
{
    "task_id": "analysis_123",
    "step": 2,
    "error": "Timeout after 180 seconds",
    "timestamp": "2026-02-02T18:35:00Z"
}
```

### Recovery Manual

```python
# Recuperar tarea fallida
marathon_agent = MarathonAgent()

# Cargar último checkpoint
checkpoint = await marathon_agent._load_checkpoint("analysis_123")

if checkpoint:
    # Reanudar desde el paso fallido
    result = await marathon_agent.execute_long_running_task(
        task_id="analysis_123",
        task_config=task_config,
        progress_callback=my_progress_handler
    )
    # Continúa desde step 2 automáticamente
```

### Retry con Exponential Backoff

Cada paso se reintenta automáticamente:

```python
# Configuración de retry
max_retries = 3  # De settings
backoff_formula = 2 ** attempt  # Exponential

# Intentos:
# Attempt 1: Inmediato
# Attempt 2: Espera 2 segundos
# Attempt 3: Espera 4 segundos
# Attempt 4: Falla definitivamente
```

---

## 📡 WebSocket para Progreso en Tiempo Real

### Endpoint WebSocket

**URL:** `ws://localhost:8000/api/v1/ws/marathon/{task_id}`

### Conexión desde Frontend

```typescript
// Frontend: Connect to WebSocket
const taskId = "analysis_123";
const ws = new WebSocket(`ws://localhost:8000/api/v1/ws/marathon/${taskId}`);

ws.onopen = () => {
    console.log("Connected to Marathon Agent");
};

ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    
    if (message.type === "progress_update") {
        const data = message.data;
        console.log(`Progress: ${(data.progress * 100).toFixed(0)}%`);
        console.log(`Current step: ${data.current_step}`);
        console.log(`Status: ${data.status}`);
        
        // Update UI
        updateProgressBar(data.progress);
        updateCurrentStep(data.current_step_name);
    }
};

ws.onerror = (error) => {
    console.error("WebSocket error:", error);
};

ws.onclose = () => {
    console.log("WebSocket closed");
};

// Keep-alive ping
setInterval(() => {
    if (ws.readyState === WebSocket.OPEN) {
        ws.send("ping");
    }
}, 30000);
```

### Mensajes de Progreso

```json
{
    "type": "progress_update",
    "data": {
        "task_id": "analysis_123",
        "progress": 0.5,
        "current_step": "analyze_bcg",
        "status": "running",
        "step_index": 2,
        "total_steps": 4
    },
    "timestamp": "2026-02-02T18:32:00Z"
}
```

---

## 🌐 API Endpoints

### POST `/api/v1/marathon/start`

Inicia una tarea Marathon.

**Request:**
```json
{
    "task_type": "full_analysis",
    "session_id": "optional_session_id",
    "input_data": {
        "sales_csv": "path/to/sales.csv",
        "menu_images": ["path/to/menu1.jpg"]
    },
    "enable_checkpoints": true,
    "checkpoint_interval_seconds": 60,
    "max_retries_per_step": 3
}
```

**Response:**
```json
{
    "task_id": "analysis_123",
    "status": "started"
}
```

### GET `/api/v1/marathon/status/{task_id}`

Obtiene el estado actual de una tarea.

**Response:**
```json
{
    "task_id": "analysis_123",
    "status": "running",
    "progress": 0.5,
    "current_step": 2,
    "total_steps": 4,
    "current_step_name": "analyze_bcg",
    "started_at": "2026-02-02T18:30:00Z",
    "steps": [
        {
            "step_id": "step_0",
            "name": "extract_menu",
            "status": "completed",
            "completed_at": "2026-02-02T18:31:00Z"
        },
        {
            "step_id": "step_1",
            "name": "analyze_bcg",
            "status": "running",
            "started_at": "2026-02-02T18:31:30Z"
        }
    ],
    "checkpoints": [...],
    "can_recover": false
}
```

### POST `/api/v1/marathon/recover/{task_id}`

Recupera una tarea fallida desde el último checkpoint.

**Response:**
```json
{
    "task_id": "analysis_123",
    "status": "recovering"
}
```

### POST `/api/v1/marathon/cancel/{task_id}`

Cancela una tarea en ejecución.

**Response:**
```json
{
    "status": "cancelled"
}
```

---

## 🔗 Integración con el Workflow

### Análisis Completo con Marathon

```python
from app.services.gemini.marathon_agent import MarathonAgent
from app.services.orchestrator import orchestrator

# Inicializar Marathon Agent
marathon_agent = MarathonAgent()

# Inyectar WebSocket manager
from app.api.routes.marathon import manager
marathon_agent.set_websocket_manager(manager)

# Definir pipeline completo
async def run_full_analysis_marathon(session_id: str):
    """Pipeline completo con Marathon Agent."""
    
    task_config = {
        "steps": [
            {
                "name": "menu_extraction",
                "function": lambda ctx: orchestrator.run_stage(
                    session_id, "MENU_EXTRACTION"
                )
            },
            {
                "name": "bcg_analysis",
                "function": lambda ctx: orchestrator.run_stage(
                    session_id, "BCG_ANALYSIS"
                )
            },
            {
                "name": "competitive_intel",
                "function": lambda ctx: orchestrator.run_stage(
                    session_id, "COMPETITOR_ENRICHMENT"
                )
            },
            {
                "name": "sentiment_analysis",
                "function": lambda ctx: orchestrator.run_stage(
                    session_id, "SENTIMENT_ANALYSIS"
                )
            },
            {
                "name": "campaign_generation",
                "function": lambda ctx: orchestrator.run_stage(
                    session_id, "CAMPAIGN_GENERATION"
                )
            }
        ]
    }
    
    result = await marathon_agent.execute_long_running_task(
        task_id=session_id,
        task_config=task_config
    )
    
    return result
```

### Competitive Intelligence Marathon

```python
async def run_competitive_marathon(restaurant_name: str, location: str):
    """Análisis competitivo profundo con Marathon."""
    
    task_config = {
        "steps": [
            {
                "name": "identify_competitors",
                "function": lambda ctx: identify_competitors_async(location)
            },
            {
                "name": "enrich_competitors",
                "function": lambda ctx: enrich_all_competitors(
                    ctx["identify_competitors"]["competitors"]
                )
            },
            {
                "name": "analyze_menus",
                "function": lambda ctx: analyze_competitor_menus(
                    ctx["enrich_competitors"]["enriched"]
                )
            },
            {
                "name": "price_intelligence",
                "function": lambda ctx: analyze_pricing(
                    ctx["analyze_menus"]["menus"]
                )
            },
            {
                "name": "strategic_recommendations",
                "function": lambda ctx: generate_strategy(ctx)
            }
        ]
    }
    
    result = await marathon_agent.execute_long_running_task(
        task_id=f"competitive_{restaurant_name}",
        task_config=task_config
    )
    
    return result
```

---

## ⚙️ Configuración

### Settings

```python
# backend/app/core/config.py

# Marathon Agent Configuration
marathon_checkpoint_interval: int = 60  # Guardar cada 60 segundos
marathon_max_retries_per_step: int = 3  # Reintentos por paso
marathon_enable_recovery: bool = True  # Recuperación habilitada
marathon_enable_checkpoints: bool = True  # Checkpoints habilitados
marathon_max_task_duration: int = 3600  # 1 hora máximo por tarea

# Redis para checkpoints
redis_url: str = "redis://localhost:6379"
```

### Variables de Entorno

```bash
# .env
MARATHON_CHECKPOINT_INTERVAL=60
MARATHON_MAX_RETRIES_PER_STEP=3
MARATHON_ENABLE_RECOVERY=true
MARATHON_ENABLE_CHECKPOINTS=true
MARATHON_MAX_TASK_DURATION=3600
REDIS_URL=redis://localhost:6379
```

---

## 📈 Casos de Uso

### 1. Análisis de 50 Competidores

```python
# Tarea larga: ~30 minutos
task_config = {
    "steps": [
        {"name": f"analyze_competitor_{i}", "function": analyze_competitor}
        for i in range(50)
    ]
}

result = await marathon_agent.execute_long_running_task(
    task_id="competitive_50",
    task_config=task_config
)
```

### 2. Procesamiento de 100 Fotos de Platos

```python
# Tarea larga: ~20 minutos
task_config = {
    "steps": [
        {"name": f"analyze_photo_{i}", "function": analyze_dish_photo}
        for i in range(100)
    ]
}

result = await marathon_agent.execute_long_running_task(
    task_id="photos_100",
    task_config=task_config
)
```

### 3. Generación de 20 Variaciones de Campaña

```python
# Tarea larga: ~15 minutos
task_config = {
    "steps": [
        {"name": f"campaign_variant_{i}", "function": generate_campaign_variant}
        for i in range(20)
    ]
}

result = await marathon_agent.execute_long_running_task(
    task_id="campaigns_20",
    task_config=task_config
)
```

---

## 🎯 Beneficios

### Sin Marathon Agent
- ❌ Timeout después de 5 minutos
- ❌ Se pierde todo el progreso si falla
- ❌ No hay visibilidad del progreso
- ❌ No se puede recuperar de errores
- ❌ Bloquea el servidor

### Con Marathon Agent
- ✅ Ejecuta tareas de horas
- ✅ Checkpoints cada 60 segundos
- ✅ Progreso en tiempo real vía WebSocket
- ✅ Recovery automático de fallos
- ✅ Ejecución en background

---

## 🔍 Monitoring y Debugging

### Ver Estado de Tarea

```python
# Obtener estado actual
status = await marathon_agent.get_task_status("analysis_123")

print(f"Status: {status['status']}")
print(f"Current step: {status['current_step']}")
print(f"Has checkpoint: {status['has_checkpoint']}")
```

### Ver Checkpoints en Redis

```bash
# CLI de Redis
redis-cli

# Listar checkpoints
KEYS checkpoint:*

# Ver checkpoint específico
GET checkpoint:analysis_123

# Ver error si existe
GET error:analysis_123
```

### Logs

```python
# Marathon Agent usa loguru
logger.info("Checkpoint saved to Redis: analysis_123 step 2")
logger.warning("Failed to send WebSocket update: Connection closed")
logger.error("Failed to save checkpoint for analysis_123: Redis timeout")
```

---

## ✅ Checklist de Implementación

- [x] Marathon Agent con checkpoints persistentes
- [x] Redis storage con fallback a memoria
- [x] WebSocket para progreso en tiempo real
- [x] ConnectionManager para múltiples clientes
- [x] Recovery de fallos con retry exponencial
- [x] API endpoints (start, status, recover, cancel)
- [x] Integración con settings
- [x] State snapshots para debugging
- [x] Documentación completa
- [ ] Tests unitarios
- [ ] Integración en frontend
- [ ] Métricas y analytics

---

## 🚀 Próximos Pasos

1. **Frontend Integration:** Componente de progreso con WebSocket
2. **Advanced Recovery:** Recovery selectivo por paso
3. **Parallel Execution:** Ejecutar pasos en paralelo cuando sea posible
4. **Priority Queue:** Priorizar tareas críticas
5. **Cost Tracking:** Trackear costo de tokens por tarea

---

**Fecha:** 2026-02-02  
**Versión:** 2.0  
**Status:** ✅ Implementado con Checkpoints Persistentes y WebSocket
