// Customer Page JavaScript
async function loadCustomers() {
    try {
        const customers = await API.getCustomers();
        const tbody = document.querySelector('#customersTableBody, tbody');
        tbody.innerHTML = '';
        
        if (customers.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">No customers found</td></tr>';
            return;
        }
        
        customers.forEach(customer => {
            const row = tbody.insertRow();
            row.innerHTML = `
                <td>${customer.customer_id}</td>
                <td>${customer.name}</td>
                <td>${customer.email}</td>
                <td>${customer.address || 'N/A'}</td>
                <td><span class="status ${customer.status === 'active' ? 'delivered' : 'pending'}">${customer.status}</span></td>
            `;
        });
    } catch (error) {
        console.error('Error loading customers:', error);
    }
}

if (window.location.pathname.includes('customer.html')) {
    loadCustomers();
}
