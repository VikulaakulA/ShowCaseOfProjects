document.addEventListener('DOMContentLoaded', function() {
    const shortDesc = document.getElementById('short_description');
    const shortDescCount = document.getElementById('short_desc_count');

    if (shortDesc && shortDescCount) {
        shortDesc.addEventListener('input', function() {
            shortDescCount.textContent = `${this.value.length}/500`;
        });
    }

    const categories = document.querySelectorAll('.tag-category-form');
    categories.forEach(category => {
        const tagOptions = category.querySelector('.tag-options');
        const icon = category.querySelector('.category-icon');
        tagOptions.classList.add('collapsed');
        icon.classList.remove('fa-chevron-up');
        icon.classList.add('fa-chevron-down');
    });

    const form = document.querySelector('.project-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            const requiredFields = this.querySelectorAll('[required]');
            let isValid = true;

            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('error');
                } else {
                    field.classList.remove('error');
                }
            });

            if (!isValid) {
                e.preventDefault();
                alert('Пожалуйста, заполните все обязательные поля (помечены *).');
            }
        });
    }
});

function toggleCategory(header) {
    const categoryForm = header.closest('.tag-category-form');
    const tagOptions = categoryForm.querySelector('.tag-options');
    const icon = categoryForm.querySelector('.category-icon');

    tagOptions.classList.toggle('collapsed');
    icon.classList.toggle('fa-chevron-down');
    icon.classList.toggle('fa-chevron-up');
}

function addField(type) {
    const container = document.getElementById(`${type}-container`);
    if (!container) return;

    const newField = document.createElement('div');

    switch(type) {
        case 'departments':
        case 'mentors':
        case 'participants':
        case 'partners':
            newField.className = 'dynamic-field-group removable-field';
            newField.innerHTML = `
                <input type="text" name="${type}[]" placeholder="${getPlaceholder(type)}" required>
                <button type="button" class="remove-field-btn" onclick="removeField(this)">×</button>
            `;
            break;
        case 'majors':
            newField.className = 'dynamic-field-group major-group removable-field';
            newField.innerHTML = `
                <input type="text" name="major_codes[]" placeholder="Код направления" required>
                <input type="text" name="major_profiles[]" placeholder="Профиль/специализация" required>
                <button type="button" class="remove-field-btn" onclick="removeField(this)">×</button>
            `;
            break;
        case 'files':
            newField.className = 'dynamic-field-group file-group removable-field';
            newField.innerHTML = `
                <input type="file" name="project_files[]">
                <button type="button" class="remove-field-btn" onclick="removeField(this)">×</button>
            `;
            break;
        default:
            return;
    }

    container.appendChild(newField);
}

function removeField(button) {
    const fieldGroup = button.closest('.removable-field');
    if (fieldGroup) {
        fieldGroup.remove();
    }
}

function getPlaceholder(type) {
    const placeholders = {
        'departments': 'Название департамента/кафедры',
        'mentors': 'ФИО наставника',
        'participants': 'ФИО участника',
        'partners': 'Название организации'
    };
    return placeholders[type] || 'Введите значение';
}
