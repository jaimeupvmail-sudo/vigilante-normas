import requests
import json
import os
import time
import re
from datetime import datetime

def guardar_web(html_content):
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

def revisar_normas():
    print("--- INICIANDO ROBOT CON RADAR DE NOVEDADES ---")
    
    try:
        with open('normas.json', 'r') as f:
            lista_normas = json.load(f)
    except Exception as e:
        print(f"ERROR: {e}")
        return

    resultados_web = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8'
    }

    for norma in lista_normas:
        print(f"Escaneando: {norma['nombre']}...")
        
        # Tipos de modos especiales
        es_transicion = norma.get('modo') == 'transicion'
        es_radar = norma.get('modo') == 'detectar_nueva' # Nuevo modo espía
        
        estado_final = "error" # Por defecto
        
        try:
            session = requests.Session()
            respuesta = session.get(norma['url'], headers=headers, timeout=25)
            
            if respuesta.status_code == 200:
                contenido = respuesta.text
                busqueda = norma['texto_a_buscar']
                encontrado = bool(re.search(re.escape(busqueda), contenido, re.IGNORECASE))

                if es_radar:
                    # LÓGICA INVERSA PARA EL RADAR
                    if encontrado:
                        # Si lo encuentra, es que ha salido la nueva -> ALERTA
                        estado_final = "nueva_detectada"
                        print(f"   [ALERTA] ¡NUEVA VERSIÓN DETECTADA!: {busqueda}")
                    else:
                        # Si NO lo encuentra, todo sigue igual -> OK
                        estado_final = "ok"
                        print(f"   [OK] Aún no hay rastro de: {busqueda}")
                
                else:
                    # LÓGICA NORMAL (Vigilar vigencia)
                    if encontrado:
                        estado_final = "ok"
                        print(f"   [OK] Detectado: {busqueda}")
                    else:
                        estado_final = "error"
                        print(f"   [ALERTA] No se encuentra: {busqueda}")
            else:
                print(f"   [ERROR] HTTP {respuesta.status_code}")
                estado_final = "error"

        except Exception as e:
            print(f"   [ERROR] Error de conexión: {e}")
            estado_final = "error"
        
        resultados_web.append({
            "nombre": norma['nombre'],
            "url": norma['url'],
            "version": norma['texto_a_buscar'],
            "estado_final": estado_final,
            "transicion": es_transicion,
            "es_radar": es_radar
        })
        time.sleep(2)

    # --- GENERAR WEB ---
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    html_final = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Vigilancia Normativa</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f8fafc; padding: 20px; }}
            .container {{ max-width: 950px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); overflow: hidden; }}
            h1 {{ text-align: center; color: #1e293b; padding: 25px; margin: 0; border-bottom: 1px solid #e2e8f0; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th {{ background: #f1f5f9; color: #475569; padding: 16px; text-align: left; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; }}
            td {{ padding: 18px 16px; border-bottom: 1px solid #f1f5f9; vertical-align: middle; }}
            
            .badge {{ padding: 6px 12px; border-radius: 99px; font-weight: 700; font-size: 12px; display: inline-flex; align-items: center; gap: 6px; }}
            .ok {{ background: #dcfce7; color: #166534; }}
            .warn {{ background: #fef9c3; color: #854d0e; }}
            .error {{ background: #fee2e2; color: #991b1b; }}
            .radar {{ background: #e0f2fe; color: #075985; border: 1px solid #bae6fd; }} /* Azul para el radar */
            .new-release {{ background: #ffedd5; color: #9a3412; border: 1px solid #fed7aa; animation: pulse 2s infinite; }} 

            .version-tag {{ font-family: 'SF Mono', Consolas, monospace; background: #f1f5f9; padding: 4px 8px; border-radius: 6px; color: #64748b; font-size: 13px; }}
            a {{ text-decoration: none; color: #0f172a; font-weight: 600; transition: color 0.2s; }}
            a:hover {{ color: #2563eb; }}
            
            @keyframes pulse {{
                0% {{ box-shadow: 0 0 0 0 rgba(255, 165, 0, 0.4); }}
                70% {{ box-shadow: 0 0 0 10px rgba(255, 165, 0, 0); }}
                100% {{ box-shadow: 0 0 0 0 rgba(255, 165, 0, 0); }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛡️ Monitor de Normas Oficiales</h1>
            <table>
                <thead>
                    <tr><th>Norma / Radar</th><th>Objetivo</th><th>Estado</th></tr>
                </thead>
                <tbody>
    """
    
    for r in resultados_web:
        # LÓGICA VISUAL
        if r['es_radar']:
            # Diseño específico para Radares
            if r['estado_final'] == "nueva_detectada":
                clase = "new-release"
                texto = "🚀 ¡PUBLICADA!" # Se encontró lo que buscábamos (IFS 9)
            else:
                clase = "radar"
                texto = "📡 Escaneando..." # No se encontró nada nuevo
        else:
            # Diseño normal
            if r['estado_final'] == "ok":
                if r['transicion']:
                    clase, texto = "warn", "⚠️ TRANSICIÓN"
                else:
                    clase, texto = "ok", "✅ VIGENTE"
            else:
                clase, texto = "error", "🚨 ALERTA CAMBIO"
        
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
            <div style="text-align:center; padding:20px; color:#94a3b8; font-size:12px;">
                Última actualización: {fecha}
            </div>
        </div>
    </body>
    </html>
    """
    guardar_web(html_final)

if __name__ == "__main__":
    revisar_normas()
