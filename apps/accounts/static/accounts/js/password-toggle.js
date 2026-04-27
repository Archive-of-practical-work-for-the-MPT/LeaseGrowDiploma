(function () {
    var toggles = document.querySelectorAll('[data-password-toggle]');

    toggles.forEach(function (toggle) {
        var targetIds = toggle
            .getAttribute('data-password-toggle')
            .split(',')
            .map(function (id) { return id.trim(); })
            .filter(Boolean);

        var fields = targetIds
            .map(function (id) { return document.getElementById(id); })
            .filter(function (field) { return field; });

        if (!fields.length) {
            return;
        }

        toggle.addEventListener('mousedown', function (event) {
            event.preventDefault();
        });

        toggle.addEventListener('click', function () {
            var shouldShow = fields[0].type === 'password';

            fields.forEach(function (field) {
                field.type = shouldShow ? 'text' : 'password';
            });

            toggle.classList.toggle('is-visible', shouldShow);
            toggle.setAttribute('aria-pressed', shouldShow ? 'true' : 'false');
            toggle.setAttribute('aria-label', shouldShow ? 'Hide password' : 'Show password');
        });
    });
})();
