# Simping Cats 🐱💕

A fun interactive webpage where cute cats try to get your attention! The cats will keep asking "Will you miss me?" and won't take "No" for an answer.

## Features ✨

- 🐱 **Cute cat in the center** - Changes every time you click "No"
- 🥺 **Interactive question** - "Will you miss me?" with Yes/No options
- 🏃‍♀️ **Escaping No button** - Clicks "No" and watch it run away to random positions!
- 🔄 **Dynamic cat photos** - Uses The Cat API for fresh, adorable cat images
- 💕 **Yes rewards** - Click "Yes" for a heartwarming response and gallery of cats
- 📱 **Mobile responsive** - Works perfectly on phones and tablets
- 🌈 **Cute animations** - Floating hearts and smooth transitions

## How to Run Locally 🚀

### Option 1: Simple Double-Click
1. Simply double-click the `index.html` file
2. It will open in your default browser
3. That's it! No installation required.

### Option 2: Using Python (for sharing)
If you want to share the page with others on your network:

```bash
# Navigate to the project folder
cd /Users/ashutosh.singh/CodeBase/Simp_Project

# Python 3 (most common)
python3 -m http.server 8000

# Or Python 2
python -m SimpleHTTPServer 8000
```

Then open: `http://localhost:8000`

### Option 3: Using Node.js
If you have Node.js installed:

```bash
# Install a simple server (one-time)
npm install -g http-server

# Run from the project folder
http-server -p 8000
```

## Sharing with Others 🌐

### Local Network Sharing
1. Start a local server (Option 2 or 3 above)
2. Find your IP address:
   - **Mac/Linux**: `ifconfig | grep inet`
   - **Windows**: `ipconfig`
3. Share your local IP with port: `http://YOUR_IP_ADDRESS:8000`
   - Example: `http://192.168.1.100:8000`

### Online Sharing Options
- Upload to **GitHub Pages** (free)
- Use **Netlify Drop** (drag & drop deployment)
- Use **Vercel** for instant deployment
- Host on any web server

## Technical Details 🛠️

- **Pure HTML/CSS/JavaScript** - No dependencies required
- **The Cat API** - Fetches random cute cat images
- **Fallback images** - Works offline with pre-defined cat images
- **Responsive design** - Mobile-friendly
- **Cross-browser compatible** - Works in all modern browsers

## API Information 📡

The page uses [The Cat API](https://thecatapi.com/) for fetching random cat images. If the API is unavailable, it falls back to pre-defined cat images, so the page always works!

## Have Fun! 😸

Try clicking "No" multiple times and see what happens! The cats get more and more desperate for your attention. And don't forget to eventually click "Yes" for a sweet surprise! 💕

---

*Made with 💕 for cat lovers everywhere* 