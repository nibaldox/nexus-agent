// Theme switcher
const themeToggle = document.getElementById('theme-toggle');
const themeIcon = document.getElementById('theme-icon');
const html = document.documentElement;

// Moon SVG path
const moonSVG = `
    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
`;

// Sun SVG paths
const sunSVG = `
    <circle cx="12" cy="12" r="5"></circle>
    <line x1="12" y1="1" x2="12" y2="3"></line>
    <line x1="12" y1="21" x2="12" y2="23"></line>
    <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
    <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
    <line x1="1" y1="12" x2="3" y2="12"></line>
    <line x1="21" y1="12" x2="23" y2="12"></line>
    <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
    <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
`;

// Load saved theme or use default (dark)
function loadTheme() {
    const savedTheme = localStorage.getItem('nexus-theme') || 'dark';
    setTheme(savedTheme);
}

// Set theme
function setTheme(theme) {
    html.setAttribute('data-theme', theme);
    localStorage.setItem('nexus-theme', theme);

    // Update icon
    if (theme === 'light') {
        themeIcon.innerHTML = moonSVG;
        themeIcon.style.color = '#1A1A1A';
        if (themeToggle) {
            themeToggle.setAttribute('aria-pressed', 'true');
            themeToggle.setAttribute('title', 'Cambiar a tema oscuro');
        }
    } else {
        themeIcon.innerHTML = sunSVG;
        themeIcon.style.color = '#00E0FF';
        if (themeToggle) {
            themeToggle.setAttribute('aria-pressed', 'false');
            themeToggle.setAttribute('title', 'Cambiar a tema claro');
        }
    }
}

// Toggle theme
function toggleTheme() {
    const currentTheme = html.getAttribute('data-theme') || 'dark';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
}

// Event listener
if (themeToggle) {
    themeToggle.addEventListener('click', toggleTheme);
}

// Initialize theme on page load
loadTheme();
