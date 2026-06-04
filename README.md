# 🐦 Flappy Bird - Premium Edition

A premium, highly-polished retro Flappy Bird game built using modern Web standards (HTML5 Canvas, CSS custom properties, and Vanilla JavaScript) with hot reloading powered by Vite.

## ✨ Features
- **Dynamic Physics & Smooth Controls**: Fine-tuned bird physics, responsive keyboard controls (`Space`, `ArrowUp`, or `W`) and click/touch screen controls.
- **Selectable Themes**: Switch between three gorgeous visual styles on the fly:
  - 🌅 **Retro Arcade**: Classic pixels with warm sunset tones and green pipe barriers.
  - 🌌 **Neon Cyberpunk**: Glowing cyan/magenta grid landscape and dark vaporwave vibes.
  - 🌲 **Midnight Forest**: Sleek silhouette graphics with forest-themed backdrops and deep green/blue colorways.
- **Parallax Background Layers**: Multi-layer scrolling background (sky/clouds, city skyline, foreground mountains) that adds depth and movement.
- **Built-in Web Audio Sound Synthesizer**: Uses the browser's native **Web Audio API** to generate sound effects dynamically (jump, score, crash) without requiring external MP3/WAV assets. Works 100% offline out-of-the-box!
- **Particle System**: Feather burst effects on jumps, star bursts on passing obstacles, and explosion particles on crash.
- **Juicy Screen Shake**: Feels satisfyingly impact-oriented when crashing.
- **High Scores Leaderboard**: Track your best scores directly via `localStorage` persistence.

## 🛠️ Tech Stack
- **Bundler / Dev Server**: Vite (Vanilla JS)
- **Graphics**: HTML5 Canvas API (highly optimized 60fps rendering)
- **Styling**: Modern CSS3 (Glassmorphism overlays, custom typography, Google Fonts)
- **Audio**: Web Audio API (Synthesizer)

---

## 🚀 How to Run Locally

### Prerequisites
Make sure you have [Node.js](https://nodejs.org/) installed.

### 1. Install dependencies:
```bash
npm install
```

### 2. Start the development server:
```bash
npm run dev
```
Open your browser and navigate to the address printed in the terminal (usually `http://localhost:5173`).

### 3. Build for Production:
```bash
npm run build
```
This will bundle the game inside the `/dist` directory.

---

## 📦 How to Push to GitHub

To publish this project to your GitHub account:

### 1. Initialize a Git Repository
If you haven't initialized Git in this folder yet, run:
```bash
git init
```

### 2. Add files and make your first commit
```bash
git add .
git commit -m "feat: initial commit of premium flappy bird game"
```

### 3. Create a repository on GitHub
- Go to [GitHub](https://github.com/) and click **New Repository**.
- Name it (e.g., `flappy-bird-premium`) and leave it public or private.
- **Do not** initialize it with a README, gitignore, or license (we already created them!).

### 4. Link your local repository to GitHub and push
Replace `your-username` and `your-repo-name` with your actual details:
```bash
git branch -M main
git remote add origin https://github.com/your-username/your-repo-name.git
git push -u origin main
```

---

Enjoy the game! 🎮
