// ===== ADMIN INTERFACE JAVASCRIPT =====

// Variables globales
let currentUser = null;
let notifications = [];
let sidebarCollapsed = false;

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    initializeAdmin();
    setupEventListeners();
    loadUserData();
    setupNotifications();
});

// ===== INITIALISATION =====
function initializeAdmin() {
    console.log('Initialisation de l\'interface d\'administration CSIG...');
    
    // Initialiser les tooltips Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialiser les popovers Bootstrap
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Initialiser les DataTables
    initializeDataTables();
    
    // Initialiser Select2
    initializeSelect2();
    
    // Vérifier la résolution et ajuster la sidebar
    checkScreenSize();
}

// ===== EVENT LISTENERS =====
function setupEventListeners() {
    // Toggle sidebar sur mobile
    const sidebarToggle = document.querySelector('.navbar-toggler');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', toggleSidebar);
    }
    
    // Fermer la sidebar en cliquant à l'extérieur sur mobile
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 992) {
            const sidebar = document.querySelector('.admin-sidebar');
            const toggle = document.querySelector('.navbar-toggler');
            
            if (sidebar && !sidebar.contains(e.target) && !toggle.contains(e.target)) {
                sidebar.classList.remove('show');
            }
        }
    });
    
    // Gestion du redimensionnement de la fenêtre
    window.addEventListener('resize', debounce(checkScreenSize, 250));
    
    // Gestion des raccourcis clavier
    document.addEventListener('keydown', handleKeyboardShortcuts);
    
    // Gestion des formulaires
    setupFormHandlers();
    
    // Gestion des modals
    setupModalHandlers();
}

// ===== SIDEBAR MANAGEMENT =====
function toggleSidebar() {
    const sidebar = document.querySelector('.admin-sidebar');
    const container = document.querySelector('.admin-container');
    
    if (sidebar) {
        sidebar.classList.toggle('show');
        container.classList.toggle('sidebar-open');
    }
}

function checkScreenSize() {
    const sidebar = document.querySelector('.admin-sidebar');
    const container = document.querySelector('.admin-container');
    
    if (window.innerWidth <= 992) {
        if (sidebar) sidebar.classList.remove('show');
        if (container) container.classList.remove('sidebar-open');
    }
}

// ===== DATA TABLES =====
function initializeDataTables() {
    const tables = document.querySelectorAll('.datatable');
    
    tables.forEach(table => {
        if (!table.classList.contains('dataTable')) {
            new DataTable(table, {
                language: {
                    url: '//cdn.datatables.net/plug-ins/1.13.6/i18n/fr-FR.json'
                },
                pageLength: 25,
                responsive: true,
                dom: '<"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6"f>>' +
                     '<"row"<"col-sm-12"tr>>' +
                     '<"row"<"col-sm-12 col-md-5"i><"col-sm-12 col-md-7"p>>',
                lengthMenu: [[10, 25, 50, 100], [10, 25, 50, 100]],
                order: [[0, 'desc']],
                columnDefs: [
                    { orderable: false, targets: -1 }
                ]
            });
        }
    });
}

// ===== SELECT2 =====
function initializeSelect2() {
    const selects = document.querySelectorAll('.select2');
    
    selects.forEach(select => {
        if (!select.classList.contains('select2-hidden-accessible')) {
            $(select).select2({
                theme: 'bootstrap-5',
                width: '100%',
                placeholder: select.getAttribute('placeholder') || 'Sélectionner...',
                allowClear: true
            });
        }
    });
}

// ===== FORM HANDLERS =====
function setupFormHandlers() {
    // Validation des formulaires
    const forms = document.querySelectorAll('form[data-validate]');
    forms.forEach(form => {
        form.addEventListener('submit', validateForm);
    });
    
    // Auto-save des formulaires
    const autoSaveForms = document.querySelectorAll('form[data-autosave]');
    autoSaveForms.forEach(form => {
        setupAutoSave(form);
    });
    
    // Upload de fichiers
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', handleFileUpload);
    });
}

function validateForm(e) {
    const form = e.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Validation...';
    }
    
    // Logique de validation personnalisée ici
    
    return true;
}

function setupAutoSave(form) {
    const inputs = form.querySelectorAll('input, textarea, select');
    let autoSaveTimer;
    
    inputs.forEach(input => {
        input.addEventListener('input', () => {
            clearTimeout(autoSaveTimer);
            autoSaveTimer = setTimeout(() => {
                autoSaveForm(form);
            }, 2000);
        });
    });
}

function autoSaveForm(form) {
    const formData = new FormData(form);
    const url = form.action || window.location.href;
    
    fetch(url, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Sauvegarde automatique effectuée', 'success');
        }
    })
    .catch(error => {
        console.error('Erreur auto-save:', error);
    });
}

// ===== FILE UPLOAD =====
function handleFileUpload(e) {
    const input = e.target;
    const files = input.files;
    const previewContainer = input.parentNode.querySelector('.file-preview');
    
    if (previewContainer) {
        previewContainer.innerHTML = '';
        
        Array.from(files).forEach(file => {
            const preview = createFilePreview(file);
            previewContainer.appendChild(preview);
        });
    }
    
    // Mettre à jour le label
    updateFileInputLabel(input);
}

function createFilePreview(file) {
    const preview = document.createElement('div');
    preview.className = 'file-preview-item';
    
    if (file.type.startsWith('image/')) {
        const img = document.createElement('img');
        img.src = URL.createObjectURL(file);
        img.className = 'file-preview-image';
        preview.appendChild(img);
    } else {
        const icon = document.createElement('i');
        icon.className = 'fas fa-file fa-2x text-muted';
        preview.appendChild(icon);
    }
    
    const name = document.createElement('span');
    name.className = 'file-preview-name';
    name.textContent = file.name;
    preview.appendChild(name);
    
    const removeBtn = document.createElement('button');
    removeBtn.type = 'button';
    removeBtn.className = 'btn btn-sm btn-outline-danger file-preview-remove';
    removeBtn.innerHTML = '<i class="fas fa-times"></i>';
    removeBtn.onclick = () => preview.remove();
    preview.appendChild(removeBtn);
    
    return preview;
}

function updateFileInputLabel(input) {
    const label = input.parentNode.querySelector('.file-input-label');
    if (label) {
        const fileCount = input.files.length;
        if (fileCount > 0) {
            label.textContent = `${fileCount} fichier(s) sélectionné(s)`;
        } else {
            label.textContent = 'Choisir des fichiers';
        }
    }
}

// ===== MODAL HANDLERS =====
function setupModalHandlers() {
    // Gestion des modals de confirmation
    const confirmModals = document.querySelectorAll('[data-confirm]');
    confirmModals.forEach(modal => {
        modal.addEventListener('click', handleConfirmAction);
    });
    
    // Gestion des modals de suppression
    const deleteModals = document.querySelectorAll('[data-delete]');
    deleteModals.forEach(modal => {
        modal.addEventListener('click', handleDeleteAction);
    });
}

function handleConfirmAction(e) {
    e.preventDefault();
    const action = e.target.getAttribute('data-confirm');
    const message = e.target.getAttribute('data-message') || 'Êtes-vous sûr de vouloir effectuer cette action ?';
    
    if (confirm(message)) {
        // Exécuter l'action
        console.log('Action confirmée:', action);
    }
}

function handleDeleteAction(e) {
    e.preventDefault();
    const itemId = e.target.getAttribute('data-delete');
    const itemType = e.target.getAttribute('data-type');
    const message = e.target.getAttribute('data-message') || 'Êtes-vous sûr de vouloir supprimer cet élément ?';
    
    if (confirm(message)) {
        deleteItem(itemId, itemType);
    }
}

function deleteItem(id, type) {
    const url = `/content-management/${type}/${id}/delete/`;
    
    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Élément supprimé avec succès', 'success');
            // Recharger la page ou mettre à jour l'interface
            setTimeout(() => location.reload(), 1000);
        } else {
            showNotification('Erreur lors de la suppression', 'error');
        }
    })
    .catch(error => {
        console.error('Erreur suppression:', error);
        showNotification('Erreur lors de la suppression', 'error');
    });
}

// ===== NOTIFICATIONS =====
function setupNotifications() {
    // Créer le conteneur de notifications
    const notificationContainer = document.createElement('div');
    notificationContainer.id = 'notification-container';
    notificationContainer.className = 'notification-container';
    document.body.appendChild(notificationContainer);
    
    // Styles pour le conteneur
    const style = document.createElement('style');
    style.textContent = `
        .notification-container {
            position: fixed;
            top: 80px;
            right: 20px;
            z-index: 9999;
            max-width: 400px;
        }
        .notification {
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            margin-bottom: 10px;
            padding: 15px 20px;
            border-left: 4px solid #0d4786;
            animation: slideInRight 0.3s ease-out;
            max-width: 400px;
        }
        .notification.success { border-left-color: #28a745; }
        .notification.error { border-left-color: #dc3545; }
        .notification.warning { border-left-color: #ffc107; }
        .notification.info { border-left-color: #17a2b8; }
        .notification-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 5px;
        }
        .notification-title {
            font-weight: 600;
            color: #333;
            margin: 0;
        }
        .notification-close {
            background: none;
            border: none;
            font-size: 18px;
            cursor: pointer;
            color: #666;
            padding: 0;
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .notification-message {
            color: #666;
            margin: 0;
            font-size: 14px;
        }
        @keyframes slideInRight {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
    `;
    document.head.appendChild(style);
}

function showNotification(message, type = 'info', title = null) {
    const container = document.getElementById('notification-container');
    if (!container) return;
    
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    
    const header = document.createElement('div');
    header.className = 'notification-header';
    
    const notificationTitle = document.createElement('h6');
    notificationTitle.className = 'notification-title';
    notificationTitle.textContent = title || getNotificationTitle(type);
    
    const closeBtn = document.createElement('button');
    closeBtn.className = 'notification-close';
    closeBtn.innerHTML = '×';
    closeBtn.onclick = () => notification.remove();
    
    header.appendChild(notificationTitle);
    header.appendChild(closeBtn);
    
    const messageDiv = document.createElement('p');
    messageDiv.className = 'notification-message';
    messageDiv.textContent = message;
    
    notification.appendChild(header);
    notification.appendChild(messageDiv);
    
    container.appendChild(notification);
    
    // Auto-remove après 5 secondes
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

function getNotificationTitle(type) {
    const titles = {
        'success': 'Succès',
        'error': 'Erreur',
        'warning': 'Attention',
        'info': 'Information'
    };
    return titles[type] || 'Information';
}

// ===== UTILITAIRES =====
function getCSRFToken() {
    const token = document.querySelector('meta[name="csrf-token"]');
    return token ? token.getAttribute('content') : '';
}

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

function handleKeyboardShortcuts(e) {
    // Ctrl/Cmd + S pour sauvegarder
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        const activeForm = document.querySelector('form:focus-within');
        if (activeForm) {
            activeForm.submit();
        }
    }
    
    // Ctrl/Cmd + K pour rechercher
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('input[type="search"], .search-input');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    // Échap pour fermer les modals
    if (e.key === 'Escape') {
        const openModal = document.querySelector('.modal.show');
        if (openModal) {
            const modal = bootstrap.Modal.getInstance(openModal);
            if (modal) modal.hide();
        }
    }
}

// ===== USER DATA =====
function loadUserData() {
    // Charger les données utilisateur depuis l'API
    fetch('/users/api/profile/', {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        currentUser = data;
        updateUserInterface();
    })
    .catch(error => {
        console.error('Erreur chargement profil:', error);
    });
}

function updateUserInterface() {
    if (!currentUser || !currentUser.user) return;
    
    const user = currentUser.user;
    
    // Mettre à jour l'affichage du nom d'utilisateur
    const userNameElements = document.querySelectorAll('.user-name');
    userNameElements.forEach(element => {
        const fullName = user.first_name && user.last_name ? 
            `${user.first_name} ${user.last_name}` : user.username;
        element.textContent = fullName;
    });
    
    // Mettre à jour l'avatar si disponible
    const avatarElements = document.querySelectorAll('.user-avatar');
    avatarElements.forEach(element => {
        if (user.profile && user.profile.avatar) {
            element.src = user.profile.avatar;
        }
    });
}

// ===== EXPORT FUNCTIONS =====
// Rendre les fonctions disponibles globalement
window.AdminInterface = {
    showNotification,
    toggleSidebar,
    deleteItem,
    validateForm,
    handleFileUpload
};

// ===== GLOBAL ERROR HANDLER =====
window.addEventListener('error', function(e) {
    console.error('Erreur JavaScript:', e.error);
    showNotification('Une erreur est survenue', 'error');
});

// ===== AJAX SETUP =====
// Configurer les en-têtes CSRF pour toutes les requêtes AJAX
document.addEventListener('DOMContentLoaded', function() {
    const token = getCSRFToken();
    if (token) {
        // Pour jQuery si utilisé
        if (typeof $ !== 'undefined') {
            $.ajaxSetup({
                beforeSend: function(xhr) {
                    xhr.setRequestHeader('X-CSRFToken', token);
                }
            });
        }
    }
});
