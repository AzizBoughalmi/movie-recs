// Configuration utility for environment-based settings
const config = {
  // API Configuration
  API_BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  
  // Environment
  NODE_ENV: import.meta.env.VITE_NODE_ENV || 'development',
  
  // Helper methods
  isDevelopment: () => config.NODE_ENV === 'development',
  isProduction: () => config.NODE_ENV === 'production',
  
  // API endpoint builder
  getApiUrl: (endpoint) => {
    // Remove leading slash if present to avoid double slashes
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;
    return `${config.API_BASE_URL}/${cleanEndpoint}`;
  }
};

export default config;
