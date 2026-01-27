# Alineación Frontend/Backend

Este documento resume los desajustes detectados entre el frontend y el backend, con propuestas de corrección para el equipo de frontend.

## Resumen de hallazgos

Prioridad alta (rompen UX o feedback):
- Evento `Error` del backend no se visualiza en la UI.
- Eventos `RunStarted` y `RunCompleted` no se manejan.
- El frontend no consume el endpoint `/mission_plan/{session_id}` para mostrar el plan completo.

Prioridad media/baja (mejoras):
- Endpoint `/sessions/{session_id}/compact` existe pero no se usa (sesiones largas más lentas).
- Fallback de eventos tool en minúscula (`tool_call_started`) podría ser innecesario si el backend siempre usa PascalCase.

## Detalle de problemas y fixes sugeridos

### 1) Evento `Error` no manejado
**Backend**: `api.py` emite `{"event": "Error", "content": str(e)}` en el stream SSE.  
**Frontend**: `frontend/js/main.js` no maneja ese evento.

**Impacto**: Errores silenciosos.

**Fix sugerido** (en `handleEvent`):
```javascript
if (eventType === "Error") {
  const bubble = UI.getOrCreateAgentBubble(group);
  bubble.innerHTML += `<div class="mt-2 text-xs text-red-500">❌ Error: ${event.content || 'Error desconocido'}</div>`;
  if (typeof showToast === 'function') {
    showToast('Error en la ejecución', 'error');
  }
  return;
}
```

### 2) Eventos `RunStarted` / `RunCompleted` no manejados
**Backend**: normaliza `WorkflowStarted → RunStarted` y `WorkflowCompleted → RunCompleted`.  
**Frontend**: no hay lógica para estos eventos.

**Impacto**: Estado visual inconsistente (streaming/online).

**Fix sugerido**:
```javascript
if (eventType === "RunStarted") {
  setSystemStatus('streaming');
}
if (eventType === "RunCompleted") {
  setSystemStatus('online');
}
```

### 3) Plan de misión no se muestra (solo `plan_path`)
**Backend**: expone `/mission_plan/{session_id}`.  
**Frontend**: muestra solo `plan_path` en el evento `PlanCreated`.

**Impacto**: No se puede visualizar el plan completo desde la UI.

**Fix sugerido** (cuando llega `PlanCreated`):
```javascript
const planPath = event.plan_path || "unknown";
if (planPath && planPath !== "unknown") {
  try {
    const planResponse = await fetch(`/mission_plan/${currentSessionId}`);
    const planData = await planResponse.json();
    if (planData.exists && planData.plan) {
      const details = cardEl.querySelector('.card-details');
      if (details) {
        details.innerHTML = `
          <div class="mt-2 text-[10px]">📄 ${planPath}</div>
          <details class="mt-2">
            <summary class="cursor-pointer text-[var(--accent-cyan)] text-[10px]">Ver plan completo</summary>
            <pre class="mt-2 text-[9px] mono whitespace-pre-wrap">${planData.plan}</pre>
          </details>
        `;
      }
    }
  } catch (e) {
    console.error('Error fetching plan:', e);
  }
}
```

## Mejoras recomendadas (opcional)

### A) Compactar sesiones grandes
**Backend**: `/sessions/{session_id}/compact`  
**Frontend**: no se usa.

**Sugerencia**:
```javascript
if (messages.length > 100) {
  try {
    await fetch(`/sessions/${sessionId}/compact`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ limit: 1000 })
    });
  } catch (e) {
    console.warn('Failed to compact session:', e);
  }
}
```

### B) Eventos tool en minúscula
El frontend tiene fallback para `tool_call_started` y `tool_call_completed`.  
Si el backend siempre envía `ToolCallStarted` / `ToolCallCompleted`, se puede limpiar el fallback o mantenerlo como tolerancia.

## Checklist rápido para QA
- `RunStarted` activa estado “Streaming”.
- `RunCompleted` vuelve a “Online”.
- `Error` se ve en UI y dispara toast.
- `PlanCreated` muestra contenido del plan con `/mission_plan/{session_id}`.
- `api/logs/tools` sigue funcionando con `session_id` (ya correcto).
