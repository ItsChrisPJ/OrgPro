import os
import sys
import shutil
import json
import time
import queue
import threading
import hashlib
from datetime import datetime
import webview
from groq import Groq
from plyer import notification

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

current_window = None
tray_icon      = None
tray_queue     = queue.Queue()

def call_js(code: str):
    global current_window
    if current_window:
        try: current_window.evaluate_js(code)
        except: pass

def cargar_config_usuario():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            try: return json.load(f)
            except: return {"api_key": "", "rules": {}}
    return {"api_key": "", "rules": {}}

def guardar_config_usuario(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)

class Api:
    def minimizar_ventana(self):
        global current_window
        if current_window: current_window.minimize()

    def maximizar_ventana(self):
        global current_window
        if current_window: current_window.toggle_fullscreen() 

    def manejar_cierre_inteligente(self, fantasma_activo_ui):
        global current_window, fantasma_activo, tray_icon
        config = cargar_config_usuario()
        cron_activo = config.get("cron", {}).get("activo", False)
        
        if current_window:
            # Si Fantasma O Cron están activos, ocultamos en vez de cerrar
            if fantasma_activo_ui or fantasma_activo or cron_activo:
                current_window.hide()
            else:
                if tray_icon: tray_icon.stop()
                os._exit(0)

    def guardar_bienvenida_v14(self):
        config = cargar_config_usuario()
        config["v14_vista"] = True
        guardar_config_usuario(config)
        return True

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
    
    def guardar_idioma(self, lang):
        config = cargar_config_usuario()
        config["language"] = lang
        guardar_config_usuario(config)
        return True
    
    def guardar_modo_silencio(self, activo):
        config = cargar_config_usuario()
        config["modo_silencio"] = activo
        guardar_config_usuario(config)
        return True
    
    def guardar_tema_color(self, tema):
        config = cargar_config_usuario()
        config["theme_color"] = tema
        guardar_config_usuario(config)
        return True

    # --- NUEVAS FUNCIONES: CRON ---
    def guardar_cron(self, activo, ruta, hora):
        config = cargar_config_usuario()
        config["cron"] = {"activo": activo, "ruta": ruta.strip('"').strip("'"), "hora": hora}
        guardar_config_usuario(config)
        return True

    # --- NUEVAS FUNCIONES: CAZA-DUPLICADOS (HASH) ---
    def buscar_duplicados(self, ruta):
        try:
            ruta = ruta.strip('"').strip("'")
            if not os.path.exists(ruta): return {"status": "error", "message": "La ruta no existe."}
            
            hashes = {}
            for f in os.listdir(ruta):
                p = os.path.join(ruta, f)
                if os.path.isfile(p) and not f.startswith('.'):
                    # Leemos los archivos en fragmentos de 64kb para no saturar la RAM si son grandes
                    hasher = hashlib.md5()
                    with open(p, 'rb') as afile:
                        buf = afile.read(65536)
                        while len(buf) > 0:
                            hasher.update(buf)
                            buf = afile.read(65536)
                    h = hasher.hexdigest()
                    if h in hashes: hashes[h].append(f)
                    else: hashes[h] = [f]
            
            # Filtramos solo los que tienen más de 1 coincidencia
            dups = {k: v for k, v in hashes.items() if len(v) > 1}
            return {"status": "success", "duplicados": dups}
        except Exception as e: return {"status": "error", "message": str(e)}

    # --- NUEVAS FUNCIONES: PAPELERA DE RECICLAJE INTERNA ---
    def enviar_a_papelera(self, ruta, archivos):
        try:
            ruta = ruta.strip('"').strip("'")
            papelera = os.path.join(ruta, '.orgpro_trash')
            os.makedirs(papelera, exist_ok=True)
            movidos = 0
            for arch in archivos:
                src = os.path.join(ruta, arch)
                if os.path.exists(src):
                    shutil.move(src, os.path.join(papelera, arch))
                    movidos += 1
            return {"status": "success", "cantidad": movidos}
        except Exception as e: return {"status": "error", "message": str(e)}

    def ver_papelera(self, ruta):
        try:
            ruta = ruta.strip('"').strip("'")
            papelera = os.path.join(ruta, '.orgpro_trash')
            if not os.path.exists(papelera): return {"status": "success", "archivos": []}
            archs = [f for f in os.listdir(papelera) if os.path.isfile(os.path.join(papelera, f))]
            return {"status": "success", "archivos": archs}
        except Exception as e: return {"status": "error", "message": str(e)}

    def vaciar_papelera(self, ruta):
        try:
            ruta = ruta.strip('"').strip("'")
            papelera = os.path.join(ruta, '.orgpro_trash')
            if os.path.exists(papelera):
                shutil.rmtree(papelera)
                return {"status": "success"}
            return {"status": "error", "message": "Papelera ya estaba vacía"}
        except Exception as e: return {"status": "error", "message": str(e)}

    def restaurar_papelera(self, ruta, archivo):
        try:
            ruta = ruta.strip('"').strip("'")
            papelera = os.path.join(ruta, '.orgpro_trash')
            src = os.path.join(papelera, archivo)
            if os.path.exists(src):
                shutil.move(src, os.path.join(ruta, archivo))
                return {"status": "success"}
            return {"status": "error", "message": "Archivo no encontrado"}
        except Exception as e: return {"status": "error", "message": str(e)}


    def seleccionar_carpeta(self):
        global current_window
        if current_window:
            result = current_window.create_file_dialog(webview.FOLDER_DIALOG, allow_multiple=False)
            if result: return result[0]
        return None

    def obtener_estadisticas(self):
        config = cargar_config_usuario()
        if "stats" not in config:
            config["stats"] = {"archivos_totales": 0, "megabytes_totales": 0.0, "minutos_ahorrados": 0}
            guardar_config_usuario(config)
        return config["stats"]

    def analizar_archivos(self, ruta, usar_ia, contexto_ia=""):
        try:
            ruta = ruta.strip('"').strip("'")
            if not os.path.exists(ruta): return {"status": "error", "message": "La ruta ingresada no existe."}
            archivos = [f for f in os.listdir(ruta) if os.path.isfile(os.path.join(ruta, f)) and not f.startswith('.')]
            if not archivos: return {"status": "error", "message": "No hay archivos sueltos en esa carpeta."}
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
                if not api_key: return {"status": "error", "message": "No has configurado tu API Key."}
                client = Groq(api_key=api_key)
                prompt = "Clasifica estos archivos en carpetas lógicas. "
                if contexto_ia: prompt += f" REGLA ESPECÍFICA DEL USUARIO: {contexto_ia}. "
                prompt += f" Devuelve ÚNICAMENTE un objeto JSON plano (sin anidar). Clave: Nombre del archivo, Valor: Nombre de la carpeta sugerida. Archivos: {str(archivos)}"
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.1-8b-instant", temperature=0.1, max_tokens=4096,
                    response_format={"type": "json_object"}
                )
                plan_bruto = json.loads(chat_completion.choices[0].message.content)
                if len(plan_bruto) == 1 and isinstance(list(plan_bruto.values())[0], dict): plan_bruto = list(plan_bruto.values())[0]
                plan = {str(k): str(v) for k, v in plan_bruto.items()}
                return {"status": "success", "plan": plan, "modo": "IA (Llama 3.1)"}
        except Exception as e: return {"status": "error", "message": str(e)}

    def sugerir_nombres(self, ruta):
        try:
            ruta = ruta.strip('"').strip("'")
            if not os.path.exists(ruta): return {"status": "error", "message": "La ruta no existe."}
            archivos = [f for f in os.listdir(ruta) if os.path.isfile(os.path.join(ruta, f)) and not f.startswith('.')]
            if not archivos: return {"status": "error", "message": "No hay archivos sueltos."}
            api_key = cargar_config_usuario().get("api_key", "")
            if not api_key: return {"status": "error", "message": "Falta API Key."}
            client = Groq(api_key=api_key)
            prompt = f"Actúa como experto en limpieza. Analiza esta lista de nombres. Identifica nombres confusos o genéricos. Sugiere un nombre limpio conservando la extensión original. Devuelve ÚNICAMENTE un objeto JSON plano donde la clave es el nombre original y el valor es el nuevo. Lista: {str(archivos)}"
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant", temperature=0.1, max_tokens=4096,
                response_format={"type": "json_object"}
            )
            sugerencias = json.loads(chat_completion.choices[0].message.content)
            if len(sugerencias) == 1 and isinstance(list(sugerencias.values())[0], dict): sugerencias = list(sugerencias.values())[0]
            return {"status": "success", "sugerencias": sugerencias}
        except Exception as e: return {"status": "error", "message": str(e)}

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
        except Exception as e: return {"status": "error", "message": str(e)}

    def organizar_archivos(self, ruta, plan):
        try:
            ruta = ruta.strip('"').strip("'")
            historial = {}
            historial_path = os.path.join(ruta, '.historial_org.json')
            if os.path.exists(historial_path):
                with open(historial_path, 'r', encoding='utf-8') as f:
                    try: historial = json.load(f)
                    except: pass
            
            total = len(plan)
            procesados = 0
            bytes_total = 0
            carpetas_usadas = set()

            graph_data = {"nodes": [{"id": "root", "label": "OrgPro", "group": "root"}], "edges": []}

            for archivo, carpeta in plan.items():
                ruta_origen = os.path.join(ruta, archivo)
                if not os.path.exists(ruta_origen): continue
                try: bytes_total += os.path.getsize(ruta_origen)
                except: pass
                ruta_dest = os.path.join(ruta, carpeta)
                os.makedirs(ruta_dest, exist_ok=True)
                
                if carpeta not in carpetas_usadas:
                    graph_data["nodes"].append({"id": carpeta, "label": carpeta, "group": "category"})
                    graph_data["edges"].append({"from": "root", "to": carpeta})
                
                archivo_id = f"file_{procesados}"
                graph_data["nodes"].append({"id": archivo_id, "label": archivo, "group": "file"})
                graph_data["edges"].append({"from": carpeta, "to": archivo_id})

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
                call_js(f'actualizarProgreso({round((procesados / total) * 100, 2)})')
                time.sleep(0.01)

            with open(historial_path, 'w', encoding='utf-8') as f: json.dump(historial, f, indent=4)
            tamano = self._formatear_tamano(bytes_total)
            
            return {"status": "success", "stats": {"archivos": procesados, "carpetas": len(carpetas_usadas), "tamano": tamano}, "graph": graph_data}
        except Exception as e: return {"status": "error", "message": str(e)}

    def _formatear_tamano(self, bytes_total):
        if bytes_total < 1024: return f"{bytes_total} B"
        elif bytes_total < 1024 ** 2: return f"{bytes_total / 1024:.1f} KB"
        elif bytes_total < 1024 ** 3: return f"{bytes_total / 1024 ** 2:.1f} MB"
        else: return f"{bytes_total / 1024 ** 3:.2f} GB"

    def obtener_historial(self, ruta):
        try:
            ruta = ruta.strip('"').strip("'")
            historial_path = os.path.join(ruta, '.historial_org.json')
            if not os.path.exists(historial_path): return {"status": "error", "message": "No hay historial reciente."}
            with open(historial_path, 'r', encoding='utf-8') as f: historial = json.load(f)
            return {"status": "success", "data": historial}
        except Exception as e: return {"status": "error", "message": str(e)}

    def deshacer_organizacion(self, ruta, ruta_especifica=None):
        try:
            ruta = ruta.strip('"').strip("'")
            historial_path = os.path.join(ruta, '.historial_org.json')
            if not os.path.exists(historial_path): return {"status": "error", "message": "No hay historial para deshacer."}
            
            with open(historial_path, 'r', encoding='utf-8') as f: historial = json.load(f)
                
            carpetas_afectadas = set()
            items_a_borrar = []
            
            for ruta_actual, ruta_original in historial.items():
                if ruta_especifica and ruta_actual != ruta_especifica: continue
                if os.path.exists(ruta_actual):
                    carpetas_afectadas.add(os.path.dirname(ruta_actual))
                    shutil.move(ruta_actual, ruta_original)
                    items_a_borrar.append(ruta_actual)
            
            for item in items_a_borrar: del historial[item]
            for carpeta in carpetas_afectadas:
                if os.path.exists(carpeta) and not os.listdir(carpeta):
                    try: os.rmdir(carpeta)
                    except: pass
            
            if not historial: os.remove(historial_path)
            else:
                with open(historial_path, 'w', encoding='utf-8') as f: json.dump(historial, f, indent=4)
            return {"status": "success"}
        except Exception as e: return {"status": "error", "message": str(e)}

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

# ─── DAEMON: MODO FANTASMA ─────────────────────────────────────
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
            except Exception: pass
        time.sleep(3)

# ─── DAEMON: CRON SCHEDULER ─────────────────────────────────────
def cron_loop():
    last_run_date = ""
    while True:
        try:
            config = cargar_config_usuario()
            cron = config.get("cron", {})
            if cron.get("activo") and cron.get("ruta") and cron.get("hora"):
                now = datetime.now()
                hora_actual = now.strftime("%H:%M")
                fecha_actual = now.strftime("%Y-%m-%d")
                
                # Ejecutar solo 1 vez al día a la hora exacta
                if hora_actual == cron.get("hora") and last_run_date != fecha_actual:
                    ruta = cron.get("ruta")
                    if os.path.exists(ruta):
                        archivos = [f for f in os.listdir(ruta) if os.path.isfile(os.path.join(ruta, f)) and not f.startswith('.')]
                        reglas = config.get("rules", {})
                        plan = {}
                        for a in archivos:
                            _, ext = os.path.splitext(a.lower())
                            if ext in ['.crdownload', '.part', '.tmp', '.download']: continue
                            if ext in reglas: plan[a] = reglas[ext]
                            elif ext in EXTENSIONES_CONOCIDAS: plan[a] = EXTENSIONES_CONOCIDAS[ext]
                            else: plan[a] = "Otros Archivos"
                        
                        for a, c in plan.items():
                            r_origen = os.path.join(ruta, a)
                            r_dest = os.path.join(ruta, c)
                            os.makedirs(r_dest, exist_ok=True)
                            r_final = os.path.join(r_dest, a)
                            if not os.path.exists(r_final):
                                shutil.move(r_origen, r_final)
                    
                    last_run_date = fecha_actual
                    tray_queue.put(("toast", f"Cron: Limpieza automática completada en {ruta}"))
        except Exception: pass
        time.sleep(30) # Comprueba cada 30 segundos


threading.Thread(target=fantasma_loop, daemon=True).start()
threading.Thread(target=cron_loop, daemon=True).start()

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
                config = cargar_config_usuario()
                if not config.get("modo_silencio", False):
                    try: notification.notify(title="OrgPro Daemon ⚙️", message=data, app_name="OrgPro", app_icon="icono.ico", timeout=5)
                    except: pass
            elif action == "ui_fantasma":
                call_js(f'actualizar_ui_fantasma({json.dumps(data)})')
        except queue.Empty: pass
        except Exception: pass

threading.Thread(target=procesador_cola, daemon=True).start()

if __name__ == '__main__':
    print(">>> INICIANDO ORGANIZADOR INTELIGENTE PRO (pywebview)...")

    def on_closing():
        global current_window, fantasma_activo, tray_icon
        config = cargar_config_usuario()
        cron_activo = config.get("cron", {}).get("activo", False)
        
        if fantasma_activo or cron_activo:
            if current_window: current_window.hide()
            return False
        else:
            if tray_icon: tray_icon.stop()
            os._exit(0)
            return True

    current_window = webview.create_window(
        'OrgPro v1.5 [Arch Edition]',
        HTML_PATH,
        js_api=api_instance,
        width=900,
        height=750,
        frameless=False,
        resizable=True,
        text_select=False,
        easy_drag=False,
        background_color='#1a1b26'
    )
    current_window.events.closing += on_closing

    if HAS_TRAY:
        icono_path = os.path.join(BASE_DIR, 'icono.ico')
        if not os.path.exists(icono_path):
            icono_path = os.path.join(BASE_DIR, 'web', 'icono.ico')
            
        image = Image.open(icono_path) if os.path.exists(icono_path) else Image.new('RGB', (64, 64), color=(139, 90, 43))

        def on_show(icon, item): tray_queue.put(("show", None))
        def on_quit(icon, item):
            icon.stop()
            os._exit(0)

        def toggle_fantasma_tray(icon, item):
            global fantasma_activo, carpeta_fantasma, archivos_conocidos
            if not fantasma_activo:
                if carpeta_fantasma and os.path.exists(carpeta_fantasma):
                    archivos_conocidos = set(f for f in os.listdir(carpeta_fantasma) if os.path.isfile(os.path.join(carpeta_fantasma, f)) and not f.startswith('.'))
                    fantasma_activo = True
                    tray_queue.put(("toast", "Fantasma Reactivado"))
                    tray_queue.put(("ui_fantasma", True))
                else: tray_queue.put(("show", None))
            else:
                fantasma_activo = False
                tray_queue.put(("toast", "Fantasma Pausado"))
                tray_queue.put(("ui_fantasma", False))

        def get_fantasma_state(item): return fantasma_activo

        menu = pystray.Menu(
            item('Abrir Interfaz',      on_show,              default=True),
            item('Vigilancia Fantasma', toggle_fantasma_tray, checked=get_fantasma_state),
            item('Salir Completamente', on_quit)
        )
        tray_icon = pystray.Icon("OrgPro", image, "OrgPro Daemon", menu=menu)
        threading.Thread(target=tray_icon.run, daemon=True).start()

webview.start(debug=False)