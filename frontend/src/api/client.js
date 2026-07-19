let _apiUrl = import.meta.env.VITE_API_URL || '';
if (_apiUrl && !_apiUrl.startsWith('http')) {
  _apiUrl = 'https://' + _apiUrl;
}
const API_BASE_URL = _apiUrl + '/api/v1';

class ApiError extends Error {
  constructor(message, status, data) {
    super(message);
    this.status = status;
    this.data = data;
  }
}

async function request(endpoint, options = {}) {
  const token = localStorage.getItem('token');
  
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  // If body is FormData (for file uploads), let the browser set the Content-Type
  if (options.body instanceof FormData) {
    delete headers['Content-Type'];
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorData;
    try {
      errorData = await response.json();
    } catch (e) {
      errorData = { detail: response.statusText };
    }
    
    // Auto-logout on 401 Unauthorized
    if (response.status === 401) {
      localStorage.removeItem('token');
      window.dispatchEvent(new Event('auth:unauthorized'));
    }

    throw new ApiError(
      errorData.detail || 'An error occurred',
      response.status,
      errorData
    );
  }

  // Some endpoints might return 204 No Content
  if (response.status === 204) {
    return null;
  }

  return response.json();
}

export const api = {
  get: (endpoint) => request(endpoint, { method: 'GET' }),
  
  post: (endpoint, data) => request(endpoint, { 
    method: 'POST',
    body: JSON.stringify(data)
  }),
  
  patch: (endpoint, data) => request(endpoint, {
    method: 'PATCH',
    body: JSON.stringify(data)
  }),
  
  delete: (endpoint) => request(endpoint, { method: 'DELETE' }),
  
  upload: (endpoint, file) => {
    const formData = new FormData();
    formData.append('file', file);
    return request(endpoint, {
      method: 'POST',
      body: formData
    });
  }
};
