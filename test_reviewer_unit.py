import os
import sys
from nexus_workflow import NexusWorkflow
from agno.workflow import StepInput

def test_reviewer_unit():
    print("🚀 Inciando prueba UNITARIA del Reviewer Phase...")
    workflow = NexusWorkflow()
    
    # Mock de un StepInput con contexto previo
    step_input = StepInput(
        input="¿Cual es el estado de la IA en 2025?",
        additional_data={"session_id": "unit_test_session"}
    )
    
    print("📋 Ejecutando _review_step directamente...")
    try:
        # Llamar directamente al ejecutor del paso de revisión
        stream = workflow._review_step(step_input)
        
        full_content = ""
        for chunk in stream:
            if hasattr(chunk, "content") and chunk.content:
                full_content += chunk.content
                print(".", end="", flush=True)
        
        print("\n✅ Respuesta del Reviewer recibida!")
        print("\n--- INICIO DICTAMEN ---")
        print(full_content)
        print("--- FIN DICTAMEN ---")
        
        if "APPROVED" in full_content or "NEEDS_REVISION" in full_content:
            print("\n✨ Prueba exitosa: El Reviewer responde correctamente con un dictamen.")
        else:
            print("\n❌ Advertencia: El Reviewer no incluyó un status claro en su respuesta.")
            
    except Exception as e:
        print(f"\n⚠️ Error durante la prueba unitaria: {e}")

if __name__ == "__main__":
    test_reviewer_unit()
