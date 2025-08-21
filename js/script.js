// Simping Cats Interactive Script with Analytics
let noButtonClickCount = 0;
let yesButtonClickCount = 0;
const catApiKey = 'live_1';

// Analytics System
let analytics = {
    userId: null,
    sessionId: null,
    startTime: Date.now(),
    
    // Initialize analytics
    init() {
        this.userId = this.getUserId();
        this.sessionId = this.generateSessionId();
        this.recordVisit();
        console.log('Analytics initialized for user:', this.userId);
    },
    
    // Get or create user ID using localStorage only
    getUserId() {
        let userId = localStorage.getItem('simpingCatsUserId');
        if (!userId) {
            userId = 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('simpingCatsUserId', userId);
        }
        return userId;
    },
    
    // Generate session ID
    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    },
    
    // Get browser info
    getBrowserInfo() {
        return {
            userAgent: navigator.userAgent,
            language: navigator.language,
            platform: navigator.platform,
            cookieEnabled: navigator.cookieEnabled,
            screenResolution: screen.width + 'x' + screen.height,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
            timestamp: new Date().toISOString()
        };
    },
    
    // Record a visit
    recordVisit() {
        const visits = JSON.parse(localStorage.getItem('simpingCatsVisits') || '[]');
        const visit = {
            userId: this.userId,
            sessionId: this.sessionId,
            visitTime: new Date().toISOString(),
            browserInfo: this.getBrowserInfo()
        };
        visits.push(visit);
        localStorage.setItem('simpingCatsVisits', JSON.stringify(visits));
    },
    
    // Track button clicks
    trackClick(buttonType, extraData = {}) {
        const clicks = JSON.parse(localStorage.getItem('simpingCatsClicks') || '[]');
        const click = {
            userId: this.userId,
            sessionId: this.sessionId,
            buttonType: buttonType, // 'yes' or 'no'
            timestamp: new Date().toISOString(),
            clickCount: buttonType === 'yes' ? yesButtonClickCount : noButtonClickCount,
            ...extraData
        };
        clicks.push(click);
        localStorage.setItem('simpingCatsClicks', JSON.stringify(clicks));
        
        // Also update user stats
        this.updateUserStats(buttonType);
    },
    
    // Update user statistics
    updateUserStats(buttonType) {
        const userStats = JSON.parse(localStorage.getItem('simpingCatsUserStats') || '{}');
        if (!userStats[this.userId]) {
            userStats[this.userId] = {
                userId: this.userId,
                firstVisit: new Date().toISOString(),
                totalYes: 0,
                totalNo: 0,
                totalSessions: 0,
                lastVisit: new Date().toISOString()
            };
        }
        
        userStats[this.userId][`total${buttonType.charAt(0).toUpperCase() + buttonType.slice(1)}`]++;
        userStats[this.userId].lastVisit = new Date().toISOString();
        
        localStorage.setItem('simpingCatsUserStats', JSON.stringify(userStats));
    },
    
    // Get analytics data
    getAnalyticsData() {
        return {
            visits: JSON.parse(localStorage.getItem('simpingCatsVisits') || '[]'),
            clicks: JSON.parse(localStorage.getItem('simpingCatsClicks') || '[]'),
            userStats: JSON.parse(localStorage.getItem('simpingCatsUserStats') || '{}')
        };
    },
    
    // Generate analytics summary
    generateSummary() {
        const data = this.getAnalyticsData();
        const totalVisits = data.visits.length;
        const totalClicks = data.clicks.length;
        const totalUsers = Object.keys(data.userStats).length;
        const totalYesClicks = data.clicks.filter(c => c.buttonType === 'yes').length;
        const totalNoClicks = data.clicks.filter(c => c.buttonType === 'no').length;
        
        return {
            totalUsers,
            totalVisits,
            totalClicks,
            totalYesClicks,
            totalNoClicks,
            yesPercentage: totalClicks > 0 ? ((totalYesClicks / totalClicks) * 100).toFixed(1) : 0,
            averageClicksPerUser: totalUsers > 0 ? (totalClicks / totalUsers).toFixed(1) : 0,
            data
        };
    }
}; 

// Extended collection of cute cat image URLs as fallback
const fallbackCats = [
    'https://cdn2.thecatapi.com/images/b1s.jpg',
    'https://cdn2.thecatapi.com/images/bau.jpg',
    'https://cdn2.thecatapi.com/images/bpc.jpg',
    'https://cdn2.thecatapi.com/images/c47.jpg',
    'https://cdn2.thecatapi.com/images/cgh.jpg',
    'https://cdn2.thecatapi.com/images/d3n.jpg',
    'https://cdn2.thecatapi.com/images/e35.jpg',
    'https://cdn2.thecatapi.com/images/ebv.jpg',
    'https://cdn2.thecatapi.com/images/MTYzNjkwMQ.jpg',
    'https://cdn2.thecatapi.com/images/4lp.jpg',
    'https://cdn2.thecatapi.com/images/bo8.jpg',
    'https://cdn2.thecatapi.com/images/6ot.jpg'
];

let currentCatIndex = 0;

// Enhanced simping lines with more emotion and variety
const simpingLines = [
    "Wait, please don't go! 🥺👉👈",
    "I'll purr extra loud for you... 😿💕",
    "What if I bring you my favorite toy? 🧸",
    "I promise I'm the cutest cat ever! 😸✨",
    "Don't leave me here all alone... 💔😿",
    "I'll do that cute head tilt thing! 🐱",
    "What about belly rubs? I allow those! 🤗",
    "I'll sit in your favorite chair until you come back! 😤",
    "Fine, I'll knock things off your desk... miss me yet? 😼",
    "I'm practicing my sad kitten eyes right now 🥺👀",
    "I'll leave you dead mice as presents! 🐭💝",
    "But I already picked out our wedding rings... 💍😿",
    "I'll learn to fetch! Just like dogs but cuter! 🎾",
    "What if I promise to use the litter box... most of the time? 😅",
    "I'll let you pet my belly for 3 whole seconds! 🤲💕",
    "I'm too pretty to be rejected like this! 😢✨",
    "I'll write you poetry with my paw prints! 🐾📝",
    "But who will judge your life choices if I'm not here? 🤔",
    "I'll pretend to love the food you give me! 😋",
    "Fine, I'll admit dogs are okay... JUST KIDDING! 😹"
];

// Creative success responses for when they click Yes
const successResponses = [
    {
        title: "OMG YES! 🎉✨",
        message: "I knew you had good taste! Time for celebration zoomies! 🏃‍♂️💨"
    },
    {
        title: "PURR-FECTION! 😻",
        message: "You just became my favorite human ever! *happy tail wiggles* 🐾"
    },
    {
        title: "Victory Achieved! 🏆",
        message: "I'm doing my happy dance right now! Can you see my little paws? 💃🐱"
    },
    {
        title: "Best Human Award! 🥇",
        message: "You passed the cuteness test with flying whiskers! 🎖️✨"
    },
    {
        title: "Heart Status: MELTED 💖",
        message: "Brb, gonna knock something off your table out of pure joy! 😹"
    },
    {
        title: "Mission Accomplished! 🎯",
        message: "My simping skills are legendary! You never stood a chance 😎💕"
    },
    {
        title: "Cat Approved! ✅",
        message: "Welcome to the exclusive 'Humans I Actually Like' club! 🎪"
    },
    {
        title: "Jackpot! 🎰💎",
        message: "I'm purring so loud the neighbors are complaining! 📢😸"
    },
    {
        title: "You're Pawsome! 🐾⭐",
        message: "I'll remember this when I'm deciding who gets morning cuddles! 🤗"
    },
    {
        title: "Checkmate! ♟️👑",
        message: "My cuteness strategy worked flawlessly! PhD in Adorability pays off! 🎓"
    },
    {
        title: "WOOHOO! 🎊🎈",
        message: "Time to celebrate with a victory nap in your favorite chair! 😴💺"
    },
    {
        title: "Success Unlocked! 🔓",
        message: "Achievement: 'Fell for Cat Charm' - Reward: Eternal cat friendship! 🏅"
    },
    {
        title: "Plot Twist! 🎭",
        message: "The cat was the main character all along! *dramatic paw pose* 🎬"
    },
    {
        title: "HIGH FIVE! ✋💫",
        message: "Oops, I only have paws... HIGH PAW instead! 🐾"
    },
    {
        title: "Level Up! 🆙",
        message: "You just upgraded from 'human' to 'cat whisperer'! 🗣️✨"
    }
];

// Initialize the page
window.addEventListener('load', () => {
    analytics.init(); // Initialize analytics tracking
    createHearts();
    positionNoButtonInitially();
    setupEventListeners();
});

// Position the No button initially
function positionNoButtonInitially() {
    const noBtn = document.getElementById('noBtn');
    noBtn.style.left = '55%';
    noBtn.style.top = '60%';
}

// Setup event listeners
function setupEventListeners() {
    // Handle image loading errors
    document.addEventListener('DOMContentLoaded', function() {
        const images = document.querySelectorAll('img');
        images.forEach(img => {
            img.addEventListener('error', function() {
                if (this.id === 'mainCat') {
                    this.src = fallbackCats[0];
                }
            });
        });
    });

    // Add mouse interaction fun
    document.addEventListener('mousemove', (e) => {
        if (Math.random() < 0.001) {
            createHeart();
        }
    });

    // Prevent context menu on images
    document.addEventListener('contextmenu', function(e) {
        if (e.target.tagName === 'IMG') {
            e.preventDefault();
        }
    });
}

// Load new cat photo (used for both Yes and No clicks)
async function loadNewCat() {
    const mainCat = document.getElementById('mainCat');
    
    // Add loading class for smooth transition
    mainCat.classList.add('cat-loading');

    try {
        // Try to fetch from Cat API
        const response = await fetch('https://api.thecatapi.com/v1/images/search?limit=1&size=med');
        if (response.ok) {
            const data = await response.json();
            if (data && data.length > 0) {
                mainCat.src = data[0].url;
            } else {
                throw new Error('No cat data received');
            }
        } else {
            throw new Error('API request failed');
        }
    } catch (error) {
        console.log('Using fallback cat image');
        // Use fallback images
        mainCat.src = fallbackCats[currentCatIndex % fallbackCats.length];
        currentCatIndex++;
    }

    // Remove loading class when image loads
    mainCat.onload = () => {
        mainCat.classList.remove('cat-loading');
    };
}

// Handle No button click - enhanced with better simping
function moveButton() {
    const noBtn = document.getElementById('noBtn');
    const questionElement = document.querySelector('.question');
    const simpingTextElement = document.getElementById('simpingText');
    
    noButtonClickCount++;
    
    // Track the No button click
    analytics.trackClick('no', { 
        simpingLineIndex: (noButtonClickCount - 1) % simpingLines.length,
        totalNoClicks: noButtonClickCount 
    });
    
    // Add shake animation to button
    noBtn.classList.add('btn-shake');
    setTimeout(() => noBtn.classList.remove('btn-shake'), 500);
    
    // Use viewport-based positioning with safe zones
    const safeZones = [
        { left: '5%', top: '10%' },
        { left: '75%', top: '15%' },
        { left: '10%', top: '70%' },
        { left: '70%', top: '75%' },
        { left: '85%', top: '40%' },
        { left: '15%', top: '85%' },
        { left: '45%', top: '10%' },
        { left: '60%', top: '60%' },
        { left: '25%', top: '25%' },
        { left: '80%', top: '80%' },
        { left: '90%', top: '20%' },
        { left: '20%', top: '90%' }
    ];
    
    // Pick a random safe zone
    const randomZone = safeZones[Math.floor(Math.random() * safeZones.length)];
    noBtn.style.left = randomZone.left;
    noBtn.style.top = randomZone.top;
    
    // Change cat image on No click
    loadNewCat();
    
    // Show enhanced simping lines in the simping text element (keep main question)
    const lineIndex = (noButtonClickCount - 1) % simpingLines.length;
    simpingTextElement.textContent = simpingLines[lineIndex];
    simpingTextElement.classList.add('show');
    
    // Add bounce animation to main question
    questionElement.classList.add('question-bounce');
    setTimeout(() => questionElement.classList.remove('question-bounce'), 600);
    
    // Create frustrated hearts
    for (let i = 0; i < 5; i++) {
        setTimeout(() => createHeart('💔'), i * 100);
    }
    
    // After showing all unique lines, cycle through random ones
    if (noButtonClickCount > simpingLines.length) {
        const randomIndex = Math.floor(Math.random() * simpingLines.length);
        simpingTextElement.textContent = simpingLines[randomIndex];
    }
}

// Handle Yes button click - enhanced with cat changing and creative responses
function showLove() {
    const successMessage = document.getElementById('successMessage');
    const successTitle = document.getElementById('successTitle');
    const successText = document.getElementById('successText');
    const simpingTextElement = document.getElementById('simpingText');
    
    yesButtonClickCount++;
    
    // Track the Yes button click
    analytics.trackClick('yes', { 
        totalYesClicks: yesButtonClickCount,
        responseTitle: successResponses[Math.floor(Math.random() * successResponses.length)].title
    });
    
    // Change cat image on Yes click too!
    loadNewCat();
    
    // Clear any simping text since they said yes!
    simpingTextElement.classList.remove('show');
    setTimeout(() => {
        simpingTextElement.textContent = '';
    }, 400);
    
    // Show random creative success response
    const randomResponse = successResponses[Math.floor(Math.random() * successResponses.length)];
    successTitle.textContent = randomResponse.title;
    successText.textContent = randomResponse.message;
    
    // Show success message
    successMessage.style.display = 'block';
    
    // No automatic closing - user must click to close
    
    // Create lots of happy hearts with variety
    for (let i = 0; i < 30; i++) {
        setTimeout(() => createHeart(), i * 80);
    }
}

// Close success message
function closeSuccessMessage() {
    document.getElementById('successMessage').style.display = 'none';
}

// Create hearts with optional custom emoji
function createHearts() {
    setInterval(() => createHeart(), 3000);
}

function createHeart(heartType = null) {
    const heart = document.createElement('div');
    heart.className = 'heart';
    
    // Use custom heart type or random selection
    if (heartType) {
        heart.innerHTML = heartType;
    } else {
        const heartTypes = ['💕', '💖', '💗', '💝', '💘', '😻', '🥰'];
        heart.innerHTML = heartTypes[Math.floor(Math.random() * heartTypes.length)];
    }
    
    heart.style.left = Math.random() * 100 + 'vw';
    heart.style.animationDelay = Math.random() * 3 + 's';
    heart.style.animationDuration = (Math.random() * 3 + 2) + 's';
    
    document.getElementById('hearts').appendChild(heart);
    
    // Clean up heart after animation
    setTimeout(() => {
        if (heart.parentNode) {
            heart.remove();
        }
    }, 6000);
}

// Add some random cat facts for extra charm (called occasionally)
const catFacts = [
    "Did you know cats have 32 muscles in each ear? 🐱👂",
    "Cats can rotate their ears 180 degrees! 🔄👂",
    "A group of cats is called a 'clowder' 😸👥",
    "Cats spend 70% of their lives sleeping 😴💤",
    "Every cat's nose print is unique, like fingerprints! 👃✨"
];

// Occasionally show cat facts instead of simping lines
function showCatFact() {
    if (Math.random() < 0.2) { // 20% chance
        const randomFact = catFacts[Math.floor(Math.random() * catFacts.length)];
        document.querySelector('.question').textContent = randomFact;
    }
}

// Admin Panel Functions
function openAdmin() {
    const adminPanel = document.getElementById('adminPanel');
    adminPanel.style.display = 'flex';
    loadAnalyticsData();
}

function closeAdmin() {
    const adminPanel = document.getElementById('adminPanel');
    adminPanel.style.display = 'none';
}

function showTab(tabName) {
    // Update active tab button
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
    // Show corresponding tab content
    const tabContent = document.getElementById('tabContent');
    const summary = analytics.generateSummary();
    
    switch(tabName) {
        case 'summary':
            showSummaryTab(summary);
            break;
        case 'users':
            showUsersTab(summary.data.userStats);
            break;
        case 'clicks':
            showClicksTab(summary.data.clicks);
            break;
        case 'export':
            showExportTab();
            break;
    }
}

function showSummaryTab(summary) {
    const tabContent = document.getElementById('tabContent');
    tabContent.innerHTML = `
        <div class="summary-info">
            <h3>📊 Quick Stats</h3>
            <div class="summary-grid">
                <div class="summary-item">
                    <strong>Success Rate:</strong> ${summary.yesPercentage}% users clicked "Yes"
                </div>
                <div class="summary-item">
                    <strong>Engagement:</strong> ${summary.averageClicksPerUser} clicks per user
                </div>
                <div class="summary-item">
                    <strong>Most Resistant:</strong> ${summary.totalNoClicks > summary.totalYesClicks ? 'Users prefer clicking "No"' : 'Users love clicking "Yes"'}
                </div>
            </div>
            
            <h3 style="margin-top: 30px;">📈 Recent Activity</h3>
            <div class="recent-activity">
                ${summary.data.clicks.slice(-5).reverse().map(click => `
                    <div class="activity-item">
                        <span class="activity-time">${new Date(click.timestamp).toLocaleString()}</span>
                        <span class="activity-action ${click.buttonType}">${click.buttonType.toUpperCase()} click</span>
                        <span class="activity-user">${click.userId.substr(-8)}</span>
                    </div>
                `).join('')}
            </div>
        </div>
        <style>
            .summary-grid { display: grid; gap: 15px; margin: 15px 0; }
            .summary-item { background: #f0f8ff; padding: 15px; border-radius: 8px; }
            .activity-item { display: flex; justify-content: space-between; padding: 10px; background: #f8f9fa; margin: 5px 0; border-radius: 5px; }
            .activity-action.yes { color: #28a745; font-weight: bold; }
            .activity-action.no { color: #dc3545; font-weight: bold; }
            .activity-time { color: #666; font-size: 0.9em; }
            .activity-user { color: #007bff; font-family: monospace; }
        </style>
    `;
}

function showUsersTab(userStats) {
    const tabContent = document.getElementById('tabContent');
    const users = Object.values(userStats);
    
    tabContent.innerHTML = `
        <h3>👥 User Statistics (${users.length} unique users)</h3>
        <ul class="user-list">
            ${users.map(user => `
                <li class="user-item">
                    <strong>User ID:</strong> ${user.userId}<br>
                    <strong>First Visit:</strong> ${new Date(user.firstVisit).toLocaleString()}<br>
                    <strong>Last Visit:</strong> ${new Date(user.lastVisit).toLocaleString()}<br>
                    <strong>Total Yes:</strong> <span style="color: #28a745;">${user.totalYes}</span> | 
                    <strong>Total No:</strong> <span style="color: #dc3545;">${user.totalNo}</span><br>
                    <strong>Ratio:</strong> ${user.totalYes + user.totalNo > 0 ? 
                        `${((user.totalYes / (user.totalYes + user.totalNo)) * 100).toFixed(1)}% Yes` : 'No clicks yet'}
                </li>
            `).join('')}
        </ul>
    `;
}

function showClicksTab(clicks) {
    const tabContent = document.getElementById('tabContent');
    const recentClicks = clicks.slice(-20).reverse(); // Show last 20 clicks
    
    tabContent.innerHTML = `
        <h3>👆 Recent Clicks (showing last 20 of ${clicks.length} total)</h3>
        <ul class="click-list">
            ${recentClicks.map(click => `
                <li class="click-item">
                    <strong>Time:</strong> ${new Date(click.timestamp).toLocaleString()}<br>
                    <strong>User:</strong> ${click.userId}<br>
                    <strong>Action:</strong> <span style="color: ${click.buttonType === 'yes' ? '#28a745' : '#dc3545'}; font-weight: bold;">
                        ${click.buttonType.toUpperCase()} CLICK
                    </span><br>
                    <strong>Click #:</strong> ${click.clickCount} for this user<br>
                    ${click.simpingLineIndex !== undefined ? `<strong>Simping Line:</strong> #${click.simpingLineIndex + 1}` : ''}
                    ${click.responseTitle ? `<strong>Response:</strong> "${click.responseTitle}"` : ''}
                </li>
            `).join('')}
        </ul>
    `;
}

function showExportTab() {
    const tabContent = document.getElementById('tabContent');
    
    tabContent.innerHTML = `
        <h3>📥 Export & Manage Data</h3>
        <div class="export-buttons">
            <button class="export-btn" onclick="exportData('json')">📄 Export as JSON</button>
            <button class="export-btn" onclick="exportData('csv')">📊 Export as CSV</button>
            <button class="export-btn" onclick="exportData('summary')">📋 Export Summary</button>
            <button class="export-btn clear-btn" onclick="clearAnalyticsData()">🗑️ Clear All Data</button>
        </div>
        
        <div style="margin-top: 30px;">
            <h4>🔒 Privacy Information</h4>
            <p style="color: #666; line-height: 1.6;">
                All analytics data is stored locally in your browser only. No data is sent to external servers. 
                Data includes user IDs (randomly generated), click counts, timestamps, and basic browser information.
                Users are tracked via localStorage to provide consistent analytics across sessions.
            </p>
        </div>
    `;
}

function loadAnalyticsData() {
    const summary = analytics.generateSummary();
    const statsGrid = document.getElementById('statsGrid');
    
    statsGrid.innerHTML = `
        <div class="stat-card">
            <div class="stat-number">${summary.totalUsers}</div>
            <div class="stat-label">Total Users</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">${summary.totalClicks}</div>
            <div class="stat-label">Total Clicks</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">${summary.totalYesClicks}</div>
            <div class="stat-label">Yes Clicks</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">${summary.totalNoClicks}</div>
            <div class="stat-label">No Clicks</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">${summary.yesPercentage}%</div>
            <div class="stat-label">Success Rate</div>
        </div>
    `;
    
    // Show summary tab by default
    showSummaryTab(summary);
}

function exportData(format) {
    const summary = analytics.generateSummary();
    const timestamp = new Date().toISOString().split('T')[0];
    
    let content, filename, mimeType;
    
    if (format === 'json') {
        content = JSON.stringify(summary.data, null, 2);
        filename = `simping-cats-data-${timestamp}.json`;
        mimeType = 'application/json';
    } else if (format === 'csv') {
        const clicks = summary.data.clicks;
        const csvHeader = 'Timestamp,User ID,Button Type,Click Count\n';
        const csvData = clicks.map(click => 
            `${click.timestamp},${click.userId},${click.buttonType},${click.clickCount}`
        ).join('\n');
        content = csvHeader + csvData;
        filename = `simping-cats-clicks-${timestamp}.csv`;
        mimeType = 'text/csv';
    } else if (format === 'summary') {
        content = `Simping Cats Analytics Summary - ${timestamp}
        
Total Users: ${summary.totalUsers}
Total Visits: ${summary.totalVisits}  
Total Clicks: ${summary.totalClicks}
Yes Clicks: ${summary.totalYesClicks} (${summary.yesPercentage}%)
No Clicks: ${summary.totalNoClicks}
Average Clicks per User: ${summary.averageClicksPerUser}

Generated: ${new Date().toLocaleString()}`;
        filename = `simping-cats-summary-${timestamp}.txt`;
        mimeType = 'text/plain';
    }
    
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}

function clearAnalyticsData() {
    if (confirm('⚠️ This will permanently delete all analytics data. Are you sure?')) {
        localStorage.removeItem('simpingCatsVisits');
        localStorage.removeItem('simpingCatsClicks');
        localStorage.removeItem('simpingCatsUserStats');
        localStorage.removeItem('simpingCatsUserId');
        
        alert('✅ All analytics data has been cleared!');
        closeAdmin();
    }
}



// Export functions for HTML onclick handlers
window.moveButton = moveButton;
window.showLove = showLove;
window.closeSuccessMessage = closeSuccessMessage;
window.openAdmin = openAdmin;
window.closeAdmin = closeAdmin;
window.showTab = showTab;
window.exportData = exportData;
window.clearAnalyticsData = clearAnalyticsData; 