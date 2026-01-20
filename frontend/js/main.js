import { API_URL } from './api.js';
import * as UI from './ui.js';

const chatContainer = document.querySelector('.space-y-10');
const inputField = document.querySelector('textarea');
const sendButton = document.querySelector('button');

async function sendMessage() {
    const message = inputField.value.trim();
    if (!message) return;

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

        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
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
                        console.log("[SSE Event]", event); // DEBUG: Full event log
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
                // Remove hidden class on first content to auto-expand or just show it exists? 
                // Let's keep it collapsed by default unless user clicks, OR maybe auto-expand nicely?
                // For now, just append text.
                // Simple text append, replacing newlines
                const text = event.reasoning_content.replace(/\n/g, '<br>');
                details.innerHTML += text;
            }
        }
    }

    // 2. TOOL EXECUTION
    // Debug logging for tool events
    if (eventType && eventType.toLowerCase().includes('tool')) {
        console.log("Tool Event Received:", event);
    }

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

        const { html, id } = UI.createExecutionCard('terminal', 'Exec_Code', toolName, 'Running', 'var(--accent-orange)');
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = html;
        const card = tempDiv.firstElementChild;
        card.dataset.toolId = id;

        // Inject arguments into details
        if (toolArgs) {
            const details = card.querySelector('.card-details');
            if (details) {
                details.innerHTML = `<div class="mb-2"><span class="text-[var(--accent-cyan)] font-bold">Arguments:</span><pre class="whitespace-pre-wrap mt-1 opacity-80">${toolArgs}</pre></div>`;
            }
        }

        group.appendChild(card);
    }

    if (eventType === "ToolCallCompleted" || eventType === "tool_call_completed") {
        // Find the LAST card that is still running, implicitly assuming standard order. 
        // A better way would be using tool_call_id if available, but for now this works for sequential tools.
        const cards = group.querySelectorAll('.execution-card');
        for (let i = cards.length - 1; i >= 0; i--) {
            const statusSpan = cards[i].querySelector('.status-text');
            if (statusSpan && statusSpan.textContent === 'Running') {
                statusSpan.textContent = 'Success';
                statusSpan.style.color = 'var(--accent-cyan)';
                const icon = cards[i].querySelector('.material-symbols-outlined');
                if (icon) icon.style.color = 'var(--accent-cyan)';

                // Update parent wrapper border hover effect if needed, but mainly update content
                const cardWrapper = cards[i].parentElement; // .group
                if (cardWrapper) {
                    const details = cardWrapper.querySelector('.card-details');
                    // Check multiple locations for output
                    const outputContent = event.tool_output || (event.tool && event.tool.tool_output) || (event.tool && event.tool.result);

                    if (details && outputContent) {
                        const formattedOutput = UI.formatToolOutput(outputContent);
                        details.innerHTML += `<div class="mt-2 border-t border-[var(--border)] pt-2"><span class="text-[var(--accent-cyan)] font-bold">Output:</span>${formattedOutput}</div>`;
                    }
                }
                cards[i].classList.remove('border-l-[var(--accent-orange)]');
                break;
            }
        }
    }

    // 3. MAIN CONTENT
    if (eventType === "RunContent" && event.content) {
        let bubble;

        // Detect Specialist Agent
        const agentName = event.agent_name || (event.model_provider_data && event.model_provider_data.agent_name);
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

        // Smart Autoscroll
        const messageContainer = document.querySelector('.flex-grow.overflow-y-auto');
        if (messageContainer) {
            // Check if user is near the bottom (within 100px) BEFORE content creates new height? 
            // Actually, we want to know if they WERE at bottom.
            // But since 'RunContent' fires frequently, we check if they correspond to the "stickiness".

            // Simple logic: If user is not "scrolled up" significantly, auto scroll.
            // Tolerance: 150px
            const isNearBottom = messageContainer.scrollHeight - messageContainer.scrollTop - messageContainer.clientHeight < 150;

            if (isNearBottom) {
                messageContainer.scrollTop = messageContainer.scrollHeight;
            }
        }
    }
}

sendButton.addEventListener('click', sendMessage);
inputField.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

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
