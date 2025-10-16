# Site Public CSIG - Cité des Sciences et de l'Innovation de Guinée

## Vue d'ensemble

Ce dossier contient le site public de la Cité des Sciences et de l'Innovation de Guinée (CSIG), conçu pour présenter l'institution, ses programmes, actualités et événements au grand public.

## Structure des fichiers

### Templates
- `base.html` - Template de base avec header, footer et navigation
- `home.html` - Page d'accueil avec toutes les sections principales

### CSS
- `static/css/sfront.css` - Styles principaux du site public
- `static/css/home.css` - Styles spécifiques à la page d'accueil
- `static/css/notifications.css` - Système de notifications

### JavaScript
- `static/js/sfront.js` - Fonctionnalités générales du site
- `static/js/home.js` - Fonctionnalités spécifiques à la page d'accueil

### Images
- `static/sfront/images/` - Dossier contenant toutes les images du site

## Fonctionnalités

### Page d'Accueil
1. **Section Hero** - Carousel avec 3 slides :
   - Message de bienvenue
   - Statistiques clés
   - Innovation et technologie

2. **Domaines de Collaboration** - Carousel des programmes avec navigation

3. **Actualités et Événements** - Article principal + articles récents + événements

4. **Partenaires** - Carousel des partenaires institutionnels

5. **Call-to-Action** - Section d'engagement

### Caractéristiques Techniques
- **Responsive Design** - Optimisé pour tous les appareils
- **Animations AOS** - Animations au scroll
- **Carousels Swiper** - Navigation fluide et intuitive
- **Lazy Loading** - Chargement optimisé des images
- **Accessibilité** - Support des lecteurs d'écran
- **Performance** - Optimisations pour la vitesse de chargement

## Utilisation

### Installation des dépendances
Le site utilise les CDN suivants :
- Bootstrap 5.3.0
- Font Awesome 6.4.0
- Google Fonts (Inter, Poppins)
- AOS (Animate On Scroll) 2.3.1
- Swiper 10

### Personnalisation
1. **Couleurs** - Modifier les variables CSS dans `sfront.css`
2. **Images** - Remplacer les images dans `static/sfront/images/`
3. **Contenu** - Modifier les templates Django selon les besoins
4. **Animations** - Ajuster les délais AOS dans les templates

### Ajout de nouvelles pages
1. Créer le template dans le dossier `sfront/`
2. Ajouter la vue correspondante dans `sfront/views.py`
3. Définir l'URL dans `sfront/urls.py`
4. Ajouter le lien dans la navigation (`base.html`)

## Structure des données

### Modèles utilisés
- `Program` - Programmes de l'institution
- `Article` - Actualités et articles
- `Event` - Événements et manifestations
- `Partner` - Partenaires institutionnels
- `SiteSettings` - Paramètres du site

### Contexte de la page d'accueil
La vue `home` fournit :
- `featured_article` - Article mis en avant
- `programs` - 6 programmes récents
- `main_article` - Article principal (hors mis en avant)
- `recent_articles` - 2 articles récents
- `recent_events` - 2 événements à venir
- `partners` - 10 partenaires actifs

## Responsive Design

### Breakpoints
- **Desktop** : ≥992px
- **Tablet** : ≥768px et <992px
- **Mobile** : <768px
- **Small Mobile** : <576px

### Adaptations
- Navigation mobile avec menu burger
- Carousels adaptés selon la taille d'écran
- Images et textes redimensionnés
- Boutons et actions optimisés pour le tactile

## Performance

### Optimisations
- Lazy loading des images
- Préchargement des ressources critiques
- Minification des assets (en production)
- Compression des images
- Cache des ressources statiques

### Métriques cibles
- First Contentful Paint : <1.5s
- Largest Contentful Paint : <2.5s
- Cumulative Layout Shift : <0.1
- First Input Delay : <100ms

## Accessibilité

### Standards
- WCAG 2.1 AA
- Support des lecteurs d'écran
- Navigation au clavier
- Contraste des couleurs
- Textes alternatifs

### Fonctionnalités
- Focus visible sur tous les éléments interactifs
- Structure sémantique HTML5
- Attributs ARIA appropriés
- Support des préférences de réduction de mouvement

## Maintenance

### Tâches régulières
- Vérifier les liens cassés
- Optimiser les images
- Mettre à jour les dépendances
- Tester la responsivité
- Vérifier l'accessibilité

### Déploiement
1. Collecter les fichiers statiques : `python manage.py collectstatic`
2. Vérifier les permissions des dossiers
3. Tester sur différents navigateurs
4. Valider la performance

## Support

Pour toute question ou problème :
- Consulter la documentation Django
- Vérifier les logs du serveur
- Tester sur différents appareils
- Utiliser les outils de développement du navigateur

## Licence

© 2024 Cité des Sciences et de l'Innovation de Guinée. Tous droits réservés.
