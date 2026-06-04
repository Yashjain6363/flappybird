# 🐦 Flappy Bird - Premium Edition (Python & Web)

A premium, highly-polished retro Flappy Bird game. This repository contains two versions:
1. 🐍 **Python Desktop Version**: Built using Pygame (native desktop app).
2. 🌐 **Vite Web Version**: Built using HTML5 Canvas & Vanilla JS (modern web browser app).

---

## ✨ Features
- **Dynamic Physics & Smooth Controls**: Fine-tuned bird physics, responsive keyboard controls (`Space` or `ArrowUp` or `W`) and mouse/touch controls.
- **Selectable Themes**: Switch between three gorgeous visual styles on the fly:
  - 🌅 **Retro Arcade**: Classic pixel style with warm sunset tones.
  - 🌌 **Neon Cyberpunk**: Glowing cyan/magenta grid landscape and dark vaporwave vibes.
  - 🌲 **Midnight Forest**: Silhouette pine trees and misty autumnal backdrops.
- **Parallax Background Layers**: Multi-layer scrolling background (sky/clouds, city skyline, foreground mountains/forest) that adds depth and movement.
- **Sound Synthesizer**: Generates all sound effects (flap, score, crash) dynamically using math waves. Zero external asset files needed, 100% offline, zero latency!
- **Particle System**: Feather burst effects on jumps, star bursts on passing obstacles, and explosion particles on crash.
- **Juicy Screen Shake**: Feels satisfyingly impact-oriented when crashing.
- **High Scores Leaderboard**: Track your best scores directly via local persistence.

---

## 🐍 1. Running the Python Desktop Version

### Prerequisites
Make sure you have [Python 3](https://www.python.org/) installed.

### Installation
Open your terminal in this directory and run:
```bash
pip install -r requirements.txt
```

### Running the game
```bash
python main.py
```

### Controls (Python)
- **Jump / Flap**: `Space`, `Up Arrow`, `W`, or **Left Mouse Click**
- **Pause / Resume**: `Escape`
- **Mute / Unmute Sound**: `M`
- **Theme Selection**: Click the themed buttons (*Retro*, *Cyber*, *Forest*) on the Start screen with your mouse.

---

## 🌐 2. Running the Vite Web Version

### Prerequisites
Make sure you have [Node.js](https://nodejs.org/) installed.

### Installation
Open your terminal in this directory and run:
```bash
npm install
```

### Running the game
```bash
npm run dev
```
Open your browser and navigate to the address printed in the terminal (usually `http://localhost:5173`).

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
git commit -m "feat: premium flappy bird game in python and web"
```

### 3. Create a repository on GitHub
- Go to [GitHub](https://github.com/) and click **New Repository**.
- Name it (e.g., `flappy-bird-premium`) and leave it public or private.
- **Do not** initialize it with a README, gitignore, or license.

### 4. Link your local repository to GitHub and push
Replace `your-username` and `your-repo-name` with your actual details:
```bash
git branch -M main
git remote add origin https://github.com/your-username/your-repo-name.git
git push -u origin main
```
