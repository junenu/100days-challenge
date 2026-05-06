import './style.css';
import { Synth } from './audio/synth';
import { Keyboard } from './ui/keyboard';
import { Oscilloscope } from './ui/oscilloscope';
import { buildControls } from './ui/controls';

const app = document.querySelector<HTMLDivElement>('#app')!;

app.innerHTML = `
  <header class="app-header">
    <h1 class="app-title">SYNTH<span class="accent">25</span></h1>
    <p class="app-subtitle">Web Audio Synthesizer — Day 025</p>
  </header>
  <main class="app-main">
    <section class="scope-section">
      <canvas id="oscilloscope" width="900" height="150"></canvas>
    </section>
    <div class="layout">
      <section id="controls" class="controls-panel"></section>
    </div>
    <section class="keyboard-section">
      <div class="key-hint">
        <span>Keyboard: <kbd>A</kbd>–<kbd>;</kbd> white keys &nbsp;|&nbsp; <kbd>W E T Y U O P</kbd> black keys</span>
      </div>
      <div id="keyboard" class="keyboard-wrap"></div>
    </section>
  </main>
  <footer class="app-footer">
    <span>100 Days Challenge — Day 025</span>
  </footer>
`;

const synth = new Synth();

const canvas = document.getElementById('oscilloscope') as HTMLCanvasElement;
const scope = new Oscilloscope(canvas, synth.getAnalyser());
scope.start();

const controlsContainer = document.getElementById('controls')!;
buildControls(controlsContainer, synth);

const keyboardContainer = document.getElementById('keyboard')!;
new Keyboard(keyboardContainer, synth);

function resizeCanvas(): void {
  const section = canvas.parentElement!;
  canvas.width = section.clientWidth;
}
window.addEventListener('resize', resizeCanvas);
resizeCanvas();
