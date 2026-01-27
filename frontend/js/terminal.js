/**
 * Terminal Component for Real-Time Code Execution Output
 * Shows streaming output from Developer Agent code execution
 * 
 * Features:
 * - Real-time SSE streaming
 * - Copy to clipboard
 * - Download as file
 * - Execution history
 */

const Terminal = {
    activeTerminal: null,
    eventSource: null,
    history: [],
    currentExecution: null,

    /**
     * Create and show terminal window with SSE streaming support
     */
    create(title = "Code Execution Output", executionId = null) {
        // Remove existing terminal if any
        this.close();

        const terminal = document.createElement('div');
        terminal.className = 'code-terminal';
        terminal.innerHTML = `
            <div class="terminal-header">
                <div class="terminal-title">
                    <span class="material-symbols-outlined">terminal</span>
                    <span>${title}</span>
                </div>
                <div class="terminal-toolbar">
                    <button class="terminal-action-btn" onclick="Terminal.copyOutput()" title="Copy output">
                        <span class="material-symbols-outlined">content_copy</span>
                    </button>
                    <button class="terminal-action-btn" onclick="Terminal.downloadOutput()" title="Download as file">
                        <span class="material-symbols-outlined">download</span>
                    </button>
                    <button class="terminal-action-btn" onclick="Terminal.toggleHistory()" title="Show history">
                        <span class="material-symbols-outlined">history</span>
                    </button>
                </div>
                <div class="terminal-controls">
                    <button class="terminal-minimize" onclick="Terminal.minimize()">
                        <span class="material-symbols-outlined">remove</span>
                    </button>
                    <button class="terminal-close" onclick="Terminal.close()">
                        <span class="material-symbols-outlined">close</span>
                    </button>
                </div>
            </div>
            <div class="terminal-body">
                <div class="terminal-content"></div>
                <div class="terminal-history-panel">
                    <div class="history-header">Execution History</div>
                    <div class="history-list"></div>
                </div>
            </div>
            <div class="terminal-footer">
                <span class="terminal-status">
                    <span class="status-indicator"></span>
                    <span class="status-text">Ready</span>
                </span>
                <span class="terminal-time">0ms</span>
            </div>
        `;

        document.body.appendChild(terminal);
        this.activeTerminal = terminal;

        // Animate entrance
        setTimeout(() => terminal.classList.add('visible'), 10);

        // Connect to SSE stream if execution ID provided
        if (executionId) {
            this.connectToStream(executionId);
        }

        return terminal;
    },

    /**
     * Connect to SSE stream for real-time output
     */
    connectToStream(executionId) {
        if (this.eventSource) {
            this.eventSource.close();
        }

        this.setStatus('Connecting...', null, 'connecting');

        this.currentExecution = {
            id: executionId,
            startTime: Date.now(),
            output: []
        };

        const url = `/api/terminal/stream/${executionId}`;
        this.eventSource = new EventSource(url);

        this.eventSource.onopen = () => {
            console.log('[Terminal] SSE connection opened');
            this.setStatus('Executing...', null, 'running');
        };

        this.eventSource.onmessage = (e) => {
            try {
                const event = JSON.parse(e.data);
                this.handleStreamEvent(event);
            } catch (err) {
                console.error('[Terminal] Failed to parse SSE event:', err);
            }
        };

        this.eventSource.onerror = (err) => {
            console.error('[Terminal] SSE connection error:', err);
            this.eventSource.close();
            this.eventSource = null;

            if (this.activeTerminal) {
                this.setStatus('Connection lost', null, 'error');
            }
        };
    },

    /**
     * Handle incoming SSE event
     */
    handleStreamEvent(event) {
        const { type, line, elapsed, exit_code } = event;

        // Store in current execution
        if (this.currentExecution) {
            this.currentExecution.output.push({ type, line, elapsed });
        }

        switch (type) {
            case 'stdout':
                this.appendLine(line, 'stdout');
                this.setStatus('Running...', Math.round(elapsed * 1000), 'running');
                break;

            case 'stderr':
                this.appendLine(line, 'stderr');
                break;

            case 'complete':
                this.complete(exit_code, Math.round(elapsed * 1000));
                this.saveToHistory();
                if (this.eventSource) {
                    this.eventSource.close();
                    this.eventSource = null;
                }
                break;

            case 'error':
                this.error(line || 'Execution error');
                if (this.eventSource) {
                    this.eventSource.close();
                    this.eventSource = null;
                }
                break;
        }
    },

    /**
     * Append output line to terminal
     */
    appendLine(text, type = 'stdout') {
        if (!this.activeTerminal) return;

        const content = this.activeTerminal.querySelector('.terminal-content');
        const line = document.createElement('div');
        line.className = `terminal-line terminal-${type}`;

        // Escape HTML but preserve formatting
        line.textContent = text;

        content.appendChild(line);

        // Auto-scroll to bottom
        content.scrollTop = content.scrollHeight;
    },

    /**
     * Append command being executed
     */
    appendCommand(command, language = 'python') {
        this.appendLine(`$ ${language} ${command}`, 'command');
    },

    /**
     * Update terminal status
     */
    setStatus(statusText, time = null, statusType = 'ready') {
        if (!this.activeTerminal) return;

        const statusEl = this.activeTerminal.querySelector('.status-text');
        const timeEl = this.activeTerminal.querySelector('.terminal-time');
        const indicator = this.activeTerminal.querySelector('.status-indicator');

        statusEl.textContent = statusText;

        if (time !== null && time !== undefined) {
            timeEl.textContent = `${time}ms`;
        }

        // Update indicator
        indicator.className = 'status-indicator';
        indicator.classList.add(`status-${statusType}`);
    },

    /**
     * Show execution complete with exit code
     */
    complete(exitCode, duration) {
        if (!this.activeTerminal) return;

        const status = exitCode === 0 ? 'Completed ✓' : `Failed (exit ${exitCode})`;
        const statusType = exitCode === 0 ? 'success' : 'error';

        this.setStatus(status, duration, statusType);

        // Add completion line
        this.appendLine('', 'separator');
        this.appendLine(`Process exited with code ${exitCode}`, exitCode === 0 ? 'success' : 'error');
    },

    /**
     * Show error message
     */
    error(message) {
        this.appendLine(`ERROR: ${message}`, 'error');
        this.setStatus('Error ✗', null, 'error');
    },

    /**
     * Copy terminal output to clipboard
     */
    copyOutput() {
        if (!this.activeTerminal) return;

        const content = this.activeTerminal.querySelector('.terminal-content');
        const text = content.innerText;

        navigator.clipboard.writeText(text).then(() => {
            this.showToast('Output copied to clipboard');
        }).catch(err => {
            console.error('Failed to copy:', err);
            this.showToast('Failed to copy', 'error');
        });
    },

    /**
     * Download terminal output as file
     */
    downloadOutput() {
        if (!this.activeTerminal) return;

        const content = this.activeTerminal.querySelector('.terminal-content');
        const text = content.innerText;

        const blob = new Blob([text], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `execution_${Date.now()}.txt`;
        a.click();
        URL.revokeObjectURL(url);

        this.showToast('Output downloaded');
    },

    /**
     * Save current execution to history
     */
    saveToHistory() {
        if (!this.currentExecution) return;

        const content = this.activeTerminal?.querySelector('.terminal-content')?.innerText || '';

        this.history.unshift({
            id: this.currentExecution.id,
            timestamp: this.currentExecution.startTime,
            output: content,
            preview: content.split('\n')[0] || 'Empty output'
        });

        // Keep only last 10 executions
        if (this.history.length > 10) {
            this.history = this.history.slice(0, 10);
        }

        this.updateHistoryPanel();
        this.currentExecution = null;
    },

    /**
     * Toggle history panel
     */
    toggleHistory() {
        if (!this.activeTerminal) return;

        const panel = this.activeTerminal.querySelector('.terminal-history-panel');
        panel.classList.toggle('open');

        if (panel.classList.contains('open')) {
            this.updateHistoryPanel();
        }
    },

    /**
     * Update history panel content
     */
    updateHistoryPanel() {
        if (!this.activeTerminal) return;

        const listEl = this.activeTerminal.querySelector('.history-list');

        if (this.history.length === 0) {
            listEl.innerHTML = '<div class="history-empty">No execution history</div>';
            return;
        }

        listEl.innerHTML = this.history.map((item, index) => {
            const date = new Date(item.timestamp);
            const timeStr = date.toLocaleTimeString();
            return `
                <div class="history-item" onclick="Terminal.loadHistoryItem(${index})">
                    <div class="history-time">${timeStr}</div>
                    <div class="history-preview">${item.preview.substring(0, 50)}...</div>
                </div>
            `;
        }).join('');
    },

    /**
     * Load history item into terminal
     */
    loadHistoryItem(index) {
        const item = this.history[index];
        if (!item || !this.activeTerminal) return;

        const content = this.activeTerminal.querySelector('.terminal-content');
        content.textContent = item.output;

        this.toggleHistory(); // Close panel
        this.showToast('History loaded');
    },

    /**
     * Show toast notification
     */
    showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `terminal-toast toast-${type}`;
        toast.textContent = message;

        document.body.appendChild(toast);

        setTimeout(() => toast.classList.add('visible'), 10);
        setTimeout(() => {
            toast.classList.remove('visible');
            setTimeout(() => toast.remove(), 200);
        }, 2000);
    },

    /**
     * Clear terminal content
     */
    clear() {
        if (!this.activeTerminal) return;

        const content = this.activeTerminal.querySelector('.terminal-content');
        content.innerHTML = '';
        this.setStatus('Ready', 0, 'ready');
    },

    /**
     * Minimize terminal
     */
    minimize() {
        if (!this.activeTerminal) return;
        this.activeTerminal.classList.toggle('minimized');
    },

    /**
     * Close and remove terminal
     */
    close() {
        // Close SSE connection if active
        if (this.eventSource) {
            this.eventSource.close();
            this.eventSource = null;
        }

        if (!this.activeTerminal) return;

        this.activeTerminal.classList.remove('visible');
        setTimeout(() => {
            if (this.activeTerminal && this.activeTerminal.parentNode) {
                this.activeTerminal.parentNode.removeChild(this.activeTerminal);
            }
            this.activeTerminal = null;
        }, 200);
    },

    /**
     * Check if terminal is open
     */
    isOpen() {
        return this.activeTerminal !== null;
    }
};

// Make Terminal globally available
window.Terminal = Terminal;
