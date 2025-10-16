/**
 * CSIG - Authentication JavaScript
 * Gestion des interactions pour les pages d'authentification
 */

// Attendre que le DOM soit chargé
document.addEventListener('DOMContentLoaded', function() {
    
    // Initialiser toutes les fonctionnalités d'authentification
    initAuthForms();
    initPasswordToggle();
    initFormValidation();
    initDemoLogin();
    initAutoFocus();
    initEnterKeyNavigation();
    initFormSubmission();
    initAccessibility();
    initAnimations();
});

/**
 * Initialisation des formulaires d'authentification
 */
function initAuthForms() {
    const forms = document.querySelectorAll('.auth-form');
    
    forms.forEach(form => {
        // Ajouter des classes Bootstrap aux champs
        const inputs = form.querySelectorAll('input');
        inputs.forEach(input => {
            input.classList.add('form-control');
            
            // Ajouter des attributs d'accessibilité
            if (input.type === 'password') {
                input.setAttribute('autocomplete', 'current-password');
            } else if (input.type === 'text' && input.name === 'username') {
                input.setAttribute('autocomplete', 'username');
            } else if (input.type === 'email') {
                input.setAttribute('autocomplete', 'email');
            }
        });
        
        // Gérer la soumission du formulaire
        form.addEventListener('submit', handleFormSubmission);
    });
}

/**
 * Gestion de la soumission des formulaires
 */
function handleFormSubmission(e) {
    const form = e.target;
    const submitBtn = form.querySelector('.auth-submit-btn');
    
    if (submitBtn) {
        // Afficher l'état de chargement
        showLoadingState(submitBtn);
        
        // Valider le formulaire
        if (!validateForm(form)) {
            e.preventDefault();
            hideLoadingState(submitBtn);
            showFormErrors(form);
            return false;
        }
        
        // Le formulaire est valide, continuer la soumission
        return true;
    }
}

/**
 * Afficher l'état de chargement
 */
function showLoadingState(submitBtn) {
    const spinner = submitBtn.querySelector('.spinner-border');
    const btnText = submitBtn.querySelector('span:not(.spinner-border)');
    
    if (spinner && btnText) {
        submitBtn.disabled = true;
        spinner.classList.remove('d-none');
        btnText.classList.add('d-none');
    }
}

/**
 * Masquer l'état de chargement
 */
function hideLoadingState(submitBtn) {
    const spinner = submitBtn.querySelector('.spinner-border');
    const btnText = submitBtn.querySelector('span:not(.spinner-border)');
    
    if (spinner && btnText) {
        submitBtn.disabled = false;
        spinner.classList.add('d-none');
        btnText.classList.remove('d-none');
    }
}

/**
 * Validation des formulaires
 */
function initFormValidation() {
    const forms = document.querySelectorAll('.auth-form[data-validate]');
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input[required]');
        
        inputs.forEach(input => {
            // Validation en temps réel
            input.addEventListener('blur', function() {
                validateField(this);
            });
            
            input.addEventListener('input', function() {
                clearFieldValidation(this);
            });
        });
    });
}

/**
 * Valider un champ spécifique
 */
function validateField(field) {
    const value = field.value.trim();
    let isValid = true;
    let errorMessage = '';
    
    // Vérifier si le champ est requis
    if (field.hasAttribute('required') && !value) {
        isValid = false;
        errorMessage = 'Ce champ est requis';
    }
    
    // Validation spécifique selon le type
    if (isValid && value) {
        switch (field.type) {
            case 'email':
                if (!isValidEmail(value)) {
                    isValid = false;
                    errorMessage = 'Format d\'email invalide';
                }
                break;
            case 'password':
                if (field.name === 'new_password' && value.length < 8) {
                    isValid = false;
                    errorMessage = 'Le mot de passe doit contenir au moins 8 caractères';
                }
                break;
        }
    }
    
    // Appliquer la validation
    if (isValid) {
        markFieldAsValid(field);
    } else {
        markFieldAsInvalid(field, errorMessage);
    }
    
    return isValid;
}

/**
 * Marquer un champ comme valide
 */
function markFieldAsValid(field) {
    field.classList.remove('is-invalid');
    field.classList.add('is-valid');
    
    // Supprimer les messages d'erreur
    const errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.remove();
    }
}

/**
 * Marquer un champ comme invalide
 */
function markFieldAsInvalid(field, message) {
    field.classList.remove('is-valid');
    field.classList.add('is-invalid');
    
    // Supprimer l'ancien message d'erreur
    const existingError = field.parentNode.querySelector('.invalid-feedback');
    if (existingError) {
        existingError.remove();
    }
    
    // Ajouter le nouveau message d'erreur
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.innerHTML = `<i class="fas fa-exclamation-circle me-1"></i>${message}`;
    
    // Insérer après le groupe d'input
    const inputGroup = field.closest('.input-group') || field.parentNode;
    inputGroup.parentNode.insertBefore(errorDiv, inputGroup.nextSibling);
}

/**
 * Effacer la validation d'un champ
 */
function clearFieldValidation(field) {
    field.classList.remove('is-valid', 'is-invalid');
    
    // Supprimer les messages de validation
    const errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.remove();
    }
    
    const validDiv = field.parentNode.querySelector('.valid-feedback');
    if (validDiv) {
        validDiv.remove();
    }
}

/**
 * Valider un formulaire complet
 */
function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('input[required]');
    
    requiredFields.forEach(field => {
        if (!validateField(field)) {
            isValid = false;
        }
    });
    
    return isValid;
}

/**
 * Afficher les erreurs du formulaire
 */
function showFormErrors(form) {
    const firstInvalidField = form.querySelector('.is-invalid');
    if (firstInvalidField) {
        firstInvalidField.focus();
        firstInvalidField.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

/**
 * Toggle de visibilité du mot de passe
 */
function initPasswordToggle() {
    const toggleBtns = document.querySelectorAll('#togglePassword');
    
    toggleBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const passwordField = this.parentNode.querySelector('input[type="password"], input[type="text"]');
            const icon = this.querySelector('i');
            
            if (passwordField.type === 'password') {
                passwordField.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
                this.setAttribute('title', 'Masquer le mot de passe');
            } else {
                passwordField.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
                this.setAttribute('title', 'Afficher le mot de passe');
            }
        });
    });
}

/**
 * Connexion démo
 */
function initDemoLogin() {
    const demoBtn = document.getElementById('demoLogin');
    const confirmBtn = document.getElementById('confirmDemoLogin');
    
    if (demoBtn) {
        demoBtn.addEventListener('click', function() {
            // Afficher la modal de confirmation
            const modal = new bootstrap.Modal(document.getElementById('demoLoginModal'));
            modal.show();
        });
    }
    
    if (confirmBtn) {
        confirmBtn.addEventListener('click', function() {
            // Remplir automatiquement les champs
            const usernameField = document.querySelector('input[name="username"]');
            const passwordField = document.querySelector('input[name="password"]');
            
            if (usernameField && passwordField) {
                usernameField.value = 'demo';
                passwordField.value = 'demo123';
                
                // Marquer les champs comme valides
                markFieldAsValid(usernameField);
                markFieldAsValid(passwordField);
                
                // Fermer la modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('demoLoginModal'));
                modal.hide();
                
                // Soumettre le formulaire
                const form = document.querySelector('.auth-form');
                if (form) {
                    form.submit();
                }
            }
        });
    }
}

/**
 * Auto-focus sur le premier champ
 */
function initAutoFocus() {
    const firstInput = document.querySelector('.auth-form input:not([type="hidden"])');
    if (firstInput) {
        // Délai pour assurer que la page est chargée
        setTimeout(() => {
            firstInput.focus();
        }, 100);
    }
}

/**
 * Navigation avec la touche Entrée
 */
function initEnterKeyNavigation() {
    const forms = document.querySelectorAll('.auth-form');
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input:not([type="hidden"])');
        
        inputs.forEach((input, index) => {
            input.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    
                    if (index < inputs.length - 1) {
                        // Aller au champ suivant
                        inputs[index + 1].focus();
                    } else {
                        // Soumettre le formulaire
                        form.submit();
                    }
                }
            });
        });
    });
}

/**
 * Gestion de la soumission des formulaires
 */
function initFormSubmission() {
    const forms = document.querySelectorAll('.auth-form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('.auth-submit-btn');
            
            if (submitBtn && !submitBtn.disabled) {
                // Désactiver le bouton pour éviter la double soumission
                submitBtn.disabled = true;
                
                // Ajouter une classe pour l'état de soumission
                this.classList.add('is-submitting');
            }
        });
    });
}

/**
 * Accessibilité
 */
function initAccessibility() {
    // Ajouter des attributs ARIA
    const forms = document.querySelectorAll('.auth-form');
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input');
        
        inputs.forEach((input, index) => {
            // Ajouter des labels explicites
            if (!input.id) {
                input.id = `field_${index}`;
            }
            
            // Ajouter des attributs ARIA
            input.setAttribute('aria-describedby', `help_${input.id}`);
            
            // Créer des messages d'aide
            const helpDiv = document.createElement('div');
            helpDiv.id = `help_${input.id}`;
            helpDiv.className = 'form-text text-muted';
            helpDiv.style.display = 'none';
            
            // Ajouter le message d'aide après le champ
            const inputGroup = input.closest('.input-group') || input.parentNode;
            inputGroup.parentNode.insertBefore(helpDiv, inputGroup.nextSibling);
        });
    });
    
    // Gestion du focus pour l'accessibilité
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Tab') {
            // Ajouter une classe pour indiquer la navigation au clavier
            document.body.classList.add('keyboard-navigation');
        }
    });
    
    document.addEventListener('mousedown', function() {
        // Retirer la classe lors de l'utilisation de la souris
        document.body.classList.remove('keyboard-navigation');
    });
}

/**
 * Animations
 */
function initAnimations() {
    // Animation d'entrée pour les éléments
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);
    
    // Observer les éléments à animer
    const animatedElements = document.querySelectorAll('.auth-card, .auth-logo-section');
    animatedElements.forEach(el => {
        observer.observe(el);
    });
}

/**
 * Validation email
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Validation téléphone
 */
function isValidPhone(phone) {
    const phoneRegex = /^[\+]?[0-9\s\-\(\)]{8,}$/;
    return phoneRegex.test(phone);
}

/**
 * Afficher une notification
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.innerHTML = `
        <i class="fas fa-${getNotificationIcon(type)} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Ajouter à la page
    const container = document.querySelector('.messages-container') || document.body;
    container.appendChild(notification);
    
    // Auto-fermeture après 5 secondes
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

/**
 * Obtenir l'icône pour le type de notification
 */
function getNotificationIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

/**
 * Gestion des erreurs AJAX
 */
function handleAjaxError(xhr, status, error) {
    console.error('AJAX Error:', status, error);
    
    let message = 'Une erreur est survenue. Veuillez réessayer.';
    
    if (xhr.responseJSON && xhr.responseJSON.message) {
        message = xhr.responseJSON.message;
    } else if (xhr.status === 404) {
        message = 'Ressource non trouvée.';
    } else if (xhr.status === 500) {
        message = 'Erreur serveur. Veuillez réessayer plus tard.';
    }
    
    showNotification(message, 'error');
}

/**
 * Gestion des cookies
 */
function setCookie(name, value, days) {
    let expires = '';
    if (days) {
        const date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = '; expires=' + date.toUTCString();
    }
    document.cookie = name + '=' + value + expires + '; path=/';
}

function getCookie(name) {
    const nameEQ = name + '=';
    const ca = document.cookie.split(';');
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) === ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
}

/**
 * Gestion du thème
 */
function initThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    const currentTheme = getCookie('theme') || 'light';
    
    // Appliquer le thème actuel
    document.body.setAttribute('data-theme', currentTheme);
    
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const currentTheme = document.body.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            
            document.body.setAttribute('data-theme', newTheme);
            setCookie('theme', newTheme, 365);
            
            // Mettre à jour l'icône
            const icon = this.querySelector('i');
            if (icon) {
                icon.className = newTheme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
            }
        });
    }
}

// Initialiser le thème au chargement
initThemeToggle();
