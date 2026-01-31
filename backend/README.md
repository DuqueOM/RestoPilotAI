# 🧠 MenuPilot Backend

El backend de MenuPilot es una API robusta construida con **FastAPI** y **Python 3.11**, diseñada para orquestar análisis de inteligencia de mercado utilizando **Google Gemini 3 Multimodal** y **Google Places API**.

## 🛠 Tech Stack

- **Framework:** FastAPI
- **Lenguaje:** Python 3.11
- **IA Multimodal:** Google Gemini 3 (Flash Preview)
- **Datos Geográficos:** Google Places API (New) & Geocoding API
- **Base de Datos:** PostgreSQL (con `asyncpg`)
- **Cache & Cola:** Redis
- **Servidor:** Uvicorn

## 🚀 Configuración Local

### Prerrequisitos
- Python 3.11+
- PostgreSQL
- Redis

### 1. Instalación de Dependencias

Se recomienda usar un entorno virtual:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

pip install -r requirements.txt
```

### 2. Variables de Entorno

Copia el archivo de ejemplo y configura tus claves:

```bash
cp .env.example .env
```

Asegúrate de configurar:
- `GEMINI_API_KEY`: Para el modelo `gemini-3-flash-preview`.
- `GOOGLE_PLACES_API_KEY`: Para datos de ubicación e imágenes.
- `DATABASE_URL`: Conexión a Postgres.
- `REDIS_URL`: Conexión a Redis.

### 3. Ejecutar el Servidor

```bash
# Modo desarrollo con recarga automática
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

La documentación interactiva (Swagger UI) estará disponible en: `http://localhost:8000/docs`

## 🧪 Tests

Para verificar la conectividad de las APIs:

```bash
python ../scripts/test_apis.py
```

## 📂 Estructura Clave

- `app/api/`: Endpoints de la API.
- `app/core/`: Configuración global y manejo de base de datos.
- `app/services/intelligence/`: Lógica de negocio (Geocoding, Places, Enriquecimiento).
- `app/services/gemini/`: Agentes y orquestación de IA.
