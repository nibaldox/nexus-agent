const origin = (window.location && window.location.origin && window.location.origin !== 'null')
    ? window.location.origin
    : 'http://localhost:8000';
const baseUrl = window.__NEXUS_API_URL || origin;

export const API_URL = `${String(baseUrl).replace(/\/$/, '')}/chat`;
