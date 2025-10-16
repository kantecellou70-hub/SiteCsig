// Configuration personnalisée pour CKEditor5
window.CKEditorConfig = {
    // Configuration pour le contenu des blogs
    blog_content: {
        toolbar: {
            items: [
                'heading', '|',
                'bold', 'italic', 'underline', 'strikethrough', '|',
                'link', '|',
                'bulletedList', 'numberedList', '|',
                'indent', 'outdent', '|',
                'blockQuote', 'insertTable', '|',
                'undo', 'redo'
            ]
        },
        language: 'fr',
        placeholder: 'Commencez à écrire votre contenu...',
        heading: {
            options: [
                { model: 'paragraph', title: 'Paragraphe', class: 'ck-heading_paragraph' },
                { model: 'heading1', view: 'h1', title: 'Titre 1', class: 'ck-heading_heading1' },
                { model: 'heading2', view: 'h2', title: 'Titre 2', class: 'ck-heading_heading2' },
                { model: 'heading3', view: 'h3', title: 'Titre 3', class: 'ck-heading_heading3' },
                { model: 'heading4', view: 'h4', title: 'Titre 4', class: 'ck-heading_heading4' }
            ]
        },
        table: {
            contentToolbar: [
                'tableColumn',
                'tableRow',
                'mergeTableCells'
            ]
        },
        link: {
            addTargetToExternalLinks: true,
            defaultProtocol: 'https://'
        }
    }
};

// Fonction d'initialisation automatique de CKEditor5
function initCKEditor(fieldId, configName = 'blog_content') {
    const field = document.querySelector(fieldId);
    if (field && window.ClassicEditor) {
        const config = window.CKEditorConfig[configName] || window.CKEditorConfig.blog_content;
        
        ClassicEditor
            .create(field, config)
            .then(editor => {
                console.log('CKEditor5 initialisé avec succès pour:', fieldId);
                
                // Ajouter des classes CSS pour le style
                editor.ui.view.element.classList.add('ckeditor-container');
                
                // Gérer la soumission du formulaire
                const form = field.closest('form');
                if (form) {
                    form.addEventListener('submit', function() {
                        // Mettre à jour la valeur du champ avant soumission
                        field.value = editor.getData();
                    });
                }
            })
            .catch(error => {
                console.error('Erreur lors de l\'initialisation de CKEditor5:', error);
                // Fallback : afficher un message d'erreur
                const errorDiv = document.createElement('div');
                errorDiv.className = 'alert alert-warning';
                errorDiv.innerHTML = '<i class="fas fa-exclamation-triangle me-2"></i>L\'éditeur riche n\'a pas pu être chargé. Utilisez le champ de texte simple.';
                field.parentNode.insertBefore(errorDiv, field.nextSibling);
            });
    }
}

// Initialisation automatique au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    // Initialiser tous les champs CKEditor5
    const ckeditorFields = document.querySelectorAll('.ckeditor5');
    ckeditorFields.forEach(field => {
        initCKEditor('#' + field.id);
    });
});
