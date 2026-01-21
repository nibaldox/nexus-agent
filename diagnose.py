#!/usr/bin/env python3
"""
Nexus AI - Diagnóstico de problemas de conectividad
"""

import sys
import os
import requests
import time

def test_internet_connection():
    """Test basic internet connectivity"""
    print("🌐 Probando conexión a internet...")
    try:
        response = requests.get("https://www.google.com", timeout=10)
        if response.status_code == 200:
            print("✅ Conexión a internet: OK")
            return True
        else:
            print(f"❌ Conexión a internet: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Conexión a internet: ERROR - {e}")
        return False

def test_huggingface_connection():
    """Test connection to HuggingFace"""
    print("\n🤗 Probando conexión a HuggingFace...")
    try:
        response = requests.get("https://huggingface.co", timeout=10)
        if response.status_code == 200:
            print("✅ Conexión a HuggingFace: OK")
            return True
        else:
            print(f"❌ Conexión a HuggingFace: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Conexión a HuggingFace: ERROR - {e}")
        return False

def test_model_download():
    """Test downloading a small model"""
    print("\n📥 Probando descarga de modelo...")
    try:
        from sentence_transformers import SentenceTransformer
        print("🔄 Descargando modelo de prueba (esto puede tomar tiempo)...")

        # Use a smaller model for testing
        model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        print("✅ Modelo descargado exitosamente")

        # Test embedding
        test_text = "This is a test sentence."
        embedding = model.encode(test_text)
        print(f"✅ Embedding generado: {len(embedding)} dimensiones")

        return True
    except Exception as e:
        print(f"❌ Error al descargar modelo: {e}")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    print("\n📦 Verificando dependencias...")
    required_packages = [
        'sentence_transformers',
        'lancedb',
        'agno',
        'requests'
    ]

    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}: Instalado")
        except ImportError:
            print(f"❌ {package}: NO instalado")
            missing.append(package)

    if missing:
        print(f"\n⚠️ Paquetes faltantes: {', '.join(missing)}")
        print("Instálalos con: pip install " + " ".join(missing))
        return False
    else:
        print("✅ Todas las dependencias están instaladas")
        return True

def main():
    print("🔍 DIAGNÓSTICO DE NEXUS AI")
    print("=" * 50)

    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # Activate virtual environment if available
    venv_path = os.path.join(script_dir, '.venv', 'Scripts', 'activate')
    if os.path.exists(venv_path):
        print("🐍 Activando entorno virtual...")
        # Note: This won't actually activate in the current process
        print("💡 Ejecuta: .venv\\Scripts\\activate (Windows) o source .venv/bin/activate (Linux/Mac)")

    # Run tests
    tests_passed = 0
    total_tests = 4

    if check_dependencies():
        tests_passed += 1

    if test_internet_connection():
        tests_passed += 1

    if test_huggingface_connection():
        tests_passed += 1

    if test_model_download():
        tests_passed += 1

    print(f"\n📊 RESULTADO: {tests_passed}/{total_tests} pruebas pasaron")

    if tests_passed == total_tests:
        print("\n🎉 ¡Todo está funcionando correctamente!")
        print("🚀 Puedes ejecutar Nexus AI sin problemas")
    else:
        print("\n⚠️ Hay problemas que resolver:")
        if tests_passed < 2:
            print("   • Revisa tu conexión a internet")
        if tests_passed < 3:
            print("   • Puede haber restricciones de red/firewall")
        if tests_passed < 4:
            print("   • La descarga de modelos está fallando")
            print("   • Intenta ejecutar el servidor varias veces")
            print("   • O usa un modelo más pequeño")

    print("\n💡 Para ejecutar Nexus AI:")
    print("   python start_nexus.py")

if __name__ == "__main__":
    main()