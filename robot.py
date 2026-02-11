import requests
import json
import os
import time
import re
from datetime import datetime

# --- CONFIGURACIÓN DE HORA ESPAÑOLA ---
# Forzamos al servidor a usar la zona horaria de Madrid
os.environ['TZ'] = 'Europe/Madrid'
if hasattr(time, 'tzset'):
    time.tzset()

def guardar_web(html_content):
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

def revisar_normas():
    print("--- INICIANDO ROBOT V5.0 (DISEÑO + LEYENDA) ---")
    
    try:
        with open('normas.json', 'r', encoding='utf-8') as f:
            lista_normas = json.load(f)
    except Exception as e:
        print(f"Error crítico cargando JSON: {e}")
        return

    resultados_web = []
    # Cabeceras para simular un navegador real y evitar bloqueos (importante para IFS/FSSC)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8'
    }

    for norma in lista_normas:
        nombre = norma.get('nombre', 'Norma sin nombre')
        url = norma.get('url', '#')
        busqueda = norma.get('texto_a_buscar', '')
        
        # Detectamos los modos especiales antes de escanear
        es_transicion = norma.get('modo') == 'transicion'
        es_radar = norma.get('modo') == 'detectar_nueva'
        
        print(f"Escaneando: {nombre}...")
        estado_final = "error" # Estado por defecto si todo falla
        
        try:
            # Usamos session para mejorar la conexión
            session = requests.Session()
            respuesta = session.get(url, headers=headers, timeout=25)
            
            if respuesta.status_code == 200:
                contenido = respuesta.text
                # Búsqueda inteligente: insensible a mayúsculas/minúsculas
                encontrado = bool(re.search(re.escape(busqueda), contenido, re.IGNORECASE))
                
                if es_radar:
                    # Lógica Inversa para el Radar: Si encuentra, es una alerta de novedad
                    estado_final = "nueva_detectada" if encontrado else "ok"
                else:
                    # Lógica Normal
                    if encontrado:
                        # SI ES MODO TRANSICIÓN, FORZAMOS AMARILLO AUNQUE ESTÉ VIGENTE
                        estado_final = "warn" if es_transicion else "ok"
                    else:
                        estado_final = "error"
            else:
                print(f"   [ERROR] Web caída o bloqueo: HTTP {respuesta.status_code}")
                estado_final = "error"

        except Exception as e:
            print(f"   [ERROR] Excepción de conexión: {e}")
            estado_final = "error"
        
        resultados_web.append({
            "nombre": nombre,
            "url": url,
            "version": busqueda,
            "estado": estado_final,
            "es_radar": es_radar
        })
        # Pequeña pausa para no saturar los servidores
        time.sleep(1.5)

    # --- GENERACIÓN DEL HTML PROFESIONAL ---
    fecha = datetime.now().strftime("%d/%m/%Y a las %H:%M")
    html_final = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Vigilancia Normativa Profesional</title>
        <style>
            /* ESTILOS GENERALES */
            body {{ font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background: #f0f2f5; padding: 30px; color: #1e293b; }}
            .container {{ max-width: 1100px; margin: 0 auto; background: white; border-radius: 16px; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.05); overflow: hidden; }}
            h1 {{ text-align: center; padding: 35px; margin: 0; background: linear-gradient(to right, #1e3a8a, #2563eb); color: white; letter-spacing: 0.5px; }}
            h1 span {{ display: block; font-size: 0.6em; opacity: 0.9; font-weight: 400; margin-top: 8px; }}

            /* TABLA */
            table {{ width: 100%; border-collapse: collapse; }}
            th {{ background: #f8fafc; color: #475569; padding: 20px 25px; text-align: left; font-size: 0.9em; text-transform: uppercase; letter-spacing: 1px; font-weight: 700; border-bottom: 2px solid #e2e8f0; }}
            td {{ padding: 22px 25px; border-bottom: 1px solid #f1f5f9; vertical-align: middle; }}
            tr:hover {{ background-color: #f8fafc; transition: background 0.2s; }}

            /* BADGES Y COLORES */
            .badge {{ padding: 8px 16px; border-radius: 30px; font-weight: 700; font-size: 0.85em; display: inline-flex; align-items: center; gap: 8px; white-space: nowrap; }}
            .ok {{ background: #dcfce7; color: #166534; border: 1px solid #86efac; }}
            .warn {{ background: #fef9c3 !important; color: #854d0e !important; border: 1px solid #fde047; }} /* Importante para forzar el amarillo */
            .error {{ background: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; }}
            .radar {{ background: #e0f2fe; color: #075985; border: 1px solid #bae6fd; }}
            .new {{ background: #ffedd5; color: #9a3412; border: 1px solid #fdba74; animation: pulse 1.5s infinite; }}

            .version-tag {{ font-family: 'SF Mono', Consolas, monospace; background: #f1f5f9; padding: 6px 10px; border-radius: 8px; color: #475569; font-size: 0.95em; border: 1px solid #e2e8f0; display: inline-block; }}
            a {{ text-decoration: none; color: #0f172a; font-weight: 600; font-size: 1.05em; transition: color 0.2s; }}
            a:hover {{ color: #2563eb; }}

            /* LEYENDA */
            .legend-box {{ background: #f8fafc; padding: 25px 30px; border-top: 2px solid #e2e8f0; }}
            .legend-title {{ font-weight: 700; margin-bottom: 20px; color: #334155; display: block; font-size: 1.1em; }}
            .legend-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 25px; }}
            .legend-item {{ display: flex; flex-direction: column; gap: 10px; font-size: 0.9em; color: #64748b; line-height: 1.5; }}

            .footer {{ text-align: center; padding: 25px; background: #f1f5f9; color: #64748b; font-size: 0.9em; border-top: 1px solid #e2e8f0; }}
            @keyframes pulse {{ 0% {{ box-shadow: 0 0 0 0 rgba(251, 146, 60, 0.4); }} 70% {{ box-shadow: 0 0 0 10px rgba(251, 146, 60, 0); }} 100% {{ box-shadow: 0 0 0 0 rgba(251, 146, 60, 0); }} }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>
                🛡️ Monitor de Normas Oficiales
                <span>Centro de Control de Vigilancia Normativa</span>
            </h1>
            <table>
                <thead>
                    <tr>
                        <th style="width:40%">Norma / Radar</th>
                        <th style="width:30%">Objetivo Vigilado</th>
                        <th style="width:30%">Estado Actual</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for r in resultados_web:
        # Determinamos la clase CSS y el texto según el estado
        if r['es_radar']:
            if r['estado'] == "nueva_detectada":
                clase, texto = "new", "🚀 ¡NUEVA VERSIÓN DETECTADA!"
            else:
                clase, texto = "radar", "📡 Escaneando futuras versiones..."
        else:
            if r['estado'] == "ok":
                clase, texto = "ok", "✅ VIGENTE"
            elif r['estado'] == "warn":
                clase, texto = "warn", "⚠️ EN TRANSICIÓN (Válida)"
            else:
                clase, texto = "error", "🚨 ALERTA / CAMBIO DETECTADO"
            
        html_final += f"""
        <tr>
            <td><a href="{r['url']}" target="_blank">{r['nombre']}</a></td>
            <td><span class="version-tag">{r['version']}</span></td>
            <td><span class="badge {clase}">{texto}</span></td>
        </tr>
        """

    html_final += f"""
                </tbody>
            </table>

            <div class="legend-box">
                <span class="legend-title">📖 Guía de Estados del Monitor:</span>
                <div class="legend-grid">
                    <div class="legend-item">
                        <div><span class="badge ok">✅ VIGENTE</span></div>
                        <span>La norma está actualizada. El robot ha confirmado la presencia de la versión oficial en la fuente.</span>
                    </div>
                    <div class="legend-item">
                        <div><span class="badge warn">⚠️ EN TRANSICIÓN</span></div>
                        <span>Existe una nueva versión publicada, pero esta sigue siendo válida temporalmente durante el periodo de adaptación.</span>
                    </div>
                    <div class="legend-item">
                        <div><span class="badge error">🚨 ALERTA / CAMBIO</span></div>
                        <span>La versión vigilada no se encuentra. Requiere revisión inmediata por posible entrada en vigor de nueva norma.</span>
                    </div>
                    <div class="legend-item">
                        <div><span class="badge radar">📡 RADAR FUTURO</span></div>
                        <span>Escáner activo buscando menciones a futuras versiones aún no publicadas oficialmente.</span>
                    </div>
                </div>
            </div>

            <div class="footer">
                Última sincronización del sistema: <strong>{fecha}</strong> (Horario España Peninsular)
            </div>
        </div>
    </body>
    </html>
    """
    
    guardar_web(html_final)

if __name__ == "__main__":
    revisar_normas()
