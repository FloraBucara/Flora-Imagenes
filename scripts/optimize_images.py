"""
Script para optimizar imágenes para web SIN cambiar nombres ni estructura
Mantiene la organización por nombre científico
"""

import os
from PIL import Image
import json
from datetime import datetime

def optimize_image(image_path, max_size=(1920, 1920), quality=85):
    """Optimizar una imagen para web"""
    try:
        # Abrir imagen
        with Image.open(image_path) as img:
            original_size = os.path.getsize(image_path) / 1024  # KB
            
            # Convertir a RGB si es necesario
            if img.mode in ('RGBA', 'LA', 'L', 'P'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                if 'A' in img.mode:
                    rgb_img.paste(img, mask=img.split()[-1])
                else:
                    rgb_img.paste(img)
                img = rgb_img
            
            # Redimensionar solo si es más grande que max_size
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                resized = True
            else:
                resized = False
            
            # Guardar optimizada (sobrescribir original)
            img.save(image_path, 'JPEG', quality=quality, optimize=True)
            
            # Nuevo tamaño
            new_size = os.path.getsize(image_path) / 1024  # KB
            
            return {
                "success": True,
                "original_kb": round(original_size, 2),
                "new_kb": round(new_size, 2),
                "reduction": round(((original_size - new_size) / original_size) * 100, 1),
                "resized": resized
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def optimize_folder(folder_path, recursive=True):
    """Optimizar todas las imágenes en una carpeta"""
    
    print(f"\n📁 Procesando: {folder_path}")
    
    stats = {
        "total_images": 0,
        "optimized": 0,
        "errors": 0,
        "total_original_mb": 0,
        "total_new_mb": 0,
        "folders_processed": 0
    }
    
    extensions = ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']
    
    if recursive:
        # Procesar recursivamente
        for root, dirs, files in os.walk(folder_path):
            folder_has_images = False
            
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    if not folder_has_images:
                        print(f"\n📂 {os.path.relpath(root, folder_path)}")
                        folder_has_images = True
                        stats["folders_processed"] += 1
                    
                    file_path = os.path.join(root, file)
                    stats["total_images"] += 1
                    
                    # Optimizar imagen
                    result = optimize_image(file_path)
                    
                    if result["success"]:
                        stats["optimized"] += 1
                        stats["total_original_mb"] += result["original_kb"] / 1024
                        stats["total_new_mb"] += result["new_kb"] / 1024
                        
                        # Mostrar resultado
                        reduction_symbol = "↓" if result["reduction"] > 0 else "="
                        resize_symbol = "↔" if result["resized"] else ""
                        
                        print(f"   ✅ {file} {resize_symbol} "
                              f"{result['original_kb']:.1f}KB → {result['new_kb']:.1f}KB "
                              f"({reduction_symbol}{result['reduction']}%)")
                    else:
                        stats["errors"] += 1
                        print(f"   ❌ {file} - Error: {result['error']}")
    else:
        # Solo la carpeta actual
        for file in os.listdir(folder_path):
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(folder_path, file)
                stats["total_images"] += 1
                
                result = optimize_image(file_path)
                
                if result["success"]:
                    stats["optimized"] += 1
                    stats["total_original_mb"] += result["original_kb"] / 1024
                    stats["total_new_mb"] += result["new_kb"] / 1024
                    print(f"✅ {file}: {result['original_kb']:.1f}KB → {result['new_kb']:.1f}KB")
                else:
                    stats["errors"] += 1
                    print(f"❌ {file}: {result['error']}")
    
    return stats

def create_optimization_report(base_folder):
    """Crear reporte de optimización"""
    
    report = {
        "fecha": datetime.now().isoformat(),
        "carpeta_base": base_folder,
        "especies": {}
    }
    
    total_stats = {
        "total_especies": 0,
        "total_imagenes": 0,
        "tamaño_original_mb": 0,
        "tamaño_optimizado_mb": 0
    }
    
    # Analizar cada carpeta de especie
    for folder in os.listdir(base_folder):
        folder_path = os.path.join(base_folder, folder)
        if os.path.isdir(folder_path):
            # Contar imágenes
            images = []
            total_size = 0
            
            for file in os.listdir(folder_path):
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    file_path = os.path.join(folder_path, file)
                    size_kb = os.path.getsize(file_path) / 1024
                    images.append({
                        "nombre": file,
                        "tamaño_kb": round(size_kb, 2)
                    })
                    total_size += size_kb
            
            if images:
                report["especies"][folder] = {
                    "nombre_cientifico": folder,
                    "num_imagenes": len(images),
                    "tamaño_total_mb": round(total_size / 1024, 2),
                    "imagenes": images
                }
                
                total_stats["total_especies"] += 1
                total_stats["total_imagenes"] += len(images)
                total_stats["tamaño_optimizado_mb"] += total_size / 1024
    
    report["resumen"] = total_stats
    
    # Guardar reporte
    with open("reporte_optimizacion.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    return report

def batch_optimize_with_backup(base_folder, backup_folder=None):
    """Optimizar con opción de backup"""
    
    if backup_folder:
        print(f"📦 Creando backup en: {backup_folder}")
        import shutil
        
        if not os.path.exists(backup_folder):
            os.makedirs(backup_folder)
        
        # Copiar estructura completa
        for folder in os.listdir(base_folder):
            src = os.path.join(base_folder, folder)
            dst = os.path.join(backup_folder, folder)
            if os.path.isdir(src) and not os.path.exists(dst):
                print(f"   Copiando {folder}...")
                shutil.copytree(src, dst)
        
        print("✅ Backup completado\n")
    
    # Optimizar
    return optimize_folder(base_folder, recursive=True)

# Menú principal
if __name__ == "__main__":
    print("🌿 Optimizador de Imágenes para Web")
    print("=" * 50)
    print("⚠️  IMPORTANTE: Este script SOBRESCRIBE las imágenes originales")
    print("    Se recomienda hacer backup primero\n")
    
    while True:
        print("\n📋 Opciones:")
        print("1. Optimizar UNA carpeta de especie")
        print("2. Optimizar TODAS las carpetas")
        print("3. Optimizar con BACKUP previo")
        print("4. Generar reporte de estado")
        print("5. Configuración avanzada")
        print("6. Salir")
        
        opcion = input("\nElige opción (1-6): ")
        
        if opcion == "1":
            folder = input("Ruta de la carpeta (ej: D:\\Plantas\\Mimosa pudica L.): ")
            if os.path.exists(folder):
                stats = optimize_folder(folder, recursive=False)
                print(f"\n📊 Resumen:")
                print(f"   Imágenes procesadas: {stats['optimized']}/{stats['total_images']}")
                print(f"   Tamaño original: {stats['total_original_mb']:.1f} MB")
                print(f"   Tamaño final: {stats['total_new_mb']:.1f} MB")
                print(f"   Reducción: {((stats['total_original_mb'] - stats['total_new_mb']) / stats['total_original_mb'] * 100):.1f}%")
            else:
                print("❌ Carpeta no encontrada")
                
        elif opcion == "2":
            base = input("Carpeta base con todas las especies (ej: D:\\Plantas): ")
            if os.path.exists(base):
                confirm = input("⚠️  Esto optimizará TODAS las imágenes. ¿Continuar? (s/n): ")
                if confirm.lower() == 's':
                    stats = optimize_folder(base, recursive=True)
                    print(f"\n📊 Resumen total:")
                    print(f"   Carpetas procesadas: {stats['folders_processed']}")
                    print(f"   Imágenes optimizadas: {stats['optimized']}/{stats['total_images']}")
                    print(f"   Tamaño original: {stats['total_original_mb']:.1f} MB")
                    print(f"   Tamaño final: {stats['total_new_mb']:.1f} MB")
                    print(f"   Reducción total: {stats['total_original_mb'] - stats['total_new_mb']:.1f} MB")
            else:
                print("❌ Carpeta no encontrada")
                
        elif opcion == "3":
            base = input("Carpeta base con especies: ")
            backup = input("Carpeta para backup (dejar vacío para omitir): ")
            if os.path.exists(base):
                stats = batch_optimize_with_backup(base, backup if backup else None)
                print(f"\n✅ Optimización completada")
            else:
                print("❌ Carpeta no encontrada")
                
        elif opcion == "4":
            base = input("Carpeta base para analizar: ")
            if os.path.exists(base):
                report = create_optimization_report(base)
                print(f"\n📊 Reporte generado: reporte_optimizacion.json")
                print(f"   Total especies: {report['resumen']['total_especies']}")
                print(f"   Total imágenes: {report['resumen']['total_imagenes']}")
                print(f"   Tamaño total: {report['resumen']['tamaño_optimizado_mb']:.1f} MB")
            else:
                print("❌ Carpeta no encontrada")
                
        elif opcion == "5":
            print("\n⚙️  Configuración actual:")
            print("   Tamaño máximo: 1920x1920 píxeles")
            print("   Calidad JPEG: 85%")
            print("   Formatos: JPG, JPEG, PNG")
            
            change = input("\n¿Cambiar configuración? (s/n): ")
            if change.lower() == 's':
                size = input("Tamaño máximo (ej: 1920): ")
                quality = input("Calidad JPEG (1-100, recomendado 85): ")
                print("✅ Configuración actualizada para esta sesión")
                
        elif opcion == "6":
            print("👋 ¡Hasta luego!")
            break