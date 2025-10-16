/**
 * Content Management JavaScript
 * Gestion des fonctionnalités de l'interface de gestion de contenu
 */

// Variables globales
let currentDeleteId = null;
let deleteModal = null;

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    // Initialiser les fonctionnalités
    initSearchAndFilters();
    initBulkActions();
    initCheckboxes();
    initImageManagement();
    initCharacterCounters();
    
    // Initialiser les modals Bootstrap si disponibles
    if (typeof bootstrap !== 'undefined') {
        deleteModal = new bootstrap.Modal(document.getElementById('deleteModal'));
    }
});

// ========================================
// GESTION DE LA RECHERCHE ET DES FILTRES
// ========================================

function initSearchAndFilters() {
    const searchInput = document.getElementById('searchInput');
    const categoryFilter = document.getElementById('categoryFilter');
    const statusFilter = document.getElementById('statusFilter');
    const authorFilter = document.getElementById('authorFilter');
    
    if (!searchInput) return;
    
    // Recherche en temps réel
    let searchTimeout;
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            filterArticles();
        }, 300);
    });
    
    // Filtres
    [categoryFilter, statusFilter, authorFilter].forEach(filter => {
        if (filter) {
            filter.addEventListener('change', filterArticles);
        }
    });
}

function filterArticles() {
    const searchTerm = document.getElementById('searchInput')?.value.toLowerCase() || '';
    const category = document.getElementById('categoryFilter')?.value || '';
    const status = document.getElementById('statusFilter')?.value || '';
    const author = document.getElementById('authorFilter')?.value || '';
    
    const rows = document.querySelectorAll('#articlesTable tbody tr[data-article-id]');
    
    rows.forEach(row => {
        let show = true;
        
        // Recherche dans le titre et l'extrait
        if (searchTerm) {
            const title = row.querySelector('.article-title')?.textContent.toLowerCase() || '';
            const excerpt = row.querySelector('.article-excerpt')?.textContent.toLowerCase() || '';
            if (!title.includes(searchTerm) && !excerpt.includes(searchTerm)) {
                show = false;
            }
        }
        
        // Filtre par catégorie
        if (category) {
            const categoryElement = row.querySelector('.badge');
            if (categoryElement && categoryElement.textContent.trim() !== category) {
                show = false;
            }
        }
        
        // Filtre par statut
        if (status && row.dataset.status !== status) {
            show = false;
        }
        
        // Filtre par auteur
        if (author) {
            const authorName = row.querySelector('td:nth-child(4) span')?.textContent.trim() || '';
            if (authorName !== author) {
                show = false;
            }
        }
        
        row.style.display = show ? '' : 'none';
    });
    
    updateEmptyState();
}

function updateEmptyState() {
    const visibleRows = document.querySelectorAll('#articlesTable tbody tr[data-article-id]:not([style*="display: none"])');
    const emptyRow = document.querySelector('#articlesTable tbody tr:not([data-article-id])');
    
    if (visibleRows.length === 0 && emptyRow) {
        emptyRow.style.display = '';
        const emptyStateText = emptyRow.querySelector('.empty-state p');
        if (emptyStateText) {
            emptyStateText.textContent = 'Aucun article ne correspond à vos critères de recherche.';
        }
    } else if (emptyRow) {
        emptyRow.style.display = 'none';
    }
}

// ========================================
// ACTIONS EN LOT
// ========================================

function initBulkActions() {
    const bulkActionSelect = document.getElementById('bulkAction');
    const applyButton = document.getElementById('applyBulkAction');
    
    if (!bulkActionSelect || !applyButton) return;
    
    bulkActionSelect.addEventListener('change', function() {
        applyButton.disabled = !this.value;
    });
    
    applyButton.addEventListener('click', function() {
        const action = bulkActionSelect.value;
        const selectedIds = getSelectedArticleIds();
        
        if (selectedIds.length === 0) {
            showNotification('Veuillez sélectionner au moins un article.', 'warning');
            return;
        }
        
        if (confirm(`Êtes-vous sûr de vouloir ${getActionText(action)} ${selectedIds.length} article(s) ?`)) {
            executeBulkAction(action, selectedIds);
        }
    });
}

function getActionText(action) {
    const actions = {
        'publish': 'publier',
        'draft': 'mettre en brouillon',
        'trash': 'mettre à la corbeille',
        'delete': 'supprimer définitivement',
        'feature': 'mettre en avant',
        'unfeature': 'retirer de la une'
    };
    return actions[action] || action;
}

function executeBulkAction(action, articleIds) {
    const formData = new FormData();
    formData.append('action', action);
    formData.append('article_ids', JSON.stringify(articleIds));
    
    // Afficher un indicateur de chargement
    const applyBtn = document.getElementById('applyBulkAction');
    const originalText = applyBtn.innerHTML;
    applyBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Traitement...';
    applyBtn.disabled = true;
    
    fetch('/content-management/bulk-article-action/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(data.message, 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            showNotification(data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        showNotification('Erreur lors de l\'exécution de l\'action', 'error');
    })
    .finally(() => {
        // Restaurer le bouton
        applyBtn.innerHTML = originalText;
        applyBtn.disabled = false;
    });
}

// ========================================
// GESTION DES CASES À COCHER
// ========================================

function initCheckboxes() {
    const headerCheckbox = document.getElementById('headerCheckbox');
    const articleCheckboxes = document.querySelectorAll('.article-checkbox');
    const selectAllCheckbox = document.getElementById('selectAll');
    
    // Case à cocher de l'en-tête
    if (headerCheckbox) {
        headerCheckbox.addEventListener('change', function() {
            articleCheckboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
            if (selectAllCheckbox) selectAllCheckbox.checked = this.checked;
            updateBulkActionButton();
        });
    }
    
    // Cases à cocher des articles
    articleCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            updateHeaderCheckbox();
            updateBulkActionButton();
        });
    });
    
    // Case à cocher "Sélectionner tout"
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            articleCheckboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
            if (headerCheckbox) headerCheckbox.checked = this.checked;
            updateBulkActionButton();
        });
    }
}

function updateHeaderCheckbox() {
    const headerCheckbox = document.getElementById('headerCheckbox');
    const articleCheckboxes = document.querySelectorAll('.article-checkbox');
    const checkedCount = document.querySelectorAll('.article-checkbox:checked').length;
    
    if (!headerCheckbox) return;
    
    if (checkedCount === 0) {
        headerCheckbox.indeterminate = false;
        headerCheckbox.checked = false;
    } else if (checkedCount === articleCheckboxes.length) {
        headerCheckbox.indeterminate = false;
        headerCheckbox.checked = true;
    } else {
        headerCheckbox.indeterminate = true;
        headerCheckbox.checked = false;
    }
}

function updateBulkActionButton() {
    const selectedIds = getSelectedArticleIds();
    const applyButton = document.getElementById('applyBulkAction');
    const bulkActionSelect = document.getElementById('bulkAction');
    
    if (applyButton) {
        applyButton.disabled = selectedIds.length === 0 || !bulkActionSelect?.value;
    }
}

function getSelectedArticleIds() {
    const checkboxes = document.querySelectorAll('.article-checkbox:checked');
    return Array.from(checkboxes).map(cb => cb.value);
}

// ========================================
// ACTIONS INDIVIDUELLES
// ========================================

function toggleFeature(articleId, featured) {
    const action = featured ? 'mettre en avant' : 'retirer de la une';
    
    if (confirm(`Êtes-vous sûr de vouloir ${action} cet article ?`)) {
        fetch('/content-management/toggle-feature/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                article_id: articleId,
                featured: featured
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(data.message, 'success');
                setTimeout(() => location.reload(), 1000);
            } else {
                showNotification(data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Erreur:', error);
            showNotification('Erreur lors de la modification', 'error');
        });
    }
}

function deleteArticle(articleId) {
    currentDeleteId = articleId;
    
    if (deleteModal) {
        deleteModal.show();
    } else {
        // Fallback si Bootstrap n'est pas disponible
        if (confirm('Êtes-vous sûr de vouloir supprimer cet article ?')) {
            confirmDelete();
        }
    }
}

function confirmDelete() {
    if (!currentDeleteId) return;
    
    fetch('/content-management/delete-article/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({
            article_id: currentDeleteId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(data.message, 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            showNotification(data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        showNotification('Erreur lors de la suppression', 'error');
    });
    
    if (deleteModal) {
        deleteModal.hide();
    }
    currentDeleteId = null;
}

// ========================================
// GESTION DES IMAGES
// ========================================

function initImageManagement() {
    const imageUploadArea = document.getElementById('imageUploadArea');
    const imageInput = document.getElementById('featured_image');
    
    if (!imageUploadArea || !imageInput) return;
    
    // Cacher l'input file
    imageInput.style.display = 'none';
    
    // Gestion du clic
    imageUploadArea.addEventListener('click', () => {
        imageInput.click();
    });
    
    // Gestion du drag & drop
    imageUploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        imageUploadArea.classList.add('dragover');
    });
    
    imageUploadArea.addEventListener('dragleave', () => {
        imageUploadArea.classList.remove('dragover');
    });
    
    imageUploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        imageUploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleImageFile(files[0]);
        }
    });
    
    // Gestion de la sélection de fichier
    imageInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleImageFile(e.target.files[0]);
        }
    });
}

function handleImageFile(file) {
    if (!file.type.startsWith('image/')) {
        showNotification('Veuillez sélectionner un fichier image valide.', 'error');
        return;
    }
    
    if (file.size > 5 * 1024 * 1024) {
        showNotification('L\'image ne doit pas dépasser 5MB.', 'error');
        return;
    }
    
    const reader = new FileReader();
    reader.onload = function(e) {
        showImagePreview(e.target.result);
        // Mettre à jour l'input file
        const imageInput = document.getElementById('featured_image');
        if (imageInput) {
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            imageInput.files = dataTransfer.files;
        }
    };
    reader.readAsDataURL(file);
}

function showImagePreview(src) {
    const previewContainer = document.getElementById('imagePreview');
    const previewImage = document.getElementById('previewImage');
    
    if (previewContainer && previewImage) {
        previewImage.src = src;
        previewContainer.style.display = 'block';
    }
}

function removeImage() {
    const previewContainer = document.getElementById('imagePreview');
    const imageInput = document.getElementById('featured_image');
    
    if (previewContainer) {
        previewContainer.style.display = 'none';
    }
    if (imageInput) {
        imageInput.value = '';
    }
}

// ========================================
// GESTION DES COMPTEURS DE CARACTÈRES
// ========================================

function initCharacterCounters() {
    const excerptField = document.getElementById('id_excerpt');
    const metaTitleField = document.getElementById('id_meta_title');
    const metaDescField = document.getElementById('id_meta_description');
    
    if (excerptField) {
        excerptField.addEventListener('input', function() {
            updateCharacterCount(this, 'excerpt');
        });
    }
    
    if (metaTitleField) {
        metaTitleField.addEventListener('input', function() {
            updateCharacterCount(this, 'metaTitle');
            updateSeoPreview('title', this.value);
        });
    }
    
    if (metaDescField) {
        metaDescField.addEventListener('input', function() {
            updateCharacterCount(this, 'metaDesc');
            updateSeoPreview('description', this.value);
        });
    }
    
    // Initialiser les compteurs
    if (excerptField) updateCharacterCount(excerptField, 'excerpt');
    if (metaTitleField) updateCharacterCount(metaTitleField, 'metaTitle');
    if (metaDescField) updateCharacterCount(metaDescField, 'metaDesc');
}

function updateCharacterCount(field, type) {
    const current = field.value.length;
    const max = type === 'excerpt' ? 500 : type === 'metaTitle' ? 60 : 160;
    const currentSpan = document.getElementById(type + 'Current');
    const countDiv = document.getElementById(type + 'Count');
    
    if (currentSpan) currentSpan.textContent = current;
    
    if (countDiv) {
        // Mettre à jour les classes CSS
        countDiv.classList.remove('warning', 'danger');
        if (current > max * 0.8 && current <= max * 0.95) {
            countDiv.classList.add('warning');
        } else if (current > max * 0.95) {
            countDiv.classList.add('danger');
        }
    }
}

// ========================================
// GESTION DE LA PRÉVISUALISATION SEO
// ========================================

function initSeoPreview() {
    const metaTitleField = document.getElementById('id_meta_title');
    const metaDescField = document.getElementById('id_meta_description');
    
    if (metaTitleField) {
        updateSeoPreview('title', metaTitleField.value);
    }
    if (metaDescField) {
        updateSeoPreview('description', metaDescField.value);
    }
}

function updateSeoPreview(type, value) {
    if (type === 'title') {
        const titlePreview = document.getElementById('seoTitlePreview');
        if (titlePreview) {
            titlePreview.textContent = value || 'Titre de l\'article';
        }
    } else if (type === 'description') {
        const descPreview = document.getElementById('seoDescPreview');
        if (descPreview) {
            descPreview.textContent = value || 'Description de l\'article pour les moteurs de recherche...';
        }
    }
}

// ========================================
// UTILITAIRES
// ========================================

function getCSRFToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : '';
}

function showNotification(message, type = 'info') {
    // Créer une notification personnalisée
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-fermeture après 5 secondes
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// ========================================
// GESTION DES ÉVÉNEMENTS
// ========================================

// Gestionnaire pour la confirmation de suppression
document.addEventListener('click', function(e) {
    if (e.target.id === 'confirmDelete') {
        confirmDelete();
    }
});

// Gestionnaire pour l'aperçu de l'article
function togglePreview() {
    const previewContent = document.getElementById('previewContent');
    const toggleBtn = document.querySelector('.preview-toggle i');
    
    if (previewContent && toggleBtn) {
        if (previewContent.classList.contains('show')) {
            previewContent.classList.remove('show');
            toggleBtn.className = 'fas fa-chevron-down me-2';
        } else {
            previewContent.classList.add('show');
            toggleBtn.className = 'fas fa-chevron-up me-2';
        }
    }
}

// Export des fonctions pour utilisation globale
window.contentManagement = {
    filterArticles,
    executeBulkAction,
    toggleFeature,
    deleteArticle,
    confirmDelete,
    togglePreview,
    showNotification
};
