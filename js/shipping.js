// Shipping Page JavaScript  
let currentShippingId = null;
let currentShippingSpan = null;
let selectedShippingStatus = null;

async function loadShipping() {
    try {
        console.log('🚚 Loading shipping records...');
        const shipping = await API.getShipping();
        console.log('🚚 Shipping records received:', shipping);
        
        const tbody = document.querySelector('#shippingTableBody, tbody');
        tbody.innerHTML = '';
        
        if (!shipping || shipping.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">No shipping records found</td></tr>';
            return;
        }
        
        shipping.forEach(record => {
            const row = tbody.insertRow();
            const statusValue = typeof record.status === 'object' ? record.status.value || record.status : record.status;
            row.innerHTML = `
                <td>${record.shipping_id}</td>
                <td>${record.order_id}</td>
                <td>${record.courier}</td>
                <td>${record.address}</td>
                <td><span class="status ${statusValue}" data-id="${record.id}">${statusValue}</span></td>
            `;
        });
        
        // Attach click events to status badges
        document.querySelectorAll('.status').forEach(span => {
            span.style.cursor = "pointer";
            span.addEventListener('click', function() {
                openShippingModal(this);
            });
        });
        
        console.log('🚚 Shipping table loaded with', shipping.length, 'records');
    } catch (error) {
        console.error('Error loading shipping:', error);
        const tbody = document.querySelector('#shippingTableBody, tbody');
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: red;">Failed to load shipping: ' + error.message + '</td></tr>';
    }
}

function openShippingModal(element) {
    currentShippingId = element.getAttribute('data-id');
    currentShippingSpan = element;
    selectedShippingStatus = null;
    
    const row = element.closest('tr');
    document.getElementById('displayShippingId').innerText = row.cells[0].innerText;
    document.getElementById('shippingModal').style.display = 'flex';
    
    // Clear any previous selection
    document.querySelectorAll('.btn-opt').forEach(b => b.classList.remove('selected'));
}

function closeShippingModal() {
    document.getElementById('shippingModal').style.display = 'none';
    document.querySelectorAll('.btn-opt').forEach(b => b.classList.remove('selected'));
    currentShippingId = null;
    currentShippingSpan = null;
    selectedShippingStatus = null;
}

function selectShippingStatus(text, className) {
    selectedShippingStatus = { text, className };
    
    // Highlight the clicked button
    document.querySelectorAll('.btn-opt').forEach(b => b.classList.remove('selected'));
    event.target.classList.add('selected');
}

async function confirmShippingStatus() {
    console.log('🚚 Confirming shipping status change...');
    console.log('🚚 currentShippingId:', currentShippingId);
    console.log('🚚 selectedShippingStatus:', selectedShippingStatus);
    
    if (!currentShippingId) {
        alert("No shipping record selected!");
        return;
    }
    
    if (!selectedShippingStatus) {
        alert("Please select a shipping status!");
        return;
    }
    
    try {
        console.log('🚚 Calling API.updateShipping with:', { status: selectedShippingStatus.className });
        await API.updateShipping(currentShippingId, { 
            status: selectedShippingStatus.className 
        });
        
        console.log('🚚 Shipping status updated successfully!');
        
        // Update the UI immediately
        if (currentShippingSpan) {
            currentShippingSpan.innerText = selectedShippingStatus.text;
            currentShippingSpan.className = 'status ' + selectedShippingStatus.className;
        }
        
        closeShippingModal();
        
        // Reload shipping to get fresh data
        loadShipping();
        
    } catch (error) {
        console.error('🚚 Failed to update shipping status:', error);
        alert('Failed to update shipping status: ' + error.message);
    }
}

// Initialize when the page loads
document.addEventListener('DOMContentLoaded', function() {
    if (window.location.pathname.includes('shipping.html')) {
        console.log('🚚 Shipping page detected, initializing...');
        loadShipping();
        
        // Attach confirm button handler
        const confirmBtn = document.getElementById('confirmShippingBtn');
        if (confirmBtn) {
            confirmBtn.addEventListener('click', confirmShippingStatus);
        }
        
        // Close modal when clicking outside
        window.addEventListener('click', function(event) {
            const modal = document.getElementById('shippingModal');
            if (event.target === modal) {
                closeShippingModal();
            }
        });
    }
});
