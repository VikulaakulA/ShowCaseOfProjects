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

document.addEventListener('DOMContentLoaded', function() {
    const elements = document.querySelectorAll('.project-main-content, .project-image-container, .project-files');
    elements.forEach((el, index) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';

        setTimeout(() => {
            el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }, index * 150);
    });

    window.scrollTo(0, 0);

    document.querySelectorAll('.file-item').forEach(fileItem => {
        fileItem.addEventListener('click', function(e) {
            if (this.getAttribute('href') === '#') {
                e.preventDefault();
            }
        });
    });

    document.querySelectorAll('a[href="#"], a[href=""]').forEach(link => {
        link.addEventListener('click', function(e) {
            if (this.getAttribute('href') === '#' || this.getAttribute('href') === '') {
                e.preventDefault();
            }
        });
    });
});

function setIndexUrl(url) {
    window.indexUrl = url;
}
