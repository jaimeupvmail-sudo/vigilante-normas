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
    print("--- EJECUTANDO REVISIÓN CRÍTICA ---")
    
    try:
        with open('normas.json', 'r', encoding='utf-8') as f:
            lista_normas = json.load(f)
    except Exception as e:
        print(f"ERROR AL LEER JSON: {e}")
        return

    resultados = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

    for norma in lista_normas:
        nombre = norma.get('nombre', 'Sin nombre')
        url = norma.get('url', '')
        busqueda = norma.get('texto_a_buscar', '')
        # FORZAMOS LA LECTURA DEL MODO
        modo_especial = norma.get('modo', '').strip().lower()
        
        print(f"Analizando: {nombre} | Modo configurado: {modo_especial}")
        
        estado_final = "error"
        
        try:
            r = requests.get(url, headers=headers, timeout=25)
            if r.status_code == 200:
                encontrado = bool(re.search(re.escape(busqueda), r.text, re.IGNORECASE))
                
                if encontrado:
                    # SI EL MODO ES TRANSICION, NO HAY DUDA: VA A AMARILLO
                    if modo_especial == "transicion":
                        estado_final = "warn"
                    else:
                        estado_final = "ok"
                else:
                    estado_final = "error"
            else:
                estado_final = "error"
        except Exception as e:
            print(f"Error de red en {nombre}: {e}")
            estado_final = "error"
        
        resultados.append({
            "nombre": nombre,
            "url": url,
            "version": busqueda,
            "estado": estado_final
        })
        time.sleep(1)

    # GENERACIÓN DEL HTML
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Monitor de Normas</title>
        <style>
            body {{ font-family: sans-serif; background: #f4f7f6; padding: 20px; }}
            .card {{ max-width: 850px; margin: auto; background: white; border-radius: 12px; padding: 25px; box-shadow: 0 5px 15px rgba(0,0,0,0.08); }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th {{ background: #f8fafc; padding: 15px; text-align: left; color: #64748b; font-size: 12px; text-transform: uppercase; }}
            td {{ padding: 18px 15px; border-bottom: 1px solid #f1f5f9; }}
            .badge {{ padding: 6px 14px; border-radius: 50px; font-weight: bold; font-size: 11px; }}
            .ok {{ background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }}
            .warn {{ background: #fef9c3; color: #854d0e; border: 1px solid #fde047; }}
            .error {{ background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }}
            a {{ color: #1e293b; text-decoration: none; font-weight: 600; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🛡️ Monitor de Normas Oficiales</h1>
            <table>
                <thead>
                    <tr><th>Norma / Estándar</th><th>Versión</th><th>Estado</th></tr>
                </thead>
                <tbody>
    """
    
    for res in resultados:
        if res['estado'] == "ok":
            clase, texto = "ok", "✅ VIGENTE"
        elif res['estado'] == "warn":
            clase, texto = "warn", "⚠️ EN TRANSICIÓN"
        else:
            clase, texto = "error", "🚨 ALERTA CAMBIO"
            
        html += f"""
        <tr>
            <td><a href="{res['url']}" target="_blank">{res['nombre']}</a></td>
            <td style="font-family:monospace; color:#64748b;">{res['version']}</td>
            <td><span class="badge {clase}">{texto}</span></td>
        </tr>
        """

    html += f"""
                </tbody>
            </table>
            <p style="text-align:center; color:#94a3b8; font-size:12px; margin-top:30px;">
                Última sincronización: {fecha}
            </p>
        </div>
    </body>
    </html>
    """
    guardar_web(html)

if __name__ == "__main__":
    revisar_normas()
