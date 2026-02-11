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
    print("--- INICIANDO VERIFICACIÓN ---")
    
    try:
        with open('normas.json', 'r') as f:
            lista_normas = json.load(f)
    except Exception as e:
        print(f"Error cargando JSON: {e}")
        return

    resultados = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

    for norma in lista_normas:
        nombre = norma.get('nombre')
        url = norma.get('url')
        busqueda = norma.get('texto_a_buscar')
        # Aquí leemos si es transicion o no
        es_transicion = norma.get('modo') == 'transicion'
        
        print(f"Comprobando {nombre}...")
        
        try:
            r = requests.get(url, headers=headers, timeout=20)
            if r.status_code == 200:
                # Si encontramos el texto...
                if re.search(re.escape(busqueda), r.text, re.IGNORECASE):
                    # Si es modo transicion -> warn, si no -> ok
                    estado_final = "warn" if es_transicion else "ok"
                else:
                    estado_final = "error"
            else:
                estado_final = "error"
        except:
            estado_final = "error"
        
        resultados.append({
            "nombre": nombre,
            "url": url,
            "version": busqueda,
            "estado": estado_final
        })
        time.sleep(1)

    # Generar HTML con estilos visuales claros
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: sans-serif; background: #f4f4f9; padding: 20px; }}
            .card {{ max-width: 800px; margin: auto; background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            .badge {{ padding: 6px 12px; border-radius: 20px; font-weight: bold; font-size: 11px; text-transform: uppercase; }}
            .ok {{ background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }}
            .warn {{ background: #fef9c3; color: #854d0e; border: 1px solid #fde047; }}
            .error {{ background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Monitor de Normas</h2>
            <table>
                <tr><th>Norma</th><th>Versión</th><th>Estado</th></tr>
    """
    
    for res in resultados:
        if res['estado'] == "ok":
            clase, texto = "ok", "✅ VIGENTE"
        elif res['estado'] == "warn":
            clase, texto = "warn", "⚠️ TRANSICIÓN"
        else:
            clase, texto = "error", "🚨 ALERTA"
            
        html += f"""
        <tr>
            <td><a href="{res['url']}">{res['nombre']}</a></td>
            <td>{res['version']}</td>
            <td><span class="badge {clase}">{texto}</span></td>
        </tr>
        """

    html += f"</table><p style='color:gray; font-size:11px;'>Actualizado: {fecha}</p></div></body></html>"
    guardar_web(html)

if __name__ == "__main__":
    revisar_normas()
