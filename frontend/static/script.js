const PROD_API_URL = '/api';
const API_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' || !window.location.hostname
    ? `http://${window.location.hostname || 'localhost'}:8009`
    : PROD_API_URL;

// DOM Elements
const authSection = document.getElementById('auth-section');
const dashboardSection = document.getElementById('dashboard-section');
const registerForm = document.getElementById('register-form');
const loginForm = document.getElementById('login-form');
const notification = document.getElementById('notification');

// Nav Toggling Logic
const navDashboard = document.getElementById('nav-dashboard');
const navProfile = document.getElementById('nav-profile');
const mainDashboardView = document.getElementById('main-dashboard-view');
const profileView = document.getElementById('profile-view');

if (navDashboard && navProfile) {
    navDashboard.addEventListener('click', (e) => {
        e.preventDefault();
        showView('dashboard');
    });

    navProfile.addEventListener('click', (e) => {
        e.preventDefault();
        showView('profile');
        loadProfile();
    });
}

function showView(viewName) {
    if (viewName === 'dashboard') {
        if (mainDashboardView) mainDashboardView.classList.remove('hidden');
        if (profileView) profileView.classList.add('hidden');
        if (navDashboard) navDashboard.classList.add('active');
        if (navProfile) navProfile.classList.remove('active');
    } else {
        if (mainDashboardView) mainDashboardView.classList.add('hidden');
        if (profileView) profileView.classList.remove('hidden');
        if (navDashboard) navDashboard.classList.remove('active');
        if (navProfile) navProfile.classList.add('active');
    }
}

function getAuthHeaders() {
    const token = localStorage.getItem('access_token');
    return {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : ''
    };
}

async function loadProfile() {
    try {
        const response = await fetch(`${API_URL}/profile`, {
            headers: getAuthHeaders()
        });
        const data = await response.json();
        if (response.ok) {
            document.getElementById('prof-username').textContent = data.username;
            document.getElementById('prof-email').textContent = data.email;
            document.getElementById('prof-phone').textContent = data.phone;
            document.getElementById('prof-role').textContent = data.role;
        } else {
            showNotification(data.detail || 'Failed to load profile', 'error');
            if (response.status === 401) logout();
        }
    } catch (error) {
        console.error('Profile Load Error:', error);
        showNotification('Connection error (Check Console)', 'error');
    }
}

// Switch Auth Toggle
document.getElementById('link-login').addEventListener('click', (e) => {
    e.preventDefault();
    registerForm.classList.add('hidden');
    loginForm.classList.remove('hidden');
});

document.getElementById('link-register').addEventListener('click', (e) => {
    e.preventDefault();
    loginForm.classList.add('hidden');
    registerForm.classList.remove('hidden');
});

// Notifications
function showNotification(message, type = 'success') {
    notification.textContent = message;
    notification.className = `notification ${type}`;
    notification.classList.remove('hidden');
    setTimeout(() => {
        notification.classList.add('hidden');
    }, 4000);
}

// Registration
document.getElementById('btn-register').addEventListener('click', async () => {
    const username = document.getElementById('reg-username').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;
    const phone = document.getElementById('reg-phone').value;

    if (!username || !email || !password || !phone) {
        return showNotification('Please fill all fields', 'error');
    }

    try {
        const response = await fetch(`${API_URL}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password, phone })
        });

        const data = await response.json();
        if (response.ok) {
            showNotification('Registration successful! Please login.');
            registerForm.classList.add('hidden');
            loginForm.classList.remove('hidden');
        } else {
            showNotification(data.detail || 'Registration failed', 'error');
        }
    } catch (error) {
        console.error('Registration Connection Error:', error);
        showNotification('Connection error (Check Console)', 'error');
    }
});

// Login
document.getElementById('btn-login').addEventListener('click', async () => {
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    if (!username || !password) {
        return showNotification('Please enter credentials', 'error');
    }

    try {
        const response = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();
        if (response.ok) {
            showNotification('Login successful!');
            localStorage.setItem('username', data.username);
            localStorage.setItem('access_token', data.access_token);
            showDashboard(data.username);
        } else {
            showNotification(data.detail || 'Login failed', 'error');
        }
    } catch (error) {
        console.error('Login Connection Error Details:', {
            message: error.message,
            stack: error.stack,
            url: `${API_URL}/login`
        });
        showNotification(`Connection error: ${error.message}. Check if your backend is running at ${API_URL}`, 'error');
    }
});

function showDashboard(username) {
    authSection.classList.add('hidden');
    dashboardSection.classList.remove('hidden');
    document.getElementById('hello-user').textContent = username;

    showView('dashboard');

    // Initialize Dashboard Components
    renderTransactions();
    drawAnalyticsChart();
}

// Check Balance
document.getElementById('btn-check-balance').addEventListener('click', async () => {
    try {
        const response = await fetch(`${API_URL}/balance`, {
            headers: getAuthHeaders()
        });

        const data = await response.json();
        if (response.ok) {
            const balanceEl = document.getElementById('balance-display');
            balanceEl.textContent = `₹ ${data.balance.toLocaleString()}`;

            // Party Popper Animation
            confetti({
                particleCount: 150,
                spread: 70,
                origin: { y: 0.6 },
                colors: ['#6366f1', '#f97316', '#ec4899']
            });

            showNotification(`Your balance is: ₹ ${data.balance.toLocaleString()}`);
        } else {
            showNotification(data.detail || 'Session expired. Please login again.', 'error');
            if (response.status === 401) logout();
        }
    } catch (error) {
        console.error('Balance Connection Error:', error);
        showNotification('Connection error (Check Console)', 'error');
    }
});

// Dummy Transactions
function renderTransactions() {
    const txList = document.getElementById('tx-list');
    const transactions = [
        { name: 'Apple Store', category: 'Technology', date: 'Feb 20, 2026', amount: -999.00, status: 'Completed', icon: '🍎' },
        { name: 'Starbucks Coffee', category: 'Food & Drink', date: 'Feb 19, 2026', amount: -15.50, status: 'Completed', icon: '☕' },
        { name: 'Salary Deposit', category: 'Income', date: 'Feb 18, 2026', amount: 5000.00, status: 'Completed', icon: '💰' },
        { name: 'Amazon Prime', category: 'Subscription', date: 'Feb 17, 2026', amount: -14.99, status: 'Pending', icon: '📦' }
    ];

    txList.innerHTML = transactions.map(tx => `
        <div class="tx-item">
            <div class="tx-left">
                <div class="tx-icon">${tx.icon}</div>
                <div class="tx-info">
                    <h4>${tx.name}</h4>
                    <p>${tx.category} • ${tx.date}</p>
                </div>
            </div>
            <div class="tx-right">
                <div class="tx-amount ${tx.amount > 0 ? 'amount-pos' : 'amount-neg'}">
                    ${tx.amount > 0 ? '+' : ''}${tx.amount.toFixed(2)}
                </div>
                <div class="tx-status">${tx.status}</div>
            </div>
        </div>
    `).join('');
}

// Analytics Chart (Canvas Drawing)
function drawAnalyticsChart() {
    const canvas = document.getElementById('analyticsChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const container = canvas.parentElement;
    canvas.width = container.clientWidth;
    canvas.height = container.clientHeight;

    const data = [40, 150, 80, 200, 110, 240, 190];
    const labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

    const padding = 40;
    const width = canvas.width - padding * 2;
    const height = canvas.height - padding * 2;
    const step = width / (data.length - 1);

    // Draw Background Lines
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
    ctx.lineWidth = 1;
    for (let i = 0; i < 5; i++) {
        const y = padding + (height / 4) * i;
        ctx.beginPath();
        ctx.moveTo(padding, y);
        ctx.lineTo(padding + width, y);
        ctx.stroke();
    }

    // Draw Labels
    ctx.fillStyle = '#a1a1aa';
    ctx.font = '12px Outfit';
    labels.forEach((label, i) => {
        ctx.fillText(label, padding + i * step - 10, canvas.height - 15);
    });

    // Draw Line
    ctx.beginPath();
    ctx.lineWidth = 3;
    const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
    gradient.addColorStop(0, '#f97316');
    gradient.addColorStop(1, '#ec4899');
    ctx.strokeStyle = gradient;

    data.forEach((val, i) => {
        const x = padding + i * step;
        const y = (canvas.height - padding) - (val / 250) * height;
        if (i === 0) ctx.moveTo(x, y);
        else {
            // Bezier curve for smoothness
            const prevX = padding + (i - 1) * step;
            const prevY = (canvas.height - padding) - (data[i - 1] / 250) * height;
            const cp1x = prevX + (x - prevX) / 2;
            ctx.bezierCurveTo(cp1x, prevY, cp1x, y, x, y);
        }
    });
    ctx.stroke();

    // Draw Gradient Area
    ctx.lineTo(padding + width, canvas.height - padding);
    ctx.lineTo(padding, canvas.height - padding);
    const fillGradient = ctx.createLinearGradient(0, padding, 0, canvas.height - padding);
    fillGradient.addColorStop(0, 'rgba(249, 115, 22, 0.2)');
    fillGradient.addColorStop(1, 'rgba(236, 72, 153, 0)');
    ctx.fillStyle = fillGradient;
    ctx.fill();
}

// Logout
document.getElementById('btn-logout').addEventListener('click', logout);

function logout() {
    localStorage.removeItem('username');
    localStorage.removeItem('access_token');
    authSection.classList.remove('hidden');
    dashboardSection.classList.add('hidden');
}

// Check auto-login
window.onload = () => {
    const savedUser = localStorage.getItem('username');
    if (savedUser) {
        showDashboard(savedUser);
    }
};

window.addEventListener('resize', drawAnalyticsChart);
