/* ==========================================================================
   GAME MAIN ENTRYPOINT - main.js
   ========================================================================== */
import { FlappyBirdGame, GAME_STATE } from './game.js';
import { GameRenderer } from './renderer.js';
import { audio } from './audio.js';

// DOM Elements
const canvas = document.getElementById('game-canvas');
const gameWrapper = document.getElementById('game-wrapper');

// Screens / Overlays
const startScreen = document.getElementById('start-screen');
const pauseScreen = document.getElementById('pause-screen');
const gameOverScreen = document.getElementById('game-over-screen');
const hud = document.getElementById('hud');

// UI Elements
const hudScoreVal = document.getElementById('hud-score');
const finalScoreVal = document.getElementById('final-score');
const highScoreVal = document.getElementById('high-score');
const medalSlot = document.getElementById('medal-slot');

// Buttons
const startBtn = document.getElementById('start-btn');
const pauseBtn = document.getElementById('pause-btn');
const muteBtn = document.getElementById('mute-btn');
const muteIcon = document.getElementById('mute-icon');
const resumeBtn = document.getElementById('resume-btn');
const restartFromPauseBtn = document.getElementById('restart-from-pause-btn');
const quitBtn = document.getElementById('quit-btn');
const restartBtn = document.getElementById('restart-btn');
const menuBtn = document.getElementById('menu-btn');
const themeButtons = document.querySelectorAll('.theme-btn');

// Initialize Game & Renderer
const game = new FlappyBirdGame();
const renderer = new GameRenderer(canvas, game);

// State tracking for delta time loop
let lastTime = performance.now();
let animationFrameId = null;

/**
 * Core Game Loop
 */
function gameLoop(currentTime) {
    // Calculate delta time in seconds, capped to avoid huge jumps on frame drops/tab switching
    let dt = (currentTime - lastTime) / 1000;
    if (dt > 0.1) dt = 0.1;
    lastTime = currentTime;

    // Update game physics and objects
    game.update(dt);

    // Draw everything
    renderer.render();

    // Loop
    animationFrameId = requestAnimationFrame(gameLoop);
}

/**
 * Updates HUD score display
 */
game.onScoreChange = (score) => {
    hudScoreVal.textContent = score;
};

/**
 * Listens to state transitions from Game Engine and synchronizes DOM UI
 */
game.onGameStateChange = (state, isNewHigh = false) => {
    // Hide all overlays initially
    startScreen.classList.add('hidden');
    pauseScreen.classList.add('hidden');
    gameOverScreen.classList.add('hidden');
    hud.classList.add('hidden');

    switch (state) {
        case GAME_STATE.START:
            startScreen.classList.remove('hidden');
            break;

        case GAME_STATE.PLAYING:
            hud.classList.remove('hidden');
            hudScoreVal.textContent = game.score;
            break;

        case GAME_STATE.PAUSED:
            pauseScreen.classList.remove('hidden');
            hud.classList.remove('hidden');
            break;

        case GAME_STATE.GAMEOVER:
            gameOverScreen.classList.remove('hidden');
            
            // Populate score board
            finalScoreVal.textContent = game.score;
            highScoreVal.textContent = game.highScore;
            if (isNewHigh) {
                highScoreVal.classList.add('gold-text');
                highScoreVal.innerHTML = `${game.highScore} <i class="fa-solid fa-crown" style="font-size: 0.8rem; margin-left: 2px;"></i>`;
            } else {
                highScoreVal.classList.remove('gold-text');
            }

            // Award Medals
            renderMedal(game.score);
            break;
    }
};

/**
 * Awards medal emoji depending on game score
 */
function renderMedal(score) {
    let medalHTML = '';
    if (score >= 40) {
        medalHTML = '<span title="Gold Medal">🥇</span>';
    } else if (score >= 20) {
        medalHTML = '<span title="Silver Medal">🥈</span>';
    } else if (score >= 10) {
        medalHTML = '<span title="Bronze Medal">🥉</span>';
    } else {
        medalHTML = '<span class="no-medal">None</span>';
    }
    medalSlot.innerHTML = medalHTML;
}

/**
 * Handle Jump/Flap triggers
 */
function handleFlap(e) {
    // Prevent default scrolling on spacebar key downs
    if (e.type === 'keydown' && e.code !== 'Space' && e.code !== 'ArrowUp' && e.code !== 'KeyW') {
        return;
    }

    // Stop propagation so clicking canvas buttons doesn't trigger a flap
    if (e.target.closest('.icon-btn') || e.target.closest('.btn') || e.target.closest('.theme-btn')) {
        return;
    }

    if (e.type === 'keydown') {
        e.preventDefault();
    }

    game.flap();
}

/**
 * Setup Event Listeners
 */
function setupEventListeners() {
    // Jump inputs
    window.addEventListener('keydown', handleFlap);
    gameWrapper.addEventListener('mousedown', handleFlap);
    gameWrapper.addEventListener('touchstart', handleFlap, { passive: false });

    // Prevent touch gestures scrolling the viewport while in the game window
    gameWrapper.addEventListener('touchmove', (e) => {
        if (game.state === GAME_STATE.PLAYING) {
            e.preventDefault();
        }
    }, { passive: false });

    // Start Button
    startBtn.addEventListener('click', () => {
        audio.init();
        game.flap(); // transition to playing
    });

    // Pause / Resume
    pauseBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        game.pause();
    });

    window.addEventListener('keydown', (e) => {
        if (e.code === 'Escape') {
            if (game.state === GAME_STATE.PLAYING) {
                game.pause();
            } else if (game.state === GAME_STATE.PAUSED) {
                game.resume();
            }
        }
    });

    resumeBtn.addEventListener('click', () => {
        game.resume();
    });

    restartFromPauseBtn.addEventListener('click', () => {
        game.reset();
        game.flap(); // immediately start playing
    });

    // Quit to main menu
    quitBtn.addEventListener('click', () => {
        game.reset();
        game.onGameStateChange(GAME_STATE.START);
    });

    // Game Over restarts
    restartBtn.addEventListener('click', () => {
        game.reset();
        game.flap(); // immediately start playing
    });

    menuBtn.addEventListener('click', () => {
        game.reset();
        game.onGameStateChange(GAME_STATE.START);
    });

    // Audio volume mute toggle
    muteBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        const isMuted = audio.toggleMute();
        localStorage.setItem('flappy_muted', isMuted ? 'true' : 'false');
        updateMuteUI(isMuted);
    });

    // Theme selector
    themeButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            themeButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            const selectedTheme = btn.getAttribute('data-theme');
            game.setTheme(selectedTheme);
            localStorage.setItem('flappy_theme', selectedTheme);
        });
    });

    // Auto-pause when page goes background
    document.addEventListener('visibilitychange', () => {
        if (document.hidden && game.state === GAME_STATE.PLAYING) {
            game.pause();
        }
    });

    // Window Resize
    window.addEventListener('resize', () => {
        renderer.resize();
    });
}

/**
 * Synchronize Speaker Icon UI based on mute state
 */
function updateMuteUI(isMuted) {
    if (isMuted) {
        muteIcon.className = 'fa-solid fa-volume-xmark';
        muteBtn.setAttribute('aria-label', 'Unmute Audio');
    } else {
        muteIcon.className = 'fa-solid fa-volume-high';
        muteBtn.setAttribute('aria-label', 'Mute Audio');
    }
}

/**
 * Initialize saved configurations
 */
function loadSavedSettings() {
    // Theme
    const savedTheme = localStorage.getItem('flappy_theme') || 'retro';
    themeButtons.forEach(btn => {
        if (btn.getAttribute('data-theme') === savedTheme) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
    game.setTheme(savedTheme);

    // Audio mute
    const savedMute = localStorage.getItem('flappy_muted') === 'true';
    audio.setMute(savedMute);
    updateMuteUI(savedMute);
}

// Boot up game
setupEventListeners();
loadSavedSettings();
game.onGameStateChange(GAME_STATE.START);

// Start game loop anim
lastTime = performance.now();
animationFrameId = requestAnimationFrame(gameLoop);
