# Cambios en el frontend (2026-01-25)

Este documento describe las mejoras realizadas en el frontend y los ajustes posteriores para corregir el modo claro y el auto‑scroll inteligente.

## Resumen ejecutivo
- Se extrajo el CSS inline a un archivo dedicado y se organizaron estilos base y tema claro.
- Se mejoró la accesibilidad con etiquetas ARIA, roles y navegación por teclado.
- Se agregó un control de “Ver lo nuevo” y lógica de auto‑scroll inteligente.
- Se introdujo configuración centralizada y validación previa de uploads.
- Se mejoró la seguridad del renderizado (DOMPurify + sandbox en iframes).
- Se implementó backoff en el polling de squads para reducir carga.

## Cambios por archivo

### `frontend/index.html`
- Se agregó `lang="es"`.
- Se incluyó `css/main.css` y se eliminó el bloque `<style>` inline.
- Se agregaron roles y atributos ARIA en botones, inputs y contenedores.
- Se añadió el botón fijo “Ver lo nuevo” para el auto‑scroll.
- Se añadieron diálogos accesibles para prompt/confirm.

### `frontend/css/main.css`
- Nuevo archivo con variables de tema, estilos globales y overrides del tema claro.
- Se añadieron estilos para toasts, diálogos y botón “Ver lo nuevo”.
- Se añadieron mejoras de foco visible (`:focus-visible`).

### `frontend/responsive.css`
- Se removieron definiciones duplicadas de variables CSS en `:root` que forzaban el tema oscuro.
- Se mantuvieron únicamente las reglas responsivas.

### `frontend/js/config.js`
- Nuevo archivo de configuración central para límites, timeouts y polling.

### `frontend/js/api.js`
- La URL del API se vuelve configurable según el origen o `window.__NEXUS_API_URL`.

### `frontend/js/ui.js`
- Se agregaron hooks de DOMPurify para:
  - `rel="noopener noreferrer"` en links con `target="_blank"`.
  - `sandbox` y `loading="lazy"` en iframes.
- Renderizado de markdown con throttling adaptativo.

### `frontend/js/main.js`
- Auto‑scroll inteligente: respeta cuando el usuario sube manualmente.
- Botón “Ver lo nuevo” y control de visibilidad.
- Toasts para errores/éxitos.
- Diálogos accesibles para renombrar y confirmar acciones.
- Validación de uploads (tipo/tamaño) antes de enviar.
- Accesibilidad adicional (`aria-busy`, `aria-disabled`, etc.).
- Atajos de teclado: `Ctrl/Cmd + K` para buscar sesión, `Esc` para limpiar.

### `frontend/js/squad-status.js`
- Polling con backoff y pausa cuando la pestaña no está visible.

### `frontend/js/theme-switcher.js`
- Mejora de accesibilidad en toggle (aria-pressed y título dinámico).

## Pruebas sugeridas
1. **Tema claro/oscuro**
   - Alternar tema y verificar contraste, fondos y textos.
2. **Auto‑scroll**
   - Durante streaming, subir el scroll manualmente: no debe forzar el scroll.
   - Bajar con el botón “Ver lo nuevo”.
3. **Uploads**
   - Subir PDF válido y archivo inválido (tamaño/tipo) para validar mensajes.
4. **Diálogos**
   - Renombrar sesión y ocultar sesión usando los nuevos modales.
5. **Accesibilidad**
   - Navegar con teclado: tab, enter/espacio en botones.

## Notas
- Si se usa un API externo, definir `window.__NEXUS_API_URL` antes de cargar los módulos.
- El botón “Ver lo nuevo” aparece solo cuando hay mensajes nuevos y el usuario no está al final.
