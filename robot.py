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
    
    # 1. CREAMOS UNA WEB PROVISIONAL (Salvavidas)
    # Si el robot falla después, al menos veremos esto en la web.
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    html_provisional = f"""
    <h1>📊 El Robot está trabajando...</h1>
    <p>Iniciado a las: {fecha}</p>
    <p>Si ves esto, es que el archivo se ha creado correctamente.</p>
    """
    guardar_web(html_provisional)
    print("--- Web provisional creada (index.html) ---")

    # 2. CARGAMOS LAS NORMAS
    try:
        with open('normas.json', 'r') as f:
            lista_normas = json.load(f)
    except Exception as e:
        print(f"ERROR FATAL: No encuentro normas.json. {e}")
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
                if norma['texto_a_buscar'] in respuesta.text:
                    estado_ok = True
                    print(f"   [OK]")
                else:
                    print(f"   [ALERTA] Texto no encontrado")
            else:
                print(f"   [ERROR] Web caída: {respuesta.status_code}")

        except Exception as e:
            print(f"   [ERROR] Excepción: {e}")
        
        resultados_web.append({
            "nombre": norma['nombre'],
            "url": norma['url'],
            "texto": norma['texto_a_buscar'],
            "estado": estado_ok
        })
        time.sleep(1)

    # 4. GENERAMOS LA WEB FINAL BONITA
    html_final = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Estado Normas Alimentarias</title>
        <style>
            body {{ font-family: sans-serif; background: #f4f4f9; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }}
            h1 {{ text-align: center; color: #2c3e50; }}
            .card {{ background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 15px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #007bff; color: white; }}
            .ok {{ color: #28a745; font-weight: bold; }}
            .error {{ color: #dc3545; font-weight: bold; }}
            a {{ text-decoration: none; color: #007bff; }}
        </style>
    </head>
    <body>
        <h1>📊 Monitor de Normas</h1>
        <div class="card">
            <table>
                <thead>
                    <tr><th>Norma</th><th>Estado</th></tr>
                </thead>
                <tbody>
    """
    
    for r in resultados_web:
        icono = "✅ Vigente" if r['estado'] else "🚨 REVISAR"
        clase = "ok" if r['estado'] else "error"
        html_final += f"<tr><td><a href='{r['url']}'>{r['nombre']}</a></td><td class='{clase}'>{icono}</td></tr>"

    html_final += f"""
                </tbody>
            </table>
        </div>
        <p style="text-align:center; color:#777; margin-top:20px;">Actualizado: {fecha}</p>
    </body>
    </html>
    """
    
    guardar_web(html_final)
    print("--- Web Final Guardada Correctamente ---")

if __name__ == "__main__":
    revisar_normas()
