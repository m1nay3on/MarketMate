// Reviews Page JavaScript - Grid Layout with Modal

async function loadProductsGrid() {
    try {
        const items = await API.getItemsWithReviews();
        const grid = document.getElementById('itemsGrid');
        
        if (!grid) return;
        
        grid.innerHTML = '';
        
        if (items.length === 0) {
            grid.innerHTML = '<p style="text-align: center; color: #666; grid-column: 1 / -1;">No products with reviews yet</p>';
            return;
        }
        
        // Create card for each item
        items.forEach(item => {
            const card = document.createElement('div');
            card.className = 'item-card';
            const stars = '★'.repeat(Math.round(item.rating)) + '☆'.repeat(5 - Math.round(item.rating));
            card.innerHTML = `
                <div class="image-placeholder">
                    <img src="${item.image_url || '../images/iphonee.jpg'}" alt="${item.name}">
                </div>
                <div class="item-info">
                    <h3>${item.name}</h3>
                    <p class="rating"><span class="star">${stars}</span> ${item.rating.toFixed(1)} / 5.0</p>
                    <p class="review-count-small">${item.review_count} review${item.review_count !== 1 ? 's' : ''}</p>
                    <div class="card-actions">
                        <button class="btn-reviews" data-item-id="${item.id}">View Reviews</button>
                    </div>
                </div>
            `;
            grid.appendChild(card);
        });
        
        // Add click handlers for view reviews buttons
        document.querySelectorAll('.btn-reviews').forEach(btn => {
            btn.addEventListener('click', function() {
                const itemId = this.getAttribute('data-item-id');
                openReviewsModal(itemId);
            });
        });
    } catch (error) {
        console.error('Error loading products grid:', error);
        const grid = document.getElementById('itemsGrid');
        if (grid) {
            grid.innerHTML = '<p style="text-align: center; color: red; grid-column: 1 / -1;">Error loading products</p>';
        }
    }
}

async function openReviewsModal(itemId) {
    const modal = document.getElementById('reviewsModal');
    const container = document.getElementById('reviewsContainer');
    
    if (!modal || !container) return;
    
    // Show modal
    modal.classList.add('show');
    container.innerHTML = '<p style="text-align: center; color: #aaa;">Loading reviews...</p>';
    
    try {
        const data = await API.getReviewsByItem(itemId);
        
        // Update product info in modal
        const titleEl = document.getElementById('modalProductTitle');
        const imageEl = document.getElementById('modalProductImage');
        const avgRatingEl = document.getElementById('modalAvgRating');
        const reviewCountEl = document.getElementById('modalReviewCount');
        
        if (data.item) {
            if (titleEl) titleEl.textContent = data.item.name;
            if (imageEl) imageEl.src = data.item.image_url || '../images/iphonee.jpg';
            if (avgRatingEl) avgRatingEl.textContent = data.item.rating.toFixed(1);
        }
        
        if (reviewCountEl) reviewCountEl.textContent = `${data.review_count} review${data.review_count !== 1 ? 's' : ''}`;
        
        container.innerHTML = '';
        
        if (!data.reviews || data.reviews.length === 0) {
            container.innerHTML = '<p style="text-align: center; color: #aaa;">No reviews for this product yet</p>';
            return;
        }
        
        // Render reviews
        data.reviews.forEach(review => {
            const reviewBox = document.createElement('div');
            reviewBox.className = 'review-box';
            const stars = '★'.repeat(Math.round(review.rating)) + '☆'.repeat(5 - Math.round(review.rating));
            const date = new Date(review.created_at).toLocaleDateString();
            reviewBox.innerHTML = `
                <div class="review-header">
                    <span class="username">${review.customer_name}</span>
                    <span class="review-rating">${stars}</span>
                </div>
                <p class="review-date">${date}</p>
                <p class="review-text">${review.comment || 'No comment provided'}</p>
            `;
            container.appendChild(reviewBox);
        });
    } catch (error) {
        console.error('Error loading reviews:', error);
        container.innerHTML = '<p style="text-align: center; color: red;">Failed to load reviews</p>';
    }
}

function closeReviewsModal() {
    const modal = document.getElementById('reviewsModal');
    if (modal) modal.classList.remove('show');
}

// Initialize when page loads
if (window.location.pathname.includes('reviews.html')) {
    document.addEventListener('DOMContentLoaded', () => {
        loadProductsGrid();
        
        // Modal close handlers
        const modal = document.getElementById('reviewsModal');
        const closeBtn = document.querySelector('.modal .close');
        
        if (closeBtn) {
            closeBtn.addEventListener('click', closeReviewsModal);
        }
        
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) closeReviewsModal();
            });
        }
    });
}
