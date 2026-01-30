// API Configuration
const API_BASE_URL = 'http://127.0.0.1:8003';

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

// Cart management using localStorage
const CartManager = {
    CART_KEY: 'marketmate_cart',
    
    getCart() {
        const cart = localStorage.getItem(this.CART_KEY);
        return cart ? JSON.parse(cart) : [];
    },
    
    saveCart(cart) {
        localStorage.setItem(this.CART_KEY, JSON.stringify(cart));
    },
    
    addItem(item, quantity = 1) {
        const cart = this.getCart();
        const existingIndex = cart.findIndex(c => c.item.id === item.id);
        
        if (existingIndex >= 0) {
            cart[existingIndex].quantity += quantity;
        } else {
            cart.push({ item, quantity });
        }
        
        this.saveCart(cart);
        return cart;
    },
    
    removeItem(itemId) {
        let cart = this.getCart();
        cart = cart.filter(c => c.item.id !== itemId);
        this.saveCart(cart);
        return cart;
    },
    
    updateQuantity(itemId, quantity) {
        const cart = this.getCart();
        const index = cart.findIndex(c => c.item.id === itemId);
        
        if (index >= 0) {
            if (quantity <= 0) {
                cart.splice(index, 1);
            } else {
                cart[index].quantity = quantity;
            }
        }
        
        this.saveCart(cart);
        return cart;
    },
    
    clearCart() {
        localStorage.removeItem(this.CART_KEY);
        return [];
    },
    
    getItemCount() {
        const cart = this.getCart();
        return cart.reduce((total, item) => total + item.quantity, 0);
    },
    
    getTotal() {
        const cart = this.getCart();
        return cart.reduce((total, item) => total + (item.item.price * item.quantity), 0);
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
                console.error('API Error Response:', error);
                // Handle Pydantic validation errors (array of errors)
                if (Array.isArray(error.detail)) {
                    const messages = error.detail.map(e => e.msg || e.message || JSON.stringify(e)).join(', ');
                    throw new Error(messages);
                }
                throw new Error(error.detail || JSON.stringify(error) || 'Request failed');
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

    async getSalesReport() {
        return this.request('/api/dashboard/sales-report');
    },

    async getRatingDistribution() {
        return this.request('/api/dashboard/rating-distribution');
    },

    async getTopItemsChart() {
        return this.request('/api/dashboard/top-items-chart');
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

    // Get customer's own orders (for customer-facing pages)
    async getMyOrders() {
        return this.request('/api/orders/my-orders');
    },
    
    async createOrder(data) {
        return this.request('/api/orders/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    // Customer checkout endpoint (for customer-facing purchases)
    async customerCheckout(data) {
        return this.request('/api/orders/checkout', {
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

    // Cancel order for customer (only pending orders)
    async cancelMyOrder(orderId) {
        return this.request(`/api/orders/my-orders/${orderId}`, {
            method: 'DELETE'
        });
    },

    // Update customer's own order (e.g., mark as received/completed)
    async updateMyOrder(orderId, data) {
        return this.request(`/api/orders/my-orders/${orderId}`, {
            method: 'PUT',
            body: JSON.stringify(data)
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
    
    async uploadItemImage(itemId, file) {
        const token = TokenManager.getToken();
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`${API_BASE_URL}/api/items/${itemId}/upload-image`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Upload failed');
        }
        
        return await response.json();
    },
    
    // Shipping endpoints
    async getShipping() {
        return this.request('/api/shipping/');
    },

    // Get customer's own shipping (for customer-facing pages)
    async getMyShipping() {
        return this.request('/api/shipping/my-shipping');
    },
    
    async updateShipping(id, data) {
        return this.request(`/api/shipping/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },

    async updateShippingStatus(shippingId, status) {
        return this.updateShipping(shippingId, { status: status });
    },
    
    // Payment endpoints
    async getPayments() {
        return this.request('/api/payments/');
    },

    // Get customer's own payments
    async getMyPayments() {
        return this.request('/api/payments/my-payments');
    },

    async createPayment(data) {
        return this.request('/api/payments/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    
    async updatePayment(id, data) {
        return this.request(`/api/payments/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },

    async updatePaymentStatus(orderDbId, status) {
        // orderDbId is the numeric database ID of the order (e.g., 5, 6)
        // Find payment by the order's database ID
        try {
            console.log('💳 updatePaymentStatus called with orderDbId:', orderDbId, 'status:', status);
            const payments = await this.getMyPayments();
            console.log('💳 Found payments:', payments);
            
            let payment = payments.find(p => p.order_db_id == orderDbId);
            console.log('💳 Matching payment for order_db_id', orderDbId, ':', payment);
            
            if (payment) {
                // Update the existing payment status
                console.log('💳 Updating existing payment ID:', payment.id);
                return this.updatePayment(payment.id, { status: status });
            } else {
                // No payment exists, create one first
                console.log('💳 No payment found, creating new one...');
                const orders = await this.getMyOrders();
                const order = orders.find(o => o.id == orderDbId);
                
                if (!order) {
                    throw new Error('Order not found');
                }
                
                // Create a payment record
                const paymentId = `PAY-${Date.now().toString(36).toUpperCase()}`;
                const newPayment = await this.createPayment({
                    payment_id: paymentId,
                    order_id: orderDbId,
                    amount: order.total_amount,
                    payment_method: order.payment_method,
                    status: status
                });
                
                return newPayment;
            }
        } catch (error) {
            console.error('Error updating payment:', error);
            throw error;
        }
    },
    
    // Review endpoints
    async getReviews() {
        return this.request('/api/reviews/');
    },
    
    async getReviewsByItem(itemId) {
        return this.request(`/api/reviews/item/${itemId}`);
    },
    
    async getItemsWithReviews() {
        return this.request('/api/reviews/items-with-reviews');
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
