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
    print("--- INICIANDO ROBOT V4.0 (FIX AMARILLO) ---")
    
    try:
        with open('normas.json', 'r', encoding='utf-8') as f:
            lista_normas = json.load(f)
    except Exception as e:
        print(f"Error cargando JSON: {e}")
        return

    resultados_web = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    for norma in lista_normas:
        nombre = norma.get('nombre')
        busqueda = norma.get('texto_a_buscar')
        # Detectamos el modo ANTES de cualquier otra cosa
        es_transicion = norma.get('modo') == 'transicion'
        es_radar = norma.get('modo') == 'detectar_nueva'
        
        estado_final = "error"
        
        try:
            r = requests.get(norma['url'], headers=headers, timeout=20)
            if r.status_code == 200:
                encontrado = bool(re.search(re.escape(busqueda), r.text, re.IGNORECASE))
                
                if es_radar:
                    estado_final = "nueva_detectada" if encontrado else "ok"
                else:
                    if encontrado:
                        # AQUÍ ESTÁ EL TRUCO: Si es transición, forzamos 'warn'
                        estado_final = "warn" if es_transicion else "ok"
                    else:
                        estado_final = "error"
            else:
                estado_final = "error"
        except:
            estado_final = "error"
        
        resultados_web.append({
            "nombre": nombre,
            "url": norma['url'],
            "version": busqueda,
            "estado": estado_final,
            "es_radar": es_radar
        })
        time.sleep(1)

    # --- GENERAR HTML CON CSS ACTUALIZADO ---
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    html_final = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; background: #f4f7f9; padding: 20px; }}
            .container {{ max-width: 900px; margin: auto; background: white; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); overflow: hidden; }}
            h1 {{ text-align: center; color: #1e293b; padding: 20px; border-bottom: 1px solid #eee; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 15px; text-align: left; border-bottom: 1px solid #f1f1f1; }}
            th {{ background: #f8fafc; color: #64748b; font-size: 12px; text-transform: uppercase; }}
            .badge {{ padding: 6px 12px; border-radius: 20px; font-weight: bold; font-size: 11px; display: inline-block; }}
            .ok {{ background: #dcfce7; color: #166534; }}
            .warn {{ background: #fef9c3 !important; color: #854d0e !important; border: 1px solid #fde047; }} /* Forzado */
            .error {{ background: #fee2e2; color: #991b1b; }}
            .radar {{ background: #e0f2fe; color: #075985; }}
            .new {{ background: #ffedd5; color: #9a3412; animation: pulse 2s infinite; }}
            @keyframes pulse {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.7; }} 100% {{ opacity: 1; }} }}
            a {{ text-decoration: none; color: #1e293b; font-weight: 600; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛡️ Monitor de Normas Oficiales</h1>
            <table>
                <tr><th>Norma / Radar</th><th>Objetivo</th><th>Estado</th></tr>
    """
    
    for r in resultados_web:
        if r['es_radar']:
            clase, texto = ("new", "🚀 PUBLICADA") if r['estado'] == "nueva_detectada" else ("radar", "📡 ESCANEANDO")
        else:
            if r['estado'] == "ok": clase, texto = "ok", "✅ VIGENTE"
            elif r['estado'] == "warn": clase, texto = "warn", "⚠️ TRANSICIÓN"
            else: clase, texto = "error", "🚨 ALERTA"
            
        html_final += f"""
        <tr>
            <td><a href="{r['url']}">{r['nombre']}</a></td>
            <td style="color:gray; font-size:12px;">{r['version']}</td>
            <td><span class="badge {clase}">{texto}</span></td>
        </tr>
        """

    html_final += f"</table><div style='padding:20px; text-align:center; color:gray; font-size:11px;'>Actualizado: {fecha}</div></div></body></html>"
    guardar_web(html_final)

if __name__ == "__main__":
    revisar_normas()
