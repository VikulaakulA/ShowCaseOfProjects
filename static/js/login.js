function smartGoBack() {
    const referrer = document.referrer;
    const currentUrl = window.location.href;

    if (referrer && referrer !== currentUrl) {
        const referrerPath = new URL(referrer).pathname;
        const currentPath = new URL(currentUrl).pathname;

        if (referrerPath !== currentPath) {
            window.history.back();
            return false;
        }
    }

    window.location.href = window.indexUrl || '/';
    return false;
}

function goToHome() {
    window.location.href = window.indexUrl || '/';
    return false;
}

document.addEventListener('DOMContentLoaded', function() {
    const usernameInput = document.querySelector('input[name="username"]');
    if (usernameInput) {
        usernameInput.focus();
    }

    const loginForm = document.querySelector('form');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            const username = this.querySelector('input[name="username"]');
            const password = this.querySelector('input[name="password"]');

            if (!username.value.trim() || !password.value.trim()) {
                e.preventDefault();
                alert('Пожалуйста, заполните все поля');
                if (!username.value.trim()) {
                    username.focus();
                } else {
                    password.focus();
                }
            }
        });
    }
});
