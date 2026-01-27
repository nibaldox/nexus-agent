#!/usr/bin/env python3
import os
import shutil
from pathlib import Path
from collections import defaultdict

def should_ignore(item):
    ignore_list = ['.git', '.venv', '__pycache__', '.pytest_cache', 'knowledge', 'mission_plans', 'sandbox', 'sandbox_debug', 'organiza_archivos.py', '.env', '.gitignore', 'agent.db']
    return item in ignore_list

def get_extension(filepath):
    ext = Path(filepath).suffix.lower()
    return ext if ext else 'sin_extension'

def organize_files(source_dir="."):
    source_path = Path(source_dir).absolute()
    print(f"📁 Analizando directorio: {source_path}")
    print("=" * 60)
    
    files_by_extension = defaultdict(list)
    
    for item in source_path.iterdir():
        if not item.is_file():
            continue
        if should_ignore(item.name):
            print(f"⏭️  Ignorado: {item.name}")
            continue
        ext = get_extension(item)
        files_by_extension[ext].append(item)
        print(f"📄 Encontrado: {item.name} -> {ext}")
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE ARCHIVOS POR EXTENSIÓN")
    print("=" * 60)
    
    total_moved = 0
    total_errors = 0
    
    if not files_by_extension:
        print("⚠️  No se encontraron archivos para organizar.")
        return
    
    for ext, files in sorted(files_by_extension.items()):
        if ext == 'sin_extension':
            folder_name = 'archivos_sin_extension'
        else:
            folder_name = f"archivos_{ext.replace('.', '')}"
        
        folder_path = source_path / folder_name
        print(f"\n📂 Extensión: {ext} ({len(files)} archivos)")
        print(f"   Carpeta destino: {folder_name}")
        
        try:
            folder_path.mkdir(exist_ok=True)
            print(f"   ✅ Carpeta creada/lista")
        except Exception as e:
            print(f"   ❌ Error creando carpeta: {e}")
            total_errors += 1
            continue
        
        for file_path in files:
            try:
                dest_path = folder_path / file_path.name
                if dest_path.exists():
                    base_name = file_path.stem
                    counter = 1
                    while dest_path.exists():
                        new_name = f"{base_name}_{counter}{ext}"
                        dest_path = folder_path / new_name
                        counter += 1
                shutil.move(str(file_path), str(dest_path))
                print(f"   ✅ Movido: {file_path.name}")
                total_moved += 1
            except Exception as e:
                print(f"   ❌ Error moviendo {file_path.name}: {e}")
                total_errors += 1
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN FINAL")
    print("=" * 60)
    print(f"✅ Total archivos movidos: {total_moved}")
    print(f"❌ Total errores: {total_errors}")
    print(f"📁 Total carpetas creadas: {len(files_by_extension)}")
    print(f"📂 Carpetas generadas:")
    for ext in sorted(files_by_extension.keys()):
        if ext == 'sin_extension':
            folder_name = 'archivos_sin_extension'
        else:
            folder_name = f"archivos_{ext.replace('.', '')}"
        print(f"   • {folder_name} ({len(files_by_extension[ext])} archivos)")

if __name__ == "__main__":
    print("🚀 ORGANIZADOR DE ARCHIVOS POR EXTENSIÓN")
    print("=" * 60)
    organize_files(".")
    print("\n✨ ¡Proceso completado!")