# 🎨 RestoPilotAI Frontend

El frontend de RestoPilotAI es una aplicación moderna construida con **Next.js 14** (App Router), diseñada para ofrecer una experiencia fluida y progresiva ("Single Page Application flow") para el análisis de menús y competidores.

## 🛠 Tech Stack

- **Framework:** Next.js 14 (React)
- **Lenguaje:** TypeScript
- **Estilos:** Tailwind CSS
- **Componentes:** Shadcn/ui (basado en Radix UI)
- **Iconos:** Lucide React
- **Estado:** React Hooks & Context

## 🚀 Configuración Local

### Prerrequisitos
- Node.js 20+
- npm o yarn

### 1. Instalación de Dependencias

```bash
npm install
# o
yarn install
```

### 2. Variables de Entorno

Crea un archivo `.env.local` en este directorio:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Ejecutar en Desarrollo

```bash
npm run dev
# o
yarn dev
```

La aplicación estará disponible en: `http://localhost:3000`

## 📂 Estructura Clave

- `app/`: Rutas y páginas (App Router).
  - `page.tsx`: Controlador principal del flujo progresivo.
- `components/`: Componentes de UI reutilizables.
  - `analysis/`: Componentes específicos del flujo de análisis (Upload, Location, Dashboard).
- `lib/`: Utilidades y configuración de cliente API.

## 🌟 Características Principales

- **Flujo Progresivo:** Interfaz vertical que guía al usuario paso a paso sin recargas.
- **Upload Multimodal:** Soporte para subir imágenes de menús y recibir feedback visual.
- **Dashboard Interactivo:** Visualización de competidores y métricas de análisis.
