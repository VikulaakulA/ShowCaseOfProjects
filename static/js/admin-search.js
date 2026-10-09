let searchTimeout;
let allProjects = [];

document.addEventListener('DOMContentLoaded', function() {
    const projectCards = document.querySelectorAll('.searchable-card');
    projectCards.forEach(card => {
        allProjects.push({
            element: card,
            title: card.dataset.title,
            description: card.dataset.description,
            tags: card.dataset.tags,
            status: card.dataset.status
        });
    });

    initAdminSearch();

    const urlParams = new URLSearchParams(window.location.search);
    const searchQuery = urlParams.get('search');
    if (searchQuery) {
        document.getElementById('searchInput').value = searchQuery;
        filterProjects(searchQuery);
    }
});

function initAdminSearch() {
    const searchInput = document.getElementById('searchInput');
    const searchForm = document.getElementById('searchForm');

    if (!searchInput || !searchForm) return;

    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);

        searchTimeout = setTimeout(() => {
            const query = this.value.trim().toLowerCase();
            filterProjects(query);
            updateUrlWithSearch(query);
        }, 300);
    });

    searchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            this.value = '';
            filterProjects('');
            updateUrlWithSearch('');
        }
    });

    searchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const query = searchInput.value.trim().toLowerCase();
        filterProjects(query);
        updateUrlWithSearch(query);
    });
}

function filterProjects(query) {
    const projectsGrid = document.getElementById('projectsGrid');
    const noResults = document.getElementById('noResults');

    let visibleProjects = 0;
    let hasVisibleProjects = false;

    if (!query) {
        allProjects.forEach(project => {
            project.element.classList.remove('hidden');
            project.element.classList.add('visible');
            removeHighlights(project.element);
        });
        visibleProjects = allProjects.length;
        hasVisibleProjects = true;
    } else {
        allProjects.forEach(project => {
            const matches = (
                project.title.includes(query) ||
                project.description.includes(query) ||
                project.tags.includes(query)
            );

            if (matches) {
                project.element.classList.remove('hidden');
                project.element.classList.add('visible');
                highlightMatches(project.element, query);
                visibleProjects++;
                hasVisibleProjects = true;
            } else {
                project.element.classList.add('hidden');
                project.element.classList.remove('visible');
                removeHighlights(project.element);
            }
        });
    }

    if (noResults) {
        if (hasVisibleProjects || allProjects.length === 0) {
            noResults.style.display = 'none';
        } else {
            noResults.style.display = 'block';
        }
    }

    if (projectsGrid) {
        if (hasVisibleProjects) {
            projectsGrid.style.display = 'grid';
        } else {
            projectsGrid.style.display = 'none';
        }
    }
}

function highlightMatches(element, query) {
    const title = element.querySelector('.searchable-title');
    const description = element.querySelector('.searchable-description');
    const tags = element.querySelectorAll('.searchable-tag');

    removeHighlights(element);

    if (title) {
        const text = title.textContent;
        const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
        title.innerHTML = text.replace(regex, '<span class="highlight search-match">$1</span>');
    }

    if (description && query.length > 2) {
        const text = description.textContent;
        const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
        description.innerHTML = text.replace(regex, '<span class="highlight">$1</span>');
    }

    tags.forEach(tag => {
        const tagText = tag.textContent.toLowerCase();
        if (tagText.includes(query)) {
            tag.classList.add('search-match');
            setTimeout(() => {
                tag.classList.remove('search-match');
            }, 1500);
        }
    });
}

function removeHighlights(element) {
    const title = element.querySelector('.searchable-title');
    const description = element.querySelector('.searchable-description');

    if (title) {
        title.innerHTML = title.textContent;
    }

    if (description) {
        description.innerHTML = description.textContent;
    }
}

function updateUrlWithSearch(query) {
    const url = new URL(window.location);
    const status = document.getElementById('statusFilter').value;

    if (query) {
        url.searchParams.set('search', query);
    } else {
        url.searchParams.delete('search');
    }

    url.searchParams.set('status', status);
    window.history.replaceState({}, '', url);
}

function clearSearch() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.value = '';
        filterProjects('');
        updateUrlWithSearch('');
        searchInput.focus();
    }
}
