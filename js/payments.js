// Payments Page JavaScript
async function loadPayments() {
    try {
        const payments = await API.getPayments();
        const tbody = document.getElementById('paymentsTableBody');
        tbody.innerHTML = '';
        
        if (payments.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align: center;">No payments found</td></tr>';
            updatePaymentStats([], 0);
            return;
        }
        
        // Calculate stats
        const totalRevenue = payments.reduce((sum, p) => sum + Number(p.amount), 0);
        const totalTransactions = payments.length;
        const paidPayments = payments.filter(p => p.status === 'paid').length;
        const pendingPayments = payments.filter(p => p.status === 'pending').length;
        
        // Update stat cards
        updatePaymentStats(payments, totalRevenue);
        
        payments.forEach(payment => {
            const row = tbody.insertRow();
            row.dataset.paymentId = payment.id;
            row.innerHTML = `
                <td>${payment.payment_id}</td>
                <td>${payment.order_id}</td>
                <td>${payment.customer_name}</td>
                <td>${payment.email}</td>
                <td>${payment.payment_method}</td>
                <td><span class="status-badge ${payment.status}" style="cursor: pointer;" onclick="openPaymentModal(this, ${payment.id})">${payment.status}</span></td>
            `;
        });
    } catch (error) {
        console.error('Error loading payments:', error);
        document.getElementById('paymentsTableBody').innerHTML = 
            '<tr><td colspan="6" style="text-align: center; color: red;">Failed to load payments</td></tr>';
    }
}

function updatePaymentStats(payments, totalRevenue) {
    const statValues = document.querySelectorAll('.stat-value');
    const paidPayments = payments.filter(p => p.status === 'paid').length;
    const pendingPayments = payments.filter(p => p.status === 'pending').length;
    
    if (statValues.length >= 4) {
        statValues[0].textContent = '₱' + totalRevenue.toLocaleString();
        statValues[1].textContent = payments.length;
        statValues[2].textContent = paidPayments;
        statValues[3].textContent = pendingPayments;
    }
}

// Payment status update functionality
let currentPaymentId = null;
let currentPaymentSpan = null;
let selectedStatusText = "";
let selectedStatusClass = "";

function openPaymentModal(element, paymentId) {
    currentPaymentSpan = element;
    currentPaymentId = paymentId;
    
    // Get PaymentID from the first cell of the row
    const row = element.closest('tr');
    const displayId = row.cells[0].innerText;
    
    document.getElementById('displayPaymentId').innerText = displayId;
    document.getElementById('paymentModal').style.display = 'flex';
    
    // Reset selection
    document.querySelectorAll('.btn-opt').forEach(b => b.classList.remove('selected'));
    selectedStatusText = "";
    selectedStatusClass = "";
}

function closePaymentModal() {
    document.getElementById('paymentModal').style.display = 'none';
    document.querySelectorAll('.btn-opt').forEach(b => b.classList.remove('selected'));
    currentPaymentId = null;
    currentPaymentSpan = null;
}

function selectPaymentStatus(text, className) {
    selectedStatusText = text.toLowerCase();
    selectedStatusClass = className;
    
    document.querySelectorAll('.btn-opt').forEach(b => b.classList.remove('selected'));
    event.target.classList.add('selected');
}

async function confirmPaymentStatus() {
    if (!currentPaymentId || selectedStatusText === "") {
        alert("Please select a status first!");
        return;
    }
    
    try {
        await API.updatePayment(currentPaymentId, { status: selectedStatusText });
        
        // Update UI
        if (currentPaymentSpan) {
            currentPaymentSpan.innerText = selectedStatusText;
            currentPaymentSpan.className = 'status-badge ' + selectedStatusClass;
        }
        
        closePaymentModal();
        
        // Reload to update stats
        loadPayments();
    } catch (error) {
        alert('Failed to update payment status: ' + error.message);
    }
}

// Initialize on page load
if (window.location.pathname.includes('payments.html')) {
    document.addEventListener('DOMContentLoaded', () => {
        loadPayments();
        
        // Setup confirm button
        const confirmBtn = document.getElementById('confirmPaymentBtn');
        if (confirmBtn) {
            confirmBtn.onclick = confirmPaymentStatus;
        }
    });
}
