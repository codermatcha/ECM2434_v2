// Fetch API configuration from the server
fetch('/api-config/')
  .then(response => response.json())
  .then(config => {
    // Store the API base URL in window.apiBaseUrl
    window.apiBaseUrl = config.apiBaseUrl;
    console.log('API base URL configured:', window.apiBaseUrl);
    
    // Override fetch to redirect API calls
    const originalFetch = window.fetch;
    window.fetch = function(url, options) {
      if (typeof url === 'string' && url.startsWith('http://localhost:8000')) {
        const newUrl = url.replace('http://localhost:8000', window.location.origin);
        console.log(`Redirecting API request: ${url} → ${newUrl}`);
        return originalFetch(newUrl, options);
      }
      return originalFetch(url, options);
    };
  })
  .catch(error => {
    console.error('Failed to load API configuration:', error);
  });
