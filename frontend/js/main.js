import { API_URL } from './api.js';
import * as UI from './ui.js';

let chatContainer;
let inputField;
let sendButton;
let sessionList;
let newSessionBtn; // "Ini_Session" button

let currentSessionId = null;

function cacheDom() {
    chatContainer = document.querySelector('.space-y-10');
    inputField = document.getElementById('message-input');
    sendButton = document.getElementById('send-btn');
    sessionList = document.getElementById('session-list');
    newSessionBtn = document.querySelector('.border-dashed');
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

// --- Session Logic ---
async function loadSessions() {
    try {
        const response = await fetch('/sessions');
        const sessions = await response.json();
        renderSessionList(sessions);
        return sessions;
    } catch (e) {
        console.error("Failed to load sessions:", e);
        return [];
    }
}

function renderSessionList(sessions) {
    if (!sessionList) return;
    sessionList.innerHTML = '';

    // Sort by updated_at desc (fallback to created_at)
    sessions.sort((a, b) => {
        const aTime = a.updated_at || a.created_at || 0;
        const bTime = b.updated_at || b.created_at || 0;
        return bTime - aTime;
    });

    sessions.forEach(session => {
        const li = document.createElement('li');
        li.dataset.sessionId = session.session_id;
        li.className = `text-[11px] text-[var(--text-muted)] hover:text-[var(--text-main)] cursor-pointer truncate py-1 px-2 rounded hover:bg-[rgba(255,255,255,0.05)] transition-colors ${session.session_id === currentSessionId ? 'text-[var(--accent-cyan)] font-bold' : ''}`;
        li.textContent = session.title || "Untitled Mission";
        li.title = session.title; // Tooltip
        li.onclick = () => selectSession(session.session_id);
        sessionList.appendChild(li);
    });
}

function createSession() {
    if (!chatContainer) return;
    setCurrentSessionId(uuidv4());
    chatContainer.innerHTML = ''; // Clear chat
    // Add Welcome Message
    chatContainer.innerHTML = `
        <div class="text-[12px] text-[var(--text-muted)] mono leading-relaxed opacity-60">
            Agent Zero v2.0 Online. Systems Nominal.<br />
            New Mission Initialized: ${currentSessionId.split('-')[0]}...<br />
            Waiting for operator input...
        </div>
    `;
    // Reload list to remove highlight from previous
    loadSessions();
}

async function selectSession(sessionId) {
    if (currentSessionId === sessionId) return;

    setCurrentSessionId(sessionId);
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
            chatContainer.innerHTML = `
                <div class="text-[12px] text-[var(--text-muted)] mono leading-relaxed opacity-60">
                    Agent Zero v2.0 Online. Systems Nominal.<br />
                    Mission Restore Complete.<br />
                    Waiting for operator input...
                </div>
            `;
        } else {
            renderHistory(messages);
        }

    } catch (e) {
        console.error("Error loading session:", e);
        chatContainer.innerHTML = '<div class="text-red-500 text-xs mt-10">Error loading mission data.</div>';
    }

    loadSessions(); // Re-render list to highlight current
}

function renderHistory(messages) {
    if (!chatContainer) return;
    let currentGroup = null;

    messages.forEach(msg => {
        if (msg.role === 'user') {
            chatContainer.insertAdjacentHTML('beforeend', UI.createOperatorBubble(msg.content));
            currentGroup = null; // Reset group
        } else if (msg.role === 'assistant') {
            currentGroup = UI.ensureAgentGroup(chatContainer);

            // This is a simplified history renderer. 
            // Ideally we should store tool calls separately or parse them.
            // Agno stores "content" which might be the final answer.
            // It might also store "tool_calls" but Agno's memory format varies.
            // Assuming simplified content for now.
            if (msg.content) {
                const bubble = UI.getOrCreateAgentBubble(currentGroup);
                // Append content
                bubble.dataset.markdownBuffer = (bubble.dataset.markdownBuffer || "") + msg.content;
                bubble.innerHTML = UI.parseMarkdown(bubble.dataset.markdownBuffer);
            }
        }
    });
    chatContainer.scrollTop = chatContainer.scrollHeight;
}


async function sendMessage() {
    if (!inputField) return;
    const message = inputField.value.trim();
    if (!message) return;

    // Ensure session exists
    if (!currentSessionId) {
        createSession();
    }

    inputField.value = '';
    chatContainer.insertAdjacentHTML('beforeend', UI.createOperatorBubble(message));
    chatContainer.scrollTop = chatContainer.scrollHeight;

    const turnGroup = UI.ensureAgentGroup(chatContainer);

    try {
        // Mostrar estado "Procesando"
        const loadingId = 'loading-' + Date.now();
        turnGroup.insertAdjacentHTML('beforeend', `
            <div id="${loadingId}" class="text-[10px] text-[var(--text-muted)] mono ml-4 uppercase tracking-widest animate-pulse">
                // Nexus Processing Data...
            </div>
        `);

        // Update list title after first message (delayed)
        setTimeout(loadSessions, 2000);

        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                session_id: currentSessionId
            })
        });

        // Remover loader inicial al recibir primeros bytes
        const loader = document.getElementById(loadingId);
        if (loader) loader.remove();

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            const lines = chunk.split('\n\n');

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const dataStr = line.slice(6);
                    if (dataStr === '[DONE]') break;

                    try {
                        const event = JSON.parse(dataStr);
                        // console.log("[SSE Event]", event); // DEBUG: Full event log
                        handleEvent(event, turnGroup);
                    } catch (e) {
                        console.error("Error parsing JSON", e);
                    }
                }
            }
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

    } catch (error) {
        console.error('Error:', error);
        const bubble = UI.getOrCreateAgentBubble(turnGroup);
        bubble.innerHTML += `<br><span class="text-red-500">System Error: ${error.message}</span>`;
    }
}

function handleEvent(event, group) {
    const eventType = event.event;

    // 1. REASONING
    if (eventType === "ReasoningStarted" || (eventType === "RunContent" && event.reasoning_content)) {
        // Scoped search within the current turn group
        let cardContainer = group.querySelector('.thinking-card-active');

        if (!cardContainer) {
            const { html, id } = UI.createExecutionCard('psychology', 'Thought_Process', 'analyzing', 'Processing', 'var(--accent-cyan)');
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = html;
            cardContainer = tempDiv.firstElementChild;
            // Add a class marker instead of mutating global ID
            cardContainer.classList.add('thinking-card-active');
            group.appendChild(cardContainer);
        }

        // Append content if available
        if (event.reasoning_content) {
            const details = cardContainer.querySelector('.card-details');
            if (details) {
                const text = event.reasoning_content.replace(/\n/g, '<br>');
                details.innerHTML += text;
            }
        }
    }

    // 2. TOOL EXECUTION
    // Debug logging for tool events
    // if (eventType && eventType.toLowerCase().includes('tool')) {
    //     console.log("Tool Event Received:", event);
    // }

    if (eventType === "ToolCallStarted" || eventType === "tool_call_started") {
        const toolName = event.tool ? event.tool.tool_name : 'unknown_tool';
        // Extract args safely
        let toolArgs = '';
        if (event.tool && event.tool.tool_args) {
            try {
                toolArgs = JSON.stringify(event.tool.tool_args, null, 2);
            } catch (e) {
                toolArgs = String(event.tool.tool_args);
            }
        }

        // Get or create the Tools container for this agent group
        let toolsContainer = group.querySelector('.tools-container-active');

        if (!toolsContainer) {
            // Create parent Tools container
            const { html: containerHtml, id: containerId } = UI.createExecutionCard(
                'build',
                'Tools_Execution',
                'agent_tools',
                'Active',
                'var(--accent-orange)'
            );
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = containerHtml;
            toolsContainer = tempDiv.firstElementChild;
            toolsContainer.classList.add('tools-container-active');

            // Find or create the details section to hold individual tools
            let containerDetails = toolsContainer.querySelector('.card-details');
            if (containerDetails) {
                containerDetails.classList.remove('hidden'); // Keep it open
                containerDetails.innerHTML = '<div class="space-y-2 tools-list"></div>';
            }

            group.appendChild(toolsContainer);
        }

        // Create individual tool card (smaller, as a sub-item)
        const toolCard = document.createElement('div');
        toolCard.className = 'tool-item border-l-2 border-l-[var(--accent-orange)] pl-3 py-2 bg-[rgba(255,255,255,0.01)] rounded';
        toolCard.dataset.toolName = toolName;

        toolCard.innerHTML = `
            <div class="flex items-center justify-between mb-1">
                <div class="flex items-center gap-2">
                    <span class="material-symbols-outlined text-[14px] text-[var(--accent-orange)]">terminal</span>
                    <span class="text-[10px] font-bold uppercase tracking-widest text-[var(--text-main)]">${toolName}</span>
                </div>
                <span class="tool-status text-[9px] font-bold text-[var(--accent-orange)] tracking-widest uppercase">Running</span>
            </div>
            <div class="tool-content text-[11px] text-[var(--text-muted)] mono">
                ${toolArgs ? `<details class="mt-1"><summary class="cursor-pointer text-[var(--accent-cyan)] text-[10px]">Arguments</summary><pre class="whitespace-pre-wrap mt-1 opacity-80 text-[10px]">${toolArgs}</pre></details>` : ''}
            </div>
        `;

        // Append to tools list inside container
        const toolsList = toolsContainer.querySelector('.tools-list');
        if (toolsList) {
            toolsList.appendChild(toolCard);
        }
    }

    if (eventType === "ToolCallCompleted" || eventType === "tool_call_completed") {
        // Find the tools container
        const toolsContainer = group.querySelector('.tools-container-active');
        if (!toolsContainer) return;

        // Find the LAST tool that is still running
        const toolItems = toolsContainer.querySelectorAll('.tool-item');
        for (let i = toolItems.length - 1; i >= 0; i--) {
            const statusSpan = toolItems[i].querySelector('.tool-status');
            if (statusSpan && statusSpan.textContent === 'Running') {
                statusSpan.textContent = 'Done';
                statusSpan.style.color = 'var(--accent-cyan)';

                // Update icon color
                const icon = toolItems[i].querySelector('.material-symbols-outlined');
                if (icon) icon.style.color = 'var(--accent-cyan)';

                // Add output if available
                const outputContent = event.tool_output || (event.tool && event.tool.tool_output) || (event.tool && event.tool.result);

                if (outputContent) {
                    const toolContent = toolItems[i].querySelector('.tool-content');
                    if (toolContent) {
                        const formattedOutput = UI.formatToolOutput(outputContent);
                        toolContent.innerHTML += `<details class="mt-2"><summary class="cursor-pointer text-[var(--accent-cyan)] text-[10px]">Output</summary><div class="mt-1 text-[10px]">${formattedOutput}</div></details>`;
                    }
                }

                break;
            }
        }
    }

    // WORKFLOW EVENTS: Planning, Review
    if (eventType === "PlanningStarted") {
        const planningCard = UI.createExecutionCard(
            'task',
            'Mission_Planning',
            'Analyzing request',
            'Active',
            'var(--accent-cyan)'
        );
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = planningCard.html;
        group.appendChild(tempDiv.firstElementChild);
    }

    if (eventType === "PlanCreated") {
        const planPath = event.plan_path || "unknown";
        const planCard = UI.createExecutionCard(
            'insert_drive_file',
            'Plan_Created',
            event.content || 'Mission plan generated',
            'Success',
            'var(--accent-cyan)'
        );
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = planCard.html;
        const cardEl = tempDiv.firstElementChild;

        // Add link to view plan (future enhancement)
        const details = cardEl.querySelector('.card-details');
        if (details) {
            details.innerHTML = `<div class="mt-2 text-[10px]">📄 ${planPath}</div>`;
            group.appendChild(cardEl);

            // Initialize Progress Tracker
            if (window.ProgressTracker) {
                const taskMatch = event.content.match(/(\d+) tareas/);
                const taskCount = taskMatch ? parseInt(taskMatch[1]) : 3;
                const missionTitle = event.content || "Executing complex mission";

                ProgressTracker.create(taskCount, missionTitle);
                ProgressTracker.addTask('task-research', 'Web Research & Data Gathering', 'Researcher');
                ProgressTracker.addTask('task-analysis', 'Analysis & Processing', 'Analyst');
                if (taskCount >= 3) {
                    ProgressTracker.addTask('task-visualization', 'Chart Generation', 'Visualizer');
                }
            }
        }
    }

    if (eventType === "ReviewStarted") {
        const reviewCard = UI.createExecutionCard(
            'fact_check',
            'Quality_Review',
            'Reviewer validating results',
            'Active',
            'var(--accent-purple)'
        );
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = reviewCard.html;
        group.appendChild(tempDiv.firstElementChild);
    }

    if (eventType === "ReviewCompleted") {
        const status = event.status || "UNKNOWN";
        const statusIcon = status === "APPROVED" ? 'check_circle' : 'warning';
        const statusColor = status === "APPROVED" ? 'var(--accent-cyan)' : 'var(--accent-orange)';

        const reviewCard = UI.createExecutionCard(
            statusIcon,
            'Review_Result',
            event.content || 'Review completed',
            status,
            statusColor
        );
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = reviewCard.html;
        group.appendChild(tempDiv.firstElementChild);
    }

    // 3. MAIN CONTENT
    if (eventType === "RunContent" && event.content) {
        let bubble;

        // Detect Specialist Agent
        const agentName = event.agent_name || (event.model_provider_data && event.model_provider_data.agent_name);

        // Update Progress Tracker based on agent activation
        if (window.ProgressTracker && window.ProgressTracker.currentProgress) {
            if (agentName === "Researcher") {
                ProgressTracker.updateTaskStatus('task-research', 'in-progress');
            } else if (agentName === "Analyst") {
                // Researcher is done, Analyst is starting
                ProgressTracker.updateTaskStatus('task-research', 'completed');
                ProgressTracker.updateTaskStatus('task-analysis', 'in-progress');
            } else if (agentName === "Visualizer") {
                // Analyst is done, Visualizer is starting
                ProgressTracker.updateTaskStatus('task-analysis', 'completed');
                ProgressTracker.updateTaskStatus('task-visualization', 'in-progress');
            } else if (agentName === "Reviewer") {
                // All main tasks done, reviewing
                ProgressTracker.updateTaskStatus('task-visualization', 'completed');
            }
        }

        // "Nexus Manager" is the main agent, so we treat it as default. Others are sub-agents.
        if (agentName && agentName !== "Nexus Manager") {
            bubble = UI.createSubAgentBubble(group, agentName);
        } else {
            bubble = UI.getOrCreateAgentBubble(group);
        }

        // Initialize buffer on the element if not present
        if (!bubble.dataset.markdownBuffer) {
            bubble.dataset.markdownBuffer = "";
        }

        // Append new content to buffer
        bubble.dataset.markdownBuffer += event.content;

        // Render FULL buffer
        const fullMarkdown = bubble.dataset.markdownBuffer;
        bubble.innerHTML = UI.parseMarkdown(fullMarkdown);

        // Trigger syntax highlighting for new code blocks
        if (typeof hljs !== 'undefined') {
            bubble.querySelectorAll('pre code').forEach((block) => {
                hljs.highlightElement(block);
            });
        }

    }

    // Smart Autoscroll - Only activate on manual scroll or when user is at bottom
    let userScrolled = false;
    let lastMessageCount = 0;

    function smartScroll(container) {
        const messageContainer = document.querySelector('.flex-grow.overflow-y-auto');
        if (messageContainer) {
            const currentMessageCount = messageContainer.querySelectorAll('.message-bubble').length;

            // Check if new messages were added
            const hasNewMessages = currentMessageCount > lastMessageCount;
            lastMessageCount = currentMessageCount;

            // Only auto-scroll if:
            // 1. User manually scrolled up (userScrolled is false)
            // 2. New messages were added AND user is near bottom
            const isNearBottom = messageContainer.scrollHeight - messageContainer.scrollTop - messageContainer.clientHeight < 250;

            if (!userScrolled && isNearBottom && hasNewMessages) {
                messageContainer.scrollTop = messageContainer.scrollHeight;
            }
        }
    }

    // Track user scroll position
    const messageContainer = document.querySelector('.flex-grow.overflow-y-auto');
    if (messageContainer) {
        messageContainer.addEventListener('scroll', () => {
            const isNearBottom = messageContainer.scrollHeight - messageContainer.scrollTop - messageContainer.clientHeight < 250;
            userScrolled = !isNearBottom;
        });
    }
}

// --- Bindings ---
function bindEvents() {
    if (sendButton) {
        sendButton.addEventListener('click', sendMessage);
    }

    if (inputField) {
        inputField.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }

    if (newSessionBtn) {
        newSessionBtn.addEventListener('click', createSession);
    }
}

async function initSessions() {
    const sessions = await loadSessions();
    const storedSessionId = localStorage.getItem('nexus_session_id');

    if (storedSessionId) {
        await selectSession(storedSessionId);
        return;
    }

    if (sessions.length > 0) {
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
    bindEvents();
    initSessions();
    initSidebarToggle();
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
    document.addEventListener('DOMContentLoaded', initUI);
} else {
    initUI();
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

    fileInput.addEventListener('change', async (e) => {
        if (e.target.files && e.target.files.length > 0) {
            const file = e.target.files[0];
            await uploadFile(file);
            // Reset input so same file can be selected again if needed
            fileInput.value = '';
        }
    });
}

async function uploadFile(file) {
    const turnGroup = UI.ensureAgentGroup(chatContainer);

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
        document.getElementById(uploadId).remove();

        if (response.ok && result.status === "success") {
            // Success Message
            chatContainer.insertAdjacentHTML('beforeend', UI.createOperatorBubble(`📂 Archivo subido: **${file.name}**`));
            // System Confirmation
            const bubble = UI.getOrCreateAgentBubble(turnGroup);
            bubble.innerHTML += `<div class="mt-2 text-xs text-[var(--accent-cyan)]">✅ Archivo indexado en la Base de Conocimiento. Puedes preguntarme sobre él.</div>`;
        } else {
            // Error Message
            const bubble = UI.getOrCreateAgentBubble(turnGroup);
            bubble.innerHTML += `<div class="mt-2 text-xs text-red-500">❌ Error al subir archivo: ${result.message || 'Error desconocido'}</div>`;
        }

        chatContainer.scrollTop = chatContainer.scrollHeight;
    } catch (error) {
        console.error('Upload error:', error);
        document.getElementById(uploadId).remove();
        const bubble = UI.getOrCreateAgentBubble(turnGroup);
        bubble.innerHTML += `<div class="mt-2 text-xs text-red-500">❌ Error de conexión: ${error.message}</div>`;
    }
}
