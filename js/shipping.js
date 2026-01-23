// Shipping Page JavaScript  
async function loadShipping() {
    try {
        const shipping = await API.getShipping();
        const tbody = document.querySelector('#shippingTableBody, tbody');
        tbody.innerHTML = '';
        
        if (shipping.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">No shipping records found</td></tr>';
            return;
        }
        
        shipping.forEach(record => {
            const row = tbody.insertRow();
            row.innerHTML = `
                <td>${record.shipping_id}</td>
                <td>${record.order_id}</td>
                <td>${record.courier}</td>
                <td>${record.address}</td>
                <td><span class="status ${record.status}" data-id="${record.id}">${record.status}</span></td>
            `;
        });
        
        // Attach click events
        document.querySelectorAll('.status').forEach(span => {
            span.style.cursor = "pointer";
            span.addEventListener('click', function() {
                openShippingModal(this);
            });
        });
    } catch (error) {
        console.error('Error loading shipping:', error);
    }
}

let currentShippingId = null;

function openShippingModal(element) {
    currentShippingId = element.getAttribute('data-id');
    const row = element.closest('tr');
    document.getElementById('displayShippingId').innerText = row.cells[0].innerText;
    document.getElementById('shippingModal').style.display = 'flex';
}

function closeShippingModal() {
    document.getElementById('shippingModal').style.display = 'none';
}

function selectShippingStatus(text, className) {
    window.selectedShippingStatus = { text, className };
}

async function confirmShippingStatus() {
    if (currentShippingId && window.selectedShippingStatus) {
        try {
            await API.updateShipping(currentShippingId, { 
                status: window.selectedShippingStatus.className 
            });
            closeShippingModal();
            loadShipping();
        } catch (error) {
            alert('Failed to update shipping status: ' + error.message);
        }
    }
}

if (window.location.pathname.includes('shipping.html')) {
    loadShipping();
    document.getElementById('confirmShippingBtn')?.addEventListener('click', confirmShippingStatus);
}
