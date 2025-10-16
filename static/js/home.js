/**
 * JavaScript spécifique à la page d'accueil CSIG
 * Gère les carousels, animations et interactions
 */

// Configuration des carousels
const homeConfig = {
    // Carousel principal (hero)
    hero: {
        slidesPerView: 1,
        spaceBetween: 0,
        loop: true,
        autoplay: {
            delay: 5000,
            disableOnInteraction: false,
        },
        pagination: {
            el: '.swiper-pagination',
            clickable: true,
        },
        navigation: {
            nextEl: '.swiper-button-next',
            prevEl: '.swiper-button-prev',
        },
        effect: 'fade',
        fadeEffect: {
            crossFade: true
        }
    },
    
    // Carousel des programmes
    programs: {
        slidesPerView: 1,
        spaceBetween: 20,
        loop: false,
        autoplay: false,
        pagination: {
            el: '.programs-pagination',
            clickable: true,
        },
        navigation: {
            nextEl: '.programs-next',
            prevEl: '.programs-prev',
        },
        breakpoints: {
            576: {
                slidesPerView: 2,
                spaceBetween: 20,
            },
            768: {
                slidesPerView: 3,
                spaceBetween: 30,
            },
            992: {
                slidesPerView: 4,
                spaceBetween: 30,
            }
        }
    },
    
    // Carousel des partenaires
    partners: {
        slidesPerView: 2,
        spaceBetween: 30,
        loop: true,
        autoplay: {
            delay: 3000,
            disableOnInteraction: false,
        },
        pagination: {
            el: '.partners-pagination',
            clickable: true,
        },
        navigation: {
            nextEl: '.partners-next',
            prevEl: '.partners-prev',
        },
        breakpoints: {
            576: {
                slidesPerView: 3,
                spaceBetween: 30,
            },
            768: {
                slidesPerView: 4,
                spaceBetween: 40,
            },
            992: {
                slidesPerView: 5,
                spaceBetween: 50,
            }
        }
    }
};

// Initialisation des carousels
function initHomeCarousels() {
    // Carousel principal (hero)
    const heroSwiper = new Swiper('.hero-swiper', homeConfig.hero);
    
    // Carousel des programmes
    const programsSwiper = new Swiper('.programs-swiper', homeConfig.programs);
    
    // Carousel des partenaires
    const partnersSwiper = new Swiper('.partners-swiper', homeConfig.partners);
    
    // Stocker les instances pour utilisation ultérieure
    window.homeSwipers = {
        hero: heroSwiper,
        programs: programsSwiper,
        partners: partnersSwiper
    };
    
    console.log('Carousels de la page d\'accueil initialisés');
}

// Animation des statistiques
function animateStats() {
    const stats = document.querySelectorAll('.stat-number');
    
    stats.forEach(stat => {
        const target = parseInt(stat.getAttribute('data-target') || '0');
        const duration = 2000; // 2 secondes
        const increment = target / (duration / 16); // 60 FPS
        let current = 0;
        
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            stat.textContent = Math.floor(current).toLocaleString();
        }, 16);
    });
}

// Animation des cartes au scroll
function initCardAnimations() {
    const cards = document.querySelectorAll('.program-card, .news-card, .event-card, .partner-item');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });
    
    cards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });
}

// Gestion des images de placeholder
function initImagePlaceholders() {
    const placeholders = document.querySelectorAll('.program-image-placeholder, .news-image-placeholder, .event-image-placeholder, .main-article-placeholder');
    
    placeholders.forEach(placeholder => {
        const parent = placeholder.closest('.program-image, .news-image, .event-image, .main-article-image');
        if (parent) {
            const img = parent.querySelector('img');
            if (img && img.complete && img.naturalWidth > 0) {
                placeholder.style.display = 'none';
            }
        }
    });
}

// Gestion des liens de navigation
function initNavigationLinks() {
    // Liens internes avec scroll smooth
    const internalLinks = document.querySelectorAll('a[href^="#"]');
    
    internalLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Liens externes avec ouverture dans un nouvel onglet
    const externalLinks = document.querySelectorAll('a[href^="http"]');
    
    externalLinks.forEach(link => {
        if (!link.hostname.includes(window.location.hostname)) {
            link.setAttribute('target', '_blank');
            link.setAttribute('rel', 'noopener noreferrer');
        }
    });
}

// Gestion des formulaires
function initForms() {
    // Formulaire de newsletter
    const newsletterForm = document.querySelector('.newsletter-form');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const email = newsletterForm.querySelector('input[type="email"]').value;
            
            if (isValidEmail(email)) {
                showNotification('Inscription à la newsletter réussie !', 'success');
                newsletterForm.reset();
            } else {
                showNotification('Veuillez saisir une adresse email valide.', 'error');
            }
        });
    }
    
    // Formulaire de recherche
    const searchForm = document.querySelector('.search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', (e) => {
            const query = searchForm.querySelector('input[name="q"]').value.trim();
            if (!query) {
                e.preventDefault();
                showNotification('Veuillez saisir un terme de recherche.', 'warning');
            }
        });
    }
}

// Validation d'email
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Affichage des notifications
function showNotification(message, type = 'info') {
    // Créer la notification
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${getNotificationIcon(type)}"></i>
            <span>${message}</span>
            <button class="notification-close">&times;</button>
        </div>
    `;
    
    // Ajouter au DOM
    document.body.appendChild(notification);
    
    // Afficher avec animation
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    // Fermer automatiquement après 5 secondes
    setTimeout(() => {
        hideNotification(notification);
    }, 5000);
    
    // Fermer manuellement
    const closeBtn = notification.querySelector('.notification-close');
    closeBtn.addEventListener('click', () => {
        hideNotification(notification);
    });
}

// Masquer une notification
function hideNotification(notification) {
    notification.classList.remove('show');
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 300);
}

// Obtenir l'icône de notification
function getNotificationIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Gestion du lazy loading des images
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

// Gestion des erreurs d'images
function initImageErrorHandling() {
    const images = document.querySelectorAll('img');
    
    images.forEach(img => {
        img.addEventListener('error', function() {
            // Remplacer par une image de placeholder
            this.src = '/static/sfront/images/placeholder.jpg';
            this.alt = 'Image non disponible';
            
            // Masquer le placeholder si c'est une image de contenu
            const placeholder = this.closest('.program-image, .news-image, .event-image, .main-article-image')?.querySelector('.program-image-placeholder, .news-image-placeholder, .event-image-placeholder, .main-article-placeholder');
            if (placeholder) {
                placeholder.style.display = 'none';
            }
        });
    });
}

// Gestion de la performance
function initPerformanceOptimizations() {
    // Préchargement des images critiques
    const criticalImages = document.querySelectorAll('.hero-background img, .main-article-image img');
    criticalImages.forEach(img => {
        if (img.dataset.src) {
            const preloadLink = document.createElement('link');
            preloadLink.rel = 'preload';
            preloadLink.as = 'image';
            preloadLink.href = img.dataset.src;
            document.head.appendChild(preloadLink);
        }
    });
    
    // Désactiver les animations sur les appareils à faible performance
    if (navigator.connection && navigator.connection.effectiveType === 'slow-2g') {
        document.body.classList.add('reduced-motion');
    }
}

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initialisation de la page d\'accueil CSIG...');
    
    try {
        // Initialiser les carousels
        if (typeof Swiper !== 'undefined') {
            initHomeCarousels();
        } else {
            console.warn('Swiper non disponible, carousels non initialisés');
        }
        
        // Initialiser les animations
        initCardAnimations();
        
        // Initialiser les placeholders d'images
        initImagePlaceholders();
        
        // Initialiser la navigation
        initNavigationLinks();
        
        // Initialiser les formulaires
        initForms();
        
        // Initialiser le lazy loading
        initLazyLoading();
        
        // Initialiser la gestion des erreurs d'images
        initImageErrorHandling();
        
        // Initialiser les optimisations de performance
        initPerformanceOptimizations();
        
        // Animer les statistiques après un délai
        setTimeout(animateStats, 1000);
        
        console.log('Page d\'accueil CSIG initialisée avec succès');
        
    } catch (error) {
        console.error('Erreur lors de l\'initialisation de la page d\'accueil:', error);
    }
});

// Gestion des erreurs globales
window.addEventListener('error', function(e) {
    console.error('Erreur JavaScript:', e.error);
});

// Gestion des erreurs de promesses non gérées
window.addEventListener('unhandledrejection', function(e) {
    console.error('Promesse rejetée non gérée:', e.reason);
});

// Export pour utilisation externe
window.homePage = {
    initCarousels: initHomeCarousels,
    animateStats: animateStats,
    showNotification: showNotification,
    initCardAnimations: initCardAnimations
};
