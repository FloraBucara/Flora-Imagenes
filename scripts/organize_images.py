"""
Script para organizar imágenes de plantas en la estructura correcta
"""

import os
import shutil
from PIL import Image
import json

def create_folder_structure(base_path="plantas", num_plants=500):
    """Crear estructura de carpetas para las plantas"""
    
    if not os.path.exists(base_path):
        os.makedirs(base_path)
    
    created_folders = []
    
    for i in range(1, num_plants + 1):
        folder_name = f"planta_{i:03d}"
        folder_path = os.path.join(base_path, folder_name)
        
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            created_folders.append(folder_path)
    
    print(f"✅ Creadas {len(created_folders)} carpetas")
    return created_folders

def optimize_image(image_path, max_size=(1920, 1920), quality=85):
    """Optimizar imagen para web"""
    try:
        with Image.open(image_path) as img:
            # Convertir a RGB si es necesario
            if img.mode in ('RGBA', 'LA', 'L'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img)
                img = rgb_img
            
            # Redimensionar si es muy grande
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Guardar optimizada
            img.save(image_path, 'JPEG', quality=quality, optimize=True)
            
            # Obtener tamaño final
            size_kb = os.path.getsize(image_path) / 1024
            return True, size_kb
    except Exception as e:
        print(f"Error optimizando {image_path}: {e}")
        return False, 0

def process_plant_images(source_folder, plant_id, plant_name=None):
    """Procesar imágenes de una planta específica"""
    
    # Crear carpeta destino
    dest_folder = f"plantas/planta_{plant_id:03d}"
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    
    # Buscar imágenes en carpeta fuente
    image_extensions = ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']
    images = []
    
    for file in os.listdir(source_folder):
        if any(file.endswith(ext) for ext in image_extensions):
            images.append(file)
    
    print(f"\n📸 Procesando {len(images)} imágenes para planta_{plant_id:03d}")
    
    # Copiar y renombrar imágenes
    processed = []
    for idx, image_file in enumerate(images[:3], 1):  # Máximo 3 principales
        source_path = os.path.join(source_folder, image_file)
        dest_filename = f"planta_{plant_id:03d}_{idx:02d}.jpg"
        dest_path = os.path.join(dest_folder, dest_filename)
        
        # Copiar imagen
        shutil.copy2(source_path, dest_path)
        
        # Optimizar
        success, size = optimize_image(dest_path)
        if success:
            processed.append({
                "filename": dest_filename,
                "size_kb": round(size, 2),
                "type": "principal"
            })
            print(f"  ✅ {dest_filename} ({size:.1f} KB)")
    
    # Si hay más imágenes, procesarlas como detalles
    detail_types = ['flor', 'hoja', 'fruto', 'tallo', 'general']
    for idx, image_file in enumerate(images[3:8], 0):  # Siguientes 5 como detalles
        if idx < len(detail_types):
            source_path = os.path.join(source_folder, image_file)
            dest_filename = f"planta_{plant_id:03d}_{detail_types[idx]}.jpg"
            dest_path = os.path.join(dest_folder, dest_filename)
            
            shutil.copy2(source_path, dest_path)
            success, size = optimize_image(dest_path)
            if success:
                processed.append({
                    "filename": dest_filename,
                    "size_kb": round(size, 2),
                    "type": detail_types[idx]
                })
                print(f"  ✅ {dest_filename} ({size:.1f} KB)")
    
    # Crear archivo de metadata
    metadata = {
        "plant_id": f"planta_{plant_id:03d}",
        "plant_name": plant_name,
        "images": processed,
        "total_size_mb": round(sum(img['size_kb'] for img in processed) / 1024, 2)
    }
    
    metadata_path = os.path.join(dest_folder, "metadata.json")
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    return processed

def generate_readme():
    """Generar README.md para el repositorio"""
    
    readme_content = """# 🌿 Banco de Imágenes - Flora Classifier

Este repositorio contiene el banco de imágenes para el proyecto Flora Classifier.

## 📁 Estructura

```
plantas/
├── planta_001/
│   ├── planta_001_01.jpg    # Imagen principal 1
│   ├── planta_001_02.jpg    # Imagen principal 2
│   ├── planta_001_03.jpg    # Imagen principal 3
│   ├── planta_001_flor.jpg  # Detalle flor (opcional)
│   ├── planta_001_hoja.jpg  # Detalle hoja (opcional)
│   └── metadata.json        # Información de las imágenes
└── planta_002/
    └── ...
```

## 🖼️ Especificaciones de imágenes

- **Formato**: JPEG
- **Tamaño máximo**: 1920x1920 píxeles
- **Calidad**: 85% (optimizado para web)
- **Peso promedio**: 200-500 KB por imagen

## 📊 Estadísticas

- Total de plantas: 500+
- Imágenes por planta: 3-8
- Tamaño total estimado: ~2-3 GB

## 🔗 URLs de acceso

Las imágenes son accesibles mediante:
```
https://raw.githubusercontent.com/[usuario]/flora-imagenes/main/plantas/planta_001/planta_001_01.jpg
```

## 📝 Metadata

Cada carpeta incluye un archivo `metadata.json` con:
- ID de la planta
- Nombre científico
- Lista de imágenes
- Tamaño total

## 🤝 Contribuciones

Para agregar nuevas imágenes:
1. Seguir la nomenclatura establecida
2. Optimizar imágenes antes de subir
3. Actualizar metadata.json

---

**Proyecto Flora Classifier** - Huila, Colombia 🇨🇴
"""
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("✅ README.md generado")

def batch_rename_images(source_folder, naming_pattern="planta"):
    """Renombrar imágenes en lote según patrón"""
    
    print(f"\n🔄 Renombrando imágenes en {source_folder}")
    
    # Listar todas las imágenes
    image_files = []
    for root, dirs, files in os.walk(source_folder):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                image_files.append(os.path.join(root, file))
    
    print(f"Encontradas {len(image_files)} imágenes")
    
    # Renombrar según patrón
    for idx, image_path in enumerate(image_files, 1):
        directory = os.path.dirname(image_path)
        new_name = f"{naming_pattern}_{idx:04d}.jpg"
        new_path = os.path.join(directory, new_name)
        
        try:
            os.rename(image_path, new_path)
            print(f"✅ {os.path.basename(image_path)} → {new_name}")
        except Exception as e:
            print(f"❌ Error: {e}")

# Menú principal
if __name__ == "__main__":
    print("🌿 Organizador de Imágenes - Flora Classifier")
    print("=" * 50)
    
    while True:
        print("\n📋 Opciones:")
        print("1. Crear estructura de carpetas")
        print("2. Procesar imágenes de una planta")
        print("3. Renombrar imágenes en lote")
        print("4. Generar README.md")
        print("5. Salir")
        
        opcion = input("\nElige opción (1-5): ")
        
        if opcion == "1":
            num = int(input("¿Cuántas plantas? (default: 500): ") or "500")
            create_folder_structure(num_plants=num)
            
        elif opcion == "2":
            source = input("Carpeta con imágenes originales: ")
            plant_id = int(input("ID de planta (1-500): "))
            plant_name = input("Nombre científico (opcional): ")
            if os.path.exists(source):
                process_plant_images(source, plant_id, plant_name)
            else:
                print("❌ Carpeta no encontrada")
                
        elif opcion == "3":
            folder = input("Carpeta a procesar: ")
            pattern = input("Patrón de nombre (default: planta): ") or "planta"
            if os.path.exists(folder):
                batch_rename_images(folder, pattern)
                
        elif opcion == "4":
            generate_readme()
            
        elif opcion == "5":
            print("👋 ¡Hasta luego!")
            break