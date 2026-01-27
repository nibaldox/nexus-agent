// Terminal Integration for Developer Agent - DEBUGGED VERSION
function checkTerminalTrigger(event, agentName) {
    console.log('[Terminal Debug] Event received:', { agentName, hasTerminal: !!window.Terminal, content: event.content?.substring(0, 100) });

    if (!window.Terminal) {
        console.log('[Terminal Debug] Terminal not available');
        return;
    }

    // Check if it's Developer agent (try different variations)
    const isDeveloper = agentName && (
        agentName === 'Developer' ||
        agentName.includes('Developer') ||
        agentName === 'Developer Expert'
    );

    console.log('[Terminal Debug] Is Developer?', isDeveloper);

    if (!isDeveloper) return;

    const content = event.content || '';

    // Check if content contains code execution output
    if (content.includes('[STDOUT]') || content.includes('[EXIT_CODE]') || content.includes('[STDERR]')) {
        console.log('[Terminal Debug] Code execution detected! Creating terminal...');

        // Create terminal if not exists
        if (!Terminal.isOpen()) {
            Terminal.create('Code Execution Output');
            console.log('[Terminal Debug] Terminal created');
        }

        // Parse execution output
        const lines = content.split('\n');
        let currentSection = null;
        let exitCode = null;
        let duration = 0;

        lines.forEach(line => {
            const trimmed = line.trim();

            if (trimmed.includes('[STDOUT]')) {
                currentSection = 'stdout';
                Terminal.appendLine('=== Output ===', 'command');
            } else if (trimmed.includes('[STDERR]')) {
                currentSection = 'stderr';
                Terminal.appendLine('=== Errors ===', 'command');
            } else if (trimmed.includes('[EXIT_CODE]')) {
                const match = trimmed.match(/\[EXIT_CODE\]\s*(\d+)/);
                if (match) exitCode = parseInt(match[1]);
            } else if (trimmed.includes('[DURATION]')) {
                const match = trimmed.match(/\[DURATION\]\s*(\d+)ms/);
                if (match) duration = parseInt(match[1]);
            } else if (trimmed.includes('[PROFILE]')) {
                const match = trimmed.match(/\[PROFILE\]\s*(\w+)/);
                if (match) {
                    Terminal.appendLine('', 'separator');
                    Terminal.appendLine(`Profile: ${match[1].toUpperCase()}`, 'success');
                }
            } else if (trimmed && currentSection && !trimmed.startsWith('[')) {
                Terminal.appendLine(trimmed, currentSection);
            }
        });

        // Complete terminal if we have exit code
        if (exitCode !== null) {
            Terminal.complete(exitCode, duration);
            console.log('[Terminal Debug] Terminal completed with exit code:', exitCode);
        }
    } else {
        console.log('[Terminal Debug] No execution markers found in content');
    }
}

// Make function available globally
window.checkTerminalTrigger = checkTerminalTrigger;

console.log('[Terminal Integration] Loaded with debug enabled');
