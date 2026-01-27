import { API_URL } from './api.js';
import { FRONTEND_CONFIG } from './config.js';
import * as UI from './ui.js';

let chatContainer;
let inputField;
let sendButton;
let stopButton;
let sessionList;
let newSessionBtn; // "Ini_Session" button
let messageContainer;
let charCounter;
let systemStatusLabel;
let systemStatusDot;
let hiddenSessionsToggle;
let hiddenSessionsPanel;
let sessionSearchInput;
let exportSessionBtn;
let clearChatBtn;
let resetFiltersBtn;
let scrollToLatestBtn;
let promptDialog;
let promptInput;
let promptTitle;
let confirmDialog;
let confirmTitle;
let confirmMessage;

let currentSessionId = null;
let isStreaming = false;
let currentAbortController = null;
let activeTurnGroup = null;
let userScrolled = false;
let lastMessageCount = 0;
let lastConnectionOk = true;
let lastUserMessage = null;
let sessionSearchTerm = '';
let activeStreamingBubble = null;
let sessionExplicitSelection = false;
let sessionAutoRestored = false;

const MAX_MESSAGE_LENGTH = FRONTEND_CONFIG.maxMessageLength;
const SESSION_TITLE_OVERRIDES_KEY = 'nexus_session_titles';
const SESSION_TITLE_LOCKS_KEY = 'nexus_session_title_locks';
const SESSION_HIDDEN_KEY = 'nexus_hidden_sessions';

function cacheDom() {
    chatContainer = document.getElementById('chat-log');
    inputField = document.getElementById('message-input');
    sendButton = document.getElementById('send-btn');
    stopButton = document.getElementById('stop-btn');
    sessionList = document.getElementById('session-list');
    newSessionBtn = document.getElementById('new-session-btn');
    messageContainer = document.getElementById('chat-log');
    charCounter = document.getElementById('char-counter');
    systemStatusLabel = document.getElementById('system-status');
    systemStatusDot = document.getElementById('system-status-dot');
    hiddenSessionsToggle = document.getElementById('hidden-sessions-toggle');
    hiddenSessionsPanel = document.getElementById('hidden-sessions-panel');
    sessionSearchInput = document.getElementById('session-search');
    exportSessionBtn = document.getElementById('export-session-btn');
    clearChatBtn = document.getElementById('clear-chat-btn');
    resetFiltersBtn = document.getElementById('reset-filters-btn');
    scrollToLatestBtn = document.getElementById('scroll-to-latest');
    promptDialog = document.getElementById('prompt-dialog');
    promptInput = document.getElementById('prompt-input');
    promptTitle = document.getElementById('prompt-title');
    confirmDialog = document.getElementById('confirm-dialog');
    confirmTitle = document.getElementById('confirm-title');
    confirmMessage = document.getElementById('confirm-message');
}

function setCurrentSessionId(sessionId) {
    currentSessionId = sessionId;
    localStorage.setItem('nexus_session_id', sessionId);
}

// --- Helper Functions ---
function uuidv4() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

function showToast(message, type = 'info') {
    if (!message) return;
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
    }
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toast.setAttribute('role', 'status');
    toast.setAttribute('aria-live', 'polite');
    container.appendChild(toast);
    setTimeout(() => {
        toast.classList.add('toast-hide');
        setTimeout(() => toast.remove(), 300);
    }, 2600);
}

function showPrompt({ title, value = '' }) {
    if (!promptDialog || !promptInput || !promptTitle) {
        return Promise.resolve(null);
    }
    promptTitle.textContent = title || 'Actualizar';
    promptInput.value = value;
    promptDialog.showModal();
    promptInput.focus();
    promptInput.select();
    return new Promise((resolve) => {
        const handler = () => {
            const result = promptDialog.returnValue === 'confirm'
                ? promptInput.value.trim()
                : null;
            promptDialog.removeEventListener('close', handler);
            resolve(result && result.length > 0 ? result : null);
        };
        promptDialog.addEventListener('close', handler, { once: true });
    });
}

function showConfirm({ title, message, confirmLabel = 'Aceptar' }) {
    if (!confirmDialog || !confirmTitle || !confirmMessage) {
        return Promise.resolve(false);
    }
    confirmTitle.textContent = title || 'Confirmar';
    confirmMessage.textContent = message || '';
    const confirmBtn = document.getElementById('confirm-ok');
    if (confirmBtn) confirmBtn.textContent = confirmLabel;
    confirmDialog.showModal();
    return new Promise((resolve) => {
        const handler = () => {
            const result = confirmDialog.returnValue === 'confirm';
            confirmDialog.removeEventListener('close', handler);
            resolve(result);
        };
        confirmDialog.addEventListener('close', handler, { once: true });
    });
}

// --- Session Logic ---
async function loadSessions() {
    try {
        const response = await fetch('/sessions');
        const sessions = await response.json();
        renderSessionList(sessions);
        return sessions;
    } catch (e) {
        console.error("Failed to load sessions:", e);
        showToast('No se pudieron cargar las sesiones.', 'warning');
        return [];
    }
}

function getSessionTitleOverrides() {
    try {
        return JSON.parse(localStorage.getItem(SESSION_TITLE_OVERRIDES_KEY) || '{}');
    } catch (e) {
        return {};
    }
}

function saveSessionTitleOverrides(overrides) {
    localStorage.setItem(SESSION_TITLE_OVERRIDES_KEY, JSON.stringify(overrides));
}

function getSessionTitleLocks() {
    try {
        return new Set(JSON.parse(localStorage.getItem(SESSION_TITLE_LOCKS_KEY) || '[]'));
    } catch (e) {
        return new Set();
    }
}

function saveSessionTitleLocks(lockSet) {
    localStorage.setItem(SESSION_TITLE_LOCKS_KEY, JSON.stringify(Array.from(lockSet)));
}

function getHiddenSessions() {
    try {
        return new Set(JSON.parse(localStorage.getItem(SESSION_HIDDEN_KEY) || '[]'));
    } catch (e) {
        return new Set();
    }
}

function saveHiddenSessions(hiddenSet) {
    localStorage.setItem(SESSION_HIDDEN_KEY, JSON.stringify(Array.from(hiddenSet)));
}

function resolveSessionTitle(session, overrides) {
    return overrides[session.session_id] || session.title || "Untitled Mission";
}

function deriveTitleFromManagerContent(content, fallback) {
    if (!content) return fallback || '';
    // Drop code fences and markdown artifacts
    let text = content
        .replace(/```[\s\S]*?```/g, '')
        .replace(/[#>*`_-]+/g, ' ')
        .replace(/\s+/g, ' ')
        .trim();

    if (!text) return fallback || '';

    const firstSentence = text.split(/(?<=[.!?])\s/)[0] || text;
    const clean = firstSentence
        .replace(/^(entendido|perfecto|claro|ok|vale|de acuerdo)[\s:.-]*/i, '')
        .replace(/\b(vamos a|voy a|procederé a|se realizará|realizaremos)\b/gi, '')
        .trim();

    if (clean.length >= 12) {
        return clean.slice(0, 60).trim();
    }
    return fallback || clean.slice(0, 60).trim();
}

function deriveTitleFromUserMessage(message) {
    if (!message) return '';
    const stopwords = new Set([
        'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'de', 'del', 'al', 'y', 'o', 'u', 'en', 'para', 'por', 'con', 'sin',
        'sobre', 'que', 'qué', 'como', 'cómo', 'cuál', 'cual', 'cuáles', 'cuales', 'dame', 'haz', 'hacer', 'quiero', 'necesito',
        'analiza', 'analizar', 'ver', 'muestra', 'buscar', 'busca', 'investiga', 'investigar', 'explica', 'explicar'
    ]);
    const tokens = message
        .toLowerCase()
        .replace(/[^a-záéíóúñ0-9\s]/gi, ' ')
        .split(/\s+/)
        .filter(t => t && !stopwords.has(t));

    if (tokens.length === 0) {
        return message.slice(0, 60).trim();
    }
    const title = tokens.slice(0, 6).join(' ');
    return title.charAt(0).toUpperCase() + title.slice(1);
}

function setSessionTitleFromUserRequest(message) {
    if (!currentSessionId) return;
    const overrides = getSessionTitleOverrides();
    const locks = getSessionTitleLocks();
    if (locks.has(currentSessionId)) return;
    const title = deriveTitleFromUserMessage(message);
    if (!title) return;
    if (overrides[currentSessionId] === title) return;
    overrides[currentSessionId] = title;
    saveSessionTitleOverrides(overrides);
    loadSessions();
}

function ensureSessionTitleFromManager() {
    if (!lastUserMessage) return;
    setSessionTitleFromUserRequest(lastUserMessage);
}

function renderSessionList(sessions) {
    if (!sessionList) return;
    sessionList.innerHTML = '';

    const overrides = getSessionTitleOverrides();
    const hiddenSessions = getHiddenSessions();
    const searchTerm = sessionSearchTerm.trim().toLowerCase();

    // Sort by updated_at desc (fallback to created_at)
    sessions.sort((a, b) => {
        const aTime = a.updated_at || a.created_at || 0;
        const bTime = b.updated_at || b.created_at || 0;
        return bTime - aTime;
    });

    sessions
        .filter(session => !hiddenSessions.has(session.session_id))
        .filter(session => {
            if (!searchTerm) return true;
            const title = resolveSessionTitle(session, overrides).toLowerCase();
            return title.includes(searchTerm);
        })
        .forEach(session => {
            const li = document.createElement('li');
            li.dataset.sessionId = session.session_id;
            li.className = `flex items-center justify-between gap-2 text-[11px] text-[var(--text-muted)] hover:text-[var(--text-main)] cursor-pointer truncate py-1 px-2 rounded hover:bg-[rgba(255,255,255,0.05)] transition-colors ${session.session_id === currentSessionId ? 'text-[var(--accent-cyan)] font-bold' : ''}`;
            li.onclick = () => selectSession(session.session_id, true);

            const displayTitle = resolveSessionTitle(session, overrides);
            const titleSpan = document.createElement('span');
            titleSpan.className = 'truncate flex-1';
            titleSpan.textContent = displayTitle;
            titleSpan.title = displayTitle;
            titleSpan.onclick = () => selectSession(session.session_id, true);

            const actions = document.createElement('div');
            actions.className = 'flex items-center gap-1 opacity-60 hover:opacity-100';

            const renameBtn = document.createElement('button');
            renameBtn.className = 'material-symbols-outlined text-[14px] hover:text-[var(--accent-cyan)] transition-colors';
            renameBtn.textContent = 'edit';
            renameBtn.title = 'Renombrar';
            renameBtn.onclick = async (e) => {
                e.stopPropagation();
                const newTitle = await showPrompt({
                    title: 'Nuevo nombre de la sesión',
                    value: displayTitle
                });
                if (newTitle && newTitle.trim()) {
                    overrides[session.session_id] = newTitle.trim();
                    saveSessionTitleOverrides(overrides);
                    const locks = getSessionTitleLocks();
                    locks.add(session.session_id);
                    saveSessionTitleLocks(locks);
                    loadSessions();
                }
            };

            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'material-symbols-outlined text-[14px] hover:text-red-400 transition-colors';
            deleteBtn.textContent = 'delete';
            deleteBtn.title = 'Ocultar sesión';
            deleteBtn.onclick = async (e) => {
                e.stopPropagation();
                const confirmed = await showConfirm({
                    title: 'Ocultar sesión',
                    message: '¿Ocultar esta sesión de la lista?',
                    confirmLabel: 'Ocultar'
                });
                if (!confirmed) return;
                const hidden = getHiddenSessions();
                hidden.add(session.session_id);
                saveHiddenSessions(hidden);
                if (currentSessionId === session.session_id) {
                    currentSessionId = null;
                    localStorage.removeItem('nexus_session_id');
                }
                loadSessions().then(() => {
                    if (!currentSessionId) {
                        initSessions();
                    }
                });
            };

            actions.appendChild(renameBtn);
            actions.appendChild(deleteBtn);

            li.appendChild(titleSpan);
            li.appendChild(actions);
            sessionList.appendChild(li);
        });

    renderHiddenSessions(sessions, hiddenSessions, overrides);
}

function renderHiddenSessions(sessions, hiddenSessions, overrides) {
    if (!hiddenSessionsPanel || !hiddenSessionsToggle) return;
    hiddenSessionsPanel.innerHTML = '';

    const hiddenList = sessions.filter(session => hiddenSessions.has(session.session_id));
    hiddenSessionsToggle.classList.toggle('hidden', hiddenList.length === 0);
    if (hiddenList.length === 0) {
        hiddenSessionsPanel.classList.add('hidden');
        hiddenSessionsToggle.textContent = 'Ver sesiones ocultas';
    }

    hiddenList.forEach(session => {
        const row = document.createElement('div');
        row.className = 'flex items-center justify-between gap-2 text-[10px] text-[var(--text-muted)]';

        const title = resolveSessionTitle(session, overrides);
        const titleSpan = document.createElement('span');
        titleSpan.className = 'truncate flex-1';
        titleSpan.textContent = title;

        const restoreBtn = document.createElement('button');
        restoreBtn.className = 'material-symbols-outlined text-[14px] hover:text-[var(--accent-cyan)] transition-colors';
        restoreBtn.textContent = 'restore_from_trash';
        restoreBtn.title = 'Restaurar sesión';
        restoreBtn.onclick = () => {
            const hidden = getHiddenSessions();
            hidden.delete(session.session_id);
            saveHiddenSessions(hidden);
            loadSessions();
        };

        row.appendChild(titleSpan);
        row.appendChild(restoreBtn);
        hiddenSessionsPanel.appendChild(row);
    });
}

function createSession() {
    if (!chatContainer) return;
    setCurrentSessionId(uuidv4());
    sessionExplicitSelection = true;
    sessionAutoRestored = false;
    resetChatView(`New Mission Initialized: ${currentSessionId.split('-')[0]}...`);
    // Reload list to remove highlight from previous
    loadSessions();
}

async function selectSession(sessionId, isUserInitiated = false) {
    if (currentSessionId === sessionId) return;

    setCurrentSessionId(sessionId);
    if (isUserInitiated) {
        sessionExplicitSelection = true;
        sessionAutoRestored = false;
    }
    if (!chatContainer) return;
    chatContainer.innerHTML = '<div class="text-center text-[var(--accent-cyan)] text-xs mt-10 animate-pulse">Loading Mission Data...</div>';

    // Highlight handled by loadSessions()

    try {
        const response = await fetch(`/sessions/${sessionId}`);
        const data = await response.json();
        const messages = data.messages || [];

        // Render History
        chatContainer.innerHTML = '';

        // If empty, show default welcome
        if (messages.length === 0) {
            resetChatView('Mission Restore Complete.');
        } else {
            renderHistory(messages);
        }

    } catch (e) {
        console.error("Error loading session:", e);
        chatContainer.innerHTML = '<div class="text-red-500 text-xs mt-10">Error loading mission data.</div>';
        showToast('Error cargando la sesión.', 'error');
    }

    loadSessions(); // Re-render list to highlight current
}

function resetChatView(subtitle) {
    if (!chatContainer) return;
    const detail = subtitle ? `${subtitle}<br />` : '';
    chatContainer.innerHTML = `
        <div class="text-[12px] text-[var(--text-muted)] mono leading-relaxed opacity-60">
            Agent Zero v2.0 Online. Systems Nominal.<br />
            ${detail}
            Waiting for operator input...
        </div>
    `;
    activeTurnGroup = null;
    updateAutoScroll(true);
}

function renderHistory(messages) {
    if (!chatContainer) return;
    let currentGroup = null;

    function ensureToolsContainer(group) {
        let toolsContainer = group.querySelector('.tools-container-active');
        if (!toolsContainer) {
            const { html } = UI.createExecutionCard(
                'build',
                'Tools_Execution',
                'agent_tools',
                'History',
                'var(--accent-orange)'
            );
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = html;
            toolsContainer = tempDiv.firstElementChild;
            toolsContainer.classList.add('tools-container-active');
            const containerDetails = toolsContainer.querySelector('.card-details');
            if (containerDetails) {
                containerDetails.innerHTML = '<div class="space-y-2 tools-list"></div>';
            }
            group.appendChild(toolsContainer);
        }
        return toolsContainer;
    }

    function extractToolCalls(msg) {
        if (Array.isArray(msg.tool_calls)) return msg.tool_calls;
        if (msg.tool_call) return [msg.tool_call];
        if (typeof msg.tool_calls === 'string') {
            try {
                const parsed = JSON.parse(msg.tool_calls);
                return Array.isArray(parsed) ? parsed : [parsed];
            } catch {
                return [];
            }
        }
        return [];
    }

    messages.forEach(msg => {
        if (msg.role === 'user') {
            chatContainer.insertAdjacentHTML('beforeend', UI.createOperatorBubble(msg.content));
            currentGroup = null; // Reset group
        } else if (msg.role === 'assistant') {
            currentGroup = UI.ensureAgentGroup(chatContainer);

            // We assume assistant messages in history are "Nexus" unless specified
            const agentName = msg.name || msg.agent_name || "Nexus";
            const card = UI.ensureAgentCard(currentGroup, agentName);

            const toolCalls = extractToolCalls(msg);
            if (toolCalls.length > 0) {
                toolCalls.forEach(call => {
                    const toolName = call.name || call.tool_name || (call.function && call.function.name) || 'tool';
                    const toolArgs = call.args || call.tool_args || call.arguments || (call.function && call.function.arguments);
                    // Redirect to Sidebar Log
                    UI.renderToolLog(toolName, toolArgs, call.output || call.tool_output || call.result);
                });
            }

            if (msg.tool_output || msg.output || msg.result) {
                // Redirect to Sidebar Log
                UI.renderToolLog(
                    msg.tool_name || msg.name || 'tool',
                    msg.tool_args || msg.args,
                    msg.tool_output || msg.output || msg.result
                );
            }

            if (msg.content) {
                const currentContent = card.dataset.fullContent || "";
                // Use a double newline separator for history segments if appending to same card
                const separator = currentContent ? "\n\n" : "";
                card.dataset.fullContent = currentContent + separator + msg.content;
                UI.updateAgentResponse(card, card.dataset.fullContent);
            }
        } else if (msg.role === 'tool') {
            // Redirect to Sidebar Log
            UI.renderToolLog(
                msg.tool_name || msg.name || 'tool',
                msg.tool_args || msg.args,
                msg.content || msg.output || msg.result
            );
        }
    });
    updateAutoScroll(true);
}

document.addEventListener('DOMContentLoaded', () => {
    cacheDom();
    // Initialize Sidebar Logic
    if (UI.initResizeHandle) UI.initResizeHandle();
    if (UI.initSidebarTabs) UI.initSidebarTabs();

    // ... existing init code ...
});

// We need to inject the init call properly without rewriting the whole listener if possible, 
// or just ensure we call it. Since I am replacing a big block, I'll rely on the user refreshing or
// the existing listeners. Wait, I should verify where DOMContentLoaded is.
// Actually, let's just make sure we call it.

function setStreamingState(active) {
    isStreaming = active;
    if (sendButton) {
        sendButton.disabled = active;
        sendButton.classList.toggle('opacity-50', active);
        sendButton.classList.toggle('cursor-not-allowed', active);
        sendButton.setAttribute('aria-disabled', active ? 'true' : 'false');
    }
    if (inputField) {
        inputField.disabled = active;
        inputField.classList.toggle('opacity-60', active);
        inputField.setAttribute('aria-disabled', active ? 'true' : 'false');
    }
    if (stopButton) {
        stopButton.classList.toggle('hidden', !active);
        stopButton.setAttribute('aria-hidden', active ? 'false' : 'true');
    }
    if (active) {
        setSystemStatus('streaming');
    } else {
        setSystemStatus(lastConnectionOk ? 'online' : 'offline');
    }
    if (chatContainer) {
        chatContainer.setAttribute('aria-busy', active ? 'true' : 'false');
    }
}

function updateAutoScroll(force = false) {
    if (!messageContainer) return;
    const currentMessageCount = messageContainer.querySelectorAll('.agent-message-group, .operator-bubble').length;
    const hasNewMessages = currentMessageCount > lastMessageCount;
    lastMessageCount = currentMessageCount;

    const isNearBottom = messageContainer.scrollHeight - messageContainer.scrollTop - messageContainer.clientHeight < FRONTEND_CONFIG.scroll.bottomThresholdPx;
    const shouldScroll = force || (!userScrolled && (isStreaming || isNearBottom));
    if (shouldScroll && (hasNewMessages || isStreaming)) {
        messageContainer.scrollTop = messageContainer.scrollHeight;
    }
    if (scrollToLatestBtn) {
        const showButton = userScrolled && hasNewMessages && !isNearBottom;
        scrollToLatestBtn.classList.toggle('hidden', !showButton);
    }
}

async function sendMessage() {
    if (!inputField) return;
    if (isStreaming) return;
    const message = inputField.value.trim();
    if (!message) return;
    sendMessageWithText(message, { isRetry: false });
}

async function sendMessageWithText(message, options = { isRetry: false }) {
    if (!chatContainer) return;
    if (isStreaming) return;
    if (!message) return;
    if (message.length > MAX_MESSAGE_LENGTH) {
        const turnGroup = UI.ensureAgentGroup(chatContainer);
        const card = UI.ensureAgentCard(turnGroup, "System");
        const body = card.querySelector('.response-content');
        if (body) body.innerHTML = `<span class="text-red-500">El mensaje excede ${MAX_MESSAGE_LENGTH} caracteres.</span>`;
        return;
    }

    // Ensure session exists (avoid using stale auto-restored sessions)
    if (!currentSessionId || currentSessionId === 'default') {
        createSession();
    } else if (sessionAutoRestored && !sessionExplicitSelection) {
        createSession();
    }

    lastUserMessage = message;
    setSessionTitleFromUserRequest(message);
    const displayMessage = options.isRetry ? `↻ ${message}` : message;

    if (inputField) {
        inputField.value = '';
        updateCharCounter();
    }

    chatContainer.insertAdjacentHTML('beforeend', UI.createOperatorBubble(displayMessage));
    updateAutoScroll(true);

    const turnGroup = UI.ensureAgentGroup(chatContainer);
    activeTurnGroup = turnGroup;

    // Create initial card for streaming
    const card = UI.ensureAgentCard(turnGroup, "Nexus");
    card.dataset.fullContent = ""; // Reset buffer
    activeStreamingBubble = card.querySelector('.response-content');
    activeStreamingBubble.dataset.markdownBuffer = "";

    // UI.setStreamingIndicator(activeStreamingBubble, true);

    try {
        setStreamingState(true);
        currentAbortController = new AbortController();

        // Update list title after first message (delayed)
        setTimeout(loadSessions, 2000);

        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                session_id: currentSessionId
            }),
            signal: currentAbortController.signal
        });


        if (!response.ok) {
            throw new Error(`Error HTTP ${response.status}`);
        }
        if (!response.body) {
            throw new Error('Respuesta vacía del servidor');
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const events = buffer.split('\n\n');

            // Re-assign buffer to the last (possibly incomplete) fragment
            buffer = events.pop();

            for (const rawEvent of events) {
                if (!rawEvent.trim()) continue;

                // An SSE event can have multiple 'data: ' lines
                const lines = rawEvent.split('\n');
                let combinedData = "";

                for (let line of lines) {
                    if (line.startsWith('data: ')) {
                        combinedData += line.slice(6);
                    }
                }

                if (!combinedData) continue;

                if (combinedData === '[DONE]') {
                    setStreamingState(false);
                    currentAbortController = null;
                    if (activeStreamingBubble) {
                        UI.renderMarkdownImmediate(activeStreamingBubble, activeStreamingBubble.dataset.markdownBuffer || '');
                        activeStreamingBubble = null;
                    }
                    updateAutoScroll(true);
                    return;
                }

                try {
                    const event = JSON.parse(combinedData);
                    await handleEvent(event, turnGroup);
                } catch (e) {
                    console.error("Error parsing JSON. Content:", combinedData, e);
                }
            }
            updateAutoScroll();
        }

    } catch (error) {
        console.error('Error:', error);
        const card = UI.ensureAgentCard(turnGroup, "System");
        const body = card.querySelector('.response-content');
        const isAbort = error.name === 'AbortError';
        if (isAbort) {
            body.innerHTML += `<br><span class="text-red-500">Solicitud detenida por el usuario.</span>`;
        } else {
            body.innerHTML += `<br><span class="text-red-500">System Error: ${error.message}</span>`;
            body.innerHTML += `<br><button class="text-[10px] text-[var(--accent-cyan)] underline mt-1" data-retry="true">Reintentar</button>`;
            showToast('Error en la solicitud. Intenta de nuevo.', 'error');
        }
        setSystemStatus('offline');
    } finally {
        setStreamingState(false);
        currentAbortController = null;
        if (activeStreamingBubble) {
            // UI.setStreamingIndicator(activeStreamingBubble, false);
            activeStreamingBubble = null;
        }
    }
}

async function handleEvent(event, group) {
    const eventType = event.event;

    if (eventType === "RunStarted") {
        setSystemStatus('streaming');
    }

    if (eventType === "RunCompleted") {
        setSystemStatus(lastConnectionOk ? 'online' : 'offline');
    }

    if (eventType === "Error") {
        const card = UI.ensureAgentCard(group, "System");
        const body = card.querySelector('.response-content');
        body.innerHTML += `<div class="mt-2 text-xs text-red-500">❌ Error: ${event.content || 'Error desconocido'}</div>`;
        showToast('Error en la ejecución', 'error');
        return;
    }
    if (event.session_id) {
        if (currentSessionId && event.session_id !== currentSessionId) {
            return;
        }
        if (!currentSessionId) {
            setCurrentSessionId(event.session_id);
        }
    }

    // Determine Agent Name
    const agentName = event.agent_name || "Nexus";
    const card = UI.ensureAgentCard(group, agentName);

    // 1. REASONING
    if (eventType === "ReasoningStarted" || (eventType === "RunContent" && event.reasoning_content)) {
        if (event.reasoning_content) {
            const newReasoning = event.reasoning_content;
            const oldReasoning = card.dataset.fullReasoning || "";
            // Smart accumulation for reasoning
            if (newReasoning.startsWith(oldReasoning) && newReasoning.length > oldReasoning.length) {
                card.dataset.fullReasoning = newReasoning;
            } else if (oldReasoning !== newReasoning) {
                card.dataset.fullReasoning = oldReasoning + newReasoning;
            }
            UI.renderThinking(card, card.dataset.fullReasoning);
        }
        // Continue processing to handle potential 'content' in the same message
    }

    // 2. TOOL CALLS
    if (eventType === "ToolCall") {
        const toolName = event.tool_name || event.name || "Unknown Tool";
        const args = event.tool_args || event.args || {};
        UI.renderToolLog(toolName, args, null);
        return;
    }

    // 3. TOOL OUTPUT
    if (eventType === "ToolOutput") {
        const toolName = event.tool_name || event.name || "Unknown Tool";
        const output = event.tool_output || event.output || "Done";
        UI.renderToolLog(toolName, {}, output);
        return;
    }

    // 4. CONTENT / STREAMING
    if (eventType === "RunContent" || eventType === "ResponseChunk") {
        let content = event.content || "";
        if (content) {
            const currentTotal = card.dataset.fullContent || "";

            if (eventType === "ResponseChunk") {
                card.dataset.fullContent = currentTotal + content;
            } else {
                // If the new content starts with the current total, it's a snapshot
                if (content.startsWith(currentTotal)) {
                    card.dataset.fullContent = content;
                } else {
                    // It's a delta or there's a minor mismatch, so we append to be safe
                    // unless the last few chars match, in which case we trim the overlap
                    card.dataset.fullContent = currentTotal + content;
                }
            }

            UI.updateAgentResponse(card, card.dataset.fullContent);

            // Case-insensitive check for Nexus/Zero
            const lowerAgent = agentName.toLowerCase();
            if (lowerAgent.includes('nexus') || lowerAgent.includes('zero')) {
                activeStreamingBubble = card.querySelector('.response-content');
            }
        }
    }

    // 5. PLANNING EVENTS
    if (eventType === "PlanningStarted" || eventType === "PlanCreated") {
        UI.renderToolLog("Mission_Planner", { event: eventType }, event.content);
    }
}










// --- Bindings ---
function bindEvents() {
    if (sendButton) {
        sendButton.addEventListener('click', sendMessage);
    }

    if (stopButton) {
        stopButton.addEventListener('click', () => {
            if (currentAbortController) {
                currentAbortController.abort();
            }
        });
    }

    if (inputField) {
        inputField.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        inputField.addEventListener('input', () => {
            updateCharCounter();
        });
    }

    if (newSessionBtn) {
        newSessionBtn.addEventListener('click', createSession);
        newSessionBtn.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                createSession();
            }
        });
    }

    if (hiddenSessionsToggle) {
        hiddenSessionsToggle.addEventListener('click', () => {
            if (!hiddenSessionsPanel) return;
            hiddenSessionsPanel.classList.toggle('hidden');
            hiddenSessionsToggle.textContent = hiddenSessionsPanel.classList.contains('hidden')
                ? 'Ver sesiones ocultas'
                : 'Ocultar sesiones';
            hiddenSessionsToggle.setAttribute(
                'aria-expanded',
                hiddenSessionsPanel.classList.contains('hidden') ? 'false' : 'true'
            );
        });
    }

    if (sessionSearchInput) {
        sessionSearchInput.addEventListener('input', (e) => {
            sessionSearchTerm = e.target.value || '';
            loadSessions();
        });
    }

    if (exportSessionBtn) {
        exportSessionBtn.addEventListener('click', async () => {
            if (!currentSessionId) {
                showToast('No hay sesión activa para exportar.', 'warning');
                return;
            }
            try {
                const response = await fetch(`/sessions/${currentSessionId}`);
                const data = await response.json();
                const payload = {
                    session_id: currentSessionId,
                    exported_at: new Date().toISOString(),
                    messages: data.messages || []
                };
                const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `nexus_session_${currentSessionId}.json`;
                a.click();
                URL.revokeObjectURL(url);
                showToast('Sesión exportada.', 'info');
            } catch (error) {
                showToast(`Error exportando sesión: ${error.message}`, 'error');
            }
        });
    }

    if (clearChatBtn) {
        clearChatBtn.addEventListener('click', async () => {
            if (isStreaming) {
                showToast('Detén la ejecución actual antes de limpiar.', 'warning');
                return;
            }
            const confirmed = await showConfirm({
                title: 'Limpiar vista',
                message: '¿Deseas limpiar la vista del chat?',
                confirmLabel: 'Limpiar'
            });
            if (!confirmed) return;
            resetChatView('Vista limpiada.');
        });
    }

    if (resetFiltersBtn) {
        resetFiltersBtn.addEventListener('click', () => {
            sessionSearchTerm = '';
            if (sessionSearchInput) {
                sessionSearchInput.value = '';
            }
            if (hiddenSessionsPanel && hiddenSessionsToggle) {
                hiddenSessionsPanel.classList.add('hidden');
                hiddenSessionsToggle.textContent = 'Ver sesiones ocultas';
                hiddenSessionsToggle.setAttribute('aria-expanded', 'false');
            }
            loadSessions();
        });
    }

    if (scrollToLatestBtn && messageContainer) {
        scrollToLatestBtn.addEventListener('click', () => {
            messageContainer.scrollTop = messageContainer.scrollHeight;
            userScrolled = false;
            scrollToLatestBtn.classList.add('hidden');
        });
    }
}

function updateCharCounter() {
    if (!charCounter || !inputField) return;
    const count = inputField.value.length;
    charCounter.textContent = `${count}/${MAX_MESSAGE_LENGTH}`;
    charCounter.classList.toggle('text-red-400', count > MAX_MESSAGE_LENGTH);

    // Auto-resize textarea
    inputField.style.height = 'auto';
    const newHeight = Math.min(inputField.scrollHeight, 200); // Max 200px
    inputField.style.height = (newHeight > 48 ? newHeight : 48) + 'px';
}

function setSystemStatus(state) {
    if (!systemStatusLabel || !systemStatusDot) return;
    if (state === 'streaming') {
        systemStatusLabel.textContent = 'Streaming';
        systemStatusDot.className = 'w-1.5 h-1.5 rounded-full bg-[var(--accent-purple)] shadow-[0_0_8px_var(--accent-purple)]';
        return;
    }
    if (state === 'offline') {
        systemStatusLabel.textContent = 'Offline';
        systemStatusDot.className = 'w-1.5 h-1.5 rounded-full bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.6)]';
        return;
    }
    systemStatusLabel.textContent = 'Online';
    systemStatusDot.className = 'w-1.5 h-1.5 rounded-full bg-[var(--accent-cyan)] shadow-[0_0_8px_var(--accent-cyan)]';
}

async function checkConnection() {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), FRONTEND_CONFIG.connection.timeoutMs);
    try {
        const response = await fetch('/', { signal: controller.signal });
        lastConnectionOk = response.ok;
    } catch (e) {
        lastConnectionOk = false;
    } finally {
        clearTimeout(timeout);
        if (!isStreaming) {
            setSystemStatus(lastConnectionOk ? 'online' : 'offline');
        }
    }
}

async function initSessions() {
    const sessions = await loadSessions();
    const storedSessionId = localStorage.getItem('nexus_session_id');

    if (storedSessionId) {
        sessionAutoRestored = true;
        sessionExplicitSelection = false;
        await selectSession(storedSessionId);
        return;
    }

    if (sessions.length > 0) {
        sessionAutoRestored = true;
        sessionExplicitSelection = false;
        await selectSession(sessions[0].session_id);
    } else {
        createSession();
    }
}

function initUI() {
    cacheDom();
    if (!chatContainer || !inputField || !sendButton) {
        setTimeout(initUI, 100);
        return;
    }

    // Initialize Sidebar Logic (Safe to call here as DOM is cached/ready)
    if (UI.initResizeHandle) UI.initResizeHandle();
    if (UI.initSidebarTabs) UI.initSidebarTabs();

    bindEvents();
    initKeyboardShortcuts();
    initSessions();
    initSidebarToggle();
    updateCharCounter();
    checkConnection();
    setInterval(checkConnection, FRONTEND_CONFIG.connection.checkIntervalMs);
    window.addEventListener('online', () => {
        lastConnectionOk = true;
        if (!isStreaming) setSystemStatus('online');
    });
    window.addEventListener('offline', () => {
        lastConnectionOk = false;
        if (!isStreaming) setSystemStatus('offline');
    });
    if (messageContainer) {
        // Intersection Observer for Carousel Focus and Radioactive Glow
        const focusObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('carousel-focus');
                } else {
                    entry.target.classList.remove('carousel-focus');
                }
            });
        }, {
            root: messageContainer,
            threshold: 0.6, // More than 60% visible
            rootMargin: "-20% 0px -20% 0px" // Focus on center
        });

        // Helper to watch new elements
        const observerInstance = new MutationObserver((mutations) => {
            mutations.forEach(mutation => {
                mutation.addedNodes.forEach(node => {
                    if (node.nodeType === 1 && (node.matches('.agent-card-container') || node.matches('.operator-bubble'))) {
                        focusObserver.observe(node);
                    }
                    if (node.nodeType === 1) {
                        node.querySelectorAll('.agent-card-container, .operator-bubble').forEach(child => focusObserver.observe(child));
                    }
                });
            });
        });
        observerInstance.observe(messageContainer, { childList: true, subtree: true });

        messageContainer.addEventListener('scroll', () => {
            const isNearBottom = messageContainer.scrollHeight - messageContainer.scrollTop - messageContainer.clientHeight < FRONTEND_CONFIG.scroll.bottomThresholdPx;
            userScrolled = !isNearBottom;
            if (isNearBottom && scrollToLatestBtn) {
                scrollToLatestBtn.classList.add('hidden');
            }
        });
    }
}

function initKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
            e.preventDefault();
            if (sessionSearchInput) {
                sessionSearchInput.focus();
                sessionSearchInput.select();
            }
        }
        if (e.key === 'Escape' && sessionSearchInput) {
            if (document.activeElement === sessionSearchInput) {
                sessionSearchInput.value = '';
                sessionSearchTerm = '';
                loadSessions();
                sessionSearchInput.blur();
            }
        }
    });
}

function initSidebarToggle() {
    const sidebar = document.querySelector('aside');
    const toggleBtn = document.getElementById('sidebar-toggle');
    const toggleIcon = document.getElementById('toggle-icon');

    if (!sidebar || !toggleBtn || !toggleIcon) return;

    // Check localStorage for saved state
    const isCollapsed = localStorage.getItem('sidebar_collapsed') === 'true';
    if (isCollapsed) {
        sidebar.classList.add('collapsed');
        toggleIcon.textContent = 'menu';
    }

    toggleBtn.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
        const collapsed = sidebar.classList.contains('collapsed');
        toggleIcon.textContent = collapsed ? 'menu' : 'menu_open';
        localStorage.setItem('sidebar_collapsed', collapsed);
    });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        console.log("DEBUG: DOMContentLoaded triggered");
        try {
            initUI();
        } catch (e) {
            console.error("FATAL: Error in initUI:", e);
        }
    });
} else {
    try {
        console.log("DEBUG: Document ready, calling initUI directly");
        initUI();
    } catch (e) {
        console.error("FATAL: Error in immediate initUI:", e);
    }
}

// Global Event Delegation for Dynamic Elements (Cards)
document.addEventListener('click', (e) => {
    // Find closest card header
    const header = e.target.closest('.toggle-header');
    if (header) {
        const group = header.closest('.group');
        if (group && group.id) {
            UI.toggleCard(group.id);
        }
    }
    const retryBtn = e.target.closest('[data-retry="true"]');
    if (retryBtn) {
        if (!lastUserMessage || isStreaming) return;
        sendMessageWithText(lastUserMessage, { isRetry: true });
    }
});

// Styles for Fade In
const style = document.createElement('style');
style.innerHTML = `
.fade-in { animation: fadeIn 0.3s ease-out forwards; opacity: 0; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
`;
document.head.appendChild(style);

// --- File Upload Logic ---
const uploadBtn = document.getElementById('upload-btn');
const fileInput = document.getElementById('file-input');

if (uploadBtn && fileInput) {
    uploadBtn.addEventListener('click', () => {
        fileInput.click();
    });
    uploadBtn.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            fileInput.click();
        }
    });

    fileInput.addEventListener('change', async (e) => {
        if (e.target.files && e.target.files.length > 0) {
            const file = e.target.files[0];
            await uploadFile(file);
            // Reset input so same file can be selected again if needed
            fileInput.value = '';
        }
    });
}

function validateUploadFile(file) {
    if (!file) return { ok: false, message: 'Archivo inválido.' };
    if (file.size > FRONTEND_CONFIG.upload.maxSizeBytes) {
        const maxMb = Math.round(FRONTEND_CONFIG.upload.maxSizeBytes / (1024 * 1024));
        return { ok: false, message: `El archivo supera el límite de ${maxMb} MB.` };
    }
    const hasAllowedType = FRONTEND_CONFIG.upload.allowedMimeTypes.includes(file.type);
    const hasPdfExtension = /\.pdf$/i.test(file.name || '');
    if (FRONTEND_CONFIG.upload.allowedMimeTypes.length > 0
        && !hasAllowedType
        && !hasPdfExtension) {
        return { ok: false, message: 'Formato no permitido. Solo PDF.' };
    }
    return { ok: true };
}

async function uploadFile(file) {
    const turnGroup = UI.ensureAgentGroup(chatContainer);
    const validation = validateUploadFile(file);
    if (!validation.ok) {
        const bubble = UI.getOrCreateAgentBubble(turnGroup);
        bubble.innerHTML += `<div class="mt-2 text-xs text-red-500">❌ ${validation.message}</div>`;
        showToast(validation.message, 'warning');
        return;
    }

    // UI Feedback: Uploading
    const uploadId = 'upload-' + Date.now();
    turnGroup.insertAdjacentHTML('beforeend', `
        <div id="${uploadId}" class="flex items-center gap-2 mb-2 ml-4">
            <span class="material-symbols-outlined text-[var(--accent-cyan)] animate-spin text-sm">sync</span>
            <span class="text-[10px] text-[var(--text-muted)] mono uppercase tracking-widest">Uploading ${file.name}...</span>
        </div>
    `);

    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        // Remove loading state
        const uploadEl = document.getElementById(uploadId);
        if (uploadEl) uploadEl.remove();

        if (response.ok && result.status === "success") {
            // Success Message
            chatContainer.insertAdjacentHTML('beforeend', UI.createOperatorBubble(`📂 Archivo subido: **${file.name}**`));
            // System Confirmation
            const bubble = UI.getOrCreateAgentBubble(turnGroup);
            bubble.innerHTML += `<div class="mt-2 text-xs text-[var(--accent-cyan)]">✅ Archivo indexado en la Base de Conocimiento. Puedes preguntarme sobre él.</div>`;
            showToast('Archivo subido correctamente.', 'info');
        } else {
            // Error Message
            const bubble = UI.getOrCreateAgentBubble(turnGroup);
            bubble.innerHTML += `<div class="mt-2 text-xs text-red-500">❌ Error al subir archivo: ${result.message || 'Error desconocido'}</div>`;
            showToast(`Error al subir: ${result.message || 'Error desconocido'}`, 'error');
        }

        chatContainer.scrollTop = chatContainer.scrollHeight;
    } catch (error) {
        console.error('Upload error:', error);
        const uploadEl = document.getElementById(uploadId);
        if (uploadEl) uploadEl.remove();
        const bubble = UI.getOrCreateAgentBubble(turnGroup);
        bubble.innerHTML += `<div class="mt-2 text-xs text-red-500">❌ Error de conexión: ${error.message}</div>`;
    }
}
