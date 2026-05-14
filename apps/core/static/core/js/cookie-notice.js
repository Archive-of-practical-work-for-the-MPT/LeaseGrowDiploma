(function () {
    var STORAGE_KEY = 'leasegrow-cookie-notice-dismissed';

    function init() {
        var el = document.getElementById('cookie-notice');
        var btn = document.getElementById('cookie-notice-accept');
        if (!el || !btn) return;

        try {
            if (localStorage.getItem(STORAGE_KEY) === '1') return;
        } catch (e) {
            /* private mode / disabled storage — показываем уведомление каждый раз */
        }

        el.removeAttribute('hidden');

        btn.addEventListener('click', function () {
            try {
                localStorage.setItem(STORAGE_KEY, '1');
            } catch (ignore) {}
            el.setAttribute('hidden', '');
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
