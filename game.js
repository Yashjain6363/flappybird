/* ==========================================================================
   FLAPPY BIRD CORE ENGINE - game.js
   ========================================================================== */
import { audio } from './audio.js';

export const GAME_STATE = {
    START: 'START',
    PLAYING: 'PLAYING',
    PAUSED: 'PAUSED',
    GAMEOVER: 'GAMEOVER'
};

export const THEMES = {
    retro: {
        id: 'retro',
        skyColor: '#4EC0CA',
        pipeColor: '#73BF2E',
        pipeBorderColor: '#538018',
        groundColor: '#DDD894',
        groundBorderColor: '#84C078',
        birdColors: ['#FFEB3B', '#F57F17', '#E65100'], // yellow body, dark beak, red wing accent
        particleColor: '#FFF'
    },
    neon: {
        id: 'neon',
        skyColor: '#0f0c1b',
        pipeColor: '#ff007f',
        pipeBorderColor: '#7b2ff7',
        groundColor: '#1d1936',
        groundBorderColor: '#00ffff',
        birdColors: ['#00ffff', '#0072ff', '#7b2ff7'], // cyan body, blue beak, purple accent
        particleColor: '#00ffff'
    },
    forest: {
        id: 'forest',
        skyColor: '#1d2a23',
        pipeColor: '#27ae60',
        pipeBorderColor: '#1e8449',
        groundColor: '#19251f',
        groundBorderColor: '#2ecc71',
        birdColors: ['#f5b041', '#cb4335', '#ebf5fb'], // autumnal colors
        particleColor: '#2ecc71'
    }
};

export class FlappyBirdGame {
    constructor() {
        // Virtual resolution for scaling calculations
        this.width = 480;
        this.height = 800;

        // Theme
        this.currentTheme = THEMES.retro;

        // Highscore
        this.highScore = parseInt(localStorage.getItem('flappy_highscore') || '0', 10);

        // Callback hooks to notify UI layers
        this.onScoreChange = null;
        this.onGameStateChange = null;

        this.reset();
    }

    /**
     * Resets the game variables to initial state
     */
    reset() {
        this.state = GAME_STATE.START;
        this.score = 0;

        // Bird Physics
        this.bird = {
            x: 100,
            y: 350,
            radius: 16,
            velocity: 0,
            gravity: 0.45,
            jumpStrength: -8.0,
            maxFallSpeed: 12,
            angle: 0,
            flapTimer: 0
        };

        // Obstacles (Pipes)
        this.pipes = [];
        this.pipeSpawnTimer = 0;
        this.pipeSpawnInterval = 1700; // in ms
        this.pipeSpeed = 190; // pixels per second
        this.pipeGapDefault = 160; // size of opening between top and bottom pipe
        this.minPipeHeight = 80;

        // Environment & Parallax Scrolling
        this.groundHeight = 90;
        this.skyOffset = 0;
        this.cityOffset = 0;
        this.groundOffset = 0;

        // Visual Juice & Feedback
        this.particles = [];
        this.screenShakeTime = 0;
        this.screenShakeMagnitude = 0;
        this.flashScreen = false;
        this.flashTimer = 0;
    }

    /**
     * Set active theme
     */
    setTheme(themeId) {
        if (THEMES[themeId]) {
            this.currentTheme = THEMES[themeId];
            document.body.className = `theme-${themeId}`;
        }
    }

    /**
     * Triggers bird jump / flap
     */
    flap() {
        if (this.state === GAME_STATE.START) {
            this.state = GAME_STATE.PLAYING;
            if (this.onGameStateChange) this.onGameStateChange(this.state);
        }

        if (this.state !== GAME_STATE.PLAYING) return;

        this.bird.velocity = this.bird.jumpStrength;
        audio.playFlap();

        // Spawn jump particles (feathers)
        const particleCount = 6 + Math.floor(Math.random() * 4);
        for (let i = 0; i < particleCount; i++) {
            this.spawnParticle(
                this.bird.x - 8,
                this.bird.y + (Math.random() * 10 - 5),
                -(Math.random() * 2 + 1), // movement to left
                (Math.random() * 3 - 1.5), // up/down scatter
                Math.random() * 3 + 2, // size
                this.currentTheme.particleColor, // color
                0.8, // alpha
                0.95 // fade rate
            );
        }
    }

    /**
     * Pause game
     */
    pause() {
        if (this.state === GAME_STATE.PLAYING) {
            this.state = GAME_STATE.PAUSED;
            if (this.onGameStateChange) this.onGameStateChange(this.state);
        }
    }

    /**
     * Resume game
     */
    resume() {
        if (this.state === GAME_STATE.PAUSED) {
            this.state = GAME_STATE.PLAYING;
            if (this.onGameStateChange) this.onGameStateChange(this.state);
        }
    }

    /**
     * Spawn a particle in the particle pool
     */
    spawnParticle(x, y, vx, vy, size, color, alpha, decay) {
        this.particles.push({
            x,
            y,
            vx,
            vy,
            size,
            color,
            alpha,
            decay,
            rotation: Math.random() * Math.PI * 2,
            rotSpeed: (Math.random() - 0.5) * 0.1
        });
    }

    /**
     * Updates physics, movements, collision, and animation states
     * @param {number} deltaTime - Time elapsed since last frame in seconds
     */
    update(deltaTime) {
        if (this.state === GAME_STATE.PAUSED) return;

        // 1. Update Screen Shake and visual effects
        if (this.screenShakeTime > 0) {
            this.screenShakeTime -= deltaTime;
            if (this.screenShakeTime <= 0) {
                this.screenShakeMagnitude = 0;
            }
        }

        if (this.flashTimer > 0) {
            this.flashTimer -= deltaTime;
            if (this.flashTimer <= 0) {
                this.flashScreen = false;
            }
        }

        // 2. Update Particles (always update, even in Game Over for animation leftovers)
        for (let i = this.particles.length - 1; i >= 0; i--) {
            const p = this.particles[i];
            p.x += p.vx;
            p.y += p.vy;
            p.alpha *= p.decay;
            p.rotation += p.rotSpeed;
            if (p.alpha < 0.05) {
                this.particles.splice(i, 1);
            }
        }

        if (this.state === GAME_STATE.START) {
            // Passive bobbing animation for bird on start screen
            const time = Date.now() * 0.005;
            this.bird.y = 350 + Math.sin(time) * 15;
            this.bird.angle = Math.sin(time * 1.5) * 0.1;

            // Scroll background slowly
            this.skyOffset = (this.skyOffset + 15 * deltaTime) % this.width;
            this.cityOffset = (this.cityOffset + 35 * deltaTime) % this.width;
            this.groundOffset = (this.groundOffset + this.pipeSpeed * deltaTime) % this.width;
            return;
        }

        if (this.state === GAME_STATE.GAMEOVER) {
            // Fall to the ground
            const groundLimit = this.height - this.groundHeight - this.bird.radius;
            if (this.bird.y < groundLimit) {
                this.bird.velocity += this.bird.gravity * 60 * deltaTime;
                this.bird.y = Math.min(groundLimit, this.bird.y + this.bird.velocity);
                this.bird.angle = Math.min(Math.PI / 2, this.bird.angle + 0.1);
            }
            return;
        }

        // --- PLAYING STATE ---

        // 3. Bird Physics
        this.bird.velocity += this.bird.gravity * 60 * deltaTime;
        // Cap terminal velocity
        if (this.bird.velocity > this.bird.maxFallSpeed) {
            this.bird.velocity = this.bird.maxFallSpeed;
        }
        this.bird.y += this.bird.velocity;

        // Bird Angle calculation based on velocity
        if (this.bird.velocity < 3) {
            // Angled up on flap
            this.bird.angle = -0.3;
        } else {
            // Tumbles down when falling
            this.bird.angle = Math.min(Math.PI / 2, this.bird.angle + 0.05 * (this.bird.velocity - 3));
        }

        // Ground collision
        const groundY = this.height - this.groundHeight;
        if (this.bird.y + this.bird.radius >= groundY) {
            this.bird.y = groundY - this.bird.radius;
            this.triggerGameOver();
            return;
        }

        // Sky ceiling collision (forbid passing off-screen top)
        if (this.bird.y - this.bird.radius < 0) {
            this.bird.y = this.bird.radius;
            this.bird.velocity = 0.5;
        }

        // 4. Parallax Background Scrolling
        this.skyOffset = (this.skyOffset + 20 * deltaTime) % this.width;
        this.cityOffset = (this.cityOffset + 50 * deltaTime) % this.width;
        this.groundOffset = (this.groundOffset + this.pipeSpeed * deltaTime) % this.width;

        // 5. Dynamic Difficulty calculation
        // As score increases, narrow the pipe gap slightly (down to a minimum of 110)
        const currentGap = Math.max(110, this.pipeGapDefault - Math.floor(this.score / 6) * 6);
        // Slightly increase speed
        const currentSpeed = this.pipeSpeed + Math.min(60, Math.floor(this.score / 8) * 8);

        // 6. Spawn and Update Pipes
        this.pipeSpawnTimer += deltaTime * 1000;
        if (this.pipeSpawnTimer >= this.pipeSpawnInterval) {
            this.spawnPipe(currentGap);
            this.pipeSpawnTimer = 0;
        }

        for (let i = this.pipes.length - 1; i >= 0; i--) {
            const pipe = this.pipes[i];
            pipe.x -= currentSpeed * deltaTime;

            // Collision Check
            if (this.checkCollision(this.bird, pipe)) {
                this.triggerGameOver();
                return;
            }

            // Check if passed for scoring
            if (!pipe.passed && pipe.x + pipe.width < this.bird.x) {
                pipe.passed = true;
                this.score++;
                audio.playScore();
                if (this.onScoreChange) this.onScoreChange(this.score);

                // Spawn score celebration stars
                for (let j = 0; j < 8; j++) {
                    this.spawnParticle(
                        pipe.x + pipe.width / 2,
                        this.height / 2 + (Math.random() * 200 - 100),
                        (Math.random() * 4 - 2),
                        (Math.random() * 4 - 2),
                        Math.random() * 4 + 3,
                        '#ffd700', // Gold stars
                        1.0,
                        0.93
                    );
                }
            }

            // Remove off-screen pipes
            if (pipe.x + pipe.width < 0) {
                this.pipes.splice(i, 1);
            }
        }
    }

    /**
     * Spawn a new set of pipes (top and bottom)
     */
    spawnPipe(gapSize) {
        const pipeWidth = 72;
        const groundY = this.height - this.groundHeight;
        
        // Randomize gap location
        const availableSpace = groundY - gapSize - (this.minPipeHeight * 2);
        const topHeight = this.minPipeHeight + Math.random() * availableSpace;
        const bottomHeight = groundY - topHeight - gapSize;

        this.pipes.push({
            x: this.width,
            width: pipeWidth,
            topHeight,
            bottomHeight,
            passed: false
        });
    }

    /**
     * Collison detection using bounding box vs circle
     */
    checkCollision(bird, pipe) {
        // Tighten bounding box slightly for modern forgiving gameplay
        const tolerance = 4;
        const birdLeft = bird.x - bird.radius + tolerance;
        const birdRight = bird.x + bird.radius - tolerance;
        const birdTop = bird.y - bird.radius + tolerance;
        const birdBottom = bird.y + bird.radius - tolerance;

        // Pipe borders
        const pipeLeft = pipe.x;
        const pipeRight = pipe.x + pipe.width;
        const pipeTopLimit = pipe.topHeight;
        const pipeBottomStart = this.height - this.groundHeight - pipe.bottomHeight;

        // Check if bird is inside pipe x-bounds
        if (birdRight > pipeLeft && birdLeft < pipeRight) {
            // Collision with top pipe
            if (birdTop < pipeTopLimit) {
                return true;
            }
            // Collision with bottom pipe
            if (birdBottom > pipeBottomStart) {
                return true;
            }
        }
        return false;
    }

    /**
     * Trigger crash events, highscore checks, and game over state transition
     */
    triggerGameOver() {
        this.state = GAME_STATE.GAMEOVER;
        audio.playCrash();

        // Highscore calculation
        let isNewHigh = false;
        if (this.score > this.highScore) {
            this.highScore = this.score;
            localStorage.setItem('flappy_highscore', this.highScore.toString());
            isNewHigh = true;
        }

        // Trigger screen shake
        this.screenShakeTime = 0.35; // 350ms screen shake
        this.screenShakeMagnitude = 10;
        this.flashScreen = true;
        this.flashTimer = 0.15; // 150ms screen flash

        // Spawn explosion particle cloud
        for (let i = 0; i < 25; i++) {
            const angle = Math.random() * Math.PI * 2;
            const speed = Math.random() * 8 + 2;
            this.spawnParticle(
                this.bird.x,
                this.bird.y,
                Math.cos(angle) * speed,
                Math.sin(angle) * speed,
                Math.random() * 6 + 4,
                i % 2 === 0 ? this.currentTheme.particleColor : '#ff3333',
                1.0,
                0.93
            );
        }

        if (this.onGameStateChange) {
            this.onGameStateChange(this.state, isNewHigh);
        }
    }
}
