import requests
import json
import os
import time
from datetime import datetime
import urllib.parse

def guardar_web(html_content):
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

def revisar_normas():
    print("--- INICIANDO ROBOT ---")
    
    # 1. CREAMOS WEB PROVISIONAL
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    html_provisional = f"""
    <h1>📊 Actualizando datos...</h1>
    <p>El robot está trabajando. Hora inicio: {fecha}</p>
    """
    guardar_web(html_provisional)

    # 2. CARGAMOS NORMAS
    try:
        with open('normas.json', 'r') as f:
            lista_normas = json.load(f)
    except Exception as e:
        print(f"ERROR: {e}")
        return

    resultados_web = []
    
    # 3. ESCANEAMOS
    for norma in lista_normas:
        print(f"Revisando: {norma['nombre']}...")
        estado_ok = False
        
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            respuesta = requests.get(norma['url'], headers=headers, timeout=15)
            
            if respuesta.status_code == 200:
                # Buscamos el texto exacto (la versión)
                if norma['texto_a_buscar'] in respuesta.text:
                    estado_ok = True
                    print(f"   [OK] Encontrado: {norma['texto_a_buscar']}")
                else:
                    print(f"   [ALERTA] No veo la versión: {norma['texto_a_buscar']}")
            else:
                print(f"   [ERROR] Web caída: {respuesta.status_code}")

        except Exception as e:
            print(f"   [ERROR] Excepción: {e}")
        
        resultados_web.append({
            "nombre": norma['nombre'],
            "url": norma['url'],
            "version": norma['texto_a_buscar'], # AQUÍ GUARDAMOS LA VERSIÓN
            "estado": estado_ok
        })
        time.sleep(1)

    # 4. GENERAMOS LA WEB FINAL (CON 3 COLUMNAS)
    html_final = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Monitor de Normas</title>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; background: #f4f4f9; color: #333; max-width: 900px; margin: 0 auto; padding: 20px; }}
            h1 {{ text-align: center; color: #2c3e50; margin-bottom: 30px; }}
            .card {{ background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 15px; text-align: left; border-bottom: 1px solid #eee; }}
            th {{ background-color: #007bff; color: white; text-transform: uppercase; font-size: 0.85em; letter-spacing: 1px; }}
            tr:hover {{ background-color: #f9f9f9; }}
            .version-tag {{ background: #eef2f7; padding: 4px 8px; border-radius: 4px; font-family: monospace; color: #555; font-size: 0.9em; }}
            .ok {{ color: #28a745; font-weight: bold; }}
            .error {{ color: #dc3545; font-weight: bold; }}
            a {{ text-decoration: none; color: #2c3e50; font-weight: 600; }}
            a:hover {{ color: #007bff; }}
            .footer {{ text-align: center; margin-top: 30px; font-size: 0.8em; color: #888; }}
        </style>
    </head>
    <body>
        <h1>📊 Monitor de Normas Oficiales</h1>
        <div class="card">
            <table>
                <thead>
                    <tr>
                        <th style="width: 40%">Norma / Estándar</th>
                        <th style="width: 30%">Versión Vigente</th>
                        <th style="width: 30%">Estado</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for r in resultados_web:
        icono = "✅ OK" if r['estado'] else "🚨 ALERTA"
        clase = "ok" if r['estado'] else "error"
        
        # Aquí pintamos las 3 columnas
        html_final += f"""
        <tr>
            <td><a href='{r['url']}' target='_blank'>{r['nombre']}</a></td>
            <td><span class="version-tag">{r['version']}</span></td>
            <td class="{clase}">{icono}</td>
        </tr>
        """

    html_final += f"""
                </tbody>
            </table>
        </div>
        <div class="footer">
            Última verificación: {fecha} <br>
            Sistema de vigilancia automática.
        </div>
    </body>
    </html>
    """
    
    guardar_web(html_final)
    print("--- Web Actualizada con Versiones ---")

if __name__ == "__main__":
    revisar_normas()
