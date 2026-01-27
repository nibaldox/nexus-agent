/**
 * squad-status.js
 * Handles real-time visualization of agent squad activities.
 */

import { FRONTEND_CONFIG } from './config.js';

class SquadStatusManager {
    constructor() {
        this.container = document.getElementById('squad-status-container');
        this.pollingInterval = FRONTEND_CONFIG.squads.pollMinMs;
        this.maxPollingInterval = FRONTEND_CONFIG.squads.pollMaxMs;
        this.backoffFactor = FRONTEND_CONFIG.squads.backoffFactor;
        this.pollTimer = null;
        this.lastData = null;
        this.lastToolKey = '';
        this.toolMap = {};
        this.staleSeconds = 90;
        this.staleSeconds = 90;
        this.blockedSeconds = 180;
        this.history = {}; // { squadName: [val1, val2, ...] }
        this.maxHistory = 20;
        this.expandedTasks = new Set();
        this.expandedKey = 'nexus_task_expanded';
        this.showAllSquads = true;

        // Graph View State
        this.viewMode = 'list'; // 'list' | 'graph'
        this.network = null;
        this.networkNodes = null;
        this.networkEdges = null;
        this.discoveredNodes = new Set(['nexus_core']); // The "Brain" starts discovered

        this.init();
    }

    init() {
        if (!this.container) return;
        console.log('🛡️ Squad Status Manager initialized');
        this.loadShowAllSquads();
        this.bindShowAllToggle();
        this.loadExpandedState();
        this.bindVisibility();
        this.bindViewToggles(); // New
        this.startPolling();
    }

    bindVisibility() {
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                if (this.pollTimer) {
                    clearTimeout(this.pollTimer);
                    this.pollTimer = null;
                }
            } else {
                this.scheduleNextPoll(100);
            }
        });
    }

    startPolling() {
        this.fetchStatus();
    }

    scheduleNextPoll(delayMs) {
        if (this.pollTimer) clearTimeout(this.pollTimer);
        this.pollTimer = setTimeout(() => this.fetchStatus(), delayMs);
    }

    bindViewToggles() {
        const listBtn = document.getElementById('view-list-btn');
        const graphBtn = document.getElementById('view-graph-btn');

        if (!listBtn || !graphBtn) return;

        listBtn.onclick = () => this.switchView('list');
        graphBtn.onclick = () => this.switchView('graph');
    }

    switchView(mode) {
        if (this.viewMode === mode) return;
        this.viewMode = mode;

        const listBtn = document.getElementById('view-list-btn');
        const graphBtn = document.getElementById('view-graph-btn');
        const listContainer = document.getElementById('squad-status-container');
        const graphContainer = document.getElementById('squad-network-container');

        // Update Buttons
        const activeClass = ['text-[var(--text-main)]', 'bg-[var(--surface)]', 'shadow-sm'];
        const inactiveClass = ['text-[var(--text-muted)]', 'hover:text-[var(--text-main)]'];

        if (mode === 'list') {
            listBtn.className = `px-2 py-1 text-[8px] uppercase font-bold text-[var(--text-main)] bg-[var(--surface)] rounded shadow-sm transition-all`;
            graphBtn.className = `px-2 py-1 text-[8px] uppercase font-bold text-[var(--text-muted)] hover:text-[var(--text-main)] transition-colors`;

            listContainer.classList.remove('hidden');
            graphContainer.classList.add('hidden');
        } else {
            graphBtn.className = `px-2 py-1 text-[8px] uppercase font-bold text-[var(--text-main)] bg-[var(--surface)] rounded shadow-sm transition-all`;
            listBtn.className = `px-2 py-1 text-[8px] uppercase font-bold text-[var(--text-muted)] hover:text-[var(--text-main)] transition-colors`;

            listContainer.classList.add('hidden');
            graphContainer.classList.remove('hidden');

            // Trigger graph render if we have data
            if (this.lastData) {
                this.renderGraph(this.lastData);
            }
        }
    }

    async fetchStatus() {
        try {
            const sessionId = localStorage.getItem('nexus_session_id') || 'default';
            const response = await fetch('/api/squads/status');
            if (!response.ok) throw new Error('Failed to fetch squad status');

            const data = await response.json();
            const toolMap = await this.fetchToolMap(sessionId);

            // Updated change detection to include viewMode specific updates
            const toolKey = JSON.stringify(toolMap);
            if (JSON.stringify(data) !== JSON.stringify(this.lastData) || toolKey !== this.lastToolKey || this.viewMode === 'graph') {
                if (this.viewMode === 'list') {
                    this.renderStatus(data, toolMap, sessionId);
                } else {
                    this.renderGraph(data);
                }
                this.lastData = data;
                this.lastToolKey = toolKey;
            }
            this.pollingInterval = FRONTEND_CONFIG.squads.pollMinMs;
        } catch (error) {
            console.error('❌ Squad Status Error:', error);
            const nextInterval = Math.min(
                this.maxPollingInterval,
                Math.ceil(this.pollingInterval * this.backoffFactor)
            );
            this.pollingInterval = nextInterval;
        } finally {
            if (!document.hidden) {
                this.scheduleNextPoll(this.pollingInterval);
            }
        }
    }

    // ... (fetchToolMap, buildToolMap, renderStatus methods...)

    renderGraph(data) {
        const container = document.getElementById('squad-network-container');
        if (!container) return;

        // Safety check for vis
        if (typeof vis === 'undefined') {
            console.error('❌ Vis.js library not loaded.');
            container.innerHTML = `
                <div class="flex flex-col items-center justify-center h-full text-[var(--text-muted)] space-y-2">
                    <span class="material-symbols-outlined text-2xl text-[var(--accent-orange)]">warning</span>
                    <span class="text-[10px] text-center">Librería de gráficos no disponible.<br>Verifique su conexión a internet.</span>
                </div>
            `;
            return;
        }

        console.log("Rendering graph with data:", data);

        // Prepare data
        const nodes = [];
        const edges = [];

        // Central Node
        nodes.push({
            id: 'nexus_core',
            label: 'NEXUS',
            color: '#00E0FF',
            font: { color: '#000', size: 10, face: 'IBM Plex Mono' },
            shape: 'hexagon',
            size: 20,
            shadow: { color: 'rgba(0,224,255,0.6)', size: 10 }
        });

        // Iterate Squads
        if (data && data.squads) {
            Object.entries(data.squads).forEach(([squadName, members], i) => {
                const squadId = `squad_${squadName}`;

                // Check if members is purely agents map or Mission object
                const agentList = members.assignments ? [] : Object.entries(members);

                agentList.forEach(([agentName, info]) => {
                    const agentId = `agent_${agentName}`;
                    const isActive = (info.activity || '').toLowerCase() !== 'idle';

                    // IF active, discover BOTH the agent and its squad hub
                    if (isActive) {
                        this.discoveredNodes.add(squadId);
                        this.discoveredNodes.add(agentId);
                    }

                    // Only push if discovered
                    if (this.discoveredNodes.has(agentId)) {
                        nodes.push({
                            id: agentId,
                            label: agentName,
                            color: isActive ? '#00E0FF' : '#333',
                            font: { color: isActive ? '#fff' : '#666', size: 7, face: 'IBM Plex Mono' },
                            shape: 'dot',
                            size: 6,
                            title: `${agentName}\n${info.activity || 'Idle'}`
                        });

                        edges.push({
                            from: squadId,
                            to: agentId,
                            color: { color: isActive ? '#00E0FF' : '#333', opacity: isActive ? 0.8 : 0.2 },
                            dashes: !isActive
                        });
                    }
                });

                // Only push the Squad Hub if discovered
                if (this.discoveredNodes.has(squadId)) {
                    nodes.push({
                        id: squadId,
                        label: squadName,
                        color: '#9D00FF',
                        font: { color: '#fff', size: 8, face: 'IBM Plex Mono', background: '#000' },
                        shape: 'dot',
                        size: 10
                    });

                    // Edge Nexus -> Squad
                    edges.push({ from: 'nexus_core', to: squadId, color: { color: '#9D00FF', opacity: 0.4 } });
                }
            });
        }

        // --- NEW: Deduplicate nodes and edges ---
        const uniqueNodesMap = new Map();
        nodes.forEach(n => uniqueNodesMap.set(n.id, n));
        const finalNodes = Array.from(uniqueNodesMap.values());

        const uniqueEdgesMap = new Map();
        edges.forEach(e => {
            const edgeKey = `${e.from}_${e.to}`;
            uniqueEdgesMap.set(edgeKey, e);
        });
        const finalEdges = Array.from(uniqueEdgesMap.values());

        try {
            // Initialize or Update Vis Network
            if (!this.network) {
                this.networkNodes = new vis.DataSet(finalNodes);
                this.networkEdges = new vis.DataSet(finalEdges);

                const options = {
                    nodes: { borderWidth: 0 },
                    edges: { width: 1, smooth: { type: 'continuous' } },
                    physics: {
                        stabilization: false,
                        barnesHut: {
                            gravitationalConstant: -2000,
                            springConstant: 0.04,
                            springLength: 60
                        }
                    },
                    interaction: { hover: true, tooltipDelay: 200 }
                };

                this.network = new vis.Network(container, { nodes: this.networkNodes, edges: this.networkEdges }, options);
                console.log("Graph network initialized.");
            } else {
                this.networkNodes.update(finalNodes);
                this.networkEdges.clear();
                this.networkEdges.add(finalEdges);
                this.network.fit({ animation: true }); // Prevent lost view
                console.log("Graph network updated.");
            }
        } catch (err) {
            console.error("Error rendering network:", err);
            container.innerHTML = `<div class="p-4 text-[var(--accent-orange)] text-[10px]">Error renderizando grafo: ${err.message}</div>`;
        }
    }

    async fetchToolMap(sessionId) {
        if (!sessionId) return {};
        try {
            const response = await fetch(`/api/logs/tools?session_id=${encodeURIComponent(sessionId)}&tail=300`);
            if (!response.ok) return {};
            const payload = await response.json();
            return this.buildToolMap(payload.events || []);
        } catch (error) {
            return {};
        }
    }

    buildToolMap(events) {
        const map = {};
        events.forEach((event) => {
            const taskId = event.task_id || 'default';
            const toolObj = event.tool || {};
            const toolName = typeof toolObj === 'string'
                ? toolObj
                : toolObj.tool_name || toolObj.name || 'tool';
            const agentName = event.agent_name
                || (event.data && (event.data.agent_name || event.data.team_name))
                || 'Unknown';
            if (!map[taskId]) map[taskId] = {};
            if (!map[taskId][agentName]) map[taskId][agentName] = {};
            const entry = map[taskId][agentName][toolName] || { count: 0, lastArgs: null, lastResult: null };
            entry.count += 1;
            if (toolObj && toolObj.tool_args) {
                entry.lastArgs = toolObj.tool_args;
            }
            if (toolObj && toolObj.result) {
                entry.lastResult = toolObj.result;
            }
            map[taskId][agentName][toolName] = entry;
        });
        return map;
    }

    renderStatus(data, toolMap, sessionId) {
        const tasks = Array.isArray(data.tasks) ? data.tasks : [];
        const filteredTasks = tasks
            .filter(task => !sessionId || task.session_id === sessionId)
            .filter(task => task.agents && Object.keys(task.agents).length > 0);

        if (filteredTasks.length > 0) {
            const sorted = filteredTasks
                .slice()
                .sort((a, b) => (b.updated_at || b.created_at || 0) - (a.updated_at || a.created_at || 0));
            this.container.innerHTML = sorted.map((task) => this.createTaskCard(task, toolMap)).join('');
            this.bindTaskToggles();
            return;
        }

        if (!data.squads || Object.keys(data.squads).length === 0) {
            this.container.innerHTML = `
                <div class="text-[10px] text-[var(--text-muted)] italic mono p-4 border border-dashed border-[var(--border)] rounded">
                    Esperando misiones de escuadrón...
                </div>
            `;
            return;
        }

        let html = '';

        for (const [squadName, members] of Object.entries(data.squads)) {
            // Check if it's a mission plan or individual member status
            if (members.assignments) {
                // For missions, calculate "activity" as active assignments
                const activeCount = members.assignments.filter(a => a.status === 'IN_PROGRESS').length;
                this.updateHistory(squadName, activeCount * 10); // Wrapper multiplier for visibility
                html += this.createMissionCard(squadName, members);
            } else {
                // For regular squads, calculate "activity" as sum of progress or active agents
                const memberList = Object.values(members);
                const activeAgents = memberList.filter(m => (m.activity || '').toLowerCase() !== 'idle').length;
                const totalProgress = memberList.reduce((acc, m) => acc + (m.progress || 0), 0);
                const activityMetric = activeAgents * 20 + (totalProgress / (memberList.length || 1));

                this.updateHistory(squadName, activityMetric);
                const sparkline = this.generateSparkline(squadName);

                html += `
                    <div class="mb-6">
                        <div class="flex items-center justify-between mb-3 border-b border-[var(--border)] pb-1">
                            <h3 class="text-[9px] uppercase tracking-wider text-[var(--text-muted)]">
                                ${squadName} Squad
                            </h3>
                            ${sparkline}
                        </div>
                        <div class="space-y-3">
                            ${Object.entries(members).map(([name, info]) => this.createMemberCard(name, info)).join('')}
                        </div>
                    </div>
                `;
            }
        }

        this.container.innerHTML = html;
        this.bindTaskToggles();
    }

    bindTaskToggles() {
        const headers = this.container.querySelectorAll('[data-task-toggle="true"]');
        headers.forEach(header => {
            header.onclick = () => {
                const taskId = header.getAttribute('data-task-id');
                if (!taskId) return;
                if (this.expandedTasks.has(taskId)) {
                    this.expandedTasks.delete(taskId);
                } else {
                    this.expandedTasks.add(taskId);
                }
                this.saveExpandedState();
                const taskBody = this.container.querySelector(`[data-task-body="${taskId}"]`);
                const chevron = header.querySelector('[data-task-chevron="true"]');
                if (taskBody) {
                    taskBody.classList.toggle('hidden');
                }
                if (chevron) {
                    chevron.style.transform = taskBody && !taskBody.classList.contains('hidden') ? 'rotate(180deg)' : 'rotate(0deg)';
                }
            };
        });
    }

    bindShowAllToggle() {
        const toggle = document.getElementById('squad-show-all');
        if (!toggle) return;
        toggle.checked = this.showAllSquads;
        toggle.onchange = () => {
            this.showAllSquads = toggle.checked;
            this.saveShowAllSquads();
            this.fetchStatus();
        };
    }

    loadShowAllSquads() {
        try {
            const raw = localStorage.getItem(this.showAllSquadsKey);
            if (raw === null) {
                this.showAllSquads = true;
                return;
            }
            this.showAllSquads = raw === 'true';
        } catch {
            this.showAllSquads = true;
        }
    }

    saveShowAllSquads() {
        try {
            localStorage.setItem(this.showAllSquadsKey, String(this.showAllSquads));
        } catch {
            // ignore
        }
    }

    loadExpandedState() {
        try {
            const raw = localStorage.getItem(this.expandedKey);
            if (!raw) return;
            const list = JSON.parse(raw);
            if (Array.isArray(list)) {
                this.expandedTasks = new Set(list);
            }
        } catch {
            this.expandedTasks = new Set();
        }
    }

    saveExpandedState() {
        try {
            localStorage.setItem(this.expandedKey, JSON.stringify(Array.from(this.expandedTasks)));
        } catch {
            // ignore
        }
    }

    formatAgo(timestampSeconds) {
        if (!timestampSeconds) return '';
        const delta = Math.max(0, Math.floor(Date.now() / 1000) - timestampSeconds);
        if (delta < 60) return `hace ${delta}s`;
        if (delta < 3600) return `hace ${Math.floor(delta / 60)}m`;
        return `hace ${Math.floor(delta / 3600)}h`;
    }

    // Sparkline Helpers
    updateHistory(squadName, activityLevel) {
        if (!this.history[squadName]) this.history[squadName] = new Array(this.maxHistory).fill(0);
        this.history[squadName].push(activityLevel);
        if (this.history[squadName].length > this.maxHistory) {
            this.history[squadName].shift();
        }
    }

    generateSparkline(squadName) {
        const data = this.history[squadName] || [];
        if (data.length < 2) return '';

        const width = 60;
        const height = 20;
        const maxVal = Math.max(...data, 10); // Scale to max or at least 10
        const minVal = 0;
        const range = maxVal - minVal;

        const points = data.map((val, i) => {
            const x = (i / (this.maxHistory - 1)) * width;
            const y = height - ((val - minVal) / range) * height;
            return `${x},${y}`;
        }).join(' ');

        return `
            <svg width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" class="sparkline">
                <polyline points="${points}" fill="none" stroke="var(--accent-cyan)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" opacity="0.8" />
            </svg>
        `;
    }

    normalizeStatus(status) {
        const value = (status || '').toUpperCase();
        if (value.includes('DONE') || value.includes('COMPLETE')) return 'DONE';
        if (value.includes('BLOCK')) return 'BLOCKED';
        if (value.includes('QUEUE') || value.includes('PEND')) return 'QUEUED';
        if (value.includes('REVIEW')) return 'IN_REVIEW';
        if (value.includes('RUN') || value.includes('PROGRESS')) return 'IN_PROGRESS';
        return value || 'IN_PROGRESS';
    }

    statusClass(status) {
        switch (status) {
            case 'DONE':
                return 'status-done';
            case 'BLOCKED':
                return 'status-blocked';
            case 'QUEUED':
                return 'status-queued';
            case 'IN_REVIEW':
                return 'status-review';
            default:
                return 'status-running';
        }
    }

    computeTaskProgress(agents) {
        const entries = Object.entries(agents || {});
        if (entries.length === 0) return { progress: 0, activeCount: 0, total: 0 };
        const total = entries.length;
        let sum = 0;
        let activeCount = 0;
        entries.forEach(([, info]) => {
            const progress = Number(info.progress || 0);
            sum += progress;
            if ((info.activity || '').toLowerCase() !== 'idle' && progress > 0) {
                activeCount += 1;
            }
        });
        return { progress: Math.round(sum / total), activeCount, total };
    }

    createMissionCard(name, mission) {
        return `
            <div class="p-3 border border-[var(--accent-purple)]/30 bg-[var(--surface)] rounded-lg mb-4">
                <div class="flex items-center justify-between mb-2">
                    <span class="text-[10px] font-bold text-[var(--accent-purple)] uppercase tracking-tighter">Mission: ${name}</span>
                    <span class="text-[8px] px-1.5 py-0.5 bg-[var(--accent-purple)]/20 text-[var(--accent-purple)] rounded-full">${mission.status}</span>
                </div>
                <div class="text-[9px] text-[var(--text-muted)] mb-2 mono">
                    Assignments: ${mission.assignments.length}
                </div>
                <div class="w-full bg-black/40 h-1 rounded-full overflow-hidden">
                    <div class="h-full bg-[var(--accent-purple)]" style="width: ${mission.status === 'COMPLETED' ? '100%' : '50%'}"></div>
                </div>
            </div>
        `;
    }

    createTaskCard(task, toolMap) {
        const status = this.normalizeStatus(task.status || 'RUNNING');
        const agents = task.agents || {};
        const agentEntries = Object.entries(agents).sort((a, b) => {
            const progressDiff = (b[1].progress || 0) - (a[1].progress || 0);
            if (progressDiff !== 0) return progressDiff;
            return (b[1].last_update || 0) - (a[1].last_update || 0);
        });
        const createdAt = task.created_at ? new Date(task.created_at * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '';
        const updatedAt = task.updated_at ? this.formatAgo(task.updated_at) : '';
        const taskId = task.id || task.task_id || task.title || String(task.created_at || Math.random());
        const isExpanded = this.expandedTasks.has(taskId);
        const { progress, activeCount, total } = this.computeTaskProgress(agents);
        const taskTools = (toolMap && toolMap[taskId]) ? toolMap[taskId] : {};
        const squads = this.groupAgentsBySquad(agentEntries);
        const activeSquad = this.getActiveSquad(agentEntries);
        const squadsToRender = this.showAllSquads
            ? squads
            : (activeSquad && squads[activeSquad]
                ? { [activeSquad]: squads[activeSquad] }
                : squads);
        const hiddenSquadsCount = Math.max(0, Object.keys(squads).length - Object.keys(squadsToRender).length);

        return `
            <div class="p-4 border border-[var(--accent-purple)]/20 bg-[var(--surface)] rounded-lg mb-4">
                <div class="flex items-center justify-between mb-2 cursor-pointer" data-task-toggle="true" data-task-id="${taskId}">
                    <div class="flex flex-col">
                        <span class="text-[11px] font-bold text-[var(--accent-purple)] uppercase tracking-tighter">
                            ${task.title || 'Tarea'}
                        </span>
                        <span class="text-[9px] text-[var(--text-muted)] mono">
                            ${createdAt ? `Inicio ${createdAt}` : ''} ${updatedAt ? `• ${updatedAt}` : ''}
                        </span>
                    </div>
                    <div class="flex items-center gap-2">
                        <span class="text-[9px] px-1.5 py-0.5 rounded-full ${this.statusClass(status)}">${status}</span>
                        <span class="material-symbols-outlined text-[14px] text-[var(--text-muted)] transition-transform duration-300" data-task-chevron="true">expand_more</span>
                    </div>
                </div>
                <div class="flex items-center gap-2 mb-3">
                    <div class="flex-grow bg-black/40 h-1.5 rounded-full overflow-hidden">
                        <div class="h-full bg-[var(--accent-cyan)]" style="width: ${progress}%"></div>
                    </div>
                    <span class="text-[9px] font-bold text-[var(--accent-cyan)]">${progress}%</span>
                    <span class="text-[9px] text-[var(--text-muted)] mono">${activeCount}/${total} activos</span>
                </div>
                <div class="space-y-4 ${isExpanded ? '' : 'hidden'}" data-task-body="${taskId}">
                    ${(!this.showAllSquads && hiddenSquadsCount > 0) ? `
                        <div class="text-[9px] text-[var(--text-muted)] mono">
                            ${hiddenSquadsCount} squads ocultos. Activa “Mostrar todos los squads”.
                        </div>
                    ` : ''}
                    ${Object.entries(squadsToRender).map(([squadName, squadAgents]) => `
                        <div class="squad-card ${activeSquad === squadName ? 'squad-card-active' : ''}">
                            <div class="squad-card-header mb-3">
                                <span class="squad-title text-[11px] font-bold">${squadName}</span>
                                <span class="squad-meta text-[9px]">${squadAgents.length} agentes</span>
                            </div>
                            <div class="space-y-3">
                                ${squadAgents.map(([name, info]) => this.createMemberCard(name, info, taskTools[name] || {})).join('')}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    groupAgentsBySquad(agentEntries) {
        const groups = {};
        agentEntries.forEach(([name, info]) => {
            const squadName = info.squad || 'Sin squad';
            if (!groups[squadName]) groups[squadName] = [];
            groups[squadName].push([name, info]);
        });
        return groups;
    }

    getActiveSquad(agentEntries) {
        if (agentEntries.length === 0) return null;
        let latest = null;
        agentEntries.forEach(([, info]) => {
            const updated = info.last_update || 0;
            if (!latest || updated > latest.updated) {
                latest = { updated, squad: info.squad || 'Sin squad' };
            }
        });
        return latest ? latest.squad : null;
    }

    createMemberCard(name, info, tools) {
        // Calculate transparency based on last update (stale check)
        const lastUpdateSeconds = info.last_update || 0;
        const secondsSinceUpdate = (Date.now() / 1000) - lastUpdateSeconds;
        const isStale = secondsSinceUpdate > this.staleSeconds;
        const isBlocked = secondsSinceUpdate > this.blockedSeconds && (info.progress || 0) < 100;
        const opacity = isStale ? 'opacity-40' : 'opacity-100';
        const status = isBlocked ? 'BLOCKED' : (info.activity || '').toLowerCase() === 'idle' ? 'QUEUED' : 'IN_PROGRESS';
        const statusClass = this.statusClass(status);
        const ago = this.formatAgo(lastUpdateSeconds);

        const toolEntries = tools && typeof tools === 'object' ? Object.entries(tools) : [];
        const toolList = toolEntries.length > 0
            ? `<div class="tool-list">${toolEntries.map(([tool, meta]) => {
                const count = meta && typeof meta === 'object' ? meta.count || 0 : meta;
                const tooltip = this.buildToolTooltip(tool, meta);
                return `<span class="tool-chip tool-chip-rich" data-tooltip="${tooltip}">${tool}${count > 1 ? ` x${count}` : ''}</span>`;
            }).join('')}</div>`
            : `<div class="tool-list-empty">Sin herramientas registradas</div>`;

        return `
            <div class="p-3.5 border border-[var(--card-border)] bg-[var(--surface)] shadow-md rounded-lg hover:border-[var(--accent-cyan)]/50 transition-all ${opacity}">
                <div class="flex items-center justify-between mb-2">
                    <span class="text-[11px] font-semibold text-[var(--text-main)]">${name}</span>
                    <div class="flex items-center gap-2">
                        ${ago ? `<span class="text-[9px] text-[var(--text-muted)] mono">${ago}</span>` : ''}
                        <span class="text-[9px] px-1.5 py-0.5 rounded-full ${statusClass}">${status}</span>
                        ${!isStale ? '<span class="w-1.5 h-1.5 rounded-full bg-[var(--accent-cyan)] shadow-[0_0_5px_var(--accent-cyan)] animate-pulse"></span>' : ''}
                    </div>
                </div>
                <div class="text-[10px] text-[var(--text-muted)] leading-tight mb-2 mono">
                    ${info.activity || 'Idle'}
                </div>
                <div class="flex items-center gap-2">
                    <div class="flex-grow bg-black/40 h-1.5 rounded-full overflow-hidden">
                        <div class="h-full bg-[var(--accent-cyan)]" style="width: ${info.progress || 0}%"></div>
                    </div>
                    <span class="text-[9px] font-bold text-[var(--accent-cyan)]">${info.progress || 0}%</span>
                </div>
                <div class="tool-list-wrapper">
                    ${toolList}
                </div>
            </div>
        `;
    }

    buildToolTooltip(tool, meta) {
        if (!meta || typeof meta !== 'object') {
            return this.escapeAttr(`${tool}`);
        }
        const args = meta.lastArgs ? this.truncateText(JSON.stringify(meta.lastArgs, null, 2), 220) : '—';
        const result = meta.lastResult ? this.truncateText(String(meta.lastResult), 220) : '—';
        const count = meta.count || 0;
        const text = `Tool: ${tool}\nUsos: ${count}\nArgs: ${args}\nResult: ${result}`;
        return this.escapeAttr(text);
    }

    truncateText(text, maxLen) {
        if (!text) return '';
        if (text.length <= maxLen) return text;
        return `${text.slice(0, maxLen)}…`;
    }

    escapeAttr(text) {
        return String(text)
            .replace(/&/g, '&amp;')
            .replace(/"/g, '&quot;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/'/g, '&#39;');
    }
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    new SquadStatusManager();
});
