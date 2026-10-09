let searchTimeout;
let allProjects = [];

document.addEventListener('DOMContentLoaded', function() {
    const projectCards = document.querySelectorAll('.searchable-card');
    projectCards.forEach(card => {
        allProjects.push({
            element: card,
            title: card.dataset.title,
            description: card.dataset.description,
            tags: card.dataset.tags
        });
    });

    initSearch();
    initOtherFunctions();

    const urlParams = new URLSearchParams(window.location.search);
    const searchQuery = urlParams.get('search');
    if (searchQuery) {
        document.getElementById('searchInput').value = searchQuery;
        filterProjects(searchQuery);
    }
    updateHiddenSearchField();
});

function initSearch() {
    const searchInput = document.getElementById('searchInput');
    const searchForm = document.getElementById('searchForm');
    const hiddenSearch = document.getElementById('hiddenSearch');

    if (!searchInput || !searchForm) return;

    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);

        searchTimeout = setTimeout(() => {
            const query = this.value.trim().toLowerCase();
            filterProjects(query);
            updateUrlWithSearch(query);

            if (hiddenSearch) {
                hiddenSearch.value = query;
            }
        }, 300);
    });

    searchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            this.value = '';
            filterProjects('');
            updateUrlWithSearch('');
            if (hiddenSearch) {
                hiddenSearch.value = '';
            }
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
    const originalNoProjects = document.querySelector('.no-projects:not(#noResults)');
    const visibleCount = document.getElementById('visibleCount');

    let visibleProjects = 0;
    let hasVisibleProjects = false;

    if (!query) {
        allProjects.forEach(project => {
            project.element.classList.remove('hidden');
            project.element.classList.add('visible');
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
                visibleProjects++;
                hasVisibleProjects = true;
            } else {
                project.element.classList.add('hidden');
                project.element.classList.remove('visible');
            }
        });
    }

    if (visibleCount) {
        visibleCount.textContent = visibleProjects;
    }

    if (noResults && originalNoProjects) {
        if (hasVisibleProjects && allProjects.length > 0) {
            noResults.style.display = 'none';
            originalNoProjects.style.display = 'none';
            if (projectsGrid) {
                projectsGrid.style.display = 'grid';
            }
        } else if (allProjects.length === 0) {
            noResults.style.display = 'none';
            originalNoProjects.style.display = 'block';
            if (projectsGrid) {
                projectsGrid.style.display = 'none';
            }
        } else {
            noResults.style.display = 'block';
            originalNoProjects.style.display = 'none';
            if (projectsGrid) {
                projectsGrid.style.display = 'none';
            }
        }
    }
}

function updateUrlWithSearch(query) {
    const url = new URL(window.location);
    const tags = new URLSearchParams(window.location.search).getAll('tags');

    if (query) {
        url.searchParams.set('search', query);
    } else {
        url.searchParams.delete('search');
    }

    url.searchParams.delete('tags');
    tags.forEach(tag => {
        url.searchParams.append('tags', tag);
    });

    window.history.replaceState({}, '', url);
}

function updateHiddenSearchField() {
    const searchInput = document.getElementById('searchInput');
    const hiddenSearch = document.getElementById('hiddenSearch');

    if (hiddenSearch && searchInput) {
        hiddenSearch.value = searchInput.value;
    }
}

function clearSearch() {
    const searchInput = document.getElementById('searchInput');
    const hiddenSearch = document.getElementById('hiddenSearch');

    if (searchInput) {
        searchInput.value = '';
        filterProjects('');
        updateUrlWithSearch('');

        if (hiddenSearch) {
            hiddenSearch.value = '';
        }

        searchInput.focus();
    }
}

function initOtherFunctions() {
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        const hiddenTags = card.querySelectorAll('.hidden-tag');
        hiddenTags.forEach(tag => {
            tag.style.display = 'none';
        });
    });

    const selectedCount = document.querySelector('.selected-count');
    if (selectedCount && window.selectedTagsCount > 0) {
        selectedCount.style.display = 'inline';
    }

    document.querySelectorAll('.tag-checkbox input').forEach(checkbox => {
        checkbox.addEventListener('change', updateSelectedTags);
    });
}

function toggleTagsSidebar() {
    const sidebar = document.getElementById('tagsSidebar');
    const overlay = document.getElementById('tagsOverlay');

    if (sidebar && overlay) {
        sidebar.classList.toggle('active');
        overlay.classList.toggle('active');
        document.body.classList.toggle('no-scroll');
    }
}

function toggleHiddenTags(button) {
    const card = button.closest('.card');
    const hiddenTags = card.querySelectorAll('.hidden-tag');
    const isExpanded = card.classList.contains('tags-expanded');

    if (isExpanded) {
        hiddenTags.forEach(tag => {
            tag.style.display = 'none';
        });
        button.textContent = `Ещё ${hiddenTags.length} тег${getRussianEnding(hiddenTags.length)}`;
        card.classList.remove('tags-expanded');
    } else {
        hiddenTags.forEach(tag => {
            tag.style.display = 'inline-block';
        });
        button.textContent = 'Скрыть';
        card.classList.add('tags-expanded');
    }
}

function getRussianEnding(number) {
    if (number === 1) return '';
    if (number >= 2 && number <= 4) return 'а';
    return 'ов';
}

function resetFilters() {
    window.location.href = '/';
}

function updateSelectedTags() {
    const selectedCount = document.querySelector('.selected-count');
    const checkedBoxes = document.querySelectorAll('.tag-checkbox input:checked');

    if (selectedCount) {
        if (checkedBoxes.length > 0) {
            selectedCount.textContent = `(${checkedBoxes.length})`;
            selectedCount.style.display = 'inline';
        } else {
            selectedCount.style.display = 'none';
        }
    }
}

function flipCard(card) {
    if (!card) return;

    document.querySelectorAll('.card.flipped').forEach(flippedCard => {
        if (flippedCard !== card) {
            flippedCard.classList.remove('flipped');
            resetTextAnimation(flippedCard);
        }
    });

    if (card.classList.contains('flipped')) {
        card.classList.remove('flipped');
        resetTextAnimation(card);
    } else {
        card.classList.add('flipped');
        animateText(card);
    }
}

function animateText(card) {
    const description = card.querySelector('.card-back-description');
    const button = card.querySelector('.card-back-btn');

    [description, button].forEach(el => {
        if (el) {
            el.style.animation = 'none';
            el.offsetHeight; // trigger reflow
            el.style.animation = null;
        }
    });
}

function resetTextAnimation(card) {
    const description = card.querySelector('.card-back-description');
    const button = card.querySelector('.card-back-btn');

    [description, button].forEach(el => {
        if (el) {
            el.style.animation = 'none';
        }
    });
}

document.addEventListener('click', function(event) {
    const sidebar = document.getElementById('tagsSidebar');
    const overlay = document.getElementById('tagsOverlay');
    const tagsBtn = document.querySelector('.tags-btn');

    if (sidebar && sidebar.classList.contains('active') &&
        !sidebar.contains(event.target) &&
        event.target !== tagsBtn &&
        !tagsBtn?.contains(event.target) &&
        !overlay?.contains(event.target)) {
        toggleTagsSidebar();
    }

    if (!event.target.closest('.card')) {
        document.querySelectorAll('.card.flipped').forEach(card => {
            card.classList.remove('flipped');
            resetTextAnimation(card);
        });
    }
});

document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        const sidebar = document.getElementById('tagsSidebar');
        if (sidebar && sidebar.classList.contains('active')) {
            toggleTagsSidebar();
        }
    }
});

document.addEventListener('click', function(event) {
    const tagsElement = event.target.closest('.card-tags, .show-more-tags, .back-to-front');
    if (tagsElement) {
        event.stopPropagation();
    }
});

document.querySelectorAll('.show-more-tags').forEach(button => {
    button.addEventListener('click', function(event) {
        event.stopPropagation();
        toggleHiddenTags(this);
    });
});

document.querySelectorAll('.back-to-front').forEach(button => {
    button.addEventListener('click', function(event) {
        event.stopPropagation();
        const card = this.closest('.card');
        flipCard(card);
    });
});
