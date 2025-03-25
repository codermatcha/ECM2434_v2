// Intercept fetch requests
const originalFetch = window.fetch;
window.fetch = function(url, options) {
    // If the URL contains localhost:8000, redirect to the actual API endpoint
    if (typeof url === 'string' && url.includes('localhost:8000')) {
        const newUrl = url.replace('http://localhost:8000', window.location.origin);
        console.log(`Redirecting API request from ${url} to ${newUrl}`);
        return originalFetch(newUrl, options);
    }
    return originalFetch(url, options);
};

// Log that the redirect is active
console.log('API request redirection is active');
