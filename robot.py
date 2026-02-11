import requests
import json
import os
import time
from datetime import datetime

# Forzamos hora española
os.environ['TZ'] = 'Europe/Madrid'
if hasattr(time, 'tzset'):
    time.tzset()

def revisar_normas():
    print("--- INICIANDO PRUEBA FORZADA ---")
    
    try:
        with open('normas.json', 'r', encoding='utf-8') as f:
            normas = json.load(f)
    except Exception as e:
        print(f"Error: {e}")
        return

    resultados = []
    for n in normas:
        # Lógica ultra-simple:
        # Si en el JSON pone "modo": "transicion", el estado es 'amarillo'
        if n.get('modo') == 'transicion':
            estado = 'amarillo'
        else:
            estado = 'verde' # Simplificamos para la prueba
            
        resultados.append({
            "nombre": n.get('nombre'),
            "version": n.get('texto_a_buscar'),
            "estado": estado
        })

    # Generar HTML
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: sans-serif; padding: 50px; background: #f0f0f0; }}
            .caja {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
            .bloque {{ padding: 10px; margin: 10px 0; border-radius: 5px; font-weight: bold; }}
            .verde {{ background: #dcfce7; color: #166534; }}
            .amarillo {{ background: #fef9c3; color: #854d0e; border: 2px solid orange; }}
        </style>
    </head>
    <body>
        <div class="caja">
            <h1>PRUEBA DE COLORES</h1>
            <p>Hora del robot: {fecha}</p>
    """
    for r in resultados:
        clase = "amarillo" if r['estado'] == 'amarillo' else "verde"
        texto = "⚠️ TRANSICIÓN" if r['estado'] == 'amarillo' else "✅ VIGENTE"
        html += f'<div class="bloque {clase}">{r["nombre"]} - {r["version"]} -> {texto}</div>'
    
    html += "</div></body></html>"
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    revisar_normas()
