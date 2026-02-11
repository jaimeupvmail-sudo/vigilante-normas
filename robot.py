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
    print("--- INICIANDO ROBOT ---")
    
    try:
        with open('normas.json', 'r') as f:
            lista_normas = json.load(f)
    except Exception as e:
        print(f"ERROR: {e}")
        return

    resultados_web = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

    for norma in lista_normas:
        print(f"Escaneando: {norma['nombre']}...")
        
        # Leemos el modo: si es 'transicion', el estado final será 'warn' (amarillo)
        es_transicion = norma.get('modo') == 'transicion'
        estado_final = "error"
        
        try:
            respuesta = requests.get(norma['url'], headers=headers, timeout=20)
            if respuesta.status_code == 200:
                encontrado = bool(re.search(re.escape(norma['texto_a_buscar']), respuesta.text, re.IGNORECASE))
                if encontrado:
                    estado_final = "warn" if es_transicion else "ok"
                else:
                    estado_final = "error"
            else:
                estado_final = "error"
        except:
            estado_final = "error"
        
        resultados_web.append({
            "nombre": norma['nombre'],
            "url": norma['url'],
            "version": norma['texto_a_buscar'],
            "estado": estado_final
        })
        time.sleep(1)

    # Generación de HTML
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    html_final = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: sans-serif; background: #f0f2f5; padding: 20px; }}
            .container {{ max-width: 800px; margin: auto; background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 15px; text-align: left; border-bottom: 1px solid #eee; }}
            .badge {{ padding: 5px 12px; border-radius: 15px; font-weight: bold; font-size: 12px; }}
            .ok {{ background: #dcfce7; color: #166534; }}
            .warn {{ background: #fef9c3; color: #854d0e; }}
            .error {{ background: #fee2e2; color: #991b1b; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Monitor de Normas</h1>
            <table>
                <tr><th>Norma</th><th>Versión</th><th>Estado</th></tr>
    """
    
    for r in resultados_web:
        if r['estado'] == "ok":
            clase, texto = "ok", "✅ VIGENTE"
        elif r['estado'] == "warn":
            clase, texto = "warn", "⚠️ TRANSICIÓN"
        else:
            clase, texto = "error", "🚨 ALERTA"
            
        html_final += f"""
        <tr>
            <td><a href="{r['url']}">{r['nombre']}</a></td>
            <td>{r['version']}</td>
            <td><span class="badge {clase}">{texto}</span></td>
        </tr>
        """

    html_final += f"</table><p>Última actualización: {fecha}</p></div></body></html>"
    guardar_web(html_final)

if __name__ == "__main__":
    revisar_normas()
