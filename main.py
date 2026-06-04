import os
import sys
import math
import random
import array
import json
import pygame

# Initialize Pygame and Mixer
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=1)
pygame.font.init()

# Game Constants
VIRTUAL_WIDTH = 480;
VIRTUAL_HEIGHT = 800;

# Game States
class GameState:
    START = 'START'
    PLAYING = 'PLAYING'
    PAUSED = 'PAUSED'
    GAMEOVER = 'GAMEOVER'

# Themes Definitions
THEMES = {
    'retro': {
        'sky': (78, 192, 202),         # #4EC0CA
        'pipe': (115, 191, 46),        # #73BF2E
        'pipe_border': (83, 128, 24),   # #538018
        'ground': (221, 216, 148),     # #DDD894
        'ground_border': (132, 192, 120), # #84C078
        'bird_body': (255, 235, 59),   # Yellow
        'bird_accent': (245, 127, 23), # Orange
        'bird_belly': (255, 255, 255), # White
        'particle': (255, 255, 255),
        'bg_gradient_start': (30, 60, 114),
        'bg_gradient_end': (42, 82, 152),
    },
    'neon': {
        'sky': (15, 12, 27),           # Cyber dark
        'pipe': (255, 0, 127),         # Hot Magenta
        'pipe_border': (123, 47, 247),  # Glowing Purple
        'ground': (29, 25, 54),        # Dark Purple
        'ground_border': (0, 255, 255), # Neon Cyan
        'bird_body': (0, 255, 255),    # Cyan
        'bird_accent': (0, 114, 255),  # Cobalt Blue
        'bird_belly': (123, 47, 247),  # Violet
        'particle': (0, 255, 255),
        'bg_gradient_start': (10, 5, 20),
        'bg_gradient_end': (32, 15, 50),
    },
    'forest': {
        'sky': (29, 42, 35),           # Forest mist
        'pipe': (39, 174, 96),         # Emerald Green
        'pipe_border': (30, 132, 73),  # Dark Green
        'ground': (25, 37, 31),        # Spruce Ground
        'ground_border': (46, 204, 113),# Grass border
        'bird_body': (245, 176, 65),   # Autumn Yellow
        'bird_accent': (203, 67, 53),  # Auburn Red
        'bird_belly': (235, 245, 251), # Light Mist
        'particle': (46, 204, 113),
        'bg_gradient_start': (20, 32, 26),
        'bg_gradient_end': (13, 22, 18),
    }
}

# ---------------------------------------------------------------------------
# AUDIO SYNTHESIZER
# ---------------------------------------------------------------------------
class SoundEngine:
    def __init__(self):
        self.muted = False
        
        # Pre-synthesize sound buffers
        self.flap_sound = self._generate_flap()
        self.score_sound = self._generate_score()
        self.crash_sound = self._generate_crash()

    def toggle_mute(self):
        self.muted = not self.muted
        return self.muted

    def _generate_flap(self):
        sample_rate = 22050
        duration = 0.12
        num_samples = int(sample_rate * duration)
        buf = array.array('h', [0] * num_samples)
        phase = 0.0
        
        for i in range(num_samples):
            t = i / sample_rate
            # Pitch sweep up: 140Hz -> 320Hz
            freq = 140.0 + (320.0 - 140.0) * (t / duration)
            phase += 2.0 * math.pi * freq / sample_rate
            
            # Triangle wave
            norm_phase = (phase % (2.0 * math.pi)) / (2.0 * math.pi)
            val = 4.0 * abs(norm_phase - 0.5) - 1.0
            
            # Volume envelope (fade out)
            env = 1.0 - (t / duration)
            buf[i] = int(val * 0.35 * 32767 * env)
            
        return pygame.mixer.Sound(buffer=buf)

    def _generate_score(self):
        sample_rate = 22050
        duration = 0.25
        num_samples = int(sample_rate * duration)
        buf = array.array('h', [0] * num_samples)
        
        phase1 = 0.0
        phase2 = 0.0
        
        for i in range(num_samples):
            t = i / sample_rate
            val = 0.0
            
            # Chime 1: D5 (587.33Hz) for 0.08s
            if t < 0.08:
                phase1 += 2.0 * math.pi * 587.33 / sample_rate
                val += 0.12 if (math.sin(phase1) >= 0) else -0.12
                val *= (1.0 - (t / 0.08))
                
            # Chime 2: A5 (880.00Hz) starting at 0.07s for 0.18s
            if t >= 0.07:
                t2 = t - 0.07
                phase2 += 2.0 * math.pi * 880.00 / sample_rate
                n2 = 0.12 if (math.sin(phase2) >= 0) else -0.12
                val += n2 * (1.0 - (t2 / 0.18))
                
            buf[i] = int(val * 32767)
            
        return pygame.mixer.Sound(buffer=buf)

    def _generate_crash(self):
        sample_rate = 22050
        duration = 0.45
        num_samples = int(sample_rate * duration)
        buf = array.array('h', [0] * num_samples)
        
        phase_rumble = 0.0
        
        for i in range(num_samples):
            t = i / sample_rate
            val = 0.0
            
            # 1. White Noise component
            noise = random.uniform(-1.0, 1.0)
            noise_env = 1.0 - (t / duration)
            val += noise * 0.4 * noise_env
            
            # 2. Bass sawtooth rumble (180Hz -> 40Hz)
            if t < 0.3:
                freq = 180.0 - (180.0 - 40.0) * (t / 0.3)
                phase_rumble += 2.0 * math.pi * freq / sample_rate
                norm_phase = (phase_rumble % (2.0 * math.pi)) / (2.0 * math.pi)
                saw = 2.0 * norm_phase - 1.0
                rumble_env = 1.0 - (t / 0.3)
                val += saw * 0.35 * rumble_env
                
            val = max(-1.0, min(1.0, val))
            buf[i] = int(val * 32767)
            
        return pygame.mixer.Sound(buffer=buf)

    def play_flap(self):
        if not self.muted:
            self.flap_sound.play()

    def play_score(self):
        if not self.muted:
            self.score_sound.play()

    def play_crash(self):
        if not self.muted:
            self.crash_sound.play()


audio = SoundEngine()

# ---------------------------------------------------------------------------
# GAME ENTITIES
# ---------------------------------------------------------------------------
class Bird:
    def __init__(self):
        self.x = 100
        self.y = 350
        self.radius = 16
        self.velocity = 0.0
        self.gravity = 0.45
        self.jump_strength = -8.0
        self.max_fall_speed = 12.0
        self.angle = 0.0
        self.flap_anim = 0.0

    def reset(self):
        self.x = 100
        self.y = 350
        self.velocity = 0.0
        self.angle = 0.0
        self.flap_anim = 0.0

    def flap(self):
        self.velocity = self.jump_strength
        audio.play_flap()

    def update(self, dt, state, ground_y):
        if state == GameState.START:
            # Passive floating on start screen
            time_val = pygame.time.get_ticks() * 0.005
            self.y = 350 + math.sin(time_val) * 15
            self.angle = math.sin(time_val * 1.5) * 6 # in degrees
            return

        # Apply gravity (scaled by dt relative to 60fps)
        self.velocity += self.gravity * 60.0 * dt
        if self.velocity > self.max_fall_speed:
            self.velocity = self.max_fall_speed
            
        self.y += self.velocity

        if state == GameState.GAMEOVER:
            # Ground clamp
            if self.y > ground_y - self.radius:
                self.y = ground_y - self.radius
                self.velocity = 0
            # Spin down
            self.angle = min(90.0, self.angle + 8.0)
            return

        # Calculate rotation angle based on falling speed
        if self.velocity < 3:
            self.angle = -18.0 # tilt up slightly
        else:
            self.angle = min(90.0, self.angle + 3.0 * (self.velocity - 3))

        # Ceiling clamp
        if self.y - self.radius < 0:
            self.y = self.radius
            self.velocity = 0.5

        # Update wing flap animation
        self.flap_anim = math.sin(pygame.time.get_ticks() * 0.015)

    def draw(self, surface, theme):
        # Draw bird on a local rotated surface
        radius = int(self.radius)
        size = radius * 3
        bird_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        
        cx, cy = size // 2, size // 2
        body_color = theme['bird_body']
        accent_color = theme['bird_accent']
        belly_color = theme['bird_belly']

        # 1. Shadow
        pygame.draw.circle(bird_surf, (0, 0, 0, 38), (cx + 2, cy + 5), radius)

        # 2. Base Body
        pygame.draw.circle(bird_surf, body_color, (cx, cy), radius)
        pygame.draw.circle(bird_surf, (0, 0, 0), (cx, cy), radius, 2)

        # 3. Belly
        # Draw lower half arc for belly
        belly_rect = pygame.Rect(cx - radius + 1, cy - 1, (radius - 1) * 2, radius)
        pygame.draw.chord(bird_surf, belly_color, belly_rect, 0, math.pi, 0)
        # re-draw bottom border details
        pygame.draw.circle(bird_surf, (0, 0, 0), (cx, cy), radius, 2)

        # 4. Eye
        pygame.draw.circle(bird_surf, (255, 255, 255), (cx + 6, cy - 5), 5)
        pygame.draw.circle(bird_surf, (0, 0, 0), (cx + 6, cy - 5), 5, 1)
        pygame.draw.circle(bird_surf, (0, 0, 0), (cx + 7, cy - 5), 2)

        # 5. Beak
        beak_pts = [(cx + 10, cy - 4), (cx + 21, cy - 1), (cx + 8, cy + 3)]
        pygame.draw.polygon(bird_surf, accent_color, beak_pts)
        pygame.draw.polygon(bird_surf, (0, 0, 0), beak_pts, 2)

        # 6. Flapping Wing
        wing_w, wing_h = 10, 6
        wing_surf = pygame.Surface((wing_w * 2, wing_h * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(wing_surf, accent_color, (0, 0, wing_w * 2, wing_h * 2))
        pygame.draw.ellipse(wing_surf, (0, 0, 0), (0, 0, wing_w * 2, wing_h * 2), 2)
        pygame.draw.ellipse(wing_surf, (255, 255, 255), (2, 2, wing_w * 1.2, wing_h * 0.8))

        # Rotate wing slightly based on wing flap offset
        flap_angle = self.flap_anim * 35.0
        wing_rot = pygame.transform.rotate(wing_surf, flap_angle)
        wing_rect = wing_rot.get_rect(center=(cx - 6, cy))
        bird_surf.blit(wing_rot, wing_rect.topleft)

        # Rotate entire bird surface
        rotated_bird = pygame.transform.rotate(bird_surf, -self.angle)
        rot_rect = rotated_bird.get_rect(center=(self.x, self.y))
        surface.blit(rotated_bird, rot_rect.topleft)


class Pipe:
    def __init__(self, x, top_height, bottom_height, width=72):
        self.x = x
        self.width = width
        self.top_height = top_height
        self.bottom_height = bottom_height
        self.passed = False

    def update(self, speed, dt):
        self.x -= speed * dt

    def draw(self, surface, theme, ground_y):
        # Top Pipe
        self._draw_single_pipe(surface, self.x, 0, self.width, self.top_height, True, theme, ground_y)
        # Bottom Pipe
        bot_y = ground_y - self.bottom_height
        self._draw_single_pipe(surface, self.x, bot_y, self.width, self.bottom_height, False, theme, ground_y)

    def _draw_single_pipe(self, surface, px, py, pw, ph, is_top, theme, ground_y):
        pipe_color = theme['pipe']
        border_color = theme['pipe_border']
        glow = theme['sky'] == THEMES['neon']['sky'] # Neon glow check

        # Pipe Body rect
        body_rect = pygame.Rect(px, py, pw, ph)

        # Neon Glow pre-drawing
        if glow:
            glow_surf = pygame.Surface((pw + 16, ph), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*pipe_color, 45), (8, 0, pw, ph))
            pygame.draw.rect(glow_surf, (*pipe_color, 20), (0, 0, pw + 16, ph))
            surface.blit(glow_surf, (px - 8, py))

        # Draw Base Pipe Body Cylindrical Highlight Gradient
        # Since pygame doesn't do linear gradients across arbitrary shapes easily,
        # we can draw thin vertical stripes to create a 3D cylindrical lighting feel!
        for sx in range(int(pw)):
            factor = abs(sx - pw * 0.3) / (pw * 0.7)
            # Interpolate body color with border/highlight colors
            if sx < pw * 0.3:
                # Blend border to pipe color
                t = sx / (pw * 0.3)
                color = [int(border_color[c] + (pipe_color[c] - border_color[c]) * t) for c in range(3)]
            else:
                # Blend pipe color back to dark border
                t = (sx - pw * 0.3) / (pw * 0.7)
                color = [int(pipe_color[c] + (border_color[c] - pipe_color[c]) * t) for c in range(3)]
            
            pygame.draw.line(surface, color, (px + sx, py), (px + sx, py + ph))

        # Draw Side Borders
        pygame.draw.line(surface, (0, 0, 0), (px, py), (px, py + ph), 2)
        pygame.draw.line(surface, (0, 0, 0), (px + pw, py), (px + pw, py + ph), 2)

        # Pipe Collar / Lip (the wider ring at the end)
        lip_h = 28
        lip_ext = 4
        lip_x = px - lip_ext
        lip_w = pw + lip_ext * 2
        lip_y = (py + ph - lip_h) if is_top else py

        # Lip Background Gradient
        for lx in range(int(lip_w)):
            if lx < lip_w * 0.3:
                t = lx / (lip_w * 0.3)
                color = [int(border_color[c] + (255 - border_color[c]) * t * 0.7) for c in range(3)] # Sheen
            else:
                t = (lx - lip_w * 0.3) / (lip_w * 0.7)
                color = [int(pipe_color[c] + (border_color[c] - pipe_color[c]) * t) for c in range(3)]
            pygame.draw.line(surface, color, (lip_x + lx, lip_y), (lip_x + lx, lip_y + lip_h))

        # Outline collar
        pygame.draw.rect(surface, (0, 0, 0), (lip_x, lip_y, lip_w, lip_h), 2)

        # Subtle vertical ridges on collar
        pygame.draw.line(surface, (0, 0, 0, 50), (lip_x + 6, lip_y + 4), (lip_x + 6, lip_y + lip_h - 4), 2)
        pygame.draw.line(surface, (0, 0, 0, 50), (lip_x + lip_w - 6, lip_y + 4), (lip_x + lip_w - 6, lip_y + lip_h - 4), 2)


class Particle:
    def __init__(self, x, y, vx, vy, size, color, alpha=1.0, decay=0.95):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = size
        self.color = color
        self.alpha = alpha
        self.decay = decay
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-6, 6)

    def update(self, dt):
        self.x += self.vx
        self.y += self.vy
        self.alpha *= self.decay
        self.rotation += self.rot_speed

    def draw(self, surface):
        if self.alpha <= 0.05:
            return
        
        alpha_val = int(self.alpha * 255)
        p_surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)

        # Star shapes (for points) or ellipses (feathers)
        if self.color == (255, 215, 0): # Gold stars
            self._draw_star(p_surf, self.size, self.size, 5, self.size, self.size // 2, (255, 215, 0, alpha_val))
        else:
            # Ellipse / Feather
            pygame.draw.ellipse(p_surf, (*self.color, alpha_val), (0, self.size // 2, self.size * 2, self.size))

        rotated_p = pygame.transform.rotate(p_surf, self.rotation)
        rot_rect = rotated_p.get_rect(center=(self.x, self.y))
        surface.blit(rotated_p, rot_rect.topleft)

    def _draw_star(self, surface, cx, cy, spikes, outer_r, inner_r, color):
        points = []
        rot = math.pi / 2 * 3
        step = math.pi / spikes
        for _ in range(spikes):
            # Outer point
            points.append((cx + math.cos(rot) * outer_r, cy + math.sin(rot) * outer_r))
            rot += step
            # Inner point
            points.append((cx + math.cos(rot) * inner_r, cy + math.sin(rot) * inner_r))
            rot += step
        pygame.draw.polygon(surface, color, points)


# ---------------------------------------------------------------------------
# MAIN GAME CLASS
# ---------------------------------------------------------------------------
class FlappyBirdGamePython:
    def __init__(self):
        # Setup display window
        self.window = pygame.display.set_mode((480, 800), pygame.RESIZABLE)
        pygame.display.set_caption("Flappy Bird: Premium Edition")
        
        # Virtual drawing surface (locks aspect ratio, coordinates)
        self.virtual_screen = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
        
        self.clock = pygame.time.Clock()
        self.running = True

        # Load Highscore file
        self.highscore_file = ".highscore"
        self.high_score = self.load_highscore()

        # Configs
        self.state = GameState.START
        self.score = 0
        self.theme_id = 'retro'
        self.theme = THEMES[self.theme_id]

        # Entities
        self.bird = Bird()
        self.pipes = []
        self.particles = []

        # Physics variables
        self.ground_height = 90
        self.ground_y = VIRTUAL_HEIGHT - self.ground_height
        
        # Timers / Speeds
        self.pipe_spawn_timer = 0
        self.pipe_spawn_interval = 1.7 # in seconds
        self.pipe_speed = 190.0 # px per second
        self.pipe_gap_default = 160
        self.min_pipe_height = 80

        # Parallax Background Offsets
        self.sky_offset = 0.0
        self.city_offset = 0.0
        self.ground_offset = 0.0

        # Screen Shake / Juice
        self.shake_timer = 0.0
        self.shake_magnitude = 0.0
        self.flash_timer = 0.0

        # Setup Fonts
        self.font_title = self.get_font(38, bold=True)
        self.font_subtitle = self.get_font(18, bold=True)
        self.font_menu = self.get_font(22, bold=True)
        self.font_score = self.get_font(42, bold=True)
        self.font_small = self.get_font(14)
        
        # UI Interactive Buttons (Start Screen)
        self.btn_start = pygame.Rect(110, 480, 260, 52)
        # Theme Button Rects
        self.theme_btn_retro = pygame.Rect(70, 360, 100, 50)
        self.theme_btn_neon = pygame.Rect(190, 360, 100, 50)
        self.theme_btn_forest = pygame.Rect(310, 360, 100, 50)
        
        # Game Over Buttons
        self.btn_restart = pygame.Rect(75, 480, 150, 48)
        self.btn_menu = pygame.Rect(255, 480, 150, 48)
        
        # Pause Overlay Buttons
        self.btn_resume = pygame.Rect(140, 350, 200, 46)
        self.btn_restart_pause = pygame.Rect(140, 415, 200, 46)
        self.btn_quit = pygame.Rect(140, 480, 200, 46)

    def get_font(self, size, bold=False):
        # Look for system fonts or fallback to Pygame default
        font_names = ["outfit", "segoeui", "helvetica", "arial"]
        for name in font_names:
            try:
                return pygame.font.SysFont(name, size, bold=bold)
            except Exception:
                pass
        return pygame.font.Font(None, size)

    def load_highscore(self):
        if os.path.exists(self.highscore_file):
            try:
                with open(self.highscore_file, 'r') as f:
                    return int(f.read().strip())
            except Exception:
                pass
        return 0

    def save_highscore(self, score):
        try:
            with open(self.highscore_file, 'w') as f:
                f.write(str(score))
        except Exception:
            pass

    def reset(self):
        self.score = 0
        self.bird.reset()
        self.pipes.clear()
        self.particles.clear()
        self.pipe_spawn_timer = 0.0
        self.shake_timer = 0.0
        self.shake_magnitude = 0.0
        self.flash_timer = 0.0

    def trigger_gameover(self):
        self.state = GameState.GAMEOVER
        audio.play_crash()

        # Shake juice
        self.shake_timer = 0.35
        self.shake_magnitude = 10.0
        self.flash_timer = 0.15

        # Check highscore
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_highscore(self.high_score)

        # Spawn particle cloud explosion
        for _ in range(25):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 10)
            self.particles.append(Particle(
                self.bird.x,
                self.bird.y,
                math.cos(angle) * speed,
                math.sin(angle) * speed,
                random.randint(4, 9),
                random.choice([self.theme['particle'], (255, 51, 51)]),
                1.0,
                0.93
            ))

    def trigger_flap(self):
        if self.state == GameState.START:
            self.state = GameState.PLAYING
            self.reset()
            self.bird.flap()
        elif self.state == GameState.PLAYING:
            self.bird.flap()
            # Spawn flap particles
            for _ in range(5):
                self.particles.append(Particle(
                    self.bird.x - 8,
                    self.bird.y + random.uniform(-6, 6),
                    -random.uniform(1.0, 3.0),
                    random.uniform(-1.5, 1.5),
                    random.randint(2, 5),
                    self.theme['particle'],
                    0.8,
                    0.95
                ))

    def spawn_pipe(self, gap_size):
        pw = 72
        # Randomize opening space
        avail = self.ground_y - gap_size - (self.min_pipe_height * 2)
        top_h = self.min_pipe_height + random.uniform(0, avail)
        bot_h = self.ground_y - top_h - gap_size
        self.pipes.append(Pipe(VIRTUAL_WIDTH, top_h, bot_h, pw))

    # ---------------------------------------------------------------------------
    # UPDATE ENGINE LOOP
    # ---------------------------------------------------------------------------
    def update(self, dt):
        # Update flash effect
        if self.flash_timer > 0:
            self.flash_timer -= dt
            
        # Update screen shake
        if self.shake_timer > 0:
            self.shake_timer -= dt
            if self.shake_timer <= 0:
                self.shake_magnitude = 0.0

        # Update particles (always run)
        for p in self.particles[:]:
            p.update(dt)
            if p.alpha < 0.05:
                self.particles.remove(p)

        if self.state == GameState.PAUSED:
            return

        # Bird update
        self.bird.update(dt, self.state, self.ground_y)

        if self.state == GameState.START:
            # Idle scroll
            self.sky_offset = (self.sky_offset + 15.0 * dt) % VIRTUAL_WIDTH
            self.city_offset = (self.city_offset + 35.0 * dt) % VIRTUAL_WIDTH
            self.ground_offset = (self.ground_offset + self.pipe_speed * dt) % VIRTUAL_WIDTH
            return

        if self.state == GameState.GAMEOVER:
            return

        # --- PLAYING STATE ---
        # Scroll Backgrounds
        self.sky_offset = (self.sky_offset + 20.0 * dt) % VIRTUAL_WIDTH
        self.city_offset = (self.city_offset + 50.0 * dt) % VIRTUAL_WIDTH
        self.ground_offset = (self.ground_offset + self.pipe_speed * dt) % VIRTUAL_WIDTH

        # Dynamic difficulty based on score
        current_gap = max(110, self.pipe_gap_default - (self.score // 6) * 6)
        current_speed = self.pipe_speed + min(60.0, (self.score // 8) * 8.0)

        # Spawn pipes
        self.pipe_spawn_timer += dt
        if self.pipe_spawn_timer >= self.pipe_spawn_interval:
            self.spawn_pipe(current_gap)
            self.pipe_spawn_timer = 0.0

        # Update pipes
        for pipe in self.pipes[:]:
            pipe.update(current_speed, dt)

            # Ground collision or pipe collision
            if self.bird.y + self.bird.radius >= self.ground_y:
                self.trigger_gameover()
                break

            # Box Collisions (incorporating a 4px forgiving tolerance)
            tol = 4
            b_left = self.bird.x - self.bird.radius + tol
            b_right = self.bird.x + self.bird.radius - tol
            b_top = self.bird.y - self.bird.radius + tol
            b_bottom = self.bird.y + self.bird.radius - tol

            if b_right > pipe.x and b_left < pipe.x + pipe.width:
                # Top pipe collision
                if b_top < pipe.top_height:
                    self.trigger_gameover()
                    break
                # Bottom pipe collision
                if b_bottom > self.ground_y - pipe.bottom_height:
                    self.trigger_gameover()
                    break

            # Scoring check
            if not pipe.passed and pipe.x + pipe.width < self.bird.x:
                pipe.passed = True
                self.score += 1
                audio.play_score()
                
                # Point celebration stars
                for _ in range(8):
                    self.particles.append(Particle(
                        pipe.x + pipe.width // 2,
                        VIRTUAL_HEIGHT // 2 + random.randint(-150, 150),
                        random.uniform(-2, 2),
                        random.uniform(-2, 2),
                        random.randint(3, 6),
                        (255, 215, 0), # Gold star color
                        1.0,
                        0.93
                    ))

            # Remove offscreen pipes
            if pipe.x + pipe.width < 0:
                self.pipes.remove(pipe)

    # ---------------------------------------------------------------------------
    # RENDER ENGINE LAYOUTS
    # ---------------------------------------------------------------------------
    def draw(self):
        screen = self.virtual_screen
        theme = self.theme

        # 1. Sky Color
        screen.fill(theme['sky'])

        # 2. Draw Parallax Background layers
        if self.theme_id == 'retro':
            self._draw_retro_bg(screen)
        elif self.theme_id == 'neon':
            self._draw_neon_bg(screen)
        elif self.theme_id == 'forest':
            self._draw_forest_bg(screen)

        # 3. Pipes drawing
        for pipe in self.pipes:
            pipe.draw(screen, theme, self.ground_y)

        # 4. Particles drawing
        for p in self.particles:
            p.draw(screen)

        # 5. Ground Drawing
        self._draw_ground(screen, theme)

        # 6. Bird Drawing
        self.bird.draw(screen, theme)

        # 7. Render UI overlays
        if self.state == GameState.START:
            self._draw_start_screen(screen)
        elif self.state == GameState.PLAYING:
            self._draw_hud(screen)
        elif self.state == GameState.PAUSED:
            self._draw_pause_screen(screen)
        elif self.state == GameState.GAMEOVER:
            self._draw_gameover_screen(screen)

        # 8. Flash effect
        if self.flash_timer > 0:
            flash_surf = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
            flash_surf.fill((255, 255, 255))
            flash_surf.set_alpha(int((self.flash_timer / 0.15) * 255))
            screen.blit(flash_surf, (0, 0))

        # Handle screen shake by shifting virtual blit coordinate
        shake_x = 0
        shake_y = 0
        if self.shake_timer > 0:
            shake_x = random.randint(-int(self.shake_magnitude), int(self.shake_magnitude))
            shake_y = random.randint(-int(self.shake_magnitude), int(self.shake_magnitude))

        # Scale virtual screen to window size, preserving aspect ratio
        win_w, win_h = self.window.get_size()
        scale = min(win_w / VIRTUAL_WIDTH, win_h / VIRTUAL_HEIGHT)
        scaled_w = int(VIRTUAL_WIDTH * scale)
        scaled_h = int(VIRTUAL_HEIGHT * scale)
        
        scaled_screen = pygame.transform.scale(screen, (scaled_w, scaled_h))
        
        # Center the scaled screen in the window
        dx = (win_w - scaled_w) // 2 + shake_x
        dy = (win_h - scaled_h) // 2 + shake_y
        
        self.window.fill((0, 0, 0))
        self.window.blit(scaled_screen, (dx, dy))
        pygame.display.flip()

    # ---------------------------------------------------------------------------
    # ENVIRONMENT DRAWING DETAILS
    # ---------------------------------------------------------------------------
    def _draw_retro_bg(self, screen):
        # Distant Mountains (Slow Parallax)
        pts = []
        for x in range(0, VIRTUAL_WIDTH + 15, 15):
            world_x = (x + self.sky_offset) * 0.15
            y = 580 + math.sin(world_x) * 20 + math.cos(world_x * 0.5) * 10
            pts.append((x, y))
        pts.append((VIRTUAL_WIDTH, self.ground_y))
        pts.append((0, self.ground_y))
        pygame.draw.polygon(screen, (38, 67, 72), pts)

        # Retro city skyline (Medium Parallax)
        city_w = 60
        city_h = 120
        offset_x = int(self.city_offset)
        
        for i in range((VIRTUAL_WIDTH // city_w) + 3):
            x = i * city_w - offset_x
            h = city_h + math.sin(i * 1.7) * 40
            top_y = self.ground_y - h
            
            # City block
            pygame.draw.rect(screen, (52, 73, 94), (x, top_y, city_w - 5, h))
            
            # Windows
            for wx in range(int(x + 8), int(x + city_w - 12), 14):
                for wy in range(int(top_y + 15), int(self.ground_y - 10), 20):
                    if math.sin(wx + wy) > -0.2:
                        pygame.draw.rect(screen, (241, 196, 15, 50), (wx, wy, 5, 8))

    def _draw_neon_bg(self, screen):
        # Synthwave Horizon grid lines
        horizon = 400
        for y in range(horizon, int(self.ground_y), 20):
            factor = (y - horizon) / (self.ground_y - horizon)
            alpha = int(factor * 30)
            pygame.draw.line(screen, (0, 255, 255, alpha), (0, y), (VIRTUAL_WIDTH, y))

        # Neon Mountain outline
        mountains = []
        mountain_offset = self.sky_offset
        mountains.append((0, self.ground_y))
        for x in range(0, VIRTUAL_WIDTH + 25, 25):
            world_x = (x + mountain_offset) * 0.12
            y = 480 + math.sin(world_x) * 35 + math.cos(world_x * 2.1) * 12
            mountains.append((x, y))
        mountains.append((VIRTUAL_WIDTH, self.ground_y))
        
        pygame.draw.polygon(screen, (18, 10, 28), mountains)
        
        # draw neon outline
        for idx in range(1, len(mountains) - 1):
            pygame.draw.line(screen, (255, 0, 127), mountains[idx-1], mountains[idx], 2)

        # Neon City block silhouette (Medium Parallax)
        block_w = 50
        offset_x = int(self.city_offset)
        for i in range((VIRTUAL_WIDTH // block_w) + 3):
            x = i * block_w - offset_x
            h = 140 + math.cos(i * 1.5) * 50
            top_y = self.ground_y - h
            pygame.draw.rect(screen, (22, 16, 38), (x, top_y, block_w - 8, h))
            pygame.draw.rect(screen, (123, 47, 247), (x, top_y, block_w - 8, h), 2)

    def _draw_forest_bg(self, screen):
        # Draw tall silhouette pine trees
        # Far layer
        offset_x = int(self.sky_offset)
        for i in range((VIRTUAL_WIDTH // 40) + 3):
            x = i * 40 - offset_x
            h = 110 + math.sin(i) * 30
            self._draw_pine_tree(screen, x, self.ground_y, h, 28, (18, 31, 25))

        # Near layer
        offset_x_near = int(self.city_offset)
        for i in range((VIRTUAL_WIDTH // 70) + 3):
            x = i * 70 - offset_x_near
            h = 160 + math.cos(i * 1.2) * 55
            self._draw_pine_tree(screen, x, self.ground_y, h, 42, (11, 22, 18))

    def _draw_pine_tree(self, screen, x, ground_y, height, width, color):
        # Draw triangular parts of pine tree
        pts1 = [(x, ground_y), (x, ground_y - height), (x - width//2, ground_y - height + width), 
                (x - width//4, ground_y - height + width), (x - int(width*0.7), ground_y - height + width*2),
                (x - width//3, ground_y - height + width*2), (x - width, ground_y)]
        pts2 = [(x, ground_y), (x, ground_y - height), (x + width//2, ground_y - height + width), 
                (x + width//4, ground_y - height + width), (x + int(width*0.7), ground_y - height + width*2),
                (x + width//3, ground_y - height + width*2), (x + width, ground_y)]
        pygame.draw.polygon(screen, color, pts1)
        pygame.draw.polygon(screen, color, pts2)

    def _draw_ground(self, screen, theme):
        # Ground base rect
        pygame.draw.rect(screen, theme['ground'], (0, self.ground_y, VIRTUAL_WIDTH, self.ground_height))
        # Top grass strip
        pygame.draw.rect(screen, theme['ground_border'], (0, self.ground_y, VIRTUAL_WIDTH, 12))
        
        # Outlines
        pygame.draw.line(screen, (0, 0, 0), (0, self.ground_y), (VIRTUAL_WIDTH, self.ground_y), 3)
        pygame.draw.line(screen, (0, 0, 0), (0, self.ground_y + 12), (VIRTUAL_WIDTH, self.ground_y + 12), 3)

        # Ground stripes
        spacing = 24
        offset = int(self.ground_offset) % spacing
        for i in range(-1, (VIRTUAL_WIDTH // spacing) + 2):
            x = i * spacing - offset
            pygame.draw.line(screen, (0, 0, 0, 30), (x, self.ground_y + 22), (x - 8, VIRTUAL_HEIGHT - 10), 3)

    # ---------------------------------------------------------------------------
    # OVERLAY MENU SCREENS
    # ---------------------------------------------------------------------------
    def _draw_glass_card(self, screen, rect, color, border_color):
        # Helper to draw semi-transparent card (glassmorphism feel)
        card_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(card_surf, color, (0, 0, rect.width, rect.height), border_radius=16)
        pygame.draw.rect(card_surf, border_color, (0, 0, rect.width, rect.height), 2, border_radius=16)
        screen.blit(card_surf, rect.topleft)

    def _draw_start_screen(self, screen):
        # Draw translucent main menu card
        card_rect = pygame.Rect(60, 160, 360, 420)
        card_color = (*self.theme['bg_gradient_start'], 190) # HSL-themed semi-transparent background
        border_color = (255, 255, 255, 50)
        self._draw_glass_card(screen, card_rect, card_color, border_color)

        # Title Logo Text
        title_top = self.font_title.render("FLAPPY", True, (255, 255, 255))
        title_bot = self.font_title.render("BIRD", True, self.theme['bird_body'])
        sub = self.font_subtitle.render("PYTHON PREMIUM", True, (203, 213, 225))

        screen.blit(title_top, title_top.get_rect(center=(VIRTUAL_WIDTH // 2, 220)))
        screen.blit(title_bot, title_bot.get_rect(center=(VIRTUAL_WIDTH // 2, 265)))
        screen.blit(sub, sub.get_rect(center=(VIRTUAL_WIDTH // 2, 305)))

        # Theme Selector Labels
        theme_label = self.font_small.render("SELECT THEME", True, (203, 213, 225))
        screen.blit(theme_label, theme_label.get_rect(center=(VIRTUAL_WIDTH // 2, 345)))

        # Draw Theme Buttons
        for theme_name, rect, emoji in [('retro', self.theme_btn_retro, '🌅'), 
                                       ('neon', self.theme_btn_neon, '🌌'), 
                                       ('forest', self.theme_btn_forest, '🌲')]:
            active = self.theme_id == theme_name
            bg = (255, 255, 255, 45) if active else (255, 255, 255, 15)
            border = self.theme['bird_body'] if active else (255, 255, 255, 30)
            
            btn_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(btn_surf, bg, (0, 0, rect.width, rect.height), border_radius=10)
            pygame.draw.rect(btn_surf, border, (0, 0, rect.width, rect.height), 2, border_radius=10)
            
            # Text / Emoji in button
            font_btn = self.get_font(14, bold=True)
            txt_emoji = font_btn.render(emoji, True, (255, 255, 255))
            txt_name = font_btn.render(theme_name.capitalize(), True, (255, 255, 255))
            
            btn_surf.blit(txt_emoji, txt_emoji.get_rect(center=(rect.width // 2, 16)))
            btn_surf.blit(txt_name, txt_name.get_rect(center=(rect.width // 2, 34)))
            screen.blit(btn_surf, rect.topleft)

        # Draw Instructions Guide Box
        guide_rect = pygame.Rect(80, 425, 320, 40)
        pygame.draw.rect(screen, (0, 0, 0, 50), guide_rect, border_radius=8)
        guide_text = self.font_small.render("SPACEBAR  or  CLICK   to Flap / Jump", True, (203, 213, 225))
        screen.blit(guide_text, guide_text.get_rect(center=guide_rect.center))

        # Start Play Button
        # Glow pulse simulation
        pulse = int(190 + math.sin(pygame.time.get_ticks() * 0.005) * 45)
        btn_color = (*self.theme['bird_body'], pulse)
        
        btn_surf = pygame.Surface((self.btn_start.width, self.btn_start.height), pygame.SRCALPHA)
        pygame.draw.rect(btn_surf, btn_color, (0, 0, self.btn_start.width, self.btn_start.height), border_radius=25)
        
        play_txt = self.font_menu.render("START GAME", True, (0, 0, 0))
        btn_surf.blit(play_txt, play_txt.get_rect(center=(self.btn_start.width // 2, self.btn_start.height // 2)))
        screen.blit(btn_surf, self.btn_start.topleft)

        # Mute indicator instruction
        mute_guide = self.font_small.render("Press 'M' to Toggle Sound  •  'ESC' to Pause", True, (148, 163, 184))
        screen.blit(mute_guide, mute_guide.get_rect(center=(VIRTUAL_WIDTH // 2, 560)))

    def _draw_hud(self, screen):
        # Score banner
        score_surf = self.font_score.render(str(self.score), True, (255, 255, 255))
        s_rect = score_surf.get_rect(center=(VIRTUAL_WIDTH // 2, 80))
        
        # Score card plate
        bg_rect = pygame.Rect(s_rect.x - 20, s_rect.y - 5, s_rect.width + 40, s_rect.height + 10)
        pygame.draw.rect(screen, (0, 0, 0, 100), bg_rect, border_radius=20)
        screen.blit(score_surf, s_rect)

        # Mute status icon on top right
        status_txt = "MUTED" if audio.muted else "SOUND"
        sound_lbl = self.font_small.render(status_txt, True, (255, 255, 255, 120))
        screen.blit(sound_lbl, (VIRTUAL_WIDTH - 70, 20))

    def _draw_pause_screen(self, screen):
        # Translucent overlay background cover
        tint = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
        tint.fill((0, 0, 0, 120))
        screen.blit(tint, (0, 0))

        # Menu Panel Card
        card_rect = pygame.Rect(80, 240, 320, 320)
        card_color = (*self.theme['bg_gradient_start'], 220)
        self._draw_glass_card(screen, card_rect, card_color, (255, 255, 255, 40))

        title = self.font_menu.render("GAME PAUSED", True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(VIRTUAL_WIDTH // 2, 290)))

        # Draw buttons (Resume, Restart, Quit)
        for rect, label, active in [(self.btn_resume, "RESUME", True),
                                    (self.btn_restart_pause, "RESTART", False),
                                    (self.btn_quit, "QUIT TO MENU", False)]:
            bg = (*self.theme['bird_body'], 235) if active else (255, 255, 255, 20)
            fg = (0, 0, 0) if active else (255, 255, 255)
            
            btn_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(btn_surf, bg, (0, 0, rect.width, rect.height), border_radius=23)
            
            txt = self.font_subtitle.render(label, True, fg)
            btn_surf.blit(txt, txt.get_rect(center=(rect.width // 2, rect.height // 2)))
            screen.blit(btn_surf, rect.topleft)

    def _draw_gameover_screen(self, screen):
        tint = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
        tint.fill((0, 0, 0, 120))
        screen.blit(tint, (0, 0))

        # Game over card
        card_rect = pygame.Rect(60, 180, 360, 380)
        card_color = (*self.theme['bg_gradient_start'], 220)
        self._draw_glass_card(screen, card_rect, card_color, (255, 82, 82, 80))

        title = self.font_title.render("GAME OVER", True, (255, 82, 82))
        screen.blit(title, title.get_rect(center=(VIRTUAL_WIDTH // 2, 230)))

        # Score Plate Card
        plate_rect = pygame.Rect(85, 280, 310, 170)
        pygame.draw.rect(screen, (0, 0, 0, 60), plate_rect, border_radius=12)
        pygame.draw.rect(screen, (255, 255, 255, 15), plate_rect, 1, border_radius=12)

        lbl_score = self.font_subtitle.render("SCORE", True, (148, 163, 184))
        val_score = self.font_menu.render(str(self.score), True, (255, 255, 255))
        screen.blit(lbl_score, (110, 300))
        screen.blit(val_score, val_score.get_rect(right=370, y=298))

        lbl_best = self.font_subtitle.render("BEST", True, (148, 163, 184))
        val_best = self.font_menu.render(str(self.high_score), True, (241, 196, 15))
        screen.blit(lbl_best, (110, 350))
        screen.blit(val_best, val_best.get_rect(right=370, y=348))

        # Award medals based on score
        lbl_medal = self.font_subtitle.render("MEDAL", True, (148, 163, 184))
        screen.blit(lbl_medal, (110, 400))
        
        medal_name = "None"
        if self.score >= 40:
            medal_name = "GOLD 🥇"
        elif self.score >= 20:
            medal_name = "SILVER 🥈"
        elif self.score >= 10:
            medal_name = "BRONZE 🥉"
        val_medal = self.font_subtitle.render(medal_name, True, (255, 255, 255))
        screen.blit(val_medal, val_medal.get_rect(right=370, y=400))

        # Play Again / Menu Buttons
        for rect, label, bg_color in [(self.btn_restart, "PLAY AGAIN", (*self.theme['bird_body'], 240)), 
                                      (self.btn_menu, "MENU", (255, 255, 255, 25))]:
            fg = (0, 0, 0) if rect == self.btn_restart else (255, 255, 255)
            btn_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(btn_surf, bg_color, (0, 0, rect.width, rect.height), border_radius=24)
            
            txt = self.font_small.render(label, True, fg)
            btn_surf.blit(txt, txt.get_rect(center=(rect.width // 2, rect.height // 2)))
            screen.blit(btn_surf, rect.topleft)

    # ---------------------------------------------------------------------------
    # INTERACTION EVENT ROUTING
    # ---------------------------------------------------------------------------
    def handle_mouse_click(self, pos, win_w, win_h):
        # Convert window coordinate to virtual 480x800 coordinate system
        scale = min(win_w / VIRTUAL_WIDTH, win_h / VIRTUAL_HEIGHT)
        scaled_w = VIRTUAL_WIDTH * scale
        scaled_h = VIRTUAL_HEIGHT * scale
        dx = (win_w - scaled_w) / 2
        dy = (win_h - scaled_h) / 2

        # Virtual point calculation
        vx = int((pos[0] - dx) / scale)
        vy = int((pos[1] - dy) / scale)
        v_pos = (vx, vy)

        if self.state == GameState.START:
            # Check Play Button
            if self.btn_start.collidepoint(v_pos):
                self.trigger_flap()
                return
            # Check Themes
            if self.theme_btn_retro.collidepoint(v_pos):
                self.theme_id = 'retro'
                self.theme = THEMES['retro']
            elif self.theme_btn_neon.collidepoint(v_pos):
                self.theme_id = 'neon'
                self.theme = THEMES['neon']
            elif self.theme_btn_forest.collidepoint(v_pos):
                self.theme_id = 'forest'
                self.theme = THEMES['forest']
                
        elif self.state == GameState.PLAYING:
            # Click inside playing flaps
            self.trigger_flap()
            
        elif self.state == GameState.PAUSED:
            if self.btn_resume.collidepoint(v_pos):
                self.state = GameState.PLAYING
            elif self.btn_restart_pause.collidepoint(v_pos):
                self.reset()
                self.state = GameState.PLAYING
                self.bird.flap()
            elif self.btn_quit.collidepoint(v_pos):
                self.state = GameState.START
                self.reset()
                
        elif self.state == GameState.GAMEOVER:
            if self.btn_restart.collidepoint(v_pos):
                self.reset()
                self.state = GameState.PLAYING
                self.bird.flap()
            elif self.btn_menu.collidepoint(v_pos):
                self.state = GameState.START
                self.reset()

    # ---------------------------------------------------------------------------
    # MAIN APPLICATION RUN LOOP
    # ---------------------------------------------------------------------------
    def run(self):
        while self.running:
            # Calculate dynamic delta time, capped to prevent massive physics leaps
            dt = self.clock.tick(60) / 1000.0
            if dt > 0.1:
                dt = 0.1

            # Event loop
            win_w, win_h = self.window.get_size()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    
                elif event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_SPACE, pygame.K_UP, pygame.K_w]:
                        self.trigger_flap()
                    elif event.key == pygame.K_ESCAPE:
                        if self.state == GameState.PLAYING:
                            self.state = GameState.PAUSED
                        elif self.state == GameState.PAUSED:
                            self.state = GameState.PLAYING
                    elif event.key == pygame.K_m:
                        audio.toggle_mute()
                        
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # Left click
                        self.handle_mouse_click(event.pos, win_w, win_h)

            # Update & Draw Frame
            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = FlappyBirdGamePython()
    game.run()
