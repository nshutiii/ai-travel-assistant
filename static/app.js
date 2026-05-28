// API Configuration
const API_BASE = window.location.origin;

// State Management
const state = {
    token: localStorage.getItem('token') || '',
    user: null,
    trips: [],
    currentTrip: null,
    currentItinerary: null,
    currentDay: 1
};

// DOM Elements
const views = {
    auth: document.getElementById('view-auth'),
    dashboard: document.getElementById('view-dashboard'),
    itinerary: document.getElementById('view-itinerary')
};

// Toast Notifications Helper
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    const toastText = document.getElementById('toast-text');
    const toastIcon = document.getElementById('toast-icon');
    
    toast.className = `toast toast-${type}`;
    toastText.innerText = message;
    
    if (type === 'success') {
        toastIcon.innerHTML = '<i class="fa-solid fa-circle-check"></i>';
    } else if (type === 'error') {
        toastIcon.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i>';
    } else {
        toastIcon.innerHTML = '<i class="fa-solid fa-circle-info"></i>';
    }
    
    toast.classList.remove('hidden');
    
    setTimeout(() => {
        toast.classList.add('hidden');
    }, 4000);
}

// Request Helper
async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    
    // Set headers
    options.headers = options.headers || {};
    options.headers['Content-Type'] = 'application/json';
    if (state.token) {
        options.headers['Authorization'] = `Bearer ${state.token}`;
    }
    
    try {
        const response = await fetch(url, options);
        
        if (response.status === 401) {
            // Token expired or invalid
            handleLogout();
            showToast('Session expired. Please sign in again.', 'error');
            throw new Error('Unauthorized');
        }
        
        if (response.status === 204) {
            return null;
        }
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'An error occurred');
        }
        
        return data;
    } catch (error) {
        console.error(`API Error on ${endpoint}:`, error);
        throw error;
    }
}

// Check Authentication & User Profile
async function checkAuth() {
    if (!state.token) {
        switchView('auth');
        return;
    }
    
    try {
        const user = await apiRequest('/users/me');
        state.user = user;
        document.getElementById('user-email').innerText = user.email;
        document.getElementById('btn-logout').classList.remove('hidden');
        switchView('dashboard');
        loadDashboard();
    } catch (error) {
        handleLogout();
    }
}

// Switch SPA Views
function switchView(viewName) {
    Object.keys(views).forEach(key => {
        if (key === viewName) {
            views[key].classList.remove('hidden');
        } else {
            views[key].classList.add('hidden');
        }
    });
}

// Handle Login
document.getElementById('form-login').addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    
    try {
        const data = await apiRequest('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
        
        state.token = data.access_token;
        localStorage.setItem('token', data.access_token);
        showToast('Successfully signed in!', 'success');
        
        // Reset forms
        document.getElementById('form-login').reset();
        await checkAuth();
    } catch (error) {
        showToast(error.message || 'Login failed', 'error');
    }
});

// Handle Register
document.getElementById('form-register').addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    
    try {
        await apiRequest('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
        
        showToast('Registration successful! Please sign in.', 'success');
        
        // Switch tab to login
        document.getElementById('tab-login-trigger').click();
        document.getElementById('login-email').value = email;
        document.getElementById('form-register').reset();
    } catch (error) {
        showToast(error.message || 'Registration failed', 'error');
    }
});

// Auth Tabs Toggle
document.getElementById('tab-login-trigger').addEventListener('click', (e) => {
    document.getElementById('tab-register-trigger').classList.remove('active');
    e.target.classList.add('active');
    document.getElementById('auth-register-form').classList.remove('active');
    document.getElementById('auth-login-form').classList.add('active');
});

document.getElementById('tab-register-trigger').addEventListener('click', (e) => {
    document.getElementById('tab-login-trigger').classList.remove('active');
    e.target.classList.add('active');
    document.getElementById('auth-login-form').classList.remove('active');
    document.getElementById('auth-register-form').classList.add('active');
});

// Handle Logout
function handleLogout() {
    state.token = '';
    state.user = null;
    state.trips = [];
    state.currentTrip = null;
    state.currentItinerary = null;
    localStorage.removeItem('token');
    document.getElementById('user-email').innerText = 'Guest';
    document.getElementById('btn-logout').classList.add('hidden');
    switchView('auth');
}

document.getElementById('btn-logout').addEventListener('click', () => {
    handleLogout();
    showToast('Signed out successfully.', 'info');
});

// LOAD DASHBOARD
async function loadDashboard() {
    try {
        const trips = await apiRequest('/trips');
        state.trips = trips;
        
        // Stats calculations
        const totalTrips = trips.length;
        const totalBudget = trips.reduce((sum, t) => sum + parseFloat(t.budget), 0);
        
        document.getElementById('stat-total-trips').innerText = totalTrips;
        document.getElementById('stat-total-budget').innerText = `$${totalBudget.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
        
        // Calculate generated itineraries count
        let generatedCount = 0;
        const listContainer = document.getElementById('trips-list-container');
        listContainer.innerHTML = '';
        
        if (trips.length === 0) {
            listContainer.innerHTML = `
                <div class="empty-state glass">
                    <div class="empty-icon"><i class="fa-solid fa-compass-drafting"></i></div>
                    <h3>No vacations planned yet</h3>
                    <p>Begin your AI-integrated journey by clicking 'Plan New Trip' above.</p>
                </div>
            `;
            document.getElementById('stat-active-itins').innerText = '0';
            return;
        }
        
        for (const trip of trips) {
            // Check if itinerary is generated (async)
            let hasItin = false;
            try {
                const itin = await apiRequest(`/itineraries/${trip.id}`);
                if (itin && itin.itinerary && itin.itinerary.length > 0) {
                    hasItin = true;
                    generatedCount++;
                }
            } catch (e) {
                // If 404, remains false
            }
            
            const card = document.createElement('div');
            card.className = 'trip-card glass';
            
            card.innerHTML = `
                <div class="trip-card-bg"></div>
                <div class="trip-card-header">
                    <div>
                        <h3>${trip.destination}</h3>
                        <span class="badge badge-style-${trip.trip_style}">${trip.trip_style}</span>
                    </div>
                    <span class="badge"><i class="fa-solid fa-calendar"></i> ${trip.days} Days</span>
                </div>
                <div class="trip-card-body">
                    <div class="trip-detail-row">
                        <span>Total Budget:</span>
                        <strong>$${parseFloat(trip.budget).toLocaleString(undefined, {minimumFractionDigits: 2})}</strong>
                    </div>
                    <div class="trip-detail-row">
                        <span>Daily Budget:</span>
                        <strong>$${(parseFloat(trip.budget) / trip.days).toLocaleString(undefined, {maximumFractionDigits: 2})} / day</strong>
                    </div>
                </div>
                <div class="trip-card-actions">
                    <button class="btn btn-outline btn-sm btn-delete-trip" data-id="${trip.id}"><i class="fa-solid fa-trash-can"></i> Delete</button>
                    <button class="btn btn-primary btn-sm btn-view-itin" data-id="${trip.id}">
                        ${hasItin ? '<i class="fa-solid fa-compass"></i> View Itinerary' : '<i class="fa-solid fa-wand-magic-sparkles"></i> Generate AI Itinerary'}
                    </button>
                </div>
            `;
            
            listContainer.appendChild(card);
        }
        
        document.getElementById('stat-active-itins').innerText = generatedCount;
        
        // Attach Event Listeners to dynamic elements
        document.querySelectorAll('.btn-delete-trip').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.stopPropagation();
                const id = e.currentTarget.getAttribute('data-id');
                if (confirm('Are you sure you want to delete this trip and its itinerary?')) {
                    try {
                        await apiRequest(`/trips/${id}`, { method: 'DELETE' });
                        showToast('Trip deleted successfully', 'success');
                        loadDashboard();
                    } catch (error) {
                        showToast(error.message, 'error');
                    }
                }
            });
        });
        
        document.querySelectorAll('.btn-view-itin').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = e.currentTarget.getAttribute('data-id');
                openItinerary(parseInt(id));
            });
        });
        
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// MODAL CONTROLS
const modal = document.getElementById('modal-create-trip');
document.getElementById('btn-open-create').addEventListener('click', () => {
    modal.classList.remove('hidden');
});
document.getElementById('btn-close-modal').addEventListener('click', () => {
    modal.classList.add('hidden');
});
document.getElementById('btn-cancel-trip').addEventListener('click', () => {
    modal.classList.add('hidden');
});

// CREATE NEW TRIP
document.getElementById('form-create-trip').addEventListener('submit', async (e) => {
    e.preventDefault();
    const destination = document.getElementById('trip-destination').value;
    const days = parseInt(document.getElementById('trip-days').value);
    const budget = parseFloat(document.getElementById('trip-budget').value);
    const trip_style = document.getElementById('trip-style').value;
    
    try {
        const trip = await apiRequest('/trips', {
            method: 'POST',
            body: JSON.stringify({ destination, days, budget, trip_style })
        });
        
        showToast('Trip created successfully! Launching AI Planner...', 'success');
        modal.classList.add('hidden');
        document.getElementById('form-create-trip').reset();
        
        // Trigger AI Generation immediately
        openItinerary(trip.id, true);
    } catch (error) {
        showToast(error.message, 'error');
    }
});

// OPEN ITINERARY VIEW
async function openItinerary(tripId, forceGenerate = false) {
    const trip = state.trips.find(t => t.id === tripId) || await apiRequest(`/trips/${tripId}`);
    state.currentTrip = trip;
    
    document.getElementById('itin-dest-title').innerText = `${trip.destination} Trip`;
    const styleBadge = document.getElementById('itin-badge');
    styleBadge.innerText = `${trip.trip_style} style`;
    styleBadge.className = `badge badge-style-${trip.trip_style}`;
    
    let itinerary = null;
    
    if (!forceGenerate) {
        try {
            itinerary = await apiRequest(`/itineraries/${tripId}`);
        } catch (e) {
            // Itinerary not found, we will trigger generation
        }
    }
    
    if (!itinerary) {
        // Trigger generation loader
        const loader = document.getElementById('loader-overlay');
        const loaderMsg = document.getElementById('loader-message');
        const loaderProgress = document.getElementById('loader-progress-fill');
        
        loader.classList.remove('hidden');
        loaderMsg.innerText = `Searching for top accommodations & dining in ${trip.destination}...`;
        
        try {
            itinerary = await apiRequest(`/itineraries/generate/${tripId}`, {
                method: 'POST'
            });
            showToast('AI Itinerary fully generated!', 'success');
        } catch (error) {
            showToast('AI failed. Creating dynamic smart local layout.', 'warning');
        } finally {
            loader.classList.add('hidden');
        }
    }
    
    if (itinerary) {
        state.currentItinerary = itinerary;
        state.currentDay = 1;
        switchView('itinerary');
        renderItinerary();
    } else {
        showToast('Could not load itinerary.', 'error');
    }
}

// BACK BUTTON
document.getElementById('btn-back-to-dashboard').addEventListener('click', () => {
    switchView('dashboard');
    loadDashboard();
});

// REGENERATE BUTTON
document.getElementById('btn-regenerate-itin').addEventListener('click', () => {
    if (confirm('Are you sure you want to regenerate? The current plan will be replaced by a fresh AI search.')) {
        openItinerary(state.currentTrip.id, true);
    }
});

// RENDER ITINERARY DETAILS
function renderItinerary() {
    const trip = state.currentTrip;
    const itin = state.currentItinerary;
    
    // 1. Calculate overall costs & statistics
    let totalLodgingCost = 0;
    let totalEstimatedCost = 0;
    
    itin.itinerary.forEach(day => {
        totalLodgingCost += day.accommodation_cost || 0;
        totalEstimatedCost += day.total_day_cost || (day.accommodation_cost || 0) + (day.food_cost || 0) + (day.other_cost || 0);
    });
    
    const remainingBuffer = parseFloat(trip.budget) - totalEstimatedCost;
    const spentPct = Math.min(Math.round((totalEstimatedCost / parseFloat(trip.budget)) * 100), 100);
    
    // 2. Render Left Pane (Budget Breakdown Rings)
    document.getElementById('itin-total-budget').innerText = `$${parseFloat(trip.budget).toFixed(2)}`;
    document.getElementById('itin-estimated-cost').innerText = `$${totalEstimatedCost.toFixed(2)}`;
    
    const remElem = document.getElementById('itin-remaining-budget');
    remElem.innerText = `$${remainingBuffer.toFixed(2)}`;
    if (remainingBuffer < 0) {
        remElem.className = 'text-danger';
        showToast('Warning: Itinerary slightly exceeds target budget bounds!', 'warning');
    } else {
        remElem.className = 'text-pink';
    }
    
    // Gauge Ring color & visual percentage
    const gauge = document.getElementById('itin-budget-fill');
    const spentPctElem = document.getElementById('itin-spent-pct');
    spentPctElem.innerText = `${spentPct}%`;
    
    const parentRing = document.getElementById('itin-budget-fill').parentElement;
    if (remainingBuffer < 0) {
        parentRing.style.background = `conic-gradient(var(--danger) ${spentPct}%, rgba(255, 255, 255, 0.05) ${spentPct}%)`;
    } else {
        parentRing.style.background = `conic-gradient(var(--primary) ${spentPct}%, rgba(255, 255, 255, 0.05) ${spentPct}%)`;
    }
    
    // 3. Render Accommodation details
    const firstDay = itin.itinerary[0];
    if (firstDay && firstDay.accommodation) {
        document.getElementById('lodging-focus-section').classList.remove('hidden');
        document.getElementById('lodging-name').innerText = firstDay.accommodation.split(' - ')[0];
        document.getElementById('lodging-desc').innerText = firstDay.accommodation.split(' - ')[1] || 'Real-world local lodging chosen to fit your budget.';
        document.getElementById('lodging-night-cost').innerText = `$${(firstDay.accommodation_cost || 0).toFixed(2)}`;
        document.getElementById('lodging-total-cost').innerText = `$${totalLodgingCost.toFixed(2)} / total`;
    } else {
        document.getElementById('lodging-focus-section').classList.add('hidden');
    }
    
    // 4. Render Day Tabs
    const tabContainer = document.getElementById('day-tabs-container');
    tabContainer.innerHTML = '';
    
    itin.itinerary.forEach(day => {
        const btn = document.createElement('button');
        btn.className = `day-tab-btn ${state.currentDay === day.day ? 'active' : ''}`;
        btn.innerText = `Day ${day.day}`;
        btn.setAttribute('data-day', day.day);
        
        btn.addEventListener('click', (e) => {
            state.currentDay = parseInt(e.currentTarget.getAttribute('data-day'));
            renderDaySchedule();
        });
        
        tabContainer.appendChild(btn);
    });
    
    // Render current day
    renderDaySchedule();
}

// RENDER CURRENT DAY DETAIL TIMELINE & CHIPS
function renderDaySchedule() {
    // Set active tab styling
    document.querySelectorAll('.day-tab-btn').forEach(btn => {
        if (parseInt(btn.getAttribute('data-day')) === state.currentDay) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
    
    const dayData = state.currentItinerary.itinerary.find(d => d.day === state.currentDay);
    if (!dayData) return;
    
    // Cost chips update
    const accommodationCost = dayData.accommodation_cost || 0;
    const foodCost = dayData.food_cost || 0;
    const otherCost = dayData.other_cost || 0;
    const totalCost = dayData.total_day_cost || (accommodationCost + foodCost + otherCost);
    
    document.getElementById('day-cost-lodging').innerText = `$${accommodationCost.toFixed(2)}`;
    document.getElementById('day-cost-food').innerText = `$${foodCost.toFixed(2)}`;
    document.getElementById('day-cost-other').innerText = `$${otherCost.toFixed(2)}`;
    document.getElementById('day-cost-total').innerText = `$${totalCost.toFixed(2)}`;
    
    // Timeline Render
    const timeline = document.getElementById('activities-timeline');
    timeline.innerHTML = '';
    
    dayData.activities.forEach((act, idx) => {
        let timeLabel = "Morning";
        let icon = "fa-sun";
        
        if (act.toLowerCase().startsWith("morning:")) {
            timeLabel = "Morning Attraction";
            icon = "fa-umbrella-beach";
            act = act.substring("morning:".length).trim();
        } else if (act.toLowerCase().startsWith("afternoon:")) {
            timeLabel = "Afternoon Dining";
            icon = "fa-utensils";
            act = act.substring("afternoon:".length).trim();
        } else if (act.toLowerCase().startsWith("evening:")) {
            timeLabel = "Evening Experience";
            icon = "fa-moon";
            act = act.substring("evening:".length).trim();
        } else {
            // fallback labeling based on indices
            if (idx === 1) {
                timeLabel = "Afternoon Lunch";
                icon = "fa-bowl-food";
            } else if (idx === 2) {
                timeLabel = "Evening Entertainment";
                icon = "fa-champagne-glasses";
            }
        }
        
        const titleText = act.split(' - ')[0] || act;
        const descText = act.split(' - ')[1] || 'Real local destination.';
        
        const timelineItem = document.createElement('div');
        timelineItem.className = 'timeline-item';
        
        timelineItem.innerHTML = `
            <div class="timeline-dot"><i class="fa-solid ${icon}"></i></div>
            <div class="timeline-content">
                <div class="timeline-time">${timeLabel}</div>
                <div class="timeline-title">${titleText}</div>
                <div class="timeline-desc">${descText}</div>
            </div>
        `;
        
        timeline.appendChild(timelineItem);
    });
}

// Initial Run
window.addEventListener('DOMContentLoaded', () => {
    checkAuth();
});
