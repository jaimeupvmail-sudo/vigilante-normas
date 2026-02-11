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
    print("--- INICIANDO ROBOT CON SEMÁFORO TRICOLOR ---")
    
    try:
        with open('normas.json', 'r') as f:
            lista_normas = json.load(f)
    except Exception as e:
        print(f"ERROR: {e}")
        return

    resultados_web = []
    
    # Cabeceras para simular ser un humano (Crucial para IFS/FSSC)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8'
    }

    for norma in lista_normas:
        print(f"Escaneando: {norma['nombre']}...")
        
        # Detectamos si has activado el modo amarillo en el JSON
        es_transicion = norma.get('modo') == 'transicion'
        
        estado_final = "error" # Por defecto
        
        try:
            session = requests.Session()
            respuesta = session.get(norma['url'], headers=headers, timeout=25)
            
            if respuesta.status_code == 200:
                contenido = respuesta.text
                busqueda = norma['texto_a_buscar']
                
                # Buscamos el texto (insensible a mayúsculas)
                encontrado = bool(re.search(re.escape(busqueda), contenido, re.IGNORECASE))

                if encontrado:
                    # SI LO ENCUENTRA, DECIDIMOS SI ES VERDE O AMARILLO
                    if es_transicion:
                        estado_final = "warn" # Amarillo
                        print(f"   [AMARILLO] Encontrado, pero en transición.")
                    else:
                        estado_final = "ok"   # Verde
                        print(f"   [OK] Vigente y correcto.")
                else:
                    # SI NO LO ENCUENTRA -> ROJO
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
            "estado_final": estado_final
        })
        time.sleep(2)

    # --- DISEÑO DE LA WEB ---
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    html_final = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Vigilancia Normativa</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f1f5f9; padding: 20px; }}
            .container {{ max-width: 900px; margin: 0 auto; background: white; border-radius: 16px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); overflow: hidden; }}
            h1 {{ text-align: center; color: #0f172a; padding: 30px; margin: 0; border-bottom: 1px solid #e2e8f0; letter-spacing: -0.5px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th {{ background: #f8fafc; color: #64748b; padding: 20px; text-align: left; font-size: 12px; text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em; }}
            td {{ padding: 20px; border-bottom: 1px solid #f1f5f9; vertical-align: middle; }}
            tr:last-child td {{ border-bottom: none; }}
            
            .badge {{ padding: 6px 12px; border-radius: 99px; font-weight: 700; font-size: 13px; display: inline-flex; align-items: center; gap: 8px; }}
            
            /* ESTILOS DEL SEMÁFORO */
            .ok {{ background: #dcfce7; color: #15803d; border: 1px solid #bbf7d0; }}    /* Verde */
            .warn {{ background: #fef9c3; color: #a16207; border: 1px solid #fde047; }}  /* Amarillo */
            .error {{ background: #fee2e2; color: #b91c1c; border: 1px solid #fecaca; }} /* Rojo */

            .version-tag {{ font-family: 'SF Mono', Consolas, monospace; background: #f1f5f9; padding: 4px 8px; border-radius: 6px; color: #475569; font-size: 13px; border: 1px solid #e2e8f0; }}
            a {{ text-decoration: none; color: #0f172a; font-weight: 600; font-size: 15px; }}
            a:hover {{ color: #2563eb; text-decoration: underline; }}
            .footer {{ text-align: center; padding: 30px; color: #94a3b8; font-size: 13px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛡️ Monitor de Normas Oficiales</h1>
            <table>
                <thead>
                    <tr><th style="width:45%">Norma / Estándar</th><th style="width:25%">Versión Vigilada</th><th style="width:30%">Estado</th></tr>
                </thead>
                <tbody>
    """
    
    for r in resultados_web:
        # LÓGICA DE ICONOS Y TEXTOS
        if r['estado_final'] == "ok":
            clase = "ok"
            texto = "✅ VIGENTE"
        elif r['estado_final'] == "warn":
            clase = "warn"
            texto = "⚠️ EN TRANSICIÓN"
        else:
            clase = "error"
            texto = "🚨 ALERTA / CAMBIO"
        
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
            <div class="footer">
                Última verificación: <strong>{fecha}</strong>
            </div>
        </div>
    </body>
    </html>
    """
    guardar_web(html_final)

if __name__ == "__main__":
    revisar_normas()
