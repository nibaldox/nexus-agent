import os
import sys
from nexus_workflow import NexusWorkflow

def test_reviewer_phase():
    print("🚀 Inciando prueba del Reviewer Phase...")
    workflow = NexusWorkflow()
    
    # Simular una solicitud
    user_request = "Investiga sobre la IA en 2025 y crea un gráfico de tendencias."
    session_id = "test_review_session"
    
    print(f"📝 Ejecutando workflow para: '{user_request}'")
    
    # Ejecutar el workflow (en modo stream para ver los eventos)
    # Nota: Esto ejecutará el Manager real si las API keys están configuradas.
    # Si no, fallará, pero aquí validamos la estructura.
    try:
        stream = workflow.run(
            user_request=user_request,
            session_id=session_id,
            stream=True,
            stream_events=True
        )
        
        found_review_step = False
        for chunk in stream:
            # En Agno Workflow, los eventos de Step tienen nombres específicos
            if hasattr(chunk, "step_name") and chunk.step_name == "Revisión":
                found_review_step = True
                print("✅ Evento de paso 'Revisión' detectado!")
            
            if hasattr(chunk, "content"):
                # Print a small part of content to verify streaming
                content = str(chunk.content)
                if len(content) > 50:
                    content = content[:50] + "..."
                # print(f"  [Event] {chunk.event}: {content}")
                
        if found_review_step:
            print("✨ Prueba exitosa: El paso de Revisión está integrado en el workflow.")
        else:
            print("❌ Error: No se detectó el paso de Revisión en el stream.")
            
    except Exception as e:
        print(f"⚠️ Error durante la prueba: {e}")
        print("Asegúrate de tener las API keys en el .env si deseas una ejecución real.")

if __name__ == "__main__":
    test_reviewer_phase()
