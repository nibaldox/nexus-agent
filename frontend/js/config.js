export const FRONTEND_CONFIG = {
    maxMessageLength: 2000,
    upload: {
        maxSizeBytes: 15 * 1024 * 1024,
        allowedMimeTypes: ['application/pdf']
    },
    scroll: {
        bottomThresholdPx: 240
    },
    render: {
        throttleMs: 140,
        maxDelayMs: 600
    },
    connection: {
        checkIntervalMs: 15000,
        timeoutMs: 3000
    },
    squads: {
        pollMinMs: 3000,
        pollMaxMs: 20000,
        backoffFactor: 1.6
    }
};
