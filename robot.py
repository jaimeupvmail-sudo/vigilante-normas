import requests
import json
import time

# Colores
VERDE = '\033[92m'
ROJO = '\033[91m'
AMARILLO = '\033[93m'
RESET = '\033[0m'

def revisar_normas():
    with open('normas.json', 'r') as f:
        lista_normas = json.load(f)
    
    print("--- INICIANDO MODO DETECTIVE ---")

    for norma in lista_normas:
        print(f"\nRevisando: {norma['nombre']}...")
        
        try:
            # Usamos un User-Agent más completo para parecer un navegador real de Chrome
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            respuesta = requests.get(norma['url'], headers=headers, timeout=15)
            
            if respuesta.status_code == 200:
                contenido = respuesta.text
                
                # BUSQUEDA
                if norma['texto_a_buscar'] in contenido:
                    print(f"{VERDE}[OK] ENCONTRADO:{RESET} {norma['texto_a_buscar']}")
                else:
                    print(f"{ROJO}[ALERTA] NO ENCONTRADO:{RESET} {norma['texto_a_buscar']}")
                    # AQUÍ ESTÁ LA MAGIA: Nos dirá qué está viendo realmente
                    print(f"{AMARILLO}--- ¿Qué ve el robot? (Primeros 100 caracteres) ---{RESET}")
                    print(contenido[:100].replace('\n', ' ')) # Muestra un trocito de la web
                    print(f"{AMARILLO}---------------------------------------------------{RESET}")
            else:
                print(f"{ROJO}[ERROR]{RESET} Código de error: {respuesta.status_code}")

        except Exception as e:
            print(f"{ROJO}[ERROR TÉCNICO]{RESET} {e}")
            
        # Esperamos 2 segundos entre web y web para no saturar
        time.sleep(2)

if __name__ == "__main__":
    revisar_normas()
