/**
 * Progress Tracker Component for Nexus Workflow
 * Shows real-time progress of task execution
 */

const ProgressTracker = {
    currentProgress: null,

    /**
     * Create and show progress tracker
     * @param {number} totalTasks - Total number of tasks
     * @param {string} missionTitle - Title of the mission
     */
    create: function (totalTasks, missionTitle = "Mission in Progress") {
        // Remove existing tracker if any
        this.remove();

        const tracker = document.createElement('div');
        tracker.id = 'progress-tracker';
        tracker.className = 'fixed top-4 right-4 w-80 bg-[var(--bg-secondary)] border border-[var(--border)] rounded-lg p-4 shadow-2xl z-50 backdrop-blur-sm';

        tracker.innerHTML = `
            <div class="flex items-center justify-between mb-3">
                <div class="flex items-center gap-2">
                    <span class="material-symbols-outlined text-[var(--accent-cyan)] text-[16px] animate-spin">progress_activity</span>
                    <h3 class="text-[11px] font-bold uppercase tracking-widest text-[var(--text-main)]">Executing Mission</h3>
                </div>
                <button onclick="ProgressTracker.minimize()" class="material-symbols-outlined text-[12px] text-[var(--text-muted)] hover:text-[var(--text-main)] cursor-pointer">
                    minimize
                </button>
            </div>
            
            <div class="mb-2">
                <div class="text-[10px] text-[var(--text-muted)] mb-1 line-clamp-2">${missionTitle}</div>
                <div class="flex justify-between items-center mb-1">
                    <span class="text-[9px] text-[var(--text-muted)] tracking-wider">PROGRESS</span>
                    <span class="text-[10px] font-bold text-[var(--accent-cyan)]" id="progress-percentage">0%</span>
                </div>
                <div class="w-full h-2 bg-[var(--bg-main)] rounded-full overflow-hidden">
                    <div id="progress-bar" class="h-full bg-gradient-to-r from-[var(--accent-cyan)] to-[var(--accent-purple)] transition-all duration-500 ease-out" style="width: 0%"></div>
                </div>
            </div>
            
            <div id="progress-tasks" class="space-y-1 max-h-48 overflow-y-auto">
                <!-- Tasks will be added here dynamically -->
            </div>
            
            <div class="mt-3 pt-2 border-t border-[var(--border)] flex items-center justify-between">
                <div class="text-[9px] text-[var(--text-muted)]">
                    <span id="tasks-completed">0</span>/<span id="tasks-total">${totalTasks}</span> tasks
                </div>
                <div class="text-[9px] text-[var(--accent-cyan)] flex items-center gap-1">
                    <span class="material-symbols-outlined text-[10px]">schedule</span>
                    <span id="elapsed-time">0:00</span>
                </div>
            </div>
        `;

        document.body.appendChild(tracker);

        this.currentProgress = {
            totalTasks: totalTasks,
            completedTasks: 0,
            tasks: [],
            startTime: Date.now()
        };

        // Start timer
        this.startTimer();

        return tracker;
    },

    /**
     * Add a task to the tracker
     * @param {string} taskId - Unique task identifier
     * @param {string} taskName - Task description
     * @param {string} agentName - Agent assigned to task
     */
    addTask: function (taskId, taskName, agentName = "Agent") {
        if (!this.currentProgress) return;

        const tasksContainer = document.getElementById('progress-tasks');
        if (!tasksContainer) return;

        const taskElement = document.createElement('div');
        taskElement.id = `task-${taskId}`;
        taskElement.className = 'task-item flex items-start gap-2 p-2 rounded bg-[rgba(255,255,255,0.02)] border-l-2 border-l-[var(--accent-orange)]';

        taskElement.innerHTML = `
            <span class="material-symbols-outlined text-[12px] text-[var(--accent-orange)] task-icon">radio_button_unchecked</span>
            <div class="flex-1 min-w-0">
                <div class="text-[10px] text-[var(--text-main)] font-medium truncate">${taskName}</div>
                <div class="text-[9px] text-[var(--text-muted)] flex items-center gap-1 mt-0.5">
                    <span class="material-symbols-outlined text-[8px]">person</span>
                    <span>${agentName}</span>
                </div>
            </div>
            <span class="task-status text-[8px] uppercase tracking-widest font-bold text-[var(--accent-orange)]">Pending</span>
        `;

        tasksContainer.appendChild(taskElement);

        this.currentProgress.tasks.push({
            id: taskId,
            name: taskName,
            agent: agentName,
            status: 'pending'
        });
    },

    /**
     * Update task status
     * @param {string} taskId - Task identifier
     * @param {string} status - 'in-progress', 'completed', 'failed'
     */
    updateTaskStatus: function (taskId, status) {
        if (!this.currentProgress) return;

        const taskElement = document.getElementById(`task-${taskId}`);
        if (!taskElement) return;

        const icon = taskElement.querySelector('.task-icon');
        const statusSpan = taskElement.querySelector('.task-status');
        const borderColor = taskElement.style;

        switch (status) {
            case 'in-progress':
                icon.textContent = 'sync';
                icon.classList.add('animate-spin');
                icon.style.color = 'var(--accent-cyan)';
                statusSpan.textContent = 'Running';
                statusSpan.style.color = 'var(--accent-cyan)';
                taskElement.style.borderLeftColor = 'var(--accent-cyan)';
                break;

            case 'completed':
                icon.textContent = 'check_circle';
                icon.classList.remove('animate-spin');
                icon.style.color = 'var(--accent-green)';
                statusSpan.textContent = 'Done';
                statusSpan.style.color = 'var(--accent-green)';
                taskElement.style.borderLeftColor = 'var(--accent-green)';

                // Update progress
                this.currentProgress.completedTasks++;
                this.updateProgress();
                break;

            case 'failed':
                icon.textContent = 'cancel';
                icon.classList.remove('animate-spin');
                icon.style.color = 'var(--accent-red)';
                statusSpan.textContent = 'Failed';
                statusSpan.style.color = 'var(--accent-red)';
                taskElement.style.borderLeftColor = 'var(--accent-red)';
                break;
        }

        // Update task in progress object
        const task = this.currentProgress.tasks.find(t => t.id === taskId);
        if (task) {
            task.status = status;
        }
    },

    /**
     * Update progress bar
     */
    updateProgress: function () {
        if (!this.currentProgress) return;

        const percentage = (this.currentProgress.completedTasks / this.currentProgress.totalTasks) * 100;

        const progressBar = document.getElementById('progress-bar');
        const progressPercentage = document.getElementById('progress-percentage');
        const tasksCompleted = document.getElementById('tasks-completed');

        if (progressBar) {
            progressBar.style.width = `${percentage}%`;
        }

        if (progressPercentage) {
            progressPercentage.textContent = `${Math.round(percentage)}%`;
        }

        if (tasksCompleted) {
            tasksCompleted.textContent = this.currentProgress.completedTasks;
        }

        // If all tasks completed, celebrate and auto-close after 3s
        if (this.currentProgress.completedTasks === this.currentProgress.totalTasks) {
            this.complete();
        }
    },

    /**
     * Start elapsed time timer
     */
    startTimer: function () {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
        }

        this.timerInterval = setInterval(() => {
            if (!this.currentProgress) {
                clearInterval(this.timerInterval);
                return;
            }

            const elapsed = Date.now() - this.currentProgress.startTime;
            const minutes = Math.floor(elapsed / 60000);
            const seconds = Math.floor((elapsed % 60000) / 1000);

            const elapsedElement = document.getElementById('elapsed-time');
            if (elapsedElement) {
                elapsedElement.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
            }
        }, 1000);
    },

    /**
     * Mark mission as complete
     */
    complete: function () {
        const tracker = document.getElementById('progress-tracker');
        if (!tracker) return;

        // Change header to completed state
        const header = tracker.querySelector('h3');
        if (header) {
            header.textContent = 'Mission Complete';
        }

        const spinner = tracker.querySelector('.animate-spin');
        if (spinner) {
            spinner.textContent = 'check_circle';
            spinner.classList.remove('animate-spin');
            spinner.style.color = 'var(--accent-green)';
        }

        // Stop timer
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
        }

        // Auto-close after 5 seconds
        setTimeout(() => {
            this.remove();
        }, 5000);
    },

    /**
     * Minimize tracker (collapse to icon)
     */
    minimize: function () {
        const tracker = document.getElementById('progress-tracker');
        if (!tracker) return;

        tracker.classList.add('minimized');
        tracker.style.width = '48px';
        tracker.style.height = '48px';
        tracker.style.padding = '12px';
        tracker.innerHTML = `
            <button onclick="ProgressTracker.restore()" class="material-symbols-outlined text-[var(--accent-cyan)] text-[24px] cursor-pointer hover:scale-110 transition-transform">
                expand_more
            </button>
        `;
    },

    /**
     * Restore from minimized state
     */
    restore: function () {
        const tracker = document.getElementById('progress-tracker');
        if (!tracker || !this.currentProgress) return;

        tracker.classList.remove('minimized');
        tracker.style.width = '320px';
        tracker.style.height = 'auto';
        tracker.style.padding = '16px';

        // Recreate full UI
        this.create(this.currentProgress.totalTasks, 'Mission Restored');

        // Restore tasks
        this.currentProgress.tasks.forEach(task => {
            this.addTask(task.id, task.name, task.agent);
            if (task.status !== 'pending') {
                this.updateTaskStatus(task.id, task.status);
            }
        });
    },

    /**
     * Remove tracker from DOM
     */
    remove: function () {
        const tracker = document.getElementById('progress-tracker');
        if (tracker) {
            tracker.style.opacity = '0';
            tracker.style.transform = 'translateX(100px)';
            tracker.style.transition = 'all 0.3s ease-out';

            setTimeout(() => {
                tracker.remove();
            }, 300);
        }

        if (this.timerInterval) {
            clearInterval(this.timerInterval);
        }

        this.currentProgress = null;
    }
};

// Make it globally available
window.ProgressTracker = ProgressTracker;
