// Основные JavaScript функции

document.addEventListener('DOMContentLoaded', function() {
    // Инициализация tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Инициализация popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Автоматическое скрытие сообщений через 5 секунд
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Подтверждение удаления
    var deleteButtons = document.querySelectorAll('.btn-delete-confirm');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('Вы уверены, что хотите удалить этот элемент? Это действие нельзя отменить.')) {
                e.preventDefault();
            }
        });
    });
    
    // Автодополнение для полей диагноза
    initDiagnosisAutocomplete();
});

// Автодополнение диагнозов
function initDiagnosisAutocomplete() {
    const diagnosisInputs = document.querySelectorAll('[data-autocomplete-url]');
    
    diagnosisInputs.forEach(input => {
        const url = input.getAttribute('data-autocomplete-url');
        
        input.addEventListener('input', debounce(function(e) {
            const query = e.target.value.trim();
            
            if (query.length < 2) {
                clearDropdown();
                return;
            }
            
            fetch(`${url}?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    showDropdown(data.results, input);
                })
                .catch(error => console.error('Ошибка автодополнения:', error));
        }, 300));
    });
    
    function showDropdown(results, input) {
        clearDropdown();
        
        if (results.length === 0) return;
        
        const dropdown = document.createElement('div');
        dropdown.className = 'autocomplete-dropdown list-group';
        dropdown.style.position = 'absolute';
        dropdown.style.zIndex = '1000';
        dropdown.style.width = input.offsetWidth + 'px';
        dropdown.style.maxHeight = '200px';
        dropdown.style.overflowY = 'auto';
        
        results.forEach(item => {
            const option = document.createElement('a');
            option.className = 'list-group-item list-group-item-action';
            option.href = '#';
            option.innerHTML = `
                <div class="fw-bold">${item.code}</div>
                <div class="text-muted small">${item.name}</div>
            `;
            
            option.addEventListener('click', function(e) {
                e.preventDefault();
                input.value = item.code;
                clearDropdown();
            });
            
            dropdown.appendChild(option);
        });
        
        input.parentNode.appendChild(dropdown);
    }
    
    function clearDropdown() {
        const dropdowns = document.querySelectorAll('.autocomplete-dropdown');
        dropdowns.forEach(d => d.remove());
    }
    
    // Закрытие dropdown при клике вне
    document.addEventListener('click', function(e) {
        if (!e.target.closest('[data-autocomplete-url]')) {
            clearDropdown();
        }
    });
}

// Debounce функция
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Форматирование даты
function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU') + ' ' + date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
}

// Копирование в буфер обмена
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        alert('Скопировано в буфер обмена');
    }).catch(err => {
        console.error('Ошибка копирования:', err);
    });
}