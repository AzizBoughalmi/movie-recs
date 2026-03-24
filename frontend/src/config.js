// Configuration utility for environment-based settings
const config = {
  // API Configuration
  // For Heroku: Leave VITE_API_BASE_URL unset for same-origin requests (frontend + API on same domain)
  // For development: set VITE_API_BASE_URL=http://localhost:8000
  // For other deployments: set VITE_API_BASE_URL=https://api.example.com
  API_BASE_URL: import.meta.env.VITE_API_BASE_URL || '',
  
  // Environment
  NODE_ENV: import.meta.env.VITE_NODE_ENV || 'development',
  
  // Helper methods
  isDevelopment: () => config.NODE_ENV === 'development',
  isProduction: () => config.NODE_ENV === 'production',
  
  // API endpoint builder
  // If API_BASE_URL is empty (production same-origin), uses relative paths
  // If API_BASE_URL is set (development), uses absolute URL
  getApiUrl: (endpoint) => {
    // Remove leading slash if present
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;
    
    // If API_BASE_URL is empty, use relative path (same-origin)
    if (!config.API_BASE_URL) {
      return `/${cleanEndpoint}`;
    }
    
    // Otherwise use absolute URL
    return `${config.API_BASE_URL}/${cleanEndpoint}`;
  }
};


export default config;
