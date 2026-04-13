import os
import sys
import shutil
import json
import time
import queue
import threading
import webview
from groq import Groq

try:
    import pystray
    from pystray import MenuItem as item
    from PIL import Image
    HAS_TRAY = True
except ImportError:
    HAS_TRAY = False

# === PATHS ===
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

HTML_PATH = os.path.join(BASE_DIR, 'web', 'index.html')

appdata_dir = os.path.join(os.environ['LOCALAPPDATA'], 'OrgPro')
os.makedirs(appdata_dir, exist_ok=True)
CONFIG_FILE = os.path.join(appdata_dir, "custom_config.json")

EXTENSIONES_CONOCIDAS = {
    '.jpg': 'Imágenes', '.jpeg': 'Imágenes', '.png': 'Imágenes', '.gif': 'Imágenes',
    '.webp': 'Imágenes', '.bmp': 'Imágenes', '.tiff': 'Imágenes', '.tif': 'Imágenes',
    '.heic': 'Imágenes', '.raw': 'Imágenes RAW', '.cr2': 'Imágenes RAW', '.nef': 'Imágenes RAW',
    '.svg': 'Vectores', '.eps': 'Vectores', '.fig': 'Diseño UI', '.sketch': 'Diseño UI',
    '.psd': 'Diseño (Adobe)', '.ai': 'Diseño (Adobe)', '.indd': 'Diseño (Adobe)',
    '.blend': 'Modelos 3D', '.obj': 'Modelos 3D', '.fbx': 'Modelos 3D', '.stl': 'Modelos 3D (Impresión)',
    '.pdf': 'Documentos', '.doc': 'Documentos (Word)', '.docx': 'Documentos (Word)',
    '.txt': 'Notas de Texto', '.rtf': 'Notas de Texto', '.md': 'Notas de Texto (Markdown)',
    '.epub': 'Libros Electrónicos', '.mobi': 'Libros Electrónicos', '.azw3': 'Libros Electrónicos',
    '.xls': 'Hojas de Cálculo', '.xlsx': 'Hojas de Cálculo', '.csv': 'Bases de Datos (CSV)',
    '.ppt': 'Presentaciones', '.pptx': 'Presentaciones', '.key': 'Presentaciones',
    '.mp3': 'Música', '.wav': 'Audio de Alta Calidad', '.flac': 'Audio de Alta Calidad',
    '.ogg': 'Audio (Otros)', '.m4a': 'Música', '.aac': 'Música',
    '.als': 'Proyectos Musicales (Ableton)', '.flp': 'Proyectos Musicales (FL Studio)',
    '.mp4': 'Videos', '.mkv': 'Videos', '.avi': 'Videos', '.mov': 'Videos',
    '.wmv': 'Videos', '.webm': 'Videos', '.flv': 'Videos',
    '.srt': 'Subtítulos', '.ass': 'Subtítulos', '.vtt': 'Subtítulos',
    '.prproj': 'Proyectos de Video (Premiere)', '.aep': 'Proyectos de Video (After Effects)',
    '.zip': 'Comprimidos', '.rar': 'Comprimidos', '.7z': 'Comprimidos',
    '.tar': 'Comprimidos', '.gz': 'Comprimidos', '.iso': 'Imágenes de Disco',
    '.exe': 'Instaladores y Programas', '.msi': 'Instaladores y Programas',
    '.apk': 'Aplicaciones (Android)', '.dmg': 'Aplicaciones (Mac)',
    '.bat': 'Scripts de Sistema', '.sh': 'Scripts de Sistema', '.ps1': 'Scripts de Sistema',
    '.dll': 'Archivos de Sistema', '.sys': 'Archivos de Sistema', '.ini': 'Configuraciones',
    '.lnk': 'Accesos Directos',
    '.html': 'Código Web', '.css': 'Código Web', '.js': 'Código Web',
    '.ts': 'Código Web', '.jsx': 'Código Web', '.tsx': 'Código Web', '.php': 'Código Web',
    '.py': 'Código (Python)', '.java': 'Código', '.c': 'Código', '.cpp': 'Código',
    '.cs': 'Código (C#)', '.go': 'Código', '.rs': 'Código', '.rb': 'Código',
    '.json': 'Datos y Configuración', '.xml': 'Datos y Configuración',
    '.yaml': 'Datos y Configuración', '.yml': 'Datos y Configuración', '.env': 'Datos y Configuración',
    '.sql': 'Bases de Datos', '.db': 'Bases de Datos', '.sqlite': 'Bases de Datos',
    '.ttf': 'Fuentes Tipográficas', '.otf': 'Fuentes Tipográficas', '.woff': 'Fuentes Tipográficas'
}

# ─── Referencia global a la ventana ────────────────────────────────────────────
current_window = None
tray_queue     = queue.Queue()


def call_js(code: str):
    """Llama JS desde Python sin bloquear. Seguro desde cualquier hilo."""
    global current_window
    if current_window:
        try:
            current_window.evaluate_js(code)
        except Exception:
            pass


# ─── CONFIGURACIÓN ─────────────────────────────────────────────────────────────
def cargar_config_usuario():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            try: return json.load(f)
            except: return {"api_key": "", "rules": {}}
    return {"api_key": "", "rules": {}}

def guardar_config_usuario(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)


# ─── API EXPUESTA A JAVASCRIPT ─────────────────────────────────────────────────
class Api:
    """
    Todos los métodos de esta clase son accesibles desde JS como:
        await window.pywebview.api.nombreMetodo(args)
    Los métodos se ejecutan en un hilo separado automáticamente.
    """

    # ── Config ──────────────────────────────────────────────────────────────────
    def obtener_config(self):
        return cargar_config_usuario()

    def guardar_api_key(self, api_key):
        config = cargar_config_usuario()
        config["api_key"] = api_key.strip()
        guardar_config_usuario(config)
        return config

    def guardar_regla_usuario(self, extension, carpeta):
        config = cargar_config_usuario()
        if not extension.startswith('.'): extension = '.' + extension
        config["rules"][extension.lower()] = carpeta
        guardar_config_usuario(config)
        return config

    def borrar_regla_usuario(self, extension):
        config = cargar_config_usuario()
        if extension in config["rules"]:
            del config["rules"][extension]
            guardar_config_usuario(config)
        return config

    def guardar_dark_mode(self, estado):
        config = cargar_config_usuario()
        config["dark_mode"] = estado
        guardar_config_usuario(config)
        return True

    # ── Selección de carpeta con diálogo nativo de pywebview ────────────────────
    def seleccionar_carpeta(self):
        global current_window
        if current_window:
            result = current_window.create_file_dialog(
                webview.FOLDER_DIALOG, allow_multiple=False
            )
            if result:
                return result[0]
        return None

    # ── Análisis ────────────────────────────────────────────────────────────────
    def analizar_archivos(self, ruta, usar_ia):
        try:
            ruta = ruta.strip('"').strip("'")
            if not os.path.exists(ruta):
                return {"status": "error", "message": "La ruta ingresada no existe."}
            archivos = [f for f in os.listdir(ruta) if os.path.isfile(os.path.join(ruta, f)) and not f.startswith('.')]
            if not archivos:
                return {"status": "error", "message": "No hay archivos sueltos en esa carpeta."}
            config_user = cargar_config_usuario()
            reglas_user = config_user.get("rules", {})
            plan = {}
            if not usar_ia:
                for archivo in archivos:
                    _, ext = os.path.splitext(archivo.lower())
                    if ext in ['.crdownload', '.part', '.tmp', '.download']: continue
                    if ext in reglas_user: plan[archivo] = reglas_user[ext]
                    elif ext in EXTENSIONES_CONOCIDAS: plan[archivo] = EXTENSIONES_CONOCIDAS[ext]
                    else: plan[archivo] = "Otros Archivos"
                return {"status": "success", "plan": plan, "modo": "Personalizado"}
            else:
                api_key = config_user.get("api_key", "")
                if not api_key: return {"status": "error", "message": "No has configurado tu API Key de Groq en Ajustes."}
                client = Groq(api_key=api_key)
                prompt = f"Clasifica estos archivos en carpetas lógicas. Devuelve ÚNICAMENTE un objeto JSON plano (sin anidar). Clave: Nombre del archivo, Valor: Nombre de la carpeta sugerida. Archivos: {str(archivos)}"
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.1-8b-instant", temperature=0.1, max_tokens=4096,
                    response_format={"type": "json_object"}
                )
                plan_bruto = json.loads(chat_completion.choices[0].message.content)
                if len(plan_bruto) == 1 and isinstance(list(plan_bruto.values())[0], dict):
                    plan_bruto = list(plan_bruto.values())[0]
                plan = {str(k): str(v) for k, v in plan_bruto.items()}
                return {"status": "success", "plan": plan, "modo": "IA (Llama 3.1)"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ── Desfragmentador de nombres ───────────────────────────────────────────────
    def sugerir_nombres(self, ruta):
        try:
            ruta = ruta.strip('"').strip("'")
            if not os.path.exists(ruta): return {"status": "error", "message": "La ruta no existe."}
            archivos = [f for f in os.listdir(ruta) if os.path.isfile(os.path.join(ruta, f)) and not f.startswith('.')]
            if not archivos: return {"status": "error", "message": "No hay archivos sueltos."}
            api_key = cargar_config_usuario().get("api_key", "")
            if not api_key: return {"status": "error", "message": "Falta API Key."}
            client = Groq(api_key=api_key)
            prompt = f"Actúa como un experto en limpieza digital. Analiza esta lista de nombres de archivos. Identifica solo aquellos con nombres confusos o genéricos. Sugiere un nombre limpio conservando la extensión original. Devuelve ÚNICAMENTE un objeto JSON plano donde la clave es el nombre original y el valor es el nuevo sugerido. Lista: {str(archivos)}"
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant", temperature=0.1, max_tokens=4096,
                response_format={"type": "json_object"}
            )
            sugerencias = json.loads(chat_completion.choices[0].message.content)
            if len(sugerencias) == 1 and isinstance(list(sugerencias.values())[0], dict):
                sugerencias = list(sugerencias.values())[0]
            return {"status": "success", "sugerencias": sugerencias}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def aplicar_renombres(self, ruta, renombres):
        try:
            ruta = ruta.strip('"').strip("'")
            aplicados = 0
            for original, nuevo in renombres.items():
                ruta_orig = os.path.join(ruta, original)
                ruta_nueva = os.path.join(ruta, nuevo)
                if os.path.exists(ruta_orig) and not os.path.exists(ruta_nueva):
                    os.rename(ruta_orig, ruta_nueva)
                    aplicados += 1
            return {"status": "success", "cantidad": aplicados}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ── Organización ─────────────────────────────────────────────────────────────
    def organizar_archivos(self, ruta, plan):
        try:
            ruta = ruta.strip('"').strip("'")
            historial = {}
            historial_path = os.path.join(ruta, '.historial_org.json')
            if os.path.exists(historial_path):
                with open(historial_path, 'r', encoding='utf-8') as f:
                    try: historial = json.load(f)
                    except: pass
            total = len(plan); procesados = 0; bytes_total = 0; carpetas_usadas = set()
            for archivo, carpeta in plan.items():
                ruta_origen = os.path.join(ruta, archivo)
                if not os.path.exists(ruta_origen): continue
                try: bytes_total += os.path.getsize(ruta_origen)
                except: pass
                ruta_dest = os.path.join(ruta, carpeta)
                os.makedirs(ruta_dest, exist_ok=True)
                carpetas_usadas.add(carpeta)
                ruta_final = os.path.join(ruta_dest, archivo)
                if os.path.exists(ruta_final):
                    base, ext = os.path.splitext(archivo)
                    c = 1
                    while os.path.exists(os.path.join(ruta_dest, f"{base} ({c}){ext}")): c += 1
                    ruta_final = os.path.join(ruta_dest, f"{base} ({c}){ext}")
                shutil.move(ruta_origen, ruta_final)
                historial[ruta_final] = ruta_origen
                procesados += 1
                # Progreso → JS via call_js (no bloquea)
                call_js(f'actualizarProgreso({round((procesados / total) * 100, 2)})')
                time.sleep(0.01)
            with open(historial_path, 'w', encoding='utf-8') as f:
                json.dump(historial, f, indent=4)
            tamano = self._formatear_tamano(bytes_total)
            return {"status": "success", "stats": {"archivos": procesados, "carpetas": len(carpetas_usadas), "tamano": tamano}}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _formatear_tamano(self, bytes_total):
        if bytes_total < 1024: return f"{bytes_total} B"
        elif bytes_total < 1024 ** 2: return f"{bytes_total / 1024:.1f} KB"
        elif bytes_total < 1024 ** 3: return f"{bytes_total / 1024 ** 2:.1f} MB"
        else: return f"{bytes_total / 1024 ** 3:.2f} GB"

    def obtener_historial(self, ruta):
        try:
            ruta = ruta.strip('"').strip("'")
            historial_path = os.path.join(ruta, '.historial_org.json')
            if not os.path.exists(historial_path): return {"status": "error", "message": "No hay historial reciente en esta carpeta."}
            with open(historial_path, 'r', encoding='utf-8') as f: historial = json.load(f)
            return {"status": "success", "data": historial}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def deshacer_organizacion(self, ruta):
        try:
            ruta = ruta.strip('"').strip("'")
            historial_path = os.path.join(ruta, '.historial_org.json')
            if not os.path.exists(historial_path): return {"status": "error", "message": "No hay historial para deshacer."}
            with open(historial_path, 'r', encoding='utf-8') as f:
                historial = json.load(f)
            carpetas_afectadas = set()
            for ruta_actual, ruta_original in historial.items():
                if os.path.exists(ruta_actual):
                    carpetas_afectadas.add(os.path.dirname(ruta_actual))
                    shutil.move(ruta_actual, ruta_original)
            for carpeta in carpetas_afectadas:
                if os.path.exists(carpeta) and not os.listdir(carpeta):
                    try: os.rmdir(carpeta)
                    except: pass
            os.remove(historial_path)
            return {"status": "success"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ── Modo Fantasma ────────────────────────────────────────────────────────────
    def estado_fantasma(self):
        return {"activo": fantasma_activo, "carpeta": carpeta_fantasma}

    def toggle_fantasma(self, ruta, estado):
        global fantasma_activo, carpeta_fantasma, archivos_conocidos
        if estado:
            ruta = ruta.strip('"').strip("'")
            if os.path.exists(ruta):
                carpeta_fantasma = ruta
                archivos_conocidos = set(f for f in os.listdir(ruta) if os.path.isfile(os.path.join(ruta, f)) and not f.startswith('.'))
                fantasma_activo = True
                return {"status": "success"}
            return {"status": "error", "message": "La ruta seleccionada no es válida."}
        else:
            fantasma_activo = False
            return {"status": "success"}


api_instance = Api()


# ─── MODO FANTASMA (loop en segundo plano) ─────────────────────────────────────
fantasma_activo   = False
carpeta_fantasma  = ""
archivos_conocidos = set()

def fantasma_loop():
    global fantasma_activo, carpeta_fantasma, archivos_conocidos
    while True:
        if fantasma_activo and os.path.exists(carpeta_fantasma):
            try:
                actuales = set(f for f in os.listdir(carpeta_fantasma) if os.path.isfile(os.path.join(carpeta_fantasma, f)) and not f.startswith('.'))
                nuevos = actuales - archivos_conocidos
                if nuevos:
                    time.sleep(1.5)
                    config_user = cargar_config_usuario()
                    reglas_user = config_user.get("rules", {})
                    plan = {}
                    for archivo in nuevos:
                        _, ext = os.path.splitext(archivo.lower())
                        if ext in ['.crdownload', '.part', '.tmp', '.download']: continue
                        if ext in reglas_user: plan[archivo] = reglas_user[ext]
                        elif ext in EXTENSIONES_CONOCIDAS: plan[archivo] = EXTENSIONES_CONOCIDAS[ext]
                        else: plan[archivo] = "Otros Archivos"
                    fallidos = set()
                    if plan:
                        historial_path = os.path.join(carpeta_fantasma, '.historial_org.json')
                        historial = {}
                        if os.path.exists(historial_path):
                            with open(historial_path, 'r', encoding='utf-8') as f:
                                try: historial = json.load(f)
                                except: pass
                        for archivo, carpeta in plan.items():
                            r_origen = os.path.join(carpeta_fantasma, archivo)
                            if not os.path.exists(r_origen): continue
                            r_dest = os.path.join(carpeta_fantasma, carpeta)
                            os.makedirs(r_dest, exist_ok=True)
                            r_final = os.path.join(r_dest, archivo)
                            if os.path.exists(r_final):
                                base, ext = os.path.splitext(archivo)
                                c = 1
                                while os.path.exists(os.path.join(r_dest, f"{base} ({c}){ext}")): c += 1
                                r_final = os.path.join(r_dest, f"{base} ({c}){ext}")
                            try:
                                shutil.move(r_origen, r_final)
                                historial[r_final] = r_origen
                                tray_queue.put(("toast", f"Movido: {archivo[:20]}... ➔ {carpeta}"))
                            except:
                                fallidos.add(archivo)
                        with open(historial_path, 'w', encoding='utf-8') as f:
                            json.dump(historial, f, indent=4)
                    archivos_conocidos = set(f for f in os.listdir(carpeta_fantasma) if os.path.isfile(os.path.join(carpeta_fantasma, f)) and not f.startswith('.'))
                    archivos_conocidos -= fallidos
                else:
                    archivos_conocidos = actuales
            except Exception:
                pass
        time.sleep(3)

threading.Thread(target=fantasma_loop, daemon=True).start()


# ─── PROCESADOR DE COLA (anti-deadlock) ────────────────────────────────────────
def procesador_cola():
    while True:
        try:
            action, data = tray_queue.get(timeout=1.0)
            if action == "show":
                global current_window
                if current_window:
                    try: current_window.show()
                    except: pass
            elif action == "toast":
                call_js(f'mostrarToastFantasma({json.dumps(data)})')
            elif action == "ui_fantasma":
                call_js(f'actualizar_ui_fantasma({json.dumps(data)})')
        except queue.Empty:
            pass
        except Exception:
            pass

threading.Thread(target=procesador_cola, daemon=True).start()


# ─── ARRANQUE ──────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print(">>> INICIANDO ORGANIZADOR INTELIGENTE PRO (pywebview)...")

    # La ventana se oculta en vez de cerrarse → el proceso sigue vivo
    def on_closing():
        global current_window
        if current_window:
            current_window.hide()
        return False  # cancela el cierre real

    current_window = webview.create_window(
        'OrgPro – Organizador Inteligente',
        HTML_PATH,
        js_api=api_instance,
        width=800,
        height=880,
        resizable=False,
        text_select=False,
        background_color='#fdfbf7'
    )
    current_window.events.closing += on_closing

    if HAS_TRAY:
        icono_path = os.path.join(BASE_DIR, 'icono.ico')
        image = Image.open(icono_path) if os.path.exists(icono_path) else Image.new('RGB', (64, 64), color=(139, 90, 43))

        # Callbacks: SOLO encolan, nunca tocan la UI directamente
        def on_show(icon, item):
            tray_queue.put(("show", None))

        def on_quit(icon, item):
            icon.stop()
            os._exit(0)

        def toggle_fantasma_tray(icon, item):
            global fantasma_activo, carpeta_fantasma, archivos_conocidos
            if not fantasma_activo:
                if carpeta_fantasma and os.path.exists(carpeta_fantasma):
                    archivos_conocidos = set(
                        f for f in os.listdir(carpeta_fantasma)
                        if os.path.isfile(os.path.join(carpeta_fantasma, f)) and not f.startswith('.')
                    )
                    fantasma_activo = True
                    tray_queue.put(("toast", "Fantasma Reactivado"))
                    tray_queue.put(("ui_fantasma", True))
                else:
                    tray_queue.put(("show", None))
            else:
                fantasma_activo = False
                tray_queue.put(("toast", "Fantasma Pausado"))
                tray_queue.put(("ui_fantasma", False))

        def get_fantasma_state(item):
            return fantasma_activo

        menu = pystray.Menu(
            item('Abrir Interfaz',      on_show,              default=True),
            item('Vigilancia Fantasma', toggle_fantasma_tray, checked=get_fantasma_state),
            item('Salir Completamente', on_quit)
        )
        icon = pystray.Icon("OrgPro", image, "OrgPro Vigilando", menu=menu)
        threading.Thread(target=icon.run, daemon=True).start()

    # Inicia el motor nativo. Bloquea hasta que el proceso muere.
    webview.start(debug=False)