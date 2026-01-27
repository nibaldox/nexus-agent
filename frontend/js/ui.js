import { FRONTEND_CONFIG } from './config.js';

let purifyHooksReady = false;

function ensurePurifyHooks() {
    if (purifyHooksReady || typeof DOMPurify === 'undefined') return;
    DOMPurify.addHook('afterSanitizeAttributes', (node) => {
        if (node.tagName === 'A') {
            if (node.getAttribute('target') === '_blank') {
                node.setAttribute('rel', 'noopener noreferrer');
            }
        }
        if (node.tagName === 'IFRAME') {
            if (!node.getAttribute('sandbox')) {
                node.setAttribute('sandbox', 'allow-same-origin allow-scripts allow-popups allow-forms');
            }
            node.setAttribute('loading', 'lazy');
        }
    });
    purifyHooksReady = true;
}

export function parseMarkdown(text) {
    if (!text) return '';
    const theme = document.documentElement.getAttribute('data-theme') || 'dark';
    const proseClass = theme === 'light'
        ? 'prose max-w-none text-[13px] leading-snug break-words'
        : 'prose prose-invert max-w-none text-[13px] leading-snug break-words';

    if (typeof marked !== 'undefined') {
        const htmlContent = marked.parse(text, {
            mangle: false,
            headerIds: false,
            breaks: true,
            gfm: true
        });
        ensurePurifyHooks();
        const sanitized = (typeof DOMPurify !== 'undefined')
            ? DOMPurify.sanitize(htmlContent, {
                ADD_TAGS: ['iframe'],
                ADD_ATTR: ['allow', 'allowfullscreen', 'frameborder', 'scrolling', 'src', 'width', 'height', 'style', 'class', 'target', 'rel', 'sandbox', 'loading']
            })
            : htmlContent;
        return `<div class="${proseClass}">${sanitized}</div>`;
    }
    return text.replace(/\n/g, '<br>');
}

export function createOperatorBubble(text) {
    return `
    <div class="flex flex-col items-end space-y-2 fade-in-up mb-8">
        <div class="flex items-center gap-2 mb-1">
            <span class="text-[10px] uppercase tracking-widest font-bold text-[var(--text-muted)]">Operator</span>
            <span class="text-[9px] mono text-[var(--text-muted)] opacity-50">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
        </div>
        <div class="operator-bubble max-w-[80%]">
            <p class="text-[15px] leading-relaxed text-[var(--text-main)] mono">
                ${text}
            </p>
        </div>
    </div>`;
}

// --- Agent Card System (New) ---

export function ensureAgentGroup(container) {
    // This creates a container for a full "Turn" (User -> Assistant(s))
    // But internally we will stack Agent Cards.
    const last = container.lastElementChild;
    if (last && last.classList.contains('agent-message-group')) {
        return last;
    }
    const group = document.createElement('div');
    group.className = "agent-message-group";
    container.appendChild(group);
    return group;
}

export function ensureAgentCard(group, agentName = "Nexus") {
    // safeName for semantic mapping (technical ID)
    const technicalId = agentName.trim().toLowerCase().replace(/[\s\W]+/g, '_');

    // Logic: If the LAST card in the group is THIS agent, reuse it.
    const lastCard = group.lastElementChild;
    if (lastCard && lastCard.dataset.technicalId === technicalId) {
        return lastCard;
    }

    // Create New Agent Card
    const card = document.createElement('div');
    const isMain = agentName.toLowerCase().includes('zero') || agentName.toLowerCase().includes('nexus') || agentName.toLowerCase().includes('assistant');
    const accentColor = isMain ? 'var(--accent-cyan)' : 'var(--accent-purple)';
    const agentTypeClass = isMain ? 'agent-nexus' : 'agent-specialist';
    card.className = `agent-card-container flex flex-col mb-4 rounded-lg border border-[var(--border)] ${agentTypeClass}`;
    card.dataset.technicalId = technicalId;

    // Avatar / Header
    const initial = agentName[0].toUpperCase();
    card.innerHTML = `
        <div class="agent-card-header bg-[rgba(0,0,0,0.2)] px-4 py-2 flex items-center gap-3 border-b border-[var(--border)]">
            <div class="agent-avatar-small" style="color: ${accentColor}; border-color: ${accentColor}40; background: ${accentColor}10;">
                <span class="material-symbols-outlined text-[14px]">${isMain ? 'smart_toy' : 'person'}</span>
            </div>
            <span class="agent-name-label font-bold text-[11px] uppercase tracking-wider" style="color: ${accentColor}">${agentName}</span>
            <span class="text-[9px] mono text-[var(--text-muted)] opacity-50 ml-auto">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
        </div>
        <div class="agent-card-body p-5 relative overflow-visible">
            <div class="tools-container space-y-3 mb-3"></div>
            <div class="thinking-container mb-3"></div>
            <div class="response-content text-[14px] text-[var(--text-main)] mono leading-relaxed break-words overflow-wrap-anywhere"></div>
        </div>
    `;

    group.appendChild(card);
    return card;
}

export function renderThinking(card, content) {
    if (!content) return;
    const container = card.querySelector('.thinking-container');
    if (!container) return;

    let block = container.querySelector('.thinking-process-block');
    if (!block) {
        block = document.createElement('div');
        block.className = "thinking-process-block";
        block.innerHTML = `
            <div class="thinking-header" onclick="this.parentElement.classList.toggle('collapsed')">
                <div class="flex items-center gap-2">
                    <span class="material-symbols-outlined text-[14px] animate-pulse text-[var(--accent-cyan)]">psychology</span>
                    <span class="text-[11px] font-bold">Reasoning Process</span>
                </div>
                <span class="material-symbols-outlined text-[14px] chevron transition-transform transform rotate-0">expand_more</span>
            </div>
            <div class="thinking-content hidden text-[12px]"></div>
        `;

        const header = block.querySelector('.thinking-header');
        const contentDiv = block.querySelector('.thinking-content');
        const chevron = block.querySelector('.chevron');

        header.onclick = () => {
            const isHidden = contentDiv.classList.contains('hidden');
            if (isHidden) {
                contentDiv.classList.remove('hidden');
                chevron.style.transform = 'rotate(180deg)';
                block.classList.remove('collapsed');
            } else {
                contentDiv.classList.add('hidden');
                chevron.style.transform = 'rotate(0deg)';
                block.classList.add('collapsed');
            }
        };

        container.appendChild(block);
    }

    const contentDiv = block.querySelector('.thinking-content');
    contentDiv.innerHTML = parseMarkdown(content);
}

export function renderToolCompact(card, toolName, args, output) {
    const container = card.querySelector('.tools-container');
    if (!container) return;

    // Check if tool already exists (for updates) - crude check by last child or name
    // For streaming updates (output arriving later), we might need an ID.
    // Assuming sequential appends for now.

    // Determine status
    const isDone = output !== undefined && output !== null;
    const statusColor = isDone ? 'var(--accent-cyan)' : 'var(--accent-orange)';

    // Formatting Args
    let argsText = '';
    try {
        argsText = typeof args === 'object' ? JSON.stringify(args) : String(args);
    } catch { argsText = '...'; }

    // If output exists, format it
    const outputHtml = formatToolOutput(output);

    // Check if we are updating the last tool (if name matches and it's running)
    const lastTool = container.lastElementChild;
    const isUpdate = lastTool && lastTool.dataset.toolName === toolName && lastTool.dataset.status !== 'DONE' && isDone;

    let toolDiv = isUpdate ? lastTool : document.createElement('div');

    if (!isUpdate) {
        toolDiv.className = "tool-execution-compact";
        toolDiv.dataset.toolName = toolName;
    }

    toolDiv.dataset.status = isDone ? 'DONE' : 'RUN';

    toolDiv.innerHTML = `
        <div class="tool-header-compact">
            <div class="tool-name-tag">
                <span class="material-symbols-outlined text-[14px]">terminal</span>
                <span class="text-[11px] font-bold">${toolName}</span>
            </div>
            <div class="tool-args-collapsed text-[11px]">${argsText}</div>
            <div class="flex items-center gap-2">
                 <span class="text-[10px] font-bold" style="color: ${statusColor}">${isDone ? 'DONE' : 'RUN'}</span>
                 <span class="material-symbols-outlined text-[14px] text-[var(--text-muted)] chevron">expand_more</span>
            </div>
        </div>
        <div class="tool-body-details ${isDone ? 'hidden' : ''}"> <!-- Auto expand on run? no, keep hidden to reduce noise -->
            <div class="mb-2">
                <span class="text-[9px] uppercase text-[var(--text-muted)]">Input:</span>
                <pre class="text-[10px] bg-[rgba(0,0,0,0.3)] p-1 rounded mt-1 overflow-x-auto custom-scrollbar">${argsText}</pre>
            </div>
            ${isDone ? `
            <div>
                 <span class="text-[9px] uppercase text-[var(--text-muted)]">Output:</span>
                 <div class="text-[10px] mt-1 overflow-x-auto custom-scrollbar">${outputHtml}</div>
            </div>` : ''}
        </div>
    `;

    // Re-bind toggle
    const header = toolDiv.querySelector('.tool-header-compact');
    const details = toolDiv.querySelector('.tool-body-details');
    const chevron = toolDiv.querySelector('.chevron');

    header.onclick = () => {
        const isHidden = details.classList.contains('hidden');
        if (isHidden) {
            details.classList.remove('hidden');
            chevron.style.transform = 'rotate(180deg)';
        } else {
            details.classList.add('hidden');
            chevron.style.transform = 'rotate(0deg)';
        }
    };

    if (!isUpdate) {
        container.appendChild(toolDiv);
    }
    return toolDiv;
}

// --- Artifact Card System ---
export function renderArtifactCards(card, text) {
    const container = card.querySelector('.agent-card-body');
    if (!container) return;

    // Remove existing cards to avoid duplicates on streaming updates
    container.querySelectorAll('.artifact-card-container').forEach(c => c.remove());

    // Regex to detect workspace paths: workspace/conversations/.../filename.ext
    const workspaceRegex = /workspace\/conversations\/[a-zA-Z0-9-]+\/artifacts\/[a-zA-Z0-9-_]+\/[^\s)]+\.[a-zA-Z0-9]+/g;
    const matches = [...new Set(text.match(workspaceRegex))];

    if (matches.length === 0) return;

    const cardsWrapper = document.createElement('div');
    cardsWrapper.className = 'artifact-cards-wrapper flex flex-wrap gap-3 mt-4 pt-4 border-t border-[var(--border)] opacity-0 fade-in-up';
    cardsWrapper.style.animationDelay = '0.2s';
    cardsWrapper.classList.add('artifact-card-container'); // Marker for cleanup

    matches.forEach(filePath => {
        const fileName = filePath.split('/').pop();
        const ext = fileName.split('.').pop().toLowerCase();

        let icon = 'description';
        let color = 'var(--text-muted)';

        if (['pdf'].includes(ext)) { icon = 'picture_as_pdf'; color = '#ff4d4d'; }
        else if (['png', 'jpg', 'jpeg', 'webp', 'svg'].includes(ext)) { icon = 'image'; color = '#4da6ff'; }
        else if (['csv', 'xlsx', 'xls'].includes(ext)) { icon = 'table_chart'; color = '#2ecc71'; }
        else if (['py', 'js', 'html', 'css', 'json', 'md'].includes(ext)) { icon = 'code'; color = 'var(--accent-purple)'; }

        const artifactCard = document.createElement('div');
        artifactCard.className = 'artifact-card group flex items-center gap-3 p-3 rounded-lg border border-[var(--border)] bg-[rgba(255,255,255,0.03)] hover:bg-[rgba(255,255,255,0.07)] hover:border-[var(--accent-cyan)] transition-all cursor-pointer max-w-[280px] overflow-hidden';
        artifactCard.title = `Download ${fileName}`;

        artifactCard.innerHTML = `
            <div class="artifact-icon flex-shrink-0 w-10 h-10 rounded bg-[rgba(0,0,0,0.3)] flex items-center justify-center border border-[var(--border)] group-hover:border-[var(--accent-cyan)]" style="color: ${color}">
                <span class="material-symbols-outlined text-[20px]">${icon}</span>
            </div>
            <div class="artifact-info flex-1 min-w-0">
                <div class="text-[11px] font-bold text-[var(--text-main)] truncate">${fileName}</div>
                <div class="text-[9px] text-[var(--text-muted)] uppercase tracking-wider">${ext} artifact</div>
            </div>
            <div class="artifact-action opacity-40 group-hover:opacity-100 transition-opacity">
                <span class="material-symbols-outlined text-[18px] text-[var(--accent-cyan)]">download</span>
            </div>
        `;

        artifactCard.onclick = () => {
            const link = document.createElement('a');
            link.href = `/${filePath}`; // Note: Backend serves /workspace/...
            link.download = fileName;
            link.target = '_blank';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        };

        cardsWrapper.appendChild(artifactCard);
    });

    container.appendChild(cardsWrapper);
    setTimeout(() => cardsWrapper.classList.remove('opacity-0'), 10);
}

// --- Reviewer Dashboard System ---
export function renderReviewDashboard(card, jsonText) {
    const container = card.querySelector('.agent-card-body');
    if (!container) return;

    // Try to extract JSON
    let data = null;
    try {
        const jsonMatch = jsonText.match(/\{[\s\S]*\}/);
        if (jsonMatch) data = JSON.parse(jsonMatch[0]);
    } catch (e) {
        console.warn("Could not parse reviewer JSON for dashboard", e);
        return;
    }

    if (!data || !data.status) return;

    // Hide the raw code block if it was already rendered
    const responseContent = container.querySelector('.response-content');
    if (responseContent) responseContent.style.display = 'none';

    // Remove existing dashboard to avoid duplicates
    container.querySelectorAll('.review-dashboard-wrapper').forEach(c => c.remove());

    const isApproved = data.status === 'APPROVED';
    const statusColor = isApproved ? 'var(--accent-cyan)' : 'var(--accent-orange)';
    const statusBg = isApproved ? 'rgba(77, 255, 255, 0.1)' : 'rgba(255, 166, 77, 0.1)';
    const score = data.quality_score || 0;

    const wrapper = document.createElement('div');
    wrapper.className = 'review-dashboard-wrapper mt-4 p-4 rounded-xl border border-[var(--border)] bg-[rgba(255,255,255,0.02)] fade-in-up';

    wrapper.innerHTML = `
        <div class="flex items-center justify-between mb-6">
            <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-full flex items-center justify-center" style="background: ${statusBg}; border: 1px solid ${statusColor}">
                    <span class="material-symbols-outlined" style="color: ${statusColor}">${isApproved ? 'verified' : 'warning'}</span>
                </div>
                <div>
                    <div class="text-[10px] text-[var(--text-muted)] uppercase tracking-widest font-bold">Dictamen Final</div>
                    <div class="text-[14px] font-bold" style="color: ${statusColor}">${data.status.replace(/_/g, ' ')}</div>
                </div>
            </div>
            <div class="text-right">
                <div class="text-[10px] text-[var(--text-muted)] uppercase tracking-widest font-bold mb-1">Quality Score</div>
                <div class="flex items-center gap-2">
                    <div class="w-24 h-2 bg-[#222] rounded-full overflow-hidden border border-[var(--border)]">
                        <div class="h-full transition-all duration-1000" style="width: ${score}%; background: linear-gradient(90deg, #ff4d4d, #ffcc00, #2ecc71)"></div>
                    </div>
                    <span class="text-[12px] font-mono font-bold text-[var(--text-main)]">${score}/100</span>
                </div>
            </div>
        </div>

        <div class="mb-6">
            <div class="text-[11px] text-[var(--text-main)] bg-[rgba(255,255,255,0.05)] p-3 rounded-lg italic border-l-2 border-[var(--accent-purple)]">
                "${data.summary || 'Sin resumen disponible.'}"
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="review-section">
                <div class="flex items-center gap-2 text-[10px] font-bold text-[var(--accent-orange)] uppercase tracking-wider mb-2">
                    <span class="material-symbols-outlined text-[14px]">error_outline</span> Hallazgos (Issues)
                </div>
                <ul class="space-y-1">
                    ${(data.issues || []).map(issue => `<li class="text-[10px] text-[var(--text-muted)] flex items-start gap-2"><span class="text-[var(--accent-orange)]">•</span> ${issue}</li>`).join('') || '<li class="text-[10px] text-[var(--text-muted)] italic">Ninguno detectado.</li>'}
                </ul>
            </div>
            <div class="review-section">
                <div class="flex items-center gap-2 text-[10px] font-bold text-[var(--accent-cyan)] uppercase tracking-wider mb-2">
                    <span class="material-symbols-outlined text-[14px]">lightbulb</span> Recomendaciones
                </div>
                <ul class="space-y-1">
                    ${(data.recommendations || []).map(rec => `<li class="text-[10px] text-[var(--text-muted)] flex items-start gap-2"><span class="text-[var(--accent-cyan)]">•</span> ${rec}</li>`).join('') || '<li class="text-[10px] text-[var(--text-muted)] italic">Proceso óptimo.</li>'}
                </ul>
            </div>
        </div>

        <div class="mt-4 pt-4 border-t border-[var(--border)] flex justify-between items-center">
             <div class="text-[9px] text-[var(--text-muted)]">Confianza: <span class="text-[var(--text-main)]">${data.confidence}</span></div>
             <button class="text-[9px] text-[var(--accent-purple)] hover:underline opacity-60 hover:opacity-100 transition-opacity" onclick="this.closest('.agent-card-body').querySelector('.response-content').style.display = 'block'; this.remove();">Ver JSON Crudo</button>
        </div>
    `;

    container.appendChild(wrapper);
}

// Helper to update current response content (streaming)
export function updateAgentResponse(card, markdownContent) {
    const responseDiv = card.querySelector('.response-content');
    if (!responseDiv) return;

    // <think> separation logic
    let finalContent = markdownContent;
    // Use global regex to catch all closed blocks
    const hasClosedThink = /<think>([\s\S]*?)<\/think>/.test(markdownContent);

    if (hasClosedThink) {
        // Find last unclosed or latest closed for rendering
        const allMatches = [...markdownContent.matchAll(/<think>([\s\S]*?)<\/think>/g)];
        if (allMatches.length > 0) {
            renderThinking(card, allMatches[allMatches.length - 1][1]);
        }
        // Remove all closed blocks from display
        finalContent = markdownContent.replace(/<think>[\s\S]*?<\/think>/g, '').trim();
    }

    // Check for an opening but unclosed think tag at the very end
    if (finalContent.includes('<think>')) {
        const parts = finalContent.split('<think>');
        if (parts.length > 1) {
            renderThinking(card, parts[parts.length - 1]);
        }
        finalContent = parts[0].trim();
    }

    // Render remaining content
    if (finalContent !== undefined) {
        responseDiv.dataset.markdownBuffer = finalContent;
        renderMarkdownImmediate(responseDiv, finalContent);
        // Detect and render artifact cards
        renderArtifactCards(card, markdownContent);

        // --- NEW: Detect Reviewer and render Dashboard ---
        const agentName = card.querySelector('.agent-name')?.textContent || '';
        if (agentName.toLowerCase().includes('reviewer')) {
            // Only attempt if it looks like JSON (contains status)
            if (markdownContent.includes('"status"') && markdownContent.includes('}')) {
                renderReviewDashboard(card, markdownContent);
            }
        }
    }
}

// Wrappers for compatibility/Usage
export function getOrCreateAgentBubble(group) {
    // This is called by main.js default logic. 
    // We redirect to create a default "Nexus" card
    const card = ensureAgentCard(group, "Nexus_Response");
    return card.querySelector('.response-content');
}


// --- Legacy/Compatibility helper exports ---

export function formatToolOutput(output) {
    if (output === null || output === undefined || (typeof output === 'string' && output.trim() === '')) {
        return `<span class="italic text-[var(--text-muted)]">Empty output</span>`;
    }
    try {
        const data = (typeof output === 'string') ? JSON.parse(output) : output;
        return `<pre class="whitespace-pre-wrap opacity-80">${JSON.stringify(data, null, 2)}</pre>`;
    } catch {
        return `<pre class="whitespace-pre-wrap opacity-80">${output}</pre>`;
    }
}

export function enhanceMarkdown(container) {
    if (!container || !window.hljs) return;
    container.querySelectorAll('pre code').forEach(block => {
        try { window.hljs.highlightElement(block); } catch { }
    });
}

export function ensureResponseSkeleton(contentArea) {
    // Optional
}

export function removeResponseSkeleton(contentArea) {
    // Optional
}

export function setStreamingIndicator(contentArea, active) {
    const card = contentArea.closest('.agent-card-container');
    if (!card) return;
    // We could add a spinner in the header
}

export function renderMarkdownImmediate(contentArea, markdownText) {
    if (!contentArea) return;
    contentArea.innerHTML = parseMarkdown(markdownText);
    enhanceMarkdown(contentArea);
    // Bind simple enhancements if needed
}

// Needed for scrolling logic in main.js
export function createExecutionCard() {
    return { html: '<div></div>', id: 'dummy' };
}

export function toggleCard(cardId) {
    // Legacy support
}

export function applyChatEnhancements(contentArea) {
    // simplified
}

// --- Sidebar & Layout Logic ---

export function initResizeHandle() {
    const handle = document.getElementById('drag-handle');
    const sidebar = document.getElementById('squad-sidebar');
    const main = document.querySelector('main'); // to prevent iframe interaction during drag?

    if (!handle || !sidebar) return;

    let isDragging = false;

    handle.addEventListener('mousedown', (e) => {
        isDragging = true;
        document.body.style.cursor = 'col-resize';
        // Disable iframe pointer events globally to avoid drag getting stuck
        document.body.style.userSelect = 'none';
        e.preventDefault();
    });

    document.addEventListener('mousemove', (e) => {
        if (!isDragging) return;

        // Calculate width from right edge
        const containerWidth = document.body.clientWidth;
        const newWidth = containerWidth - e.clientX;

        // Constraints
        if (newWidth >= 250 && newWidth <= containerWidth * 0.6) {
            sidebar.style.width = `${newWidth}px`;
            sidebar.style.flex = `0 0 ${newWidth}px`;
        }
    });

    document.addEventListener('mouseup', () => {
        if (isDragging) {
            isDragging = false;
            document.body.style.cursor = '';
            document.body.style.userSelect = '';
        }
    });
}

export function initSidebarTabs() {
    const tabSquads = document.getElementById('tab-squads');
    const tabActivity = document.getElementById('tab-activity');
    const panelSquads = document.getElementById('panel-squads');
    const panelActivity = document.getElementById('panel-activity');
    const clearBtn = document.getElementById('clear-logs-btn');

    if (!tabSquads || !tabActivity) return;

    function switchTab(target) {
        if (target === 'squads') {
            tabSquads.classList.add('text-[var(--accent-purple)]', 'border-b-2', 'border-[var(--accent-purple)]', 'bg-[#111]');
            tabSquads.classList.remove('text-[var(--text-muted)]', 'border-transparent');

            tabActivity.classList.remove('text-[var(--accent-orange)]', 'border-b-2', 'border-[var(--accent-orange)]', 'bg-[#111]');
            tabActivity.classList.add('text-[var(--text-muted)]', 'border-transparent');

            panelSquads.style.display = 'flex'; // Use style to override tailwind hidden class if needed or toggle classes
            panelSquads.classList.remove('hidden');
            panelActivity.classList.add('hidden');
            panelActivity.style.display = 'none';
        } else {
            tabActivity.classList.add('text-[var(--accent-orange)]', 'border-b-2', 'border-[var(--accent-orange)]', 'bg-[#111]');
            tabActivity.classList.remove('text-[var(--text-muted)]', 'border-transparent');

            tabSquads.classList.remove('text-[var(--accent-purple)]', 'border-b-2', 'border-[var(--accent-purple)]', 'bg-[#111]');
            tabSquads.classList.add('text-[var(--text-muted)]', 'border-transparent');

            panelActivity.style.display = 'flex';
            panelActivity.classList.remove('hidden');
            panelSquads.classList.add('hidden');
            panelSquads.style.display = 'none';
        }
    }

    tabSquads.onclick = () => switchTab('squads');
    tabActivity.onclick = () => switchTab('activity');

    if (clearBtn) {
        clearBtn.onclick = () => {
            const container = document.getElementById('activity-log-container');
            if (container) container.innerHTML = '<div class="text-[var(--text-muted)] italic opacity-50 p-2">Logs cleared.</div>';
        };
    }
}

export function renderToolLog(toolName, args, output) {
    const container = document.getElementById('activity-log-container');
    if (!container) return;

    // If first item is placeholder, remove it
    if (container.firstElementChild && container.firstElementChild.classList.contains('italic')) {
        container.innerHTML = '';
    }

    // Auto-switch to Activity Tab if a tool runs?
    // Maybe annoying if user checking squads using "Show All"
    // Let's notify via a small dot on the tab if needed (future polish)

    const isDone = output !== undefined && output !== null;
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });

    let argsText = '{}';
    try { argsText = typeof args === 'object' ? JSON.stringify(args) : String(args); } catch { }

    const entry = document.createElement('div');
    entry.className = "tool-log-entry border-l-[var(--accent-orange)]";
    if (isDone) entry.style.borderLeftColor = "var(--accent-cyan)";

    entry.innerHTML = `
        <div class="tool-log-header">
            <span class="tool-log-name text-[10px]">${toolName}</span>
            <span class="tool-log-time">${time}</span>
        </div>
        <div class="tool-log-args">${argsText}</div>
        ${isDone ? `<div class="tool-log-output">${formatToolOutput(output)}</div>` : '<div class="text-[8px] text-[var(--accent-orange)] animate-pulse">Running...</div>'}
    `;

    // Strategy for updates: 
    // If we receive "RUN" -> append
    // If we receive "DONE" -> find last "Running" of same tool? Or just append new log with full info?
    // appending new log is safer for linear history.
    // Ideally we update the existing "Running" entry if it exists.

    if (isDone) {
        // Find last running instance of this tool?
        // Simpler: Just append "Completed" entry or update logic in main.js to pass ID
        // For now, always append. It's a log.
    }

    container.appendChild(entry);
    container.scrollTop = container.scrollHeight;
}
