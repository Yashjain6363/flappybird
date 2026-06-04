/* ==========================================================================
   WEB AUDIO API RETRO SOUND SYNTHESIZER
   ========================================================================== */

class SoundEngine {
    constructor() {
        this.ctx = null;
        this.muted = false;
    }

    /**
     * Initializes the AudioContext on first user interaction.
     * Browsers restrict audio from playing automatically.
     */
    init() {
        if (!this.ctx) {
            this.ctx = new (window.AudioContext || window.webkitAudioContext)();
        }
        if (this.ctx.state === 'suspended') {
            this.ctx.resume();
        }
    }

    toggleMute() {
        this.muted = !this.muted;
        return this.muted;
    }

    setMute(state) {
        this.muted = state;
    }

    /**
     * Synthesizes a Flap/Jump sound (quick upward pitch sweep).
     */
    playFlap() {
        if (this.muted) return;
        this.init();
        const ctx = this.ctx;
        const now = ctx.currentTime;

        const osc = ctx.createOscillator();
        const gain = ctx.createGain();

        osc.type = 'triangle'; // Retro, slightly soft triangle wave
        osc.frequency.setValueAtTime(140, now);
        osc.frequency.exponentialRampToValueAtTime(320, now + 0.12);

        gain.gain.setValueAtTime(0.3, now);
        gain.gain.linearRampToValueAtTime(0.01, now + 0.12);

        osc.connect(gain);
        gain.connect(ctx.destination);

        osc.start(now);
        osc.stop(now + 0.12);
    }

    /**
     * Synthesizes a Score sound (clean retro double-chime).
     */
    playScore() {
        if (this.muted) return;
        this.init();
        const ctx = this.ctx;
        const now = ctx.currentTime;

        // First note (chime 1)
        const osc1 = ctx.createOscillator();
        const gain1 = ctx.createGain();
        osc1.type = 'square';
        osc1.frequency.setValueAtTime(587.33, now); // D5
        gain1.gain.setValueAtTime(0.08, now);
        gain1.gain.linearRampToValueAtTime(0.001, now + 0.08);

        osc1.connect(gain1);
        gain1.connect(ctx.destination);
        osc1.start(now);
        osc1.stop(now + 0.08);

        // Second note (chime 2, slightly delayed)
        const osc2 = ctx.createOscillator();
        const gain2 = ctx.createGain();
        osc2.type = 'square';
        osc2.frequency.setValueAtTime(880.00, now + 0.07); // A5
        gain2.gain.setValueAtTime(0.08, now + 0.07);
        gain2.gain.linearRampToValueAtTime(0.001, now + 0.25);

        osc2.connect(gain2);
        gain2.connect(ctx.destination);
        osc2.start(now + 0.07);
        osc2.stop(now + 0.25);
    }

    /**
     * Synthesizes a Crash sound (white noise explosion + pitch dive).
     */
    playCrash() {
        if (this.muted) return;
        this.init();
        const ctx = this.ctx;
        const now = ctx.currentTime;

        const duration = 0.45;
        
        // 1. Synthesize White Noise for the explosion crunch
        const bufferSize = ctx.sampleRate * duration;
        const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
        const data = buffer.getChannelData(0);
        
        for (let i = 0; i < bufferSize; i++) {
            data[i] = Math.random() * 2 - 1;
        }

        const noiseNode = ctx.createBufferSource();
        noiseNode.buffer = buffer;

        // Noise lowpass filter to make it sound muffled/heavy
        const filter = ctx.createBiquadFilter();
        filter.type = 'lowpass';
        filter.frequency.setValueAtTime(1000, now);
        filter.frequency.exponentialRampToValueAtTime(100, now + duration);

        const noiseGain = ctx.createGain();
        noiseGain.gain.setValueAtTime(0.4, now);
        noiseGain.gain.linearRampToValueAtTime(0.001, now + duration);

        noiseNode.connect(filter);
        filter.connect(noiseGain);
        noiseGain.connect(ctx.destination);

        // 2. Add a heavy bass rumble pitch-dive (oscillator)
        const osc = ctx.createOscillator();
        const oscGain = ctx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(180, now);
        osc.frequency.linearRampToValueAtTime(40, now + 0.3);

        oscGain.gain.setValueAtTime(0.3, now);
        oscGain.gain.linearRampToValueAtTime(0.001, now + 0.3);

        osc.connect(oscGain);
        oscGain.connect(ctx.destination);

        // Start both elements
        noiseNode.start(now);
        noiseNode.stop(now + duration);
        osc.start(now);
        osc.stop(now + 0.3);
    }
}

export const audio = new SoundEngine();
