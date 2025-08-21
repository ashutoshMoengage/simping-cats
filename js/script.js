// Simping Cats Interactive Script
let noButtonClickCount = 0;
let yesButtonClickCount = 0;
const catApiKey = 'live_1'; 

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
    
    // Hide success message after 5 seconds
    setTimeout(() => {
        successMessage.style.display = 'none';
    }, 5000);
    
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

// Export functions for HTML onclick handlers
window.moveButton = moveButton;
window.showLove = showLove;
window.closeSuccessMessage = closeSuccessMessage; 