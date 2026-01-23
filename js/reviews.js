// Reviews Page JavaScript
async function loadReviews() {
    try {
        const reviews = await API.getReviews();
        const container = document.getElementById('reviewsContainer');
        const avgRatingEl = document.getElementById('avgRating');
        const reviewCountEl = document.getElementById('reviewCount');
        const productTitleEl = document.getElementById('productTitle');
        
        if (!container) return;
        
        container.innerHTML = '';
        
        if (reviews.length === 0) {
            container.innerHTML = '<p style="text-align: center; color: #aaa;">No reviews found</p>';
            if (avgRatingEl) avgRatingEl.textContent = '0.0';
            if (reviewCountEl) reviewCountEl.textContent = '0 reviews';
            return;
        }
        
        // Calculate average rating
        const totalRating = reviews.reduce((sum, r) => sum + r.rating, 0);
        const avgRating = (totalRating / reviews.length).toFixed(1);
        
        // Update summary stats
        if (avgRatingEl) avgRatingEl.textContent = avgRating;
        if (reviewCountEl) reviewCountEl.textContent = `${reviews.length} review${reviews.length !== 1 ? 's' : ''}`;
        if (productTitleEl) productTitleEl.textContent = 'All Reviews';
        
        // Render reviews
        reviews.forEach(review => {
            const reviewBox = document.createElement('div');
            reviewBox.className = 'review-box';
            const stars = '★'.repeat(Math.round(review.rating)) + '☆'.repeat(5 - Math.round(review.rating));
            const date = new Date(review.created_at).toLocaleDateString();
            reviewBox.innerHTML = `
                <div class="review-user">
                    <img src="../images/ppft.png" alt="User" class="user-avatar">
                    <div class="user-info">
                        <span class="username">${review.customer_name}</span>
                        <span class="user-rating">${stars}</span>
                    </div>
                </div>
                <p class="review-meta">Product: ${review.item_name} • ${date}</p>
                <p class="review-text">${review.comment || 'No comment provided'}</p>
            `;
            container.appendChild(reviewBox);
        });
    } catch (error) {
        console.error('Error loading reviews:', error);
        const container = document.getElementById('reviewsContainer');
        if (container) {
            container.innerHTML = '<p style="text-align: center; color: red;">Failed to load reviews</p>';
        }
    }
}

if (window.location.pathname.includes('reviews.html')) {
    document.addEventListener('DOMContentLoaded', loadReviews);
}
