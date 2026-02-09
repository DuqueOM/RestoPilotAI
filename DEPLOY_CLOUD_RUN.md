# 🚀 Guía de Despliegue en Google Cloud Run — RestoPilotAI

> Guía paso a paso para desplegar RestoPilotAI (Backend + Frontend) en Cloud Run.
> Optimizada para presupuesto limitado de hackathon.

## Arquitectura del Despliegue

```
┌─────────────────────────────────────────────────────┐
│                    INTERNET                          │
│                  (Jueces DevPost)                    │
└──────────┬──────────────────────┬───────────────────┘
           │                      │
           ▼                      ▼
┌─────────────────────┐  ┌─────────────────────────┐
│  Cloud Run:         │  │  Cloud Run:              │
│  FRONTEND (Next.js) │──│  BACKEND (FastAPI)       │
│  512Mi / 1 CPU      │  │  2Gi / 1 CPU             │
│  Max 2 instancias   │  │  Max 3 instancias        │
│  Puerto: dinámico   │  │  Puerto: dinámico        │
└─────────────────────┘  └──────────┬──────────────┘
                                    │
                                    ▼
                          ┌─────────────────┐
                          │ SQLite (efímero) │
                          │ + Demo Data JSON │
                          └─────────────────┘
```

**Costo estimado**: ~$0-2 USD para el período del hackathon (con min-instances=0).

---

## PRERREQUISITOS

Necesitas:
1. Una cuenta de Google Cloud (con créditos o trial gratuito de $300)
2. Un proyecto de GCP creado
3. `gcloud` CLI instalado ([instalar](https://cloud.google.com/sdk/docs/install))
4. Tu `GEMINI_API_KEY` (de https://aistudio.google.com/apikey)
5. (Opcional) Tu `GOOGLE_MAPS_API_KEY`

---

## FASE 1: Configuración Inicial de GCP (una sola vez)

### Paso 1.1: Login y selección de proyecto

```bash
# Autenticarte con Google Cloud
gcloud auth login

# Listar tus proyectos (para ver el ID)
gcloud projects list

# Seleccionar tu proyecto (reemplaza TU_PROJECT_ID)
gcloud config set project TU_PROJECT_ID
```

### Paso 1.2: Habilitar APIs necesarias

```bash
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com
```

### Paso 1.3: Crear repositorio de imágenes Docker (Artifact Registry)

```bash
gcloud artifacts repositories create restopilotai \
  --repository-format=docker \
  --location=us-central1 \
  --description="RestoPilotAI Hackathon Images"
```

### Paso 1.4: Guardar API Keys en Secret Manager (más seguro que env vars)

```bash
# Gemini API Key (OBLIGATORIO)
echo -n "TU_GEMINI_API_KEY_AQUI" | \
  gcloud secrets create GEMINI_API_KEY --data-file=-

# Google Maps API Key (OPCIONAL — para competidores y geocoding)
echo -n "TU_GOOGLE_MAPS_KEY_AQUI" | \
  gcloud secrets create GOOGLE_MAPS_API_KEY --data-file=-
```

### Paso 1.5: Dar permisos al service account de Cloud Build

```bash
# Obtener el número del proyecto
PROJECT_NUMBER=$(gcloud projects describe $(gcloud config get-value project) --format='value(projectNumber)')

# Dar permisos a Cloud Build para desplegar en Cloud Run y acceder a secretos
gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"
```

---

## FASE 2: Despliegue (Opción A — Automático con Cloud Build)

> Esta es la opción más simple. Un solo comando construye y despliega todo.

```bash
# Desde la raíz del proyecto (/home/duque_om/projects/RestoPilotAI)
gcloud builds submit --config cloudbuild.yaml \
  --substitutions=_REGION=us-central1
```

⏱️ **Esto tarda ~10-15 minutos** la primera vez (construye 2 imágenes Docker).

Al terminar, verás las URLs de tus servicios. Si hay errores, sigue la Opción B (manual).

---

## FASE 2: Despliegue (Opción B — Manual paso a paso)

> Usa esto si Cloud Build falla o si quieres entender cada paso.

### Paso 2.1: Construir y subir imagen del BACKEND

```bash
# Obtener variables
export PROJECT_ID=$(gcloud config get-value project)
export REGION=us-central1

# Construir la imagen del backend en la nube
gcloud builds submit ./backend \
  --tag ${REGION}-docker.pkg.dev/${PROJECT_ID}/restopilotai/restopilotai-backend:v1
```

⏱️ Esto tarda ~8-10 minutos (PyTorch CPU-only es grande pero no tanto como la versión CUDA).

### Paso 2.2: Desplegar el BACKEND en Cloud Run

```bash
gcloud run deploy restopilotai-backend \
  --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/restopilotai/restopilotai-backend:v1 \
  --region ${REGION} \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 1 \
  --timeout 600 \
  --concurrency 10 \
  --max-instances 3 \
  --min-instances 0 \
  --set-env-vars "APP_ENV=production,LOG_LEVEL=INFO,CORS_ORIGINS=*" \
  --set-secrets "GEMINI_API_KEY=GEMINI_API_KEY:latest,GOOGLE_MAPS_API_KEY=GOOGLE_MAPS_API_KEY:latest"
```

📋 **Anota la URL del backend** que aparece al final, ejemplo:
`https://restopilotai-backend-XXXXX-uc.a.run.app`

### Paso 2.3: Verificar que el backend funciona

```bash
# Reemplaza con TU URL del backend
curl https://restopilotai-backend-XXXXX-uc.a.run.app/health
```

Deberías ver: `{"status":"healthy","environment":"production","gemini_configured":true}`

### Paso 2.4: Construir y subir imagen del FRONTEND

```bash
# IMPORTANTE: usa la URL REAL de tu backend del paso 2.2
export BACKEND_URL=https://restopilotai-backend-XXXXX-uc.a.run.app

gcloud builds submit ./frontend \
  --tag ${REGION}-docker.pkg.dev/${PROJECT_ID}/restopilotai/restopilotai-frontend:v1 \
  --build-arg NEXT_PUBLIC_API_URL=${BACKEND_URL}
```

⚠️ **Nota**: `--build-arg` en `gcloud builds submit` no funciona directamente. Usa este método alternativo:

```bash
# Crear un cloudbuild temporal solo para el frontend
cat > /tmp/frontend-build.yaml << 'EOF'
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '--build-arg'
      - 'NEXT_PUBLIC_API_URL=${_BACKEND_URL}'
      - '-t'
      - '${_REGION}-docker.pkg.dev/$PROJECT_ID/restopilotai/restopilotai-frontend:v1'
      - '.'
images:
  - '${_REGION}-docker.pkg.dev/$PROJECT_ID/restopilotai/restopilotai-frontend:v1'
EOF

gcloud builds submit ./frontend \
  --config /tmp/frontend-build.yaml \
  --substitutions="_BACKEND_URL=${BACKEND_URL},_REGION=${REGION}"
```

### Paso 2.5: Desplegar el FRONTEND en Cloud Run

```bash
gcloud run deploy restopilotai-frontend \
  --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/restopilotai/restopilotai-frontend:v1 \
  --region ${REGION} \
  --platform managed \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --timeout 60 \
  --concurrency 80 \
  --max-instances 2 \
  --min-instances 0
```

📋 **Esta URL es la que pones en DevPost**, ejemplo:
`https://restopilotai-frontend-XXXXX-uc.a.run.app`

### Paso 2.6: Verificar el despliegue completo

```bash
# Frontend debe cargar la página
curl -s https://restopilotai-frontend-XXXXX-uc.a.run.app | head -20

# Backend health
curl https://restopilotai-backend-XXXXX-uc.a.run.app/health

# Demo data debe estar disponible
curl https://restopilotai-backend-XXXXX-uc.a.run.app/api/v1/demo/session
```

---

## FASE 3: Configuración de Ahorro de Costos

### Lo que YA está configurado para ahorro:

| Setting | Valor | Efecto |
|---------|-------|--------|
| `--min-instances 0` | Backend y Frontend | **$0 cuando nadie usa la app** |
| `--max-instances 3/2` | Backend 3, Frontend 2 | Evita gastos por picos de tráfico |
| `--cpu 1` | Ambos servicios | Mínimo necesario |
| `--memory 2Gi/512Mi` | Backend/Frontend | Mínimo para que funcione |
| CPU allocation | Request-based (default) | Solo cobra mientras procesa |

### Cold Start (arranque en frío):
- **Primera visita** de un juez tras período de inactividad: ~15-25 segundos de espera
- **Visitas siguientes** (mientras el contenedor está vivo): <1 segundo
- El contenedor se mantiene vivo ~15 min sin tráfico

### Para reducir costos aún más (después del hackathon):

```bash
# Eliminar los servicios cuando ya no los necesites
gcloud run services delete restopilotai-backend --region us-central1
gcloud run services delete restopilotai-frontend --region us-central1

# Eliminar las imágenes Docker
gcloud artifacts repositories delete restopilotai --location=us-central1
```

---

## FASE 4: Troubleshooting

### Error: "Container failed to start"
```bash
# Ver logs del servicio
gcloud run services logs read restopilotai-backend --region us-central1 --limit 50
```
Causa común: falta la GEMINI_API_KEY o no se encontró un módulo Python.

### Error: "Memory limit exceeded"
Sube la memoria del backend:
```bash
gcloud run services update restopilotai-backend --memory 4Gi --region us-central1
```

### Error: "Request timeout"
El Gemini Marathon Agent puede tardar. El timeout ya está en 600s, pero si necesitas más:
```bash
gcloud run services update restopilotai-backend --timeout 900 --region us-central1
```

### Demo data no aparece (404)
Verifica que los archivos JSON están en la imagen:
```bash
# Reconstruir la imagen del backend
gcloud builds submit ./backend \
  --tag ${REGION}-docker.pkg.dev/${PROJECT_ID}/restopilotai/restopilotai-backend:v2

# Redesplegar
gcloud run deploy restopilotai-backend \
  --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/restopilotai/restopilotai-backend:v2 \
  --region us-central1
```

### Frontend no conecta con backend
Verifica que `NEXT_PUBLIC_API_URL` apunta a la URL correcta del backend:
```bash
gcloud run services describe restopilotai-frontend --region us-central1 \
  --format='value(spec.template.spec.containers[0].env)'
```

---

## Resumen: Lo que pones en DevPost

Una vez desplegado, tendrás:

- **URL pública del frontend**: `https://restopilotai-frontend-XXXXX-uc.a.run.app`
- **URL del backend API**: `https://restopilotai-backend-XXXXX-uc.a.run.app/docs`

Pon la URL del frontend en tu submission de DevPost y en el README con un badge:

```markdown
[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-Cloud_Run-4285F4?style=for-the-badge)](https://restopilotai-frontend-XXXXX-uc.a.run.app)
```
