<h1 align="center">📁 OrgPro v1.6 - Smart AI Update</h1>

<p align="center">
  <i>Una aplicación de escritorio híbrida y moderna diseñada para automatizar la limpieza y organización de tus archivos utilizando reglas locales e Inteligencia Artificial.</i>
</p>

---

## ✨ Novedades en la v1.6
* 🧠 **Analizador de Contenido (Deep Scan):** OrgPro ya no se limita al nombre del archivo. Al activar esta opción, lee el interior de tus documentos de texto y código (`.txt`, `.md`, `.csv`, `.log`, etc.), extrae el contexto real y se lo envía a la IA para una precisión de clasificación milimétrica.
* 🎛️ **Control de Creatividad (IA Temperature):** Ajusta cómo piensa la IA. Usa el modo "Estricto" para agrupar todo en categorías globales (Documentos, Imágenes) o el modo "Creativo" para generar subcarpetas dinámicas por proyecto, año o cliente.
* 🛡️ **Filtro Anti-Spam (Agrupación Inteligente):** Evita el "caos de carpetas". Si la IA decide crear una carpeta para almacenar menos de 3 archivos, OrgPro la bloquea inteligentemente y agrupa esos archivos huérfanos en una carpeta `"Varios"` u `"Otros"`.

## 🚀 Características Principales

* ⚡ **Análisis Rápido (Local):** Clasifica archivos instantáneamente basándose en un diccionario integrado de más de 120 extensiones y reglas de prioridad configurables por el usuario.
* 🧠 **Análisis Profundo (IA):** Integración con la API de Groq para deducir y clasificar archivos desconocidos o sin extensión. Toma el control total escribiendo directivas (prompts) personalizadas antes de analizar.
* 🪄 **IA Name (Limpieza de Nombres):** Analiza nombres de archivos corruptos o generados por el sistema (ej. `IMG_001_final_xx.jpg`) y sugiere nombres legibles y profesionales automáticamente.
* 👯‍♂️ **Caza-Duplicados Inteligente (Hash MD5):** Escanea la huella digital real del contenido para encontrar y limpiar duplicados exactos, sin importar cómo se llamen.
* 🗑️ **Papelera Segura:** Los duplicados gestionados se envían a un entorno oculto (`.orgpro_trash`) donde puedes restaurarlos con un solo clic.
* 👻 **Modo Fantasma & Auto-Limpieza (Cron):** Deja a OrgPro en la bandeja de tu sistema vigilando una carpeta en tiempo real, o programa una hora exacta para que limpie en segundo plano todos los días.
* 🌌 **Mapa de Organización:** Visualiza tus archivos y carpetas en un grafo de red interactivo con cámara inteligente, zoom y buscador instantáneo.
* ↩️ **Deshacer Selectivo:** Revierte archivos a su ruta original uno por uno desde el panel de historial sin afectar la organización del resto de la carpeta.
* 🌍 **Soporte Bilingüe & Temas Premium:** Interfaz "Arch Edition" con cambio en tiempo real entre Español e Inglés. Personaliza tu experiencia con temas inspirados en programación como *Arch Blue, Hacker Green, Neón, Volcán, Menta* y *Espresso*.
* 🖱️ **Arrastrar y Soltar:** Arrastra carpetas directamente sobre la terminal para analizarlas al instante.
* 📊 **Tablero de Estadísticas:** Descubre cuántos archivos has organizado y los minutos ahorrados en total a nivel global.

## ⚙️ Instalación

1. Ve a la pestaña de **[Releases](../../releases)** a la derecha de esta página.
2. Descarga la versión más reciente (`Setup_OrgPro_v1.6.exe`).
3. Ejecuta el instalador y sigue los pasos.
4. ¡Listo! Ya puedes empezar a organizar tu PC.

## 🔑 Configuración de la Inteligencia Artificial
Para usar las funciones avanzadas de renombrado y análisis profundo:
1. Regístrate de forma gratuita en [console.groq.com](https://console.groq.com/keys).
2. Genera tu API Key.
3. Abre OrgPro, haz clic en el botón de **Config (⚙️)** en la barra superior y pega tu clave. 
*(Nota: Tu clave es privada y se guarda únicamente de forma local en tu computadora).*

---
<p align="center"><b>Desarrollado con ☕ por Chris</b></p>
