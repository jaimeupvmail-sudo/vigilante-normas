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
    print("--- INICIANDO ROBOT INTELIGENTE ---")
    
    try:
        with open('normas.json', 'r') as f:
            lista_normas = json.load(f)
    except Exception as e:
        print(f"ERROR: {e}")
        return

    resultados_web = []
    
    # Cabeceras para que las webs no nos bloqueen
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8'
    }

    for norma in lista_normas:
        print(f"Escaneando: {norma['nombre']}...")
        estado_ok = False
        es_transicion = norma.get('modo') == 'transicion'
        
        try:
            # Usamos una sesión para mantener cookies (ayuda con IFS)
            session = requests.Session()
            respuesta = session.get(norma['url'], headers=headers, timeout=25)
            
            if respuesta.status_code == 200:
                contenido = respuesta.text
                busqueda = norma['texto_a_buscar']
                
                # Buscamos de forma insensible a mayúsculas/minúsculas y espacios
                if re.search(re.escape(busqueda), contenido, re.IGNORECASE):
                    estado_ok = True
                    print(f"   [OK] Detectado: {busqueda}")
                else:
                    print(f"   [ALERTA] No se encuentra: {busqueda}")
            else:
                print(f"   [ERROR] HTTP {respuesta.status_code}")

        except Exception as e:
            print(f"   [ERROR] Error de conexión: {e}")
        
        resultados_web.append({
            "nombre": norma['nombre'],
            "url": norma['url'],
            "version": norma['texto_a_buscar'],
            "estado": estado_ok,
            "transicion": es_transicion
        })
        time.sleep(2) # Pausa amigable para no ser bloqueados

    # --- GENERAR WEB CON SEMÁFORO ---
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    html_final = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Vigilancia Normativa</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f4f7f9; padding: 20px; }}
            .container {{ max-width: 900px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); overflow: hidden; }}
            h1 {{ text-align: center; color: #1e293b; padding: 20px; margin: 0; background: #fff; border-bottom: 1px solid #e2e8f0; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th {{ background: #f8fafc; color: #64748b; padding: 15px; text-align: left; font-size: 13px; text-transform: uppercase; }}
            td {{ padding: 18px 15px; border-bottom: 1px solid #f1f5f9; }}
            .badge {{ padding: 6px 12px; border-radius: 20px; font-weight: 700; font-size: 12px; display: inline-block; }}
            .ok {{ background: #dcfce7; color: #166534; }}
            .warn {{ background: #fef9c3; color: #854d0e; }}
            .error {{ background: #fee2e2; color: #991b1b; }}
            .version {{ font-family: monospace; background: #f1f5f9; padding: 3px 6px; border-radius: 4px; color: #475569; }}
            a {{ text-decoration: none; color: #1e293b; font-weight: 600; }}
            .footer {{ text-align: center; padding: 20px; color: #94a3b8; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 Monitor de Normas Oficiales</h1>
            <table>
                <thead>
                    <tr><th>Norma / Estándar</th><th>Versión Vigilada</th><th>Estado</th></tr>
                </thead>
                <tbody>
    """
    
    for r in resultados_web:
        if r['estado']:
            clase, texto = ("warn", "⚠️ TRANSICIÓN") if r['transicion'] else ("ok", "✅ VIGENTE")
        else:
            clase, texto = "error", "🚨 ALERTA CAMBIO"
        
        html_final += f"""
        <tr>
            <td><a href="{r['url']}" target="_blank">{r['nombre']}</a></td>
            <td><span class="version">{r['version']}</span></td>
            <td><span class="badge {clase}">{texto}</span></td>
        </tr>
        """

    html_final += f"""
                </tbody>
            </table>
            <div class="footer">Última actualización: {fecha}</div>
        </div>
    </body>
    </html>
    """
    guardar_web(html_final)

if __name__ == "__main__":
    revisar_normas()
