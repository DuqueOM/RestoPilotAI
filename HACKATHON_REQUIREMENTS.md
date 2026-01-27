# Gemini 3 Hackathon - Requisitos Oficiales

## 📋 Requisitos del Proyecto

### Uso Obligatorio de Gemini 3 API

**El proyecto DEBE usar la API de Gemini 3** según las reglas oficiales del hackathon:
- URL: https://gemini3.devpost.com/
- Período: 17 de diciembre 2025 - 9 de febrero 2026

### Modelos Oficiales de Gemini 3

El código debe usar uno de estos modelos:

1. **`gemini-3-pro-preview`** ⭐ Recomendado para MenuPilot
   - Mejor modelo para razonamiento multimodal complejo
   - Soporta: Texto, Imagen, Video, Audio, PDF
   - Context window: 1,048,576 tokens
   - Características: Function calling, Code execution, Thinking, Structured outputs

2. **`gemini-3-flash-preview`** ✅ Actualmente en uso
   - Más rápido y económico
   - Mismas capacidades que Pro
   - Ideal para aplicaciones de producción

3. **`gemini-3-pro-image-preview`**
   - Para generación de imágenes (Nano Banana Pro)
   - No aplicable a MenuPilot

## 🔑 Configuración de API Key

### Obtener API Key

1. **AI Studio (Free Tier)**: https://aistudio.google.com/apikey
   - Límites gratuitos por día/minuto
   - Suficiente para desarrollo y testing

2. **Google Cloud (Paid Tier)**:
   - Mayor cuota y límites
   - Requiere billing habilitado
   - Ver: https://ai.google.dev/gemini-api/docs/rate-limits

### Límites del Free Tier

Según la documentación oficial:
- **Requests por día**: Variable según modelo
- **Requests por minuto**: ~15 RPM
- **Tokens por minuto**: Variable
- **Cuota se resetea**: Medianoche Pacific Time

### Verificar Cuota Actual

```bash
# Desde el proyecto
cd backend && source venv/bin/activate && cd ..
python3 test_gemini_api.py
```

## ⚙️ Configuración Actual de MenuPilot

### Archivo: `backend/app/services/gemini_agent.py`

```python
MODEL_NAME = "gemini-3-flash-preview"  # ✅ CORRECTO para hackathon
```

### Variables de Entorno: `backend/.env`

```bash
GEMINI_API_KEY=AIzaSy...  # Tu API key aquí
```

## 🚨 Problemas Comunes

### Error 429: RESOURCE_EXHAUSTED

**Causa**: Cuota de API agotada

**Soluciones**:

1. **Esperar reset de cuota** (medianoche PT)
2. **Crear nueva API key** en AI Studio
3. **Habilitar billing** en Google Cloud para mayor cuota
4. **Usar API key del hackathon** si proporcionan una especial

### Error 503: UNAVAILABLE

**Causa**: Modelo sobrecargado temporalmente

**Solución**: Esperar 20-30 segundos y reintentar

## 📚 Recursos Oficiales

### Documentación
- **Gemini 3 Guide**: https://ai.google.dev/gemini-api/docs/gemini-3
- **Models Reference**: https://ai.google.dev/gemini-api/docs/models
- **Rate Limits**: https://ai.google.dev/gemini-api/docs/rate-limits
- **Pricing**: https://ai.google.dev/gemini-api/docs/pricing

### Hackathon
- **Overview**: https://gemini3.devpost.com/
- **Resources**: https://gemini3.devpost.com/resources
- **Rules**: https://gemini3.devpost.com/rules

### AI Studio
- **Build Tab**: https://aistudio.google.com/
- **Gallery**: https://aistudio.google.com/apps?source=showcase&showcaseTag=gemini-3
- **API Keys**: https://aistudio.google.com/apikey
- **Usage Dashboard**: https://aistudio.google.com/usage

## 🎯 Características de Gemini 3 Usadas en MenuPilot

### 1. Multimodal Understanding
- ✅ Extracción de menús desde PDFs e imágenes
- ✅ Análisis de texto y estructura visual

### 2. Function Calling
- ✅ Herramientas definidas para extracción estructurada
- ✅ Respuestas en formato JSON

### 3. Thought Signatures (Agentic)
- ✅ Razonamiento transparente antes de ejecutar tareas
- ✅ Auto-verificación de análisis

### 4. Structured Outputs
- ✅ Schemas Pydantic para validación
- ✅ Respuestas consistentes y tipadas

### 5. Long Context Window
- ✅ 1M tokens para procesar documentos grandes
- ✅ Análisis de múltiples menús y datos de ventas

## ✅ Checklist de Cumplimiento

- [x] Usa API de Gemini 3 (`gemini-3-flash-preview`)
- [x] Implementa características avanzadas (multimodal, function calling)
- [x] Proyecto original creado durante el período del hackathon
- [x] Incluye documentación y testing
- [x] Código disponible en repositorio público
- [ ] API key con cuota disponible (PENDIENTE)
- [ ] Video demo del proyecto funcionando
- [ ] Submission en Devpost

## 🔧 Próximos Pasos

1. **Resolver problema de cuota**:
   - Obtener nueva API key con cuota disponible
   - O esperar reset de cuota actual

2. **Probar extracción de menú**:
   ```bash
   # Subir PDF desde frontend
   http://localhost:3000
   ```

3. **Preparar submission**:
   - Video demo (2-3 minutos)
   - Descripción del proyecto
   - Screenshots
   - Link a repositorio
   - Testing instructions

## 📞 Soporte

Si tienes problemas con la API:
- **Forum**: https://discuss.ai.google.dev/
- **Discord**: https://discord.com/invite/HP4BhW3hnp
- **Devpost**: https://gemini3.devpost.com/forum_topics
