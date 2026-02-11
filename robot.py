import requests
import json
import os

# Colores para que se vea bonito en el log
VERDE = '\033[92m'
ROJO = '\033[91m'
RESET = '\033[0m'

def revisar_normas():
    # 1. Leemos la lista de normas
    with open('normas.json', 'r') as f:
        lista_normas = json.load(f)
    
    hay_cambios = False
    errores = False

    print("--- INICIANDO ESCANEO DE NORMAS ---")

    # 2. Revisamos una a una
    for norma in lista_normas:
        print(f"Revisando: {norma['nombre']}...")
        
        try:
            # El robot visita la web
            respuesta = requests.get(norma['url'], headers={'User-Agent': 'Mozilla/5.0'})
            
            if respuesta.status_code == 200:
                contenido = respuesta.text
                
                # BUSCAMOS EL TEXTO CLAVE
                if norma['texto_a_buscar'] in contenido:
                    print(f"{VERDE}[OK]{RESET} Sin cambios. Sigue vigente: {norma['texto_a_buscar']}")
                else:
                    print(f"{ROJO}[ALERTA]{RESET} ¡CAMBIO DETECTADO! El texto '{norma['texto_a_buscar']}' ha desaparecido.")
                    print(f"Verificar aquí: {norma['url']}")
                    hay_cambios = True
            else:
                print(f"{ROJO}[ERROR]{RESET} No se pudo entrar en la web. Código: {respuesta.status_code}")
                errores = True

        except Exception as e:
            print(f"{ROJO}[ERROR TÉCNICO]{RESET} {e}")
            errores = True
            
    print("--- FIN DEL ESCANEO ---")
    
    # Esto sirve para avisar al sistema si hubo problemas
    if hay_cambios:
        print("RESULTADO: ¡HAY NOVEDADES!")
        # Aquí en el futuro pondremos el envío de email
    else:
        print("RESULTADO: Todo tranquilo.")

if __name__ == "__main__":
    revisar_normas()
