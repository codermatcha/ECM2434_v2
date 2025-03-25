// API Configuration
window.API_URL = window.location.origin;
window.API_BASE = window.location.origin + '/api';

// Override any configuration in the React app
if (window.APP_CONFIG) {
  window.APP_CONFIG.API_URL = window.API_BASE;
}

console.log('API configuration loaded:', {
  API_URL: window.API_URL,
  API_BASE: window.API_BASE
});
