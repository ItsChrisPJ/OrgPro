# 📂 OrgPro - Organizador Inteligente

OrgPro es una aplicación de escritorio híbrida y moderna diseñada para automatizar la limpieza y organización de archivos utilizando reglas locales e Inteligencia Artificial.

## ✨ Características Principales

* **⚡ Análisis Rápido (Local):** Clasifica archivos instantáneamente basándose en un diccionario de más de 120 extensiones personalizables.
* **🧠 Análisis Profundo (IA):** Integración con la API de Groq (Llama 3.1) para deducir y clasificar archivos desconocidos o sin extensión clara.
* **🪄 Desfragmentador de Nombres:** La IA analiza nombres de archivos corruptos o generados por sistema (ej. `IMG_001_final.jpg`) y sugiere nombres limpios y profesionales.
* **👻 Modo Fantasma (Segundo Plano):** La aplicación se ancla a la bandeja del sistema (reloj de Windows) y vigila una carpeta en tiempo real, auto-organizando cualquier archivo nuevo que se descargue.
* **⏪ Historial de Sesión:** Permite ver exactamente qué archivos se movieron y deshacer todos los cambios con un solo clic.
* **🎨 UI/UX Moderna:** Interfaz *Glassmorphism* con soporte para Drag & Drop y Modo Oscuro/Claro dinámico.

## 🛠️ Tecnologías Utilizadas

* **Backend:** Python 3 (Threading, Shutil, OS).
* **Frontend:** HTML5, CSS3, JavaScript (Vanilla).
* **Integración Híbrida:** PyWebview.
* **Inteligencia Artificial:** Groq API (Llama-3.1-8b-instant).
* **Sistema:** Pystray (Notificaciones y Bandeja del Sistema en Windows).

## 🚀 Instalación y Uso (Para Usuarios)

1. Descarga el ejecutable `OrgPro.exe` desde la sección de **Releases** a la derecha.
2. Ejecútalo (No requiere instalación).
3. Opcional: Ve a la configuración (⚙️) e ingresa tu API Key gratuita de [Groq Console](https://console.groq.com/keys) para habilitar las funciones de Inteligencia Artificial.

---
*Desarrollado por Chris.*
