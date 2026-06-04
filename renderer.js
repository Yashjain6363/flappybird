/* ==========================================================================
   CANVAS GAME GRAPHICS RENDERER - renderer.js
   ========================================================================== */

export class GameRenderer {
    /**
     * @param {HTMLCanvasElement} canvas
     * @param {FlappyBirdGame} game
     */
    constructor(canvas, game) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.game = game;

        // Visual constants
        this.birdFlapAnim = 0;

        // Resize initially
        this.resize();
    }

    /**
     * Adjust canvas internal size to fit wrapper container dimensions
     * keeps standard game coordinate resolution (480x800) mapping crisp.
     */
    resize() {
        const rect = this.canvas.parentElement.getBoundingClientRect();
        this.canvas.width = this.game.width;
        this.canvas.height = this.game.height;
    }

    /**
     * Clear and redraw the entire game frame
     */
    render() {
        const ctx = this.ctx;
        const game = this.game;

        ctx.save();

        // 1. Handle Screen Shake (Visual Juice)
        if (game.screenShakeMagnitude > 0) {
            const shakeX = (Math.random() - 0.5) * game.screenShakeMagnitude;
            const shakeY = (Math.random() - 0.5) * game.screenShakeMagnitude;
            ctx.translate(shakeX, shakeY);
        }

        // 2. Draw Sky Background
        this.drawSky(ctx, game);

        // 3. Draw Background Parallax Structures (City skyline, distant hills, digital grids)
        this.drawParallaxBackground(ctx, game);

        // 4. Draw Obstacles (Pipes)
        this.drawPipes(ctx, game);

        // 5. Draw Particles
        this.drawParticles(ctx);

        // 6. Draw Ground Layer
        this.drawGround(ctx, game);

        // 7. Draw Player (Bird)
        this.drawBird(ctx, game);

        // 8. Draw Flash Overlay (Screen hit flash)
        if (game.flashScreen) {
            ctx.fillStyle = `rgba(255, 255, 255, ${game.flashTimer / 0.15})`;
            ctx.fillRect(0, 0, game.width, game.height);
        }

        ctx.restore();
    }

    /**
     * Draws sky gradient
     */
    drawSky(ctx, game) {
        const theme = game.currentTheme;
        if (theme.id === 'retro') {
            // Sunset retro look
            const grad = ctx.createLinearGradient(0, 0, 0, game.height);
            grad.addColorStop(0, '#3a7bd5');
            grad.addColorStop(0.5, '#3a6073');
            grad.addColorStop(1, '#2c3e50');
            ctx.fillStyle = grad;
        } else if (theme.id === 'neon') {
            // Cyberpunk Grid Sky
            const grad = ctx.createLinearGradient(0, 0, 0, game.height);
            grad.addColorStop(0, '#0a0612');
            grad.addColorStop(0.6, '#170c26');
            grad.addColorStop(1, '#0a0612');
            ctx.fillStyle = grad;
        } else if (theme.id === 'forest') {
            // Deep forest mist
            const grad = ctx.createLinearGradient(0, 0, 0, game.height);
            grad.addColorStop(0, '#0c1b12');
            grad.addColorStop(0.7, '#182b21');
            grad.addColorStop(1, '#0d1813');
            ctx.fillStyle = grad;
        }
        ctx.fillRect(0, 0, game.width, game.height);
    }

    /**
     * Draws the parallax background layers
     */
    drawParallaxBackground(ctx, game) {
        const theme = game.currentTheme;

        if (theme.id === 'retro') {
            this.drawRetroBackground(ctx, game);
        } else if (theme.id === 'neon') {
            this.drawNeonBackground(ctx, game);
        } else if (theme.id === 'forest') {
            this.drawForestBackground(ctx, game);
        }
    }

    /**
     * Classic retro clouds and city silhouettes
     */
    drawRetroBackground(ctx, game) {
        // Distant Hills / Mountains (Slow Parallax)
        ctx.fillStyle = '#264348';
        const hillOffset = game.skyOffset;
        ctx.beginPath();
        for (let x = 0; x <= game.width + 10; x += 10) {
            const worldX = (x + hillOffset) * 0.15;
            const y = 580 + Math.sin(worldX) * 20 + Math.cos(worldX * 0.5) * 10;
            if (x === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }
        ctx.lineTo(game.width, game.height);
        ctx.lineTo(0, game.height);
        ctx.fill();

        // City skyline (Medium Parallax)
        ctx.fillStyle = '#34495e';
        const cityWidth = 60;
        const cityHeight = 120;
        const scrollX = game.cityOffset;
        
        ctx.save();
        ctx.translate(-scrollX, 0);
        // Loop drawing city elements to fill screen space
        for (let i = 0; i < (game.width / cityWidth) + 3; i++) {
            const x = i * cityWidth;
            const h = cityHeight + Math.sin(i * 1.7) * 40;
            const topY = game.height - game.groundHeight - h;

            // Draw skyscraper silhouette
            ctx.fillRect(x, topY, cityWidth - 5, h);

            // Small window dots
            ctx.fillStyle = 'rgba(241, 196, 15, 0.2)';
            for (let wx = x + 8; wx < x + cityWidth - 12; wx += 14) {
                for (let wy = topY + 15; wy < game.height - game.groundHeight - 10; wy += 20) {
                    if (Math.sin(wx + wy) > -0.2) {
                        ctx.fillRect(wx, wy, 5, 8);
                    }
                }
            }
            ctx.fillStyle = '#34495e';
        }
        ctx.restore();
    }

    /**
     * Cyberpunk neon grid and vaporwave horizon
     */
    drawNeonBackground(ctx, game) {
        const groundY = game.height - game.groundHeight;

        // Draw horizontal grid lines (perspective grid converging on horizon at y=350)
        ctx.strokeStyle = 'rgba(0, 255, 255, 0.08)';
        ctx.lineWidth = 1;
        const horizon = 400;

        // Draw neon mountain range silhouette
        ctx.strokeStyle = 'rgba(255, 0, 127, 0.4)';
        ctx.shadowColor = 'rgba(255, 0, 127, 0.5)';
        ctx.shadowBlur = 6;
        ctx.fillStyle = '#120a1c';
        
        ctx.beginPath();
        const mountainOffset = game.skyOffset;
        ctx.moveTo(0, groundY);
        for (let x = 0; x <= game.width + 20; x += 30) {
            const worldX = (x + mountainOffset) * 0.12;
            const y = 480 + Math.sin(worldX) * 35 + Math.cos(worldX * 2.1) * 12;
            ctx.lineTo(x, y);
        }
        ctx.lineTo(game.width, groundY);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
        ctx.shadowBlur = 0; // reset

        // Neon City Skyline (Medium Parallax)
        ctx.fillStyle = '#161026';
        ctx.strokeStyle = 'rgba(123, 47, 247, 0.6)';
        ctx.lineWidth = 2;
        const blockWidth = 50;
        ctx.save();
        ctx.translate(-game.cityOffset, 0);
        for (let i = 0; i < (game.width / blockWidth) + 3; i++) {
            const x = i * blockWidth;
            const h = 140 + Math.cos(i * 1.5) * 50;
            const topY = groundY - h;

            // Draw block building
            ctx.fillRect(x, topY, blockWidth - 8, h);
            ctx.strokeRect(x, topY, blockWidth - 8, h);
        }
        ctx.restore();
    }

    /**
     * Silhouette pine trees and spooky forest canopy
     */
    drawForestBackground(ctx, game) {
        const groundY = game.height - game.groundHeight;

        // Distant Trees (Slow Parallax)
        ctx.fillStyle = '#121f19';
        ctx.save();
        ctx.translate(-game.skyOffset, 0);
        const farSpacing = 40;
        for (let i = 0; i < (game.width / farSpacing) + 3; i++) {
            const x = i * farSpacing;
            const treeHeight = 110 + Math.sin(i) * 30;
            this.drawPineTree(ctx, x, groundY, treeHeight, 28);
        }
        ctx.restore();

        // Near Trees (Medium Parallax)
        ctx.fillStyle = '#0b1612';
        ctx.save();
        ctx.translate(-game.cityOffset, 0);
        const nearSpacing = 70;
        for (let i = 0; i < (game.width / nearSpacing) + 3; i++) {
            const x = i * nearSpacing;
            const treeHeight = 160 + Math.cos(i * 1.2) * 55;
            this.drawPineTree(ctx, x, groundY, treeHeight, 42);
        }
        ctx.restore();
    }

    /**
     * Helper to draw a stylized pine tree shape
     */
    drawPineTree(ctx, x, groundY, height, width) {
        ctx.beginPath();
        ctx.moveTo(x, groundY);
        ctx.lineTo(x, groundY - height);
        ctx.lineTo(x - width/2, groundY - height + width);
        ctx.lineTo(x - width/4, groundY - height + width);
        ctx.lineTo(x - width*0.7, groundY - height + width*2);
        ctx.lineTo(x - width/3, groundY - height + width*2);
        ctx.lineTo(x - width, groundY);
        ctx.closePath();
        ctx.fill();

        // Mirror tree side
        ctx.beginPath();
        ctx.moveTo(x, groundY);
        ctx.lineTo(x, groundY - height);
        ctx.lineTo(x + width/2, groundY - height + width);
        ctx.lineTo(x + width/4, groundY - height + width);
        ctx.lineTo(x + width*0.7, groundY - height + width*2);
        ctx.lineTo(x + width/3, groundY - height + width*2);
        ctx.lineTo(x + width, groundY);
        ctx.closePath();
        ctx.fill();
    }

    /**
     * Draws the bird (player character)
     */
    drawBird(ctx, game) {
        const bird = game.bird;
        const colors = game.currentTheme.birdColors;

        ctx.save();
        ctx.translate(bird.x, bird.y);
        ctx.rotate(bird.angle);

        // Flapping animation calculation
        if (game.state === 'PLAYING') {
            this.birdFlapAnim = Math.sin(Date.now() * 0.015);
        } else {
            this.birdFlapAnim = 0;
        }

        // Draw body shadow
        ctx.fillStyle = 'rgba(0, 0, 0, 0.15)';
        ctx.beginPath();
        ctx.arc(2, 6, bird.radius, 0, Math.PI * 2);
        ctx.fill();

        // 1. Draw Bird Base Body (main color)
        ctx.fillStyle = colors[0]; // Yellow / Cyan / Autumn Orange
        ctx.beginPath();
        ctx.arc(0, 0, bird.radius, 0, Math.PI * 2);
        ctx.fill();
        ctx.lineWidth = 2.5;
        ctx.strokeStyle = '#000000';
        ctx.stroke();

        // 2. Draw Belly (secondary color gradient)
        ctx.fillStyle = colors[2] || '#fff';
        ctx.beginPath();
        ctx.arc(0, 0, bird.radius - 1, Math.PI * 0.1, Math.PI * 0.9);
        ctx.fill();

        // 3. Draw Eye
        ctx.fillStyle = '#ffffff';
        ctx.beginPath();
        ctx.arc(6, -5, 5, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();

        ctx.fillStyle = '#000000';
        ctx.beginPath();
        ctx.arc(7, -5, 2, 0, Math.PI * 2);
        ctx.fill();

        // 4. Draw Beak (accent color)
        ctx.fillStyle = colors[1]; // Orange / Blue / Red
        ctx.beginPath();
        ctx.moveTo(11, -4);
        ctx.quadraticCurveTo(24, -4, 21, 1);
        ctx.quadraticCurveTo(12, 6, 8, 2);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();

        // 5. Draw Wing (animated flap)
        ctx.save();
        ctx.translate(-5, 0);
        // Wing rotation animation based on bounce
        const flapAngle = this.birdFlapAnim * 0.6;
        ctx.rotate(flapAngle);

        ctx.fillStyle = colors[1];
        ctx.beginPath();
        ctx.ellipse(-1, 0, 10, 6, Math.PI * 0.1, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();

        // Highlight stripe on wing
        ctx.fillStyle = '#ffffff';
        ctx.beginPath();
        ctx.ellipse(-1, -1, 6, 2, Math.PI * 0.1, 0, Math.PI * 2);
        ctx.fill();

        ctx.restore();

        ctx.restore();
    }

    /**
     * Draws the scrollable pipes
     */
    drawPipes(ctx, game) {
        const theme = game.currentTheme;

        for (const pipe of game.pipes) {
            // Draw Top Pipe
            this.drawSinglePipe(ctx, pipe.x, 0, pipe.width, pipe.topHeight, true, theme);

            // Draw Bottom Pipe
            const pipeBottomStart = game.height - game.groundHeight - pipe.bottomHeight;
            this.drawSinglePipe(ctx, pipe.x, pipeBottomStart, pipe.width, pipe.bottomHeight, false, theme);
        }
    }

    /**
     * Draw individual top or bottom pipe with beautiful linear shading & borders
     */
    drawSinglePipe(ctx, x, y, width, height, isTop, theme) {
        ctx.save();

        const endY = y + height;

        // Neon Glow effect
        if (theme.id === 'neon') {
            ctx.shadowColor = theme.pipeColor;
            ctx.shadowBlur = 10;
        }

        // Pipe Body Base Gradient (vertical highlight to feel cylindrical)
        const bodyGrad = ctx.createLinearGradient(x, 0, x + width, 0);
        bodyGrad.addColorStop(0, theme.pipeBorderColor);
        bodyGrad.addColorStop(0.3, theme.pipeColor);
        bodyGrad.addColorStop(0.7, theme.pipeColor);
        bodyGrad.addColorStop(1, theme.pipeBorderColor);

        ctx.fillStyle = bodyGrad;
        ctx.fillRect(x, y, width, height);

        // Add 2.5px dark outline for retro crispness
        ctx.shadowBlur = 0; // Disable shadow for strokes
        ctx.strokeStyle = '#000000';
        ctx.lineWidth = 2.5;
        
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.lineTo(x, endY);
        ctx.moveTo(x + width, y);
        ctx.lineTo(x + width, endY);
        ctx.stroke();

        // Draw Pipe Lip / Collar (the wider bit at the end)
        const lipHeight = 28;
        const lipExt = 4; // protrusion on each side
        const lipX = x - lipExt;
        const lipWidth = width + (lipExt * 2);
        const lipY = isTop ? endY - lipHeight : y;

        // Shadow & Gradient for Pipe Lip
        const lipGrad = ctx.createLinearGradient(lipX, 0, lipX + lipWidth, 0);
        lipGrad.addColorStop(0, theme.pipeBorderColor);
        lipGrad.addColorStop(0.3, '#ffffff'); // bright sheen highlight
        lipGrad.addColorStop(0.5, theme.pipeColor);
        lipGrad.addColorStop(1, theme.pipeBorderColor);

        ctx.fillStyle = lipGrad;
        ctx.fillRect(lipX, lipY, lipWidth, lipHeight);
        ctx.strokeRect(lipX, lipY, lipWidth, lipHeight);

        // Subtle dark rib stripes on the pipe lips for arcade feel
        ctx.strokeStyle = 'rgba(0, 0, 0, 0.2)';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(lipX + 6, lipY + 4);
        ctx.lineTo(lipX + 6, lipY + lipHeight - 4);
        ctx.moveTo(lipX + lipWidth - 6, lipY + 4);
        ctx.lineTo(lipX + lipWidth - 6, lipY + lipHeight - 4);
        ctx.stroke();

        ctx.restore();
    }

    /**
     * Draws particles in flight (feathers / score stars / sparks)
     */
    drawParticles(ctx) {
        ctx.save();
        for (const p of this.game.particles) {
            ctx.save();
            ctx.translate(p.x, p.y);
            ctx.rotate(p.rotation);
            ctx.globalAlpha = p.alpha;
            ctx.fillStyle = p.color;

            // Draw feather shape (slightly oblong ellipse) or star shape based on color
            if (p.color === '#ffd700') {
                // Gold Star
                this.drawStar(ctx, 0, 0, 5, p.size, p.size / 2);
            } else {
                // Feathers / Sparks
                ctx.beginPath();
                ctx.ellipse(0, 0, p.size, p.size * 0.4, 0, 0, Math.PI * 2);
                ctx.fill();
            }
            ctx.restore();
        }
        ctx.restore();
    }

    /**
     * Star shape drawing helper
     */
    drawStar(ctx, cx, cy, spikes, outerRadius, innerRadius) {
        let rot = Math.PI / 2 * 3;
        let x = cx;
        let y = cy;
        const step = Math.PI / spikes;

        ctx.beginPath();
        ctx.moveTo(cx, cy - outerRadius);
        for (let i = 0; i < spikes; i++) {
            x = cx + Math.cos(rot) * outerRadius;
            y = cy + Math.sin(rot) * outerRadius;
            ctx.lineTo(x, y);
            rot += step;

            x = cx + Math.cos(rot) * innerRadius;
            y = cy + Math.sin(rot) * innerRadius;
            ctx.lineTo(x, y);
            rot += step;
        }
        ctx.lineTo(cx, cy - outerRadius);
        ctx.closePath();
        ctx.fill();
    }

    /**
     * Draws moving ground layer
     */
    drawGround(ctx, game) {
        const theme = game.currentTheme;
        const groundY = game.height - game.groundHeight;

        ctx.save();
        // Ground Body
        ctx.fillStyle = theme.groundColor;
        ctx.fillRect(0, groundY, game.width, game.groundHeight);

        // Ground Top Border / Grass line
        ctx.fillStyle = theme.groundBorderColor;
        ctx.fillRect(0, groundY, game.width, 12);

        // Ground Stroke Borders
        ctx.strokeStyle = '#000000';
        ctx.lineWidth = 2.5;
        ctx.beginPath();
        ctx.moveTo(0, groundY);
        ctx.lineTo(game.width, groundY);
        ctx.moveTo(0, groundY + 12);
        ctx.lineTo(game.width, groundY + 12);
        ctx.stroke();

        // Decorative slanted retro dirt lines scrolling along
        ctx.strokeStyle = 'rgba(0, 0, 0, 0.15)';
        ctx.lineWidth = 4;
        ctx.save();
        ctx.translate(-game.groundOffset, 0);
        
        ctx.beginPath();
        const spacing = 24;
        for (let i = -1; i < (game.width / spacing) + 3; i++) {
            const x = i * spacing;
            ctx.moveTo(x, groundY + 22);
            ctx.lineTo(x - 8, groundY + game.groundHeight - 10);
        }
        ctx.stroke();
        ctx.restore();

        ctx.restore();
    }
}
