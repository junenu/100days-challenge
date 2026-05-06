import { Synth } from '../audio/synth';

// C4 = 261.63 Hz, two octaves: C4 to B5
const NOTE_LAYOUT = [
  { note: 'C4', freq: 261.63, isBlack: false, keyLabel: 'a' },
  { note: 'C#4', freq: 277.18, isBlack: true, keyLabel: 'w' },
  { note: 'D4', freq: 293.66, isBlack: false, keyLabel: 's' },
  { note: 'D#4', freq: 311.13, isBlack: true, keyLabel: 'e' },
  { note: 'E4', freq: 329.63, isBlack: false, keyLabel: 'd' },
  { note: 'F4', freq: 349.23, isBlack: false, keyLabel: 'f' },
  { note: 'F#4', freq: 369.99, isBlack: true, keyLabel: 't' },
  { note: 'G4', freq: 392.00, isBlack: false, keyLabel: 'g' },
  { note: 'G#4', freq: 415.30, isBlack: true, keyLabel: 'y' },
  { note: 'A4', freq: 440.00, isBlack: false, keyLabel: 'h' },
  { note: 'A#4', freq: 466.16, isBlack: true, keyLabel: 'u' },
  { note: 'B4', freq: 493.88, isBlack: false, keyLabel: 'j' },
  { note: 'C5', freq: 523.25, isBlack: false, keyLabel: 'k' },
  { note: 'C#5', freq: 554.37, isBlack: true, keyLabel: 'o' },
  { note: 'D5', freq: 587.33, isBlack: false, keyLabel: 'l' },
  { note: 'D#5', freq: 622.25, isBlack: true, keyLabel: 'p' },
  { note: 'E5', freq: 659.25, isBlack: false, keyLabel: ';' },
];

const KEY_TO_NOTE = new Map(NOTE_LAYOUT.map(n => [n.keyLabel, n.note]));

export class Keyboard {
  private container: HTMLElement;
  private synth: Synth;
  private pressedKeys = new Set<string>();

  constructor(container: HTMLElement, synth: Synth) {
    this.container = container;
    this.synth = synth;
    this.render();
    this.bindEvents();
  }

  private render(): void {
    this.container.innerHTML = '';

    const whiteKeys = NOTE_LAYOUT.filter(n => !n.isBlack);
    const whiteKeyWidth = 100 / whiteKeys.length;

    // White keys
    whiteKeys.forEach((noteInfo, idx) => {
      const key = document.createElement('div');
      key.className = 'key white-key';
      key.dataset.note = noteInfo.note;
      key.style.left = `${idx * whiteKeyWidth}%`;
      key.style.width = `${whiteKeyWidth}%`;

      const label = document.createElement('span');
      label.className = 'key-label';
      label.textContent = noteInfo.keyLabel.toUpperCase();
      key.appendChild(label);

      const noteName = document.createElement('span');
      noteName.className = 'note-name';
      noteName.textContent = noteInfo.note;
      key.appendChild(noteName);

      this.attachKeyEvents(key, noteInfo.note, noteInfo.freq);
      this.container.appendChild(key);
    });

    // Black keys — position relative to white keys
    let whiteIdx = -1;
    NOTE_LAYOUT.forEach(noteInfo => {
      if (!noteInfo.isBlack) {
        whiteIdx++;
        return;
      }
      const key = document.createElement('div');
      key.className = 'key black-key';
      key.dataset.note = noteInfo.note;
      // Center between previous white key and next white key
      key.style.left = `${(whiteIdx + 0.65) * whiteKeyWidth}%`;
      key.style.width = `${whiteKeyWidth * 0.65}%`;

      const label = document.createElement('span');
      label.className = 'key-label';
      label.textContent = noteInfo.keyLabel.toUpperCase();
      key.appendChild(label);

      this.attachKeyEvents(key, noteInfo.note, noteInfo.freq);
      this.container.appendChild(key);
    });
  }

  private attachKeyEvents(el: HTMLElement, note: string, freq: number): void {
    const start = (e: Event) => {
      e.preventDefault();
      this.activateNote(note, freq, el);
    };
    const end = () => this.deactivateNote(note, el);

    el.addEventListener('mousedown', start);
    el.addEventListener('touchstart', start, { passive: false });
    el.addEventListener('mouseup', end);
    el.addEventListener('mouseleave', end);
    el.addEventListener('touchend', end);
  }

  private activateNote(note: string, freq: number, el: HTMLElement): void {
    this.synth.noteOn(note, freq);
    el.classList.add('active');
  }

  private deactivateNote(note: string, el: HTMLElement): void {
    this.synth.noteOff(note);
    el.classList.remove('active');
  }

  private bindEvents(): void {
    window.addEventListener('keydown', (e) => {
      if (e.repeat) return;
      const note = KEY_TO_NOTE.get(e.key);
      if (!note) return;
      const noteInfo = NOTE_LAYOUT.find(n => n.note === note);
      if (!noteInfo) return;
      this.pressedKeys.add(e.key);
      const el = this.container.querySelector(`[data-note="${note}"]`) as HTMLElement;
      if (el) this.activateNote(note, noteInfo.freq, el);
    });

    window.addEventListener('keyup', (e) => {
      const note = KEY_TO_NOTE.get(e.key);
      if (!note) return;
      this.pressedKeys.delete(e.key);
      const el = this.container.querySelector(`[data-note="${note}"]`) as HTMLElement;
      if (el) this.deactivateNote(note, el);
    });
  }
}
