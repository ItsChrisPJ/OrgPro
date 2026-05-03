<h1 align="center">📁 OrgPro v1.5 - Arch Edition</h1>

<p align="center">
  <i>Una aplicación de escritorio híbrida y moderna diseñada para automatizar la limpieza y organización de tus archivos utilizando reglas locales e Inteligencia Artificial.</i>
</p>

---

## ✨ Novedades en la v1.5
* 🖥️ **Interfaz "Arch Edition":** Rediseño total de la ventana inspirado en la estética minimalista de los gestores de ventanas en mosaico (Tiling Window Managers) como **Hyprland** o **i3**, muy populares en la comunidad de Arch Linux. Una experiencia de terminal elegante, completamente responsiva y con integración nativa a los bordes de Windows.
* 👯‍♂️ **Caza-Duplicados Inteligente (Hash MD5):** Nuevo motor que escanea el contenido real de los archivos (su huella digital) para encontrar y limpiar duplicados exactos, sin importar si tienen nombres distintos.
* 🗑️ **Papelera Segura:** Los archivos duplicados gestionados ya no se borran permanentemente. Se envían a un entorno seguro oculto (`.orgpro_trash`) donde puedes restaurarlos con un clic.
* ⏰ **Auto-Limpieza (Cron):** Configura una hora exacta y OrgPro organizará la carpeta seleccionada automáticamente todos los días en segundo plano.
* 🤖 **Instrucciones IA (Prompts):** Toma el control total de la IA. Escribe directivas específicas (ej. *"Ignora los PDFs y agrupa por año"*) antes de realizar el análisis.
* ↩️ **Deshacer Selectivo:** El panel de historial ahora te permite revertir archivos a su ruta original **uno por uno**, sin afectar la organización del resto de la carpeta.
* 🌍 **Soporte Multi-Idioma:** Nueva arquitectura interna que soporta cambio en tiempo real entre Español e Inglés directamente desde Ajustes.

## 🚀 Características Principales

* ⚡ **Análisis Rápido (Local):** Clasifica archivos instantáneamente basándose en un diccionario integrado y reglas propias configurables.
* 🧠 **Análisis Profundo (IA):** Integración con la API de Groq para deducir y clasificar archivos desconocidos o sin extensión clara.
* 🪄 **Limpieza de Nombres:** La IA analiza nombres de archivos corruptos o generados por el sistema (ej. `IMG_001_final_xx.jpg`) y sugiere nombres legibles y profesionales.
* 👻 **Modo Fantasma (Segundo Plano):** La aplicación se ancla a la bandeja del sistema (reloj de Windows) y vigila una carpeta en tiempo real, auto-organizando cualquier archivo nuevo de forma silenciosa.
* 🌌 **Mapa de Organización:** Visualiza tus archivos y carpetas en un grafo de red interactivo con cámara inteligente, zoom y buscador instantáneo.
* 🎨 **Colorways Premium:** Personaliza tu experiencia con temas inspirados en programación como *Arch Blue, Hacker Green, Neón, Volcán, Menta* y *Espresso*.
* 🖱️ **Arrastrar y Soltar:** Arrastra carpetas directamente sobre la terminal para analizarlas al instante.
* 🔔 **Notificaciones Nativas:** Integración directa con el sistema de Windows para avisarte cuando limpia una carpeta en segundo plano (con Modo Silencio opcional).
* 📊 **Tablero de Estadísticas:** Descubre cuántos archivos has organizado y los minutos ahorrados en total a nivel global.

## ⚙️ Instalación

1. Ve a la pestaña de **[Releases](../../releases)** a la derecha de esta página.
2. Descarga la versión más reciente (`Setup_OrgPro_v1.5.exe`).
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
