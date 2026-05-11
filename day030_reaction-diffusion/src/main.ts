import './style.css';
import {
  createState, resetState, seedRandom, addDrop, stepN,
  PRESETS, GRID_W, GRID_H,
  type SimParams,
} from './simulation.ts';
import { render, type ColorTheme } from './renderer.ts';

// --- State ---
const simState = createState();
resetState(simState);

let params: SimParams = { da: 1.0, db: 0.5, f: 0.0545, k: 0.062 };
let theme: ColorTheme = 'ocean';
let stepsPerFrame = 8;
let paused = false;
let generation = 0;

// --- Canvas ---
const canvas = document.getElementById('canvas') as HTMLCanvasElement;
const ctx = canvas.getContext('2d', { willReadFrequently: false })!;
const imageData = ctx.createImageData(GRID_W, GRID_H);

// --- FPS ---
let lastTime = 0;
let frameCount = 0;
let fps = 0;

// --- UI elements ---
const fSlider   = document.getElementById('f-slider') as HTMLInputElement;
const kSlider   = document.getElementById('k-slider') as HTMLInputElement;
const speedSlider = document.getElementById('speed-slider') as HTMLInputElement;
const fVal      = document.getElementById('f-val')!;
const kVal      = document.getElementById('k-val')!;
const speedVal  = document.getElementById('speed-val')!;
const fpsDisplay  = document.getElementById('fps-display')!;
const genDisplay  = document.getElementById('gen-display')!;
const btnPause  = document.getElementById('btn-pause')!;
const btnReset  = document.getElementById('btn-reset')!;
const btnRandom = document.getElementById('btn-random')!;

// --- Preset buttons ---
document.querySelectorAll<HTMLButtonElement>('.preset-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const key = btn.dataset.preset ?? '';
    const p = PRESETS[key];
    if (!p) return;
    params = { ...params, f: p.f, k: p.k };
    fSlider.value = p.f.toFixed(4);
    kSlider.value = p.k.toFixed(4);
    fVal.textContent = p.f.toFixed(4);
    kVal.textContent = p.k.toFixed(4);
    document.querySelectorAll('.preset-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    resetState(simState);
    generation = 0;
  });
});

// --- Theme buttons ---
document.querySelectorAll<HTMLButtonElement>('.theme-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    theme = (btn.dataset.theme ?? 'ocean') as ColorTheme;
    document.querySelectorAll('.theme-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
  });
});

// --- Parameter sliders ---
fSlider.addEventListener('input', () => {
  const v = parseFloat(fSlider.value);
  params = { ...params, f: v };
  fVal.textContent = v.toFixed(4);
  document.querySelectorAll('.preset-btn').forEach(b => b.classList.remove('active'));
});

kSlider.addEventListener('input', () => {
  const v = parseFloat(kSlider.value);
  params = { ...params, k: v };
  kVal.textContent = v.toFixed(4);
  document.querySelectorAll('.preset-btn').forEach(b => b.classList.remove('active'));
});

speedSlider.addEventListener('input', () => {
  stepsPerFrame = parseInt(speedSlider.value, 10);
  speedVal.textContent = stepsPerFrame.toString();
});

// --- Control buttons ---
btnPause.addEventListener('click', () => {
  paused = !paused;
  btnPause.textContent = paused ? 'Resume' : 'Pause';
});

btnReset.addEventListener('click', () => {
  resetState(simState);
  generation = 0;
});

btnRandom.addEventListener('click', () => {
  seedRandom(simState, 50);
  generation = 0;
});

// --- Canvas interaction ---
function canvasToGrid(clientX: number, clientY: number): [number, number] {
  const rect = canvas.getBoundingClientRect();
  const scaleX = GRID_W / rect.width;
  const scaleY = GRID_H / rect.height;
  const gx = Math.round((clientX - rect.left) * scaleX);
  const gy = Math.round((clientY - rect.top) * scaleY);
  return [gx, gy];
}

let isPointerDown = false;

canvas.addEventListener('pointerdown', e => {
  isPointerDown = true;
  const [gx, gy] = canvasToGrid(e.clientX, e.clientY);
  addDrop(simState, gx, gy, 10);
});

canvas.addEventListener('pointermove', e => {
  if (!isPointerDown) return;
  const [gx, gy] = canvasToGrid(e.clientX, e.clientY);
  addDrop(simState, gx, gy, 10);
});

canvas.addEventListener('pointerup', () => { isPointerDown = false; });
canvas.addEventListener('pointerleave', () => { isPointerDown = false; });

// --- Animation loop ---
function loop(timestamp: number): void {
  if (!paused) {
    stepN(simState, params, stepsPerFrame);
    generation = simState.generation;
  }

  render(ctx, simState, theme, imageData);

  // FPS counter
  frameCount++;
  const elapsed = timestamp - lastTime;
  if (elapsed >= 500) {
    fps = Math.round((frameCount * 1000) / elapsed);
    frameCount = 0;
    lastTime = timestamp;
    fpsDisplay.textContent = `FPS: ${fps}`;
    genDisplay.textContent = `Gen: ${(generation / 1000).toFixed(1)}k`;
  }

  requestAnimationFrame(loop);
}

requestAnimationFrame(loop);
