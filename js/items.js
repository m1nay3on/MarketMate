// Items Page JavaScript

// Store for variants
let addItemVariants = [];
let editItemVariants = [];
let currentEditItemId = null;

async function loadItems() {
    try {
        const items = await API.getItems();
        const grid = document.querySelector('.items-grid');
        grid.innerHTML = '';
        
        if (items.length === 0) {
            grid.innerHTML = '<p style="text-align: center; width: 100%;">No items found</p>';
            return;
        }
        
        items.forEach(item => {
            const card = document.createElement('div');
            card.className = 'item-card';
            card.dataset.itemId = item.id;
            card.innerHTML = `
                <button class="delete-btn" onclick="deleteItem(${item.id})">×</button>
                <div class="image-placeholder">
                    <img src="${item.image_url || '../images/iphonee.jpg'}" alt="${item.name}">
                </div>
                <div class="item-info">
                    <h3>${item.name}</h3>
                    <p class="price">₱${Number(item.price).toLocaleString()}</p>
                    <p class="rating"><span class="star">★</span> ${item.rating || 0} / 5.0</p>
                    <div class="card-actions">
                        <button class="btn-edit" onclick="editItem(${item.id})">Edit</button>
                        <button class="btn-reviews" onclick="viewReviews(${item.id}, '${item.name.replace(/'/g, "\\'")}')">View Reviews</button>
                    </div>
                </div>
            `;
            grid.appendChild(card);
        });
    } catch (error) {
        console.error('Error loading items:', error);
        const grid = document.querySelector('.items-grid');
        grid.innerHTML = '<p style="text-align: center; width: 100%; color: red;">Failed to load items</p>';
    }
}

async function deleteItem(itemId) {
    if (confirm('Are you sure you want to delete this item?')) {
        try {
            await API.deleteItem(itemId);
            alert('Item deleted successfully');
            loadItems();
        } catch (error) {
            alert('Failed to delete item: ' + error.message);
        }
    }
}

// Edit Item Functions
async function editItem(itemId) {
    try {
        const item = await API.getItem(itemId);
        currentEditItemId = itemId;
        
        // Populate the edit form
        document.getElementById('editItemId').value = item.item_id;
        document.getElementById('editItemName').value = item.name;
        document.getElementById('editItemDesc').value = item.description || '';
        document.getElementById('editItemPrice').value = item.price;
        
        // Set image if available
        const editImg = document.getElementById('editPreviewImg');
        if (editImg && item.image_url) {
            editImg.src = item.image_url;
        }
        
        // Load variants
        editItemVariants = item.variants || [];
        renderEditVariants();
        
        // Show modal
        document.getElementById('editItemModal').style.display = 'flex';
    } catch (error) {
        alert('Failed to load item: ' + error.message);
    }
}

function closeEditModal() {
    document.getElementById('editItemModal').style.display = 'none';
    currentEditItemId = null;
    editItemVariants = [];
}

async function saveItemChanges() {
    if (!currentEditItemId) return;
    
    const itemData = {
        item_id: document.getElementById('editItemId').value,
        name: document.getElementById('editItemName').value,
        description: document.getElementById('editItemDesc').value,
        price: parseFloat(document.getElementById('editItemPrice').value.replace(/,/g, '')),
        variants: editItemVariants
    };
    
    if (!itemData.name || !itemData.price) {
        alert('Please fill in Name and Price!');
        return;
    }
    
    try {
        await API.updateItem(currentEditItemId, itemData);
        alert('Item updated successfully');
        closeEditModal();
        loadItems();
    } catch (error) {
        alert('Failed to update item: ' + error.message);
    }
}

// Variant Functions for Edit Modal
function addEditVariant() {
    const input = document.getElementById('editItemVariant');
    const variant = input.value.trim();
    
    if (variant && !editItemVariants.includes(variant)) {
        editItemVariants.push(variant);
        renderEditVariants();
        input.value = '';
    }
}

function removeEditVariant(index) {
    editItemVariants.splice(index, 1);
    renderEditVariants();
}

function renderEditVariants() {
    let container = document.getElementById('editVariantsList');
    if (!container) {
        // Create container if it doesn't exist
        const variantGroup = document.querySelector('#editItemModal .variant-input');
        if (variantGroup) {
            container = document.createElement('div');
            container.id = 'editVariantsList';
            container.className = 'variants-list';
            variantGroup.parentNode.appendChild(container);
        }
    }
    
    if (container) {
        container.innerHTML = editItemVariants.map((v, i) => `
            <span class="variant-tag">${v} <button type="button" onclick="removeEditVariant(${i})">×</button></span>
        `).join('');
    }
}

// Variant Functions for Add Modal
function addNewVariant() {
    const input = document.getElementById('itemVariant');
    const variant = input.value.trim();
    
    if (variant && !addItemVariants.includes(variant)) {
        addItemVariants.push(variant);
        renderAddVariants();
        input.value = '';
    }
}

function removeAddVariant(index) {
    addItemVariants.splice(index, 1);
    renderAddVariants();
}

function renderAddVariants() {
    let container = document.getElementById('addVariantsList');
    if (!container) {
        // Create container if it doesn't exist
        const variantGroup = document.querySelector('#addItemModal .variant-input');
        if (variantGroup) {
            container = document.createElement('div');
            container.id = 'addVariantsList';
            container.className = 'variants-list';
            variantGroup.parentNode.appendChild(container);
        }
    }
    
    if (container) {
        container.innerHTML = addItemVariants.map((v, i) => `
            <span class="variant-tag">${v} <button type="button" onclick="removeAddVariant(${i})">×</button></span>
        `).join('');
    }
}

// Reviews Modal Functions
async function viewReviews(itemId, itemName) {
    const modal = document.getElementById('reviewsModal');
    const reviewsList = document.getElementById('reviewsList');
    const title = document.getElementById('reviewsModalTitle');
    const avgRating = document.getElementById('itemAvgRating');
    const reviewCount = document.getElementById('itemReviewCount');
    
    // Show modal with loading state
    title.textContent = `Reviews for ${itemName}`;
    reviewsList.innerHTML = '<p class="no-reviews">Loading reviews...</p>';
    avgRating.textContent = '★ 0.0';
    reviewCount.textContent = '0 reviews';
    modal.style.display = 'flex';
    
    try {
        const reviews = await API.getReviewsByItem(itemId);
        
        if (reviews.length === 0) {
            reviewsList.innerHTML = '<p class="no-reviews">No reviews yet for this item</p>';
            return;
        }
        
        // Calculate average rating
        const avg = reviews.reduce((sum, r) => sum + r.rating, 0) / reviews.length;
        avgRating.textContent = `★ ${avg.toFixed(1)}`;
        reviewCount.textContent = `${reviews.length} review${reviews.length !== 1 ? 's' : ''}`;
        
        // Render reviews
        reviewsList.innerHTML = reviews.map(review => `
            <div class="review-item">
                <div class="review-header">
                    <span class="review-author">${review.customer_name}</span>
                    <span class="review-rating">${'★'.repeat(Math.round(review.rating))}${'☆'.repeat(5 - Math.round(review.rating))}</span>
                </div>
                <p class="review-comment">${review.comment || 'No comment provided'}</p>
                <span class="review-date">${new Date(review.created_at).toLocaleDateString()}</span>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading reviews:', error);
        reviewsList.innerHTML = '<p class="no-reviews" style="color: red;">Failed to load reviews</p>';
    }
}

function closeReviewsModal() {
    document.getElementById('reviewsModal').style.display = 'none';
}

// Add item modal
function openItemModal() {
    addItemVariants = []; // Reset variants
    renderAddVariants();
    document.getElementById('addItemModal').style.display = 'flex';
}

function closeItemModal() {
    document.getElementById('addItemModal').style.display = 'none';
    addItemVariants = [];
}

async function createNewItem() {
    const itemData = {
        item_id: document.getElementById('itemId').value,
        name: document.getElementById('itemName').value,
        description: document.getElementById('itemDesc').value,
        price: parseFloat(document.getElementById('itemPrice').value.replace(/,/g, '')),
        image_url: '../images/iphonee.jpg',
        variants: addItemVariants
    };
    
    if (!itemData.item_id || !itemData.name || !itemData.price) {
        alert('Please fill in Item ID, Name, and Price!');
        return;
    }
    
    try {
        await API.createItem(itemData);
        alert('Item created successfully');
        closeItemModal();
        // Clear inputs
        document.getElementById('itemId').value = '';
        document.getElementById('itemName').value = '';
        document.getElementById('itemDesc').value = '';
        document.getElementById('itemPrice').value = '';
        addItemVariants = [];
        loadItems();
    } catch (error) {
        alert('Failed to create item: ' + error.message);
    }
}

// Close modals when clicking outside
window.addEventListener('click', (event) => {
    const reviewsModal = document.getElementById('reviewsModal');
    const editModal = document.getElementById('editItemModal');
    const addModal = document.getElementById('addItemModal');
    
    if (event.target === reviewsModal) {
        closeReviewsModal();
    }
    if (event.target === editModal) {
        closeEditModal();
    }
    if (event.target === addModal) {
        closeItemModal();
    }
});

// Initialize page
if (window.location.pathname.includes('items.html')) {
    document.addEventListener('DOMContentLoaded', () => {
        loadItems();
        
        // Add item button
        document.querySelector('.add-item-btn')?.addEventListener('click', openItemModal);
        
        // Add variant buttons
        const addVariantBtn = document.querySelector('#addItemModal .add-variant-btn');
        if (addVariantBtn) {
            addVariantBtn.addEventListener('click', (e) => {
                e.preventDefault();
                addNewVariant();
            });
        }
        
        const editVariantBtn = document.querySelector('#editItemModal .add-variant-btn');
        if (editVariantBtn) {
            editVariantBtn.addEventListener('click', (e) => {
                e.preventDefault();
                addEditVariant();
            });
        }
        
        // Save changes button
        const saveBtn = document.getElementById('saveChangesBtn');
        if (saveBtn) {
            saveBtn.addEventListener('click', saveItemChanges);
        }
        
        // Enter key for variant inputs
        document.getElementById('itemVariant')?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                addNewVariant();
            }
        });
        
        document.getElementById('editItemVariant')?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                addEditVariant();
            }
        });
    });
}
