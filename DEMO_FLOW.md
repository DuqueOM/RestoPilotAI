# 🎭 RestoPilotAI Demo - Flujo Completo

## 📋 Flujo Correcto del Demo

### 1️⃣ Cargar el Demo
1. Ir a la página principal: `http://localhost:3000`
2. Hacer clic en **"Try Demo"**
3. Esto carga la sesión `margarita-pinta-demo-001` con:
   - 137 items del menú
   - 63,609 registros de ventas
   - Datos pre-cargados del restaurante "Margarita Pinta"

### 2️⃣ Ejecutar el Análisis (OPCIONAL - Ya está completado)
La sesión demo **ya tiene un análisis completado**. Si quieres ejecutar uno nuevo:

1. En la página de análisis: `/analysis/margarita-pinta-demo-001`
2. Hacer clic en **"Start Full Analysis"**
3. El pipeline ejecutará automáticamente:
   - ✅ BCG Classification (~30 segundos)
   - ✅ Sales Prediction (~10 minutos con Vibe Engineering)
   - ✅ Campaign Generation (~40 segundos)
   - ✅ Strategic Verification (~15 segundos)
   - ✅ Final Verification (~20 segundos)

**Duración total: ~12 minutos**

### 3️⃣ Ver los Resultados del Análisis

**IMPORTANTE:** La página "Analysis Dashboard" solo muestra el **progreso del pipeline**, NO los resultados finales.

Para ver los resultados, navega a las siguientes pestañas en el menú superior:

#### 📊 BCG Matrix
- **URL:** `/analysis/margarita-pinta-demo-001/bcg`
- **Contenido:**
  - Matriz BCG con clasificación de productos
  - Stars, Cash Cows, Question Marks, Dogs
  - Métricas de crecimiento y participación de mercado
  - Visualización interactiva de la matriz

#### 📈 Predictions
- **URL:** `/analysis/margarita-pinta-demo-001/predictions`
- **Contenido:**
  - Predicciones de ventas para cada producto
  - 3 escenarios: Baseline, Promotion, Premium
  - Predicciones diarias para los próximos 7 días
  - Métricas del modelo (MAE, RMSE)

#### 🎯 Campaigns
- **URL:** `/analysis/margarita-pinta-demo-001/campaigns`
- **Contenido:**
  - 3 campañas de marketing generadas
  - Estrategias específicas por producto
  - Copy publicitario
  - Prompts para generación de imágenes

#### 🍽️ Menu
- **URL:** `/analysis/margarita-pinta-demo-001/menu`
- **Contenido:**
  - Lista completa de 137 items del menú
  - Precios, categorías, descripciones
  - Filtros y búsqueda

#### 🎯 Competitors
- **URL:** `/analysis/margarita-pinta-demo-001/competitors`
- **Contenido:**
  - Análisis de competidores
  - Comparación de precios
  - Insights competitivos

#### 💭 Sentiment
- **URL:** `/analysis/margarita-pinta-demo-001/sentiment`
- **Contenido:**
  - Análisis de sentimiento de reviews
  - Tendencias de opinión
  - Productos mejor/peor valorados

### 4️⃣ Pestañas de la Página de Análisis

Dentro de `/analysis/margarita-pinta-demo-001`, hay 3 pestañas:

#### Pipeline Progress
- Muestra el estado actual del pipeline
- Progreso en tiempo real
- Duración y ETA
- **NO muestra resultados finales**

#### Quality Verification
- Muestra datos de Vibe Engineering
- Verificación de calidad del análisis
- Iteraciones de mejora
- **Nota:** Solo se llena si se ejecuta un nuevo análisis con auto-verify activado

#### Checkpoints
- Lista de checkpoints guardados durante el pipeline
- Permite recuperar el análisis desde un punto específico
- Útil para debugging

## 🔧 Problemas Conocidos y Soluciones

### ❌ "ETA: Calculating..." no cambia
**Causa:** El cálculo de ETA requiere datos de progreso histórico.
**Solución:** Esto es normal durante las primeras etapas. El ETA se actualiza después del primer checkpoint.

### ❌ "No verification data available yet"
**Causa:** Los datos de verificación solo se generan durante un análisis nuevo con auto-verify activado.
**Solución:** Si quieres ver datos de verificación, ejecuta un nuevo análisis con "Auto-Verification" activado.

### ❌ Al cambiar de pestaña se pierde el "Analysis Dashboard"
**Causa:** Las pestañas del menú superior son **páginas diferentes**, no tabs dentro de Analysis Dashboard.
**Solución:** Esto es el comportamiento esperado. Cada pestaña es una vista independiente:
- **Overview** → Dashboard principal
- **Creative Studio** → Generación de contenido visual
- **Menu** → Vista del menú
- **BCG Matrix** → Resultados del análisis BCG
- **Predictions** → Resultados de predicciones
- **Campaigns** → Campañas generadas

Para volver al Analysis Dashboard, haz clic en **"Overview"** en el menú superior.

## 🎯 Flujo Recomendado para el Demo

1. **Cargar Demo** → Botón "Try Demo" en home
2. **Ver Overview** → `/analysis/margarita-pinta-demo-001` (muestra el pipeline completado)
3. **Ver BCG Matrix** → Click en pestaña "BCG Matrix" para ver clasificación de productos
4. **Ver Predictions** → Click en pestaña "Predictions" para ver predicciones de ventas
5. **Ver Campaigns** → Click en pestaña "Campaigns" para ver campañas generadas
6. **(Opcional) Ejecutar nuevo análisis** → Volver a Overview y click en "Start Full Analysis"

## 📊 Datos del Demo Pre-cargado

El demo `margarita-pinta-demo-001` incluye:
- ✅ **137 items del menú** (Bebidas, Platos, Postres)
- ✅ **63,609 registros de ventas** (datos históricos)
- ✅ **Análisis BCG completado** (clasificación de productos)
- ✅ **Predicciones de ventas** (3 escenarios × 137 productos × 7 días)
- ✅ **3 campañas de marketing** generadas con IA
- ✅ **Verificación estratégica** completada

## 🚀 Comandos Útiles

### Reiniciar el backend
```bash
# Matar proceso en puerto 8000
lsof -ti:8000 | xargs kill -9

# Iniciar backend
cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8000
```

### Ver logs del pipeline
```bash
# Ver estado del orchestrator
curl http://localhost:8000/api/v1/marathon/status/margarita-pinta-demo-001 | jq

# Ver datos de la sesión
curl http://localhost:8000/api/v1/sessions/margarita-pinta-demo-001 | jq
```

### Verificar archivos de datos
```bash
# Estado del orchestrator
cat backend/data/orchestrator_states/margarita-pinta-demo-001.json | jq '.current_stage'

# Sesión de negocio
cat backend/data/sessions/margarita-pinta-demo-001.json | jq '.session_id'
```

## 💡 Notas Importantes

1. **El Analysis Dashboard NO muestra resultados finales** - Solo muestra el progreso del pipeline
2. **Los resultados están en las otras pestañas** - BCG, Predictions, Campaigns, etc.
3. **El demo ya está completado** - No necesitas ejecutar el análisis de nuevo
4. **Cambiar de pestaña es normal** - Cada pestaña es una página diferente
5. **ETA puede mostrar "Calculating..."** - Esto es normal hasta que haya suficientes datos de progreso
