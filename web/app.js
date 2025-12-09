// Configuration API
const API_URL = window.location.origin;

// Fonction pour faire des requêtes API
async function apiRequest(endpoint, options = {}) {
    const url = `${API_URL}${endpoint}`;
    
    const fetchOptions = {
        method: options.method || 'GET',
        headers: {
            'Content-Type': 'application/json',
            ...(options.headers || {})
        }
    };
    
    // Ajouter le token si nécessaire
    if (options.requireAuth !== false) {
        const token = getToken();
        if (token) {
            fetchOptions.headers['Authorization'] = token;
        }
    }
    
    // Ajouter le body si présent
    if (options.body) {
        fetchOptions.body = options.body;
    }
    
    const response = await fetch(url, fetchOptions);
    
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
}

// Créer une carte de série avec poster
function createSeriesCard(series, options = {}) {
    const {
        showRating = true,
        showKeywords = false
    } = options;
    
    const title = formatSeriesTitle(series.title);
    const language = getLanguage(series.title);
    
    // Utiliser l'endpoint /posters/ pour les images BLOB
    let posterUrl;
    if (series.poster_url && series.poster_url.startsWith('blob:')) {
        // Image en BLOB - utiliser l'endpoint
        posterUrl = `posters/${series.title}.jpg`;
    } else if (series.poster_url) {
        // URL externe
        posterUrl = series.poster_url;
    } else {
        // Fallback SVG
        posterUrl = `covers/${series.title}.svg`;
    }
    
    let card = `
        <div class="series-card">
            <div class="series-poster">
                <img src="${posterUrl}" 
                     alt="${title}" 
                     onerror="this.src='covers/${series.title}.svg'"
                     loading="lazy">
                <span class="language-badge ${language}">${language.toUpperCase()}</span>
            </div>
            <div class="series-info">
                <h3>${title}</h3>
    `;
    
    if (showRating && series.average_rating) {
        card += `
                <div class="series-rating">
                    <span class="rating-stars">${'⭐'.repeat(Math.round(series.average_rating))}</span>
                    <span class="rating-value">${series.average_rating.toFixed(1)}/5</span>
                    <span class="rating-count">(${series.num_ratings || 0} notes)</span>
                </div>
        `;
    }
    
    if (series.score !== undefined) {
        card += `
                <div class="series-score">
                    <span class="score-label">Score:</span>
                    <span class="score-value">${series.score.toFixed(2)}</span>
                </div>
        `;
    }
    
    card += `
                <button class="btn btn-primary btn-sm" onclick="viewSeriesDetails('${series.title}')">
                    Voir les détails
                </button>
            </div>
        </div>
    `;
    
    return card;
}

// Formater le titre de la série
function formatSeriesTitle(title) {
    // Enlever le suffixe _vf ou _vo
    let formatted = title.replace(/_(vf|vo)$/, '');
    
    // Remplacer les underscores par des espaces
    formatted = formatted.replace(/_/g, ' ');
    
    // Capitaliser chaque mot
    return formatted.split(' ').map(word => 
        word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
}

// Obtenir la langue d'une série
function getLanguage(title) {
    if (title.endsWith('_vf')) return 'vf';
    if (title.endsWith('_vo')) return 'vo';
    return 'vf'; // Par défaut
}

// Afficher un message de chargement
function showLoading() {
    return `
        <div class="loading">
            <div class="spinner"></div>
            <p>Chargement en cours...</p>
        </div>
    `;
}

// Afficher un message quand il n'y a pas de résultats
function showNoResults(message = 'Aucun résultat trouvé.') {
    return `
        <div class="no-results">
            <p>${message}</p>
        </div>
    `;
}

// Afficher un message d'erreur
function showError(message) {
    return `
        <div class="error">
            <p>❌ ${message}</p>
        </div>
    `;
}

// Obtenir les paramètres de l'URL
function getUrlParams() {
    const params = new URLSearchParams(window.location.search);
    return Object.fromEntries(params.entries());
}

// Naviguer vers la page de détails d'une série
function viewSeriesDetails(title) {
    window.location.href = `series-details.html?title=${encodeURIComponent(title)}`;
}

// Générer une couleur basée sur le nom
function getSeriesColor(title) {
    // Générer une couleur pseudo-aléatoire basée sur le titre
    let hash = 0;
    for (let i = 0; i < title.length; i++) {
        hash = title.charCodeAt(i) + ((hash << 5) - hash);
    }
    
    const hue = hash % 360;
    return `hsl(${hue}, 60%, 50%)`;
}

// Fonctions d'authentification
function getToken() {
    return localStorage.getItem('authToken');
}

function setToken(token) {
    localStorage.setItem('authToken', token);
}

function removeToken() {
    localStorage.removeItem('authToken');
}

function isLoggedIn() {
    return !!getToken();
}

function updateProfileLink() {
    const profileLink = document.getElementById('profileLink');
    if (profileLink) {
        if (isLoggedIn()) {
            profileLink.textContent = '👤 Mon Profil';
        } else {
            profileLink.textContent = 'Connexion';
        }
    }
}

// Gestion de la préférence de langue
function getLanguagePreference() {
    return localStorage.getItem('languagePreference') || 'all';
}

function setLanguagePreference(lang) {
    localStorage.setItem('languagePreference', lang);
    updateLanguageToggle();
    // Recharger la page pour appliquer le filtre
    window.location.reload();
}

function updateLanguageToggle() {
    const toggle = document.getElementById('languageToggle');
    if (toggle) {
        const pref = getLanguagePreference();
        if (pref === 'vf') {
            toggle.innerHTML = '🇫🇷 VF';
            toggle.className = 'language-toggle vf';
        } else if (pref === 'vo') {
            toggle.innerHTML = '🇺🇸 VO';
            toggle.className = 'language-toggle vo';
        } else {
            toggle.innerHTML = '🌍 Tous';
            toggle.className = 'language-toggle all';
        }
    }
}

function toggleLanguage() {
    const current = getLanguagePreference();
    let next;
    if (current === 'all') next = 'vf';
    else if (current === 'vf') next = 'vo';
    else next = 'all';
    setLanguagePreference(next);
}

function shouldShowSeries(seriesTitle) {
    const pref = getLanguagePreference();
    if (pref === 'all') return true;
    if (pref === 'vf') return seriesTitle.endsWith('_vf');
    if (pref === 'vo') return seriesTitle.endsWith('_vo');
    return true;
}
