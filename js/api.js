// API Configuration
const API_BASE_URL = 'http://127.0.0.1:8002';

// Token management
const TokenManager = {
    getToken() {
        return localStorage.getItem('access_token');
    },
    
    setToken(token) {
        localStorage.setItem('access_token', token);
    },
    
    removeToken() {
        localStorage.removeItem('access_token');
    },
    
    isAuthenticated() {
        return !!this.getToken();
    }
};

// API client
const API = {
    async request(endpoint, options = {}) {
        const token = TokenManager.getToken();
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };
        
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                ...options,
                headers
            });
            
            if (response.status === 401) {
                TokenManager.removeToken();
                window.location.href = 'Sign-In.html';
                throw new Error('Unauthorized');
            }
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Request failed');
            }
            
            // Handle 204 No Content
            if (response.status === 204) {
                return null;
            }
            
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },
    
    // Auth endpoints
    async signup(username, email, password) {
        return this.request('/api/auth/signup', {
            method: 'POST',
            body: JSON.stringify({ username, email, password })
        });
    },
    
    async login(username, password) {
        return this.request('/api/auth/login/json', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });
    },
    
    async getCurrentUser() {
        return this.request('/api/auth/me');
    },
    
    // Dashboard endpoints
    async getDashboardStats() {
        return this.request('/api/dashboard/stats');
    },
    
    async getTopItems() {
        return this.request('/api/dashboard/top-items');
    },
    
    async getRecentReviews() {
        return this.request('/api/dashboard/recent-reviews');
    },
    
    // Customer endpoints
    async getCustomers() {
        return this.request('/api/customers/');
    },
    
    async createCustomer(data) {
        return this.request('/api/customers/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    
    async updateCustomer(id, data) {
        return this.request(`/api/customers/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },
    
    async deleteCustomer(id) {
        return this.request(`/api/customers/${id}`, {
            method: 'DELETE'
        });
    },
    
    // Order endpoints
    async getOrders() {
        return this.request('/api/orders/');
    },
    
    async createOrder(data) {
        return this.request('/api/orders/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    
    async updateOrder(id, data) {
        return this.request(`/api/orders/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },
    
    async deleteOrder(id) {
        return this.request(`/api/orders/${id}`, {
            method: 'DELETE'
        });
    },
    
    // Item endpoints
    async getItems() {
        return this.request('/api/items/');
    },
    
    async getItem(id) {
        return this.request(`/api/items/${id}`);
    },
    
    async createItem(data) {
        return this.request('/api/items/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    
    async updateItem(id, data) {
        return this.request(`/api/items/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },
    
    async deleteItem(id) {
        return this.request(`/api/items/${id}`, {
            method: 'DELETE'
        });
    },
    
    // Shipping endpoints
    async getShipping() {
        return this.request('/api/shipping/');
    },
    
    async updateShipping(id, data) {
        return this.request(`/api/shipping/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },
    
    // Payment endpoints
    async getPayments() {
        return this.request('/api/payments/');
    },
    
    async updatePayment(id, data) {
        return this.request(`/api/payments/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },
    
    // Review endpoints
    async getReviews() {
        return this.request('/api/reviews/');
    },
    
    async getReviewsByItem(itemId) {
        return this.request(`/api/reviews/item/${itemId}`);
    },
    
    async createReview(data) {
        return this.request('/api/reviews/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    
    async deleteReview(id) {
        return this.request(`/api/reviews/${id}`, {
            method: 'DELETE'
        });
    },
    
    // Reward endpoints
    async getRewards() {
        return this.request('/api/rewards/');
    },
    
    async createReward(data) {
        return this.request('/api/rewards/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    
    async updateReward(id, data) {
        return this.request(`/api/rewards/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },
    
    async deleteReward(id) {
        return this.request(`/api/rewards/${id}`, {
            method: 'DELETE'
        });
    }
};

// Check authentication on page load (except for login/signup pages)
document.addEventListener('DOMContentLoaded', () => {
    const currentPage = window.location.pathname.split('/').pop();
    const publicPages = ['Sign-In.html', 'Sign-Up.html', 'index.html', ''];
    
    if (!publicPages.includes(currentPage) && !TokenManager.isAuthenticated()) {
        window.location.href = 'Sign-In.html';
    }
});
