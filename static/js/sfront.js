// ============================================================================
// FICHIER JAVASCRIPT PRINCIPAL - PARTIE PUBLIQUE CSIG
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    // Initialisation des composants
    initHeaderScroll();
    initBackToTop();
    initAOS();
    initSwiper();
    initSearchForm();
    initNewsletterForm();
    initSmoothScroll();
    initAnimations();
});

// ============================================================================
// GESTION DU HEADER AU SCROLL
// ============================================================================
function initHeaderScroll() {
    const navbar = document.querySelector('.navbar');
    const header = document.querySelector('.main-header');
    
    if (!navbar || !header) return;
    
    let lastScrollTop = 0;
    const scrollThreshold = 100;
    
    window.addEventListener('scroll', function() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        // Ajouter/supprimer la classe scrolled
        if (scrollTop > scrollThreshold) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
        
        // Masquer/afficher le header au scroll
        if (scrollTop > lastScrollTop && scrollTop > 200) {
            // Scroll vers le bas
            header.style.transform = 'translateY(-100%)';
        } else {
            // Scroll vers le haut
            header.style.transform = 'translateY(0)';
        }
        
        lastScrollTop = scrollTop;
    });
    
    // Transition du header
    header.style.transition = 'transform 0.3s ease-in-out';
}

// ============================================================================
// BOUTON RETOUR EN HAUT
// ============================================================================
function initBackToTop() {
    const backToTopBtn = document.getElementById('backToTop');
    
    if (!backToTopBtn) return;
    
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            backToTopBtn.classList.add('show');
        } else {
            backToTopBtn.classList.remove('show');
        }
    });
    
    backToTopBtn.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// ============================================================================
// INITIALISATION AOS (ANIMATIONS AU SCROLL)
// ============================================================================
function initAOS() {
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

// ============================================================================
// INITIALISATION SWIPER (CAROUSEL)
// ============================================================================
function initSwiper() {
    // Carousel principal
    const mainSwiper = document.querySelector('.main-carousel');
    if (mainSwiper && typeof Swiper !== 'undefined') {
        new Swiper('.main-carousel', {
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
                dynamicBullets: true,
            },
            navigation: {
                nextEl: '.swiper-button-next',
                prevEl: '.swiper-button-prev',
            },
            effect: 'fade',
            fadeEffect: {
                crossFade: true
            },
            speed: 1000,
        });
    }
    
    // Carousel des programmes
    const programsSwiper = document.querySelector('.programs-carousel');
    if (programsSwiper && typeof Swiper !== 'undefined') {
        new Swiper('.programs-carousel', {
            slidesPerView: 1,
            spaceBetween: 30,
            loop: true,
            autoplay: {
                delay: 4000,
                disableOnInteraction: false,
            },
            pagination: {
                el: '.swiper-pagination',
                clickable: true,
            },
            breakpoints: {
                768: {
                    slidesPerView: 2,
                    spaceBetween: 30,
                },
                1024: {
                    slidesPerView: 3,
                    spaceBetween: 40,
                }
            },
            speed: 800,
        });
    }
    
    // Carousel des partenaires
    const partnersSwiper = document.querySelector('.partners-carousel');
    if (partnersSwiper && typeof Swiper !== 'undefined') {
        new Swiper('.partners-carousel', {
            slidesPerView: 2,
            spaceBetween: 30,
            loop: true,
            autoplay: {
                delay: 3000,
                disableOnInteraction: false,
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
                1024: {
                    slidesPerView: 5,
                    spaceBetween: 50,
                }
            },
            speed: 600,
        });
    }
}

// ============================================================================
// GESTION DU FORMULAIRE DE RECHERCHE
// ============================================================================
function initSearchForm() {
    const searchForms = document.querySelectorAll('.search-form');
    
    searchForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const input = form.querySelector('input[type="text"]');
            if (!input.value.trim()) {
                e.preventDefault();
                input.focus();
                showNotification('Veuillez saisir un terme de recherche', 'warning');
            }
        });
    });
}

// ============================================================================
// GESTION DU FORMULAIRE NEWSLETTER
// ============================================================================
function initNewsletterForm() {
    const newsletterForms = document.querySelectorAll('.newsletter-form');
    
    newsletterForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const emailInput = form.querySelector('input[type="email"]');
            const email = emailInput.value.trim();
            
            if (!isValidEmail(email)) {
                showNotification('Veuillez saisir une adresse email valide', 'error');
                return;
            }
            
            // Simulation d'envoi
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            submitBtn.disabled = true;
            
            setTimeout(() => {
                showNotification('Inscription à la newsletter réussie !', 'success');
                emailInput.value = '';
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }, 1500);
        });
    });
}

// ============================================================================
// SCROLL SMOOTH POUR LES LIENS INTERNES
// ============================================================================
function initSmoothScroll() {
    const internalLinks = document.querySelectorAll('a[href^="#"]');
    
    internalLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                const headerHeight = document.querySelector('.main-header').offsetHeight;
                const targetPosition = targetElement.offsetTop - headerHeight - 20;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// ============================================================================
// ANIMATIONS PERSONNALISÉES
// ============================================================================
function initAnimations() {
    // Animation des compteurs
    const counters = document.querySelectorAll('.counter');
    
    const animateCounters = () => {
        counters.forEach(counter => {
            const target = parseInt(counter.getAttribute('data-target'));
            const duration = 2000; // 2 secondes
            const increment = target / (duration / 16); // 60 FPS
            let current = 0;
            
            const updateCounter = () => {
                current += increment;
                if (current < target) {
                    counter.textContent = Math.floor(current);
                    requestAnimationFrame(updateCounter);
                } else {
                    counter.textContent = target;
                }
            };
            
            updateCounter();
        });
    };
    
    // Observer pour déclencher l'animation des compteurs
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounters();
                observer.unobserve(entry.target);
            }
        });
    });
    
    counters.forEach(counter => {
        observer.observe(counter);
    });
    
    // Animation des cartes au hover
    const cards = document.querySelectorAll('.card, .program-card, .news-card, .event-card');
    
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px)';
            this.style.boxShadow = '0 20px 40px rgba(13, 71, 134, 0.15)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '';
        });
    });
}

// ============================================================================
// FONCTIONS UTILITAIRES
// ============================================================================

// Validation d'email
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Affichage de notifications
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
    
    // Styles de la notification
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${getNotificationColor(type)};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        z-index: 9999;
        transform: translateX(100%);
        transition: transform 0.3s ease;
        max-width: 400px;
        font-family: var(--font-primary);
    `;
    
    // Ajouter au DOM
    document.body.appendChild(notification);
    
    // Animer l'entrée
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Gérer la fermeture
    const closeBtn = notification.querySelector('.notification-close');
    closeBtn.addEventListener('click', () => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    });
    
    // Auto-fermeture après 5 secondes
    setTimeout(() => {
        if (document.body.contains(notification)) {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (document.body.contains(notification)) {
                    document.body.removeChild(notification);
                }
            }, 300);
        }
    }, 5000);
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

// Obtenir la couleur de notification
function getNotificationColor(type) {
    const colors = {
        success: '#28a745',
        error: '#dc3545',
        warning: '#ffc107',
        info: '#17a2b8'
    };
    return colors[type] || '#17a2b8';
}

// ============================================================================
// GESTION DES IMAGES LAZY LOADING
// ============================================================================
function initLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
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
    
    images.forEach(img => imageObserver.observe(img));
}

// ============================================================================
// GESTION DU MENU MOBILE
// ============================================================================
function initMobileMenu() {
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (!navbarToggler || !navbarCollapse) return;
    
    // Fermer le menu lors du clic sur un lien
    const navLinks = navbarCollapse.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            if (window.innerWidth < 992) {
                navbarCollapse.classList.remove('show');
            }
        });
    });
    
    // Fermer le menu lors du clic à l'extérieur
    document.addEventListener('click', (e) => {
        if (!navbarToggler.contains(e.target) && !navbarCollapse.contains(e.target)) {
            navbarCollapse.classList.remove('show');
        }
    });
}

// ============================================================================
// GESTION DU THEME ET PREFERENCES
// ============================================================================
function initThemePreferences() {
    // Vérifier les préférences de l'utilisateur
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    
    if (prefersReducedMotion.matches) {
        // Désactiver les animations si l'utilisateur préfère
        document.documentElement.style.setProperty('--transition', 'none');
        document.documentElement.style.setProperty('--transition-fast', 'none');
        document.documentElement.style.setProperty('--transition-slow', 'none');
    }
    
    // Écouter les changements de préférences
    prefersReducedMotion.addEventListener('change', (e) => {
        if (e.matches) {
            document.documentElement.style.setProperty('--transition', 'none');
        } else {
            document.documentElement.style.setProperty('--transition', 'all 0.3s ease');
        }
    });
}

// ============================================================================
// INITIALISATION DES COMPOSANTS AVANCÉS
// ============================================================================
function initAdvancedComponents() {
    // Initialiser le lazy loading
    initLazyLoading();
    
    // Initialiser le menu mobile
    initMobileMenu();
    
    // Initialiser les préférences de thème
    initThemePreferences();
}

// Appeler l'initialisation des composants avancés
document.addEventListener('DOMContentLoaded', initAdvancedComponents);

// ============================================================================
// GESTION DES ERREURS ET FALLBACKS
// ============================================================================
window.addEventListener('error', function(e) {
    console.error('Erreur JavaScript:', e.error);
    
    // Fallback pour les composants qui pourraient échouer
    if (e.error && e.error.message.includes('Swiper')) {
        console.warn('Swiper non disponible, utilisation du fallback');
        initSwiperFallback();
    }
});

function initSwiperFallback() {
    // Implémentation de fallback simple pour les carousels
    const carousels = document.querySelectorAll('.swiper');
    
    carousels.forEach(carousel => {
        const slides = carousel.querySelectorAll('.swiper-slide');
        let currentSlide = 0;
        
        // Créer des boutons de navigation simples
        const nav = document.createElement('div');
        nav.className = 'carousel-nav';
        nav.innerHTML = `
            <button class="carousel-prev">&lt;</button>
            <span class="carousel-indicator">1 / ${slides.length}</span>
            <button class="carousel-next">&gt;</button>
        `;
        
        carousel.appendChild(nav);
        
        // Fonctionnalité de navigation
        const prevBtn = nav.querySelector('.carousel-prev');
        const nextBtn = nav.querySelector('.carousel-next');
        const indicator = nav.querySelector('.carousel-indicator');
        
        function showSlide(index) {
            slides.forEach((slide, i) => {
                slide.style.display = i === index ? 'block' : 'none';
            });
            indicator.textContent = `${index + 1} / ${slides.length}`;
        }
        
        prevBtn.addEventListener('click', () => {
            currentSlide = (currentSlide - 1 + slides.length) % slides.length;
            showSlide(currentSlide);
        });
        
        nextBtn.addEventListener('click', () => {
            currentSlide = (currentSlide + 1) % slides.length;
            showSlide(currentSlide);
        });
        
        // Afficher la première slide
        showSlide(0);
    });
}
