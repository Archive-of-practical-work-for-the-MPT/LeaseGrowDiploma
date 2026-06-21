(function () {
    var MOBILE_BREAKPOINT = 900;

    function isMobile() {
        return window.innerWidth <= MOBILE_BREAKPOINT;
    }

    function getElements() {
        return {
            header: document.getElementById('site-header'),
            toggle: document.getElementById('nav-toggle'),
            nav: document.getElementById('main-nav'),
        };
    }

    function setOpen(open) {
        var els = getElements();
        if (!els.header || !els.toggle) return;

        els.header.classList.toggle('nav-open', open);
        els.toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
        els.toggle.setAttribute('aria-label', open ? 'Закрыть меню' : 'Открыть меню');
        document.body.classList.toggle('nav-menu-open', open);
    }

    function closeMenu() {
        setOpen(false);
    }

    function toggleMenu() {
        var els = getElements();
        if (!els.header) return;
        setOpen(!els.header.classList.contains('nav-open'));
    }

    function handleToggleClick(e) {
        var btn = e.target.closest && e.target.closest('#nav-toggle');
        if (!btn) return;
        e.preventDefault();
        e.stopPropagation();
        toggleMenu();
    }

    function handleDocumentClick(e) {
        var els = getElements();
        if (!els.header || !els.header.classList.contains('nav-open')) return;

        if (e.target.closest && e.target.closest('#nav-toggle')) return;
        if (e.target.closest && e.target.closest('#site-header')) return;

        closeMenu();
    }

    function handleNavLinkClick(e) {
        if (!isMobile()) return;
        if (e.target.closest && e.target.closest('#main-nav a')) {
            closeMenu();
        }
    }

    function handleKeydown(e) {
        if (e.key === 'Escape') {
            closeMenu();
        }
    }

    function handleResize() {
        if (!isMobile()) {
            closeMenu();
        }
    }

    function init() {
        var els = getElements();
        if (!els.toggle || !els.nav) return;

        document.addEventListener('click', handleToggleClick);
        document.addEventListener('click', handleDocumentClick);
        document.addEventListener('click', handleNavLinkClick);
        document.addEventListener('keydown', handleKeydown);
        window.addEventListener('resize', handleResize);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
