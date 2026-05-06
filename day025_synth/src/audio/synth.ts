export type WaveType = 'sine' | 'square' | 'sawtooth' | 'triangle';

export interface AdsrParams {
  attack: number;
  decay: number;
  sustain: number;
  release: number;
}

export interface SynthState {
  waveType: WaveType;
  adsr: AdsrParams;
  delayTime: number;
  delayFeedback: number;
  reverbAmount: number;
  volume: number;
}

interface ActiveNote {
  oscillator: OscillatorNode;
  gainNode: GainNode;
  frequency: number;
}

export class Synth {
  private ctx: AudioContext;
  private masterGain: GainNode;
  private delayNode: DelayNode;
  private delayFeedbackGain: GainNode;
  private reverbGain: GainNode;
  private dryGain: GainNode;
  private analyser: AnalyserNode;
  private activeNotes = new Map<string, ActiveNote>();
  private convolver: ConvolverNode;

  state: SynthState = {
    waveType: 'sine',
    adsr: { attack: 0.01, decay: 0.1, sustain: 0.7, release: 0.3 },
    delayTime: 0.3,
    delayFeedback: 0.3,
    reverbAmount: 0.2,
    volume: 0.7,
  };

  constructor() {
    this.ctx = new AudioContext();

    this.masterGain = this.ctx.createGain();
    this.masterGain.gain.value = this.state.volume;

    this.analyser = this.ctx.createAnalyser();
    this.analyser.fftSize = 2048;

    this.delayNode = this.ctx.createDelay(2.0);
    this.delayNode.delayTime.value = this.state.delayTime;

    this.delayFeedbackGain = this.ctx.createGain();
    this.delayFeedbackGain.gain.value = this.state.delayFeedback;

    this.dryGain = this.ctx.createGain();
    this.dryGain.gain.value = 1 - this.state.reverbAmount;

    this.reverbGain = this.ctx.createGain();
    this.reverbGain.gain.value = this.state.reverbAmount;

    this.convolver = this.ctx.createConvolver();
    this.convolver.buffer = this.createReverbBuffer();

    // Routing: source -> dryGain -> masterGain
    //          source -> convolver -> reverbGain -> masterGain
    //          source -> delayNode -> delayFeedbackGain -> delayNode (feedback loop)
    //                             -> masterGain

    this.delayNode.connect(this.delayFeedbackGain);
    this.delayFeedbackGain.connect(this.delayNode);

    this.dryGain.connect(this.masterGain);
    this.reverbGain.connect(this.masterGain);
    this.delayNode.connect(this.masterGain);

    this.masterGain.connect(this.analyser);
    this.analyser.connect(this.ctx.destination);
  }

  private createReverbBuffer(): AudioBuffer {
    const sampleRate = this.ctx.sampleRate;
    const length = sampleRate * 2;
    const buffer = this.ctx.createBuffer(2, length, sampleRate);
    for (let ch = 0; ch < 2; ch++) {
      const data = buffer.getChannelData(ch);
      for (let i = 0; i < length; i++) {
        data[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / length, 2);
      }
    }
    return buffer;
  }

  noteOn(noteId: string, frequency: number): void {
    if (this.activeNotes.has(noteId)) return;
    if (this.ctx.state === 'suspended') this.ctx.resume();

    const osc = this.ctx.createOscillator();
    const noteGain = this.ctx.createGain();

    osc.type = this.state.waveType;
    osc.frequency.value = frequency;

    const { attack, decay, sustain } = this.state.adsr;
    const now = this.ctx.currentTime;
    noteGain.gain.setValueAtTime(0, now);
    noteGain.gain.linearRampToValueAtTime(1, now + attack);
    noteGain.gain.linearRampToValueAtTime(sustain, now + attack + decay);

    osc.connect(noteGain);
    noteGain.connect(this.dryGain);
    noteGain.connect(this.convolver);
    noteGain.connect(this.delayNode);

    this.convolver.connect(this.reverbGain);

    osc.start();
    this.activeNotes.set(noteId, { oscillator: osc, gainNode: noteGain, frequency });
  }

  noteOff(noteId: string): void {
    const note = this.activeNotes.get(noteId);
    if (!note) return;

    const { release } = this.state.adsr;
    const now = this.ctx.currentTime;
    note.gainNode.gain.cancelScheduledValues(now);
    note.gainNode.gain.setValueAtTime(note.gainNode.gain.value, now);
    note.gainNode.gain.linearRampToValueAtTime(0, now + release);
    note.oscillator.stop(now + release + 0.01);

    this.activeNotes.delete(noteId);
  }

  allNotesOff(): void {
    for (const noteId of this.activeNotes.keys()) {
      this.noteOff(noteId);
    }
  }

  setWaveType(type: WaveType): void {
    this.state.waveType = type;
  }

  setAdsr(params: Partial<AdsrParams>): void {
    this.state.adsr = { ...this.state.adsr, ...params };
  }

  setVolume(value: number): void {
    this.state.volume = value;
    this.masterGain.gain.value = value;
  }

  setDelayTime(value: number): void {
    this.state.delayTime = value;
    this.delayNode.delayTime.value = value;
  }

  setDelayFeedback(value: number): void {
    this.state.delayFeedback = value;
    this.delayFeedbackGain.gain.value = value;
  }

  setReverbAmount(value: number): void {
    this.state.reverbAmount = value;
    this.reverbGain.gain.value = value;
    this.dryGain.gain.value = 1 - value;
  }

  getAnalyser(): AnalyserNode {
    return this.analyser;
  }

  isNoteActive(noteId: string): boolean {
    return this.activeNotes.has(noteId);
  }
}
