// Rewards Page JavaScript
async function loadRewards() {
    try {
        const rewards = await API.getRewards();
        const tbody = document.querySelector('#rewardsTableBody, tbody');
        tbody.innerHTML = '';
        
        if (rewards.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align: center;">No rewards found</td></tr>';
            return;
        }
        
        rewards.forEach(reward => {
            const row = tbody.insertRow();
            const validityDate = new Date(reward.validity_period).toLocaleDateString('en-US', { 
                year: 'numeric', month: 'long', day: 'numeric' 
            });
            
            row.innerHTML = `
                <td>${reward.reward_id}</td>
                <td>${reward.type}</td>
                <td>${reward.code}</td>
                <td>-${Number(reward.discount).toFixed(2)}</td>
                <td>${validityDate}</td>
                <td><span class="status ${reward.status === 'valid' ? 'delivered' : 'cancelled'}">${reward.status}</span></td>
            `;
        });
    } catch (error) {
        console.error('Error loading rewards:', error);
    }
}

function openRewardModal() {
    document.getElementById('addRewardModal').style.display = 'flex';
}

function closeRewardModal() {
    document.getElementById('addRewardModal').style.display = 'none';
}

async function saveReward() {
    const rewardData = {
        reward_id: document.getElementById('rewardId').value,
        type: document.getElementById('rewardType').value,
        code: document.getElementById('rewardCode').value,
        discount: parseFloat(document.getElementById('rewardDiscount').value),
        validity_period: document.getElementById('rewardValidity').value
    };
    
    try {
        await API.createReward(rewardData);
        alert('Reward created successfully');
        closeRewardModal();
        loadRewards();
    } catch (error) {
        alert('Failed to create reward: ' + error.message);
    }
}

if (window.location.pathname.includes('rewards.html')) {
    loadRewards();
    document.querySelector('.add-btn')?.addEventListener('click', openRewardModal);
}
