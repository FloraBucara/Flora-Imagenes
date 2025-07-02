import os
import pandas as pd
import difflib

# CONFIGURA ESTA RUTA A TUS CARPETAS DE PLANTAS
ruta_base = "C:/Users/angie/Flora-Imagenes/plantas"
  # ⚠️ CAMBIA ESTO
excel_path = "nombres_cientificos1.xlsx"

# Leer nombres científicos del Excel
excel_data = pd.read_excel(excel_path)
excel_data.columns = excel_data.columns.str.strip().str.lower()
nombres_cientificos = excel_data['nombre_cientifico'].dropna().tolist()

# Renombrar carpetas e imágenes
for nombre_cientifico in nombres_cientificos:
    nombre_carpeta_objetivo = nombre_cientifico.replace(" ", "_")

    # Buscar carpeta más parecida en la ruta base
    carpetas_actuales = os.listdir(ruta_base)
    coincidencias = difflib.get_close_matches(nombre_carpeta_objetivo, carpetas_actuales, n=1, cutoff=0.6)

    if not coincidencias:
        print(f"❌ No se encontró carpeta parecida a: {nombre_cientifico}")
        continue

    carpeta_encontrada = coincidencias[0]
    ruta_actual = os.path.join(ruta_base, carpeta_encontrada)
    ruta_nueva = os.path.join(ruta_base, nombre_carpeta_objetivo)

    if ruta_actual != ruta_nueva:
        os.rename(ruta_actual, ruta_nueva)
        print(f"📁 Renombrada carpeta: {carpeta_encontrada} → {nombre_carpeta_objetivo}")

    # Renombrar imágenes dentro
    imagenes = sorted(os.listdir(ruta_nueva))
    extensiones_validas = [".jpg", ".jpeg", ".png", ".JPG"]
    contador = 1

    for archivo in imagenes:
        ext = os.path.splitext(archivo)[1].lower()
        if ext in extensiones_validas:
            nuevo_nombre = f"{nombre_carpeta_objetivo}_{contador:02d}{ext}"
            origen = os.path.join(ruta_nueva, archivo)
            destino = os.path.join(ruta_nueva, nuevo_nombre)
            if not os.path.exists(destino):
                os.rename(origen, destino)
                print(f"🖼️ Imagen: {archivo} → {nuevo_nombre}")
                contador += 1
            else:
                print(f"⚠️ Ya existe: {nuevo_nombre}, se omitió.")


