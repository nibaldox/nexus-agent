export function parseMarkdown(text) {
    if (!text) return '';
    // Use marked.js if available, otherwise fallback or raw
    if (typeof marked !== 'undefined') {
        const htmlContent = marked.parse(text);
        // Wrap in typography container
        // Note: Highlight.js needs to run AFTER insertion, so we might need a separate init or specific structure.
        // For simple bubble injection, we wrap it here.
        return `<div class="prose prose-invert max-w-none text-[13px] leading-relaxed break-words">${htmlContent}</div>`;
    }
    console.warn("Marked.js not found, using fallback");
    return text.replace(/\n/g, '<br>');
}

export function createOperatorBubble(text) {
    return `
    <div class="flex flex-col items-end space-y-2 fade-in mb-8">
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

export function createExecutionCard(icon, title, subtitle, status, statusColor) {
    const id = 'card-' + Date.now() + Math.random().toString(36).substr(2, 9);
    // Changed text-[var(--text-muted)] to text-[#CCCCCC] for better readability in card details
    const html = `
    <div id="${id}" class="group" data-card-id="${id}">
        <div class="execution-card rounded-lg px-5 py-3 flex items-center justify-between mb-2 cursor-pointer transition-colors hover:border-[${statusColor}] toggle-header">
            <div class="flex items-center gap-4">
                <span class="material-symbols-outlined text-[18px] text-[${statusColor}]">${icon}</span>
                <div class="flex items-center gap-2">
                    <span class="text-[11px] font-bold uppercase tracking-widest text-[var(--text-main)]">${title}</span>
                    <span class="text-[11px] text-[var(--text-muted)] mono">// ${subtitle}</span>
                </div>
            </div>
            <div class="flex items-center gap-3">
                <span class="status-text text-[10px] font-bold text-[${statusColor}] tracking-widest uppercase">${status}</span>
                <span class="material-symbols-outlined text-sm text-[var(--text-muted)] transition-transform duration-300 chevron">expand_more</span>
            </div>
        </div>
        <div class="card-details hidden pl-12 pr-5 pb-4 text-[13px] text-[#BBBBBB] mono border-l border-[var(--card-border)] ml-6 mb-4 leading-relaxed">
            <!-- Content injected here -->
        </div>
    </div>`;
    return { html, id };
}

// ... unchanged formatToolOutput ...

export function createSubAgentBubble(group, agentName) {
    // Consolidated sub-agent bubble creator (single source of truth)
    const safeName = agentName.replace(/\s+/g, '_');
    const id = 'subagent-' + Date.now() + Math.random().toString(36).substr(2, 9);

    // Try to find an existing bubble for this agent in the provided group
    let bubbleWrapper = group.querySelector(`.sub-agent-bubble[data-agent="${safeName}"]`);

    if (!bubbleWrapper) {
        bubbleWrapper = document.createElement('div');
        bubbleWrapper.setAttribute('data-agent', safeName);
        bubbleWrapper.id = id;
        bubbleWrapper.className = `sub-agent-bubble group mt-2 ml-8`;

        // Icon mapping
        let icon = 'smart_toy';
        if (agentName.includes('Researcher')) icon = 'travel_explore';
        if (agentName.includes('Analyst')) icon = 'query_stats';
        if (agentName.includes('Librarian')) icon = 'library_books';

        bubbleWrapper.innerHTML = `
            <div class="execution-card rounded-lg px-4 py-2 border-l-2 border-l-[var(--accent-purple)] bg-[rgba(255,255,255,0.02)] flex items-center justify-between cursor-pointer toggle-header transition-colors hover:bg-[rgba(255,255,255,0.05)]">
                <div class="flex items-center gap-3">
                    <span class="material-symbols-outlined text-[16px] text-[var(--accent-purple)]">${icon}</span>
                    <div class="flex items-center gap-2">
                        <span class="text-[10px] font-bold uppercase tracking-widest text-[var(--accent-purple)]">${agentName}</span>
                    </div>
                </div>
                <span class="material-symbols-outlined text-sm text-[var(--text-muted)] transition-transform duration-300 chevron">expand_more</span>
            </div>
            <div class="card-details pl-4 pr-2 py-3 text-[12px] text-[var(--text-muted)] mono leading-relaxed border-l-2 border-l-[rgba(217,70,239,0.3)] ml-[18px] mt-1 relative">
                <div class="content-area"></div>
            </div>
        `;

        group.appendChild(bubbleWrapper);
    }

    // Ensure the card is visible when new content arrives
    const details = bubbleWrapper.querySelector('.card-details');
    if (details && details.classList.contains('hidden')) {
        details.classList.remove('hidden');
        const chevron = bubbleWrapper.querySelector('.chevron');
        if (chevron) chevron.style.transform = 'rotate(180deg)';
    }

    return bubbleWrapper.querySelector('.content-area');
} 

export function formatToolOutput(output) {
    // Friendly handling for empty output or empty result sets
    if (output === null || output === undefined || (typeof output === 'string' && output.trim() === '')) {
        return `<div class="mt-2 italic text-[12px] text-[var(--text-muted)]">No output.</div>`;
    }

    try {
        // Try parsing JSON
        const data = (typeof output === 'string') ? JSON.parse(output) : output;

        // If an empty array, return friendly message
        if (Array.isArray(data) && data.length === 0) {
            return `<div class="mt-2 italic text-[12px] text-yellow-300">No results found for this search.</div>`;
        }

        // Check for DuckDuckGo style results (list of objects with title, href, body)
        if (Array.isArray(data) && data.length > 0 && data[0].title && data[0].href) {
            return `
            <div class="flex flex-col gap-3 mt-2">
                ${data.map(item => `
                <div class="bg-[rgba(255,255,255,0.03)] p-3 rounded border border-[var(--border)] hover:border-[var(--accent-cyan)] transition-colors">
                    <a href="${item.href}" target="_blank" class="text-[11px] font-bold text-[var(--accent-cyan)] hover:underline block mb-1 truncate">${item.title}</a>
                    <p class="text-[10px] text-[var(--text-muted)] line-clamp-2 leading-relaxed">${item.body || item.snippet || ''}</p>
                </div>
                `).join('')}
            </div>`;
        }

        // Default Pretty JSON
        return `<pre class="whitespace-pre-wrap mt-1 opacity-80">${JSON.stringify(data, null, 2)}</pre>`;
    } catch (e) {
        // Raw String
        return `<pre class="whitespace-pre-wrap mt-1 opacity-80">${output}</pre>`;
    }
}

export function toggleCard(cardId) {
    const container = document.getElementById(cardId);
    if (!container) return;

    const details = container.querySelector('.card-details');
    const chevron = container.querySelector('.chevron');

    if (details.classList.contains('hidden')) {
        details.classList.remove('hidden');
        chevron.style.transform = 'rotate(180deg)';
    } else {
        details.classList.add('hidden');
        chevron.style.transform = 'rotate(0deg)';
    }
}

export function ensureAgentGroup(container) {
    const group = document.createElement('div');
    group.className = "space-y-2 fade-in mb-8 agent-turn-group";
    group.innerHTML = `
    <div class="flex items-center gap-3 text-[var(--text-muted)] mb-4">
        <span class="text-[11px] mono tracking-[0.2em] uppercase font-bold text-[var(--accent-cyan)] glow-cyan">Agent_Zero</span>
    </div>
    `;
    container.appendChild(group);
    return group;
}

export function getOrCreateAgentBubble(group) {
    let bubble = group.querySelector('.agent-response-bubble .content-area');
    if (bubble) return bubble;

    const bubbleWrapper = document.createElement('div');
    bubbleWrapper.className = "execution-card rounded-lg px-5 py-3 border-l-2 border-l-[var(--accent-cyan)] mt-4 agent-response-bubble";
    bubbleWrapper.innerHTML = `
        <div class="flex items-center gap-4 mb-2">
        <span class="material-symbols-outlined text-[18px] text-[var(--accent-cyan)]">smart_toy</span>
        <div class="flex items-center gap-2">
            <span class="text-[11px] font-bold uppercase tracking-widest">Nexus_Response</span>
            <span class="text-[9px] mono text-[var(--text-muted)] opacity-50 ml-2">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
        </div>
    </div>
    <div class="content-area text-[13px] text-[var(--text-main)] mono leading-relaxed"></div>
    `;

    group.appendChild(bubbleWrapper);
    return bubbleWrapper.querySelector('.content-area');
}


