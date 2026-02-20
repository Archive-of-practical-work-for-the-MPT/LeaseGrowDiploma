(function () {
    var STORAGE_KEY = 'leasegrow-theme';

    function getPreferredTheme() {
        var stored = localStorage.getItem(STORAGE_KEY);
        if (stored === 'dark' || stored === 'light') return stored;
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) return 'dark';
        return 'light';
    }

    function setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme === 'dark' ? 'dark' : '');
        localStorage.setItem(STORAGE_KEY, theme);
        updateToggle(theme);
    }

    function updateToggle(theme) {
        var btn = document.getElementById('theme-toggle');
        if (!btn) return;
        btn.setAttribute('aria-label', theme === 'dark' ? 'Включить светлую тему' : 'Включить тёмную тему');
        btn.classList.toggle('active-dark', theme === 'dark');
    }

    function handleToggleClick(e) {
        var t = e.target;
        var btn = (t.closest && t.closest('#theme-toggle')) || (t.id === 'theme-toggle' ? t : (t.parentNode && t.parentNode.id === 'theme-toggle' ? t.parentNode : null));
        if (!btn) return;
        e.preventDefault();
        e.stopPropagation();
        var current = document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
        setTheme(current === 'dark' ? 'light' : 'dark');
    }

    function init() {
        var theme = getPreferredTheme();
        setTheme(theme);
        document.addEventListener('click', handleToggleClick);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
