/**
 * CSIG - Main JavaScript File
 * Gestion des interactions et animations du site
 */

// Attendre que le DOM soit chargé
document.addEventListener('DOMContentLoaded', function() {
    
    // Initialiser toutes les fonctionnalités
    initAnimations();
    initFormValidation();
    initImageGallery();
    initSearchFunctionality();
    initNewsletterSubscription();
    initBackToTop();
    initMobileMenu();
    initCarousel();
    initLazyLoading();
    initScrollEffects();
});

/**
 * Initialisation des animations AOS
 */
function initAnimations() {
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 800,
            easing: 'ease-in-out',
            once: true,
            offset: 100,
            delay: 100
        });
    }
}

/**
 * Validation des formulaires
 */
function initFormValidation() {
    const forms = document.querySelectorAll('form[data-validate]');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                showNotification('Veuillez corriger les erreurs dans le formulaire', 'error');
            }
        });
    });
}

/**
 * Validation d'un formulaire
 */
function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            markFieldAsInvalid(field, 'Ce champ est requis');
            isValid = false;
        } else {
            markFieldAsValid(field);
        }
        
        // Validation email
        if (field.type === 'email' && field.value) {
            if (!isValidEmail(field.value)) {
                markFieldAsInvalid(field, 'Email invalide');
                isValid = false;
            }
        }
        
        // Validation téléphone
        if (field.name === 'phone' && field.value) {
            if (!isValidPhone(field.value)) {
                markFieldAsInvalid(field, 'Numéro de téléphone invalide');
                isValid = false;
            }
        }
    });
    
    return isValid;
}

/**
 * Marquer un champ comme invalide
 */
function markFieldAsInvalid(field, message) {
    field.classList.add('is-invalid');
    field.classList.remove('is-valid');
    
    // Supprimer l'ancien message d'erreur
    const existingError = field.parentNode.querySelector('.invalid-feedback');
    if (existingError) {
        existingError.remove();
    }
    
    // Ajouter le nouveau message d'erreur
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    field.parentNode.appendChild(errorDiv);
}

/**
 * Marquer un champ comme valide
 */
function markFieldAsValid(field) {
    field.classList.remove('is-invalid');
    field.classList.add('is-valid');
    
    // Supprimer le message d'erreur
    const existingError = field.parentNode.querySelector('.invalid-feedback');
    if (existingError) {
        existingError.remove();
    }
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
 * Galerie d'images
 */
function initImageGallery() {
    const imageGalleries = document.querySelectorAll('.image-gallery');
    
    imageGalleries.forEach(gallery => {
        const images = gallery.querySelectorAll('img');
        const lightbox = createLightbox();
        
        images.forEach(img => {
            img.addEventListener('click', function() {
                openLightbox(this.src, this.alt);
            });
        });
    });
}

/**
 * Créer la lightbox
 */
function createLightbox() {
    const lightbox = document.createElement('div');
    lightbox.className = 'lightbox';
    lightbox.innerHTML = `
        <div class="lightbox-content">
            <span class="lightbox-close">&times;</span>
            <img class="lightbox-image" src="" alt="">
            <div class="lightbox-caption"></div>
        </div>
    `;
    
    document.body.appendChild(lightbox);
    
    // Fermer la lightbox
    lightbox.addEventListener('click', function(e) {
        if (e.target === lightbox || e.target.classList.contains('lightbox-close')) {
            closeLightbox();
        }
    });
    
    return lightbox;
}

/**
 * Ouvrir la lightbox
 */
function openLightbox(src, alt) {
    const lightbox = document.querySelector('.lightbox');
    const image = lightbox.querySelector('.lightbox-image');
    const caption = lightbox.querySelector('.lightbox-caption');
    
    image.src = src;
    caption.textContent = alt;
    lightbox.classList.add('active');
    document.body.style.overflow = 'hidden';
}

/**
 * Fermer la lightbox
 */
function closeLightbox() {
    const lightbox = document.querySelector('.lightbox');
    lightbox.classList.remove('active');
    document.body.style.overflow = '';
}

/**
 * Fonctionnalité de recherche
 */
function initSearchFunctionality() {
    const searchForm = document.querySelector('.search-form');
    const searchInput = document.querySelector('.search-input');
    const searchResults = document.querySelector('.search-results');
    
    if (searchForm && searchInput) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            
            if (query.length >= 2) {
                searchTimeout = setTimeout(() => {
                    performSearch(query);
                }, 300);
            } else {
                hideSearchResults();
            }
        });
        
        // Fermer les résultats en cliquant ailleurs
        document.addEventListener('click', function(e) {
            if (!searchForm.contains(e.target)) {
                hideSearchResults();
            }
        });
    }
}

/**
 * Effectuer la recherche
 */
function performSearch(query) {
    // Simulation de recherche - à remplacer par une vraie API
    const results = [
        { type: 'article', title: 'Article sur ' + query, url: '/articles/article-1' },
        { type: 'event', title: 'Événement ' + query, url: '/events/event-1' },
        { type: 'project', title: 'Projet ' + query, url: '/projects/project-1' }
    ];
    
    displaySearchResults(results);
}

/**
 * Afficher les résultats de recherche
 */
function displaySearchResults(results) {
    const searchResults = document.querySelector('.search-results');
    if (!searchResults) return;
    
    if (results.length === 0) {
        searchResults.innerHTML = '<div class="no-results">Aucun résultat trouvé</div>';
    } else {
        const resultsHTML = results.map(result => `
            <a href="${result.url}" class="search-result-item">
                <i class="fas fa-${getResultIcon(result.type)}"></i>
                <span>${result.title}</span>
            </a>
        `).join('');
        
        searchResults.innerHTML = resultsHTML;
    }
    
    searchResults.classList.add('active');
}

/**
 * Obtenir l'icône pour le type de résultat
 */
function getResultIcon(type) {
    const icons = {
        article: 'newspaper',
        event: 'calendar',
        project: 'project-diagram',
        program: 'graduation-cap'
    };
    return icons[type] || 'search';
}

/**
 * Masquer les résultats de recherche
 */
function hideSearchResults() {
    const searchResults = document.querySelector('.search-results');
    if (searchResults) {
        searchResults.classList.remove('active');
    }
}

/**
 * Inscription à la newsletter
 */
function initNewsletterSubscription() {
    const newsletterForms = document.querySelectorAll('.newsletter-form');
    
    newsletterForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const email = this.querySelector('input[name="email"]').value;
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            
            // Afficher le chargement
            submitBtn.innerHTML = '<span class="loading"></span> Envoi...';
            submitBtn.disabled = true;
            
            // Simulation d'envoi - à remplacer par une vraie API
            setTimeout(() => {
                showNotification('Inscription réussie à la newsletter !', 'success');
                form.reset();
                
                // Restaurer le bouton
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }, 2000);
        });
    });
}

/**
 * Bouton retour en haut
 */
function initBackToTop() {
    const backToTopBtn = document.getElementById('backToTop');
    
    if (backToTopBtn) {
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                backToTopBtn.style.display = 'block';
            } else {
                backToTopBtn.style.display = 'none';
            }
        });
        
        backToTopBtn.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
}

/**
 * Menu mobile
 */
function initMobileMenu() {
    const mobileMenuToggle = document.querySelector('.navbar-toggler');
    const mobileMenu = document.querySelector('.navbar-collapse');
    
    if (mobileMenuToggle && mobileMenu) {
        mobileMenuToggle.addEventListener('click', function() {
            mobileMenu.classList.toggle('show');
        });
        
        // Fermer le menu en cliquant sur un lien
        const mobileLinks = mobileMenu.querySelectorAll('.nav-link');
        mobileLinks.forEach(link => {
            link.addEventListener('click', function() {
                mobileMenu.classList.remove('show');
            });
        });
    }
}

/**
 * Carousel automatique
 */
function initCarousel() {
    const carousels = document.querySelectorAll('.carousel');
    
    carousels.forEach(carousel => {
        const slides = carousel.querySelectorAll('.carousel-item');
        let currentSlide = 0;
        
        if (slides.length > 1) {
            setInterval(() => {
                slides[currentSlide].classList.remove('active');
                currentSlide = (currentSlide + 1) % slides.length;
                slides[currentSlide].classList.add('active');
            }, 5000);
        }
    });
}

/**
 * Chargement différé des images
 */
function initLazyLoading() {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        const lazyImages = document.querySelectorAll('img[data-src]');
        lazyImages.forEach(img => imageObserver.observe(img));
    }
}

/**
 * Effets de défilement
 */
function initScrollEffects() {
    const scrollElements = document.querySelectorAll('[data-scroll-effect]');
    
    if ('IntersectionObserver' in window) {
        const scrollObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const element = entry.target;
                    const effect = element.dataset.scrollEffect;
                    
                    switch (effect) {
                        case 'fade-in':
                            element.classList.add('fade-in');
                            break;
                        case 'slide-up':
                            element.classList.add('slide-up');
                            break;
                        case 'scale-in':
                            element.classList.add('scale-in');
                            break;
                    }
                }
            });
        });
        
        scrollElements.forEach(element => scrollObserver.observe(element));
    }
}

/**
 * Afficher une notification
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-message">${message}</span>
            <button class="notification-close">&times;</button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Afficher la notification
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    // Fermer automatiquement après 5 secondes
    setTimeout(() => {
        hideNotification(notification);
    }, 5000);
    
    // Fermer en cliquant sur le bouton
    const closeBtn = notification.querySelector('.notification-close');
    closeBtn.addEventListener('click', () => {
        hideNotification(notification);
    });
}

/**
 * Masquer une notification
 */
function hideNotification(notification) {
    notification.classList.remove('show');
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 300);
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
 * Formatage des dates
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    const options = { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    
    return date.toLocaleDateString('fr-FR', options);
}

/**
 * Formatage des nombres
 */
function formatNumber(number) {
    return new Intl.NumberFormat('fr-FR').format(number);
}

/**
 * Copier dans le presse-papiers
 */
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showNotification('Copié dans le presse-papiers !', 'success');
        }).catch(() => {
            showNotification('Erreur lors de la copie', 'error');
        });
    } else {
        // Fallback pour les navigateurs plus anciens
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showNotification('Copié dans le presse-papiers !', 'success');
    }
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
 * Gestion du thème sombre/clair
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
            icon.className = newTheme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
        });
    }
}

// Initialiser le thème au chargement
initThemeToggle();
