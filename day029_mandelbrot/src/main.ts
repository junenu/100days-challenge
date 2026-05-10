import './style.css';
import type { Viewport } from './mandelbrot';
import { Renderer } from './renderer';
import { COLORMAPS, COLORMAP_NAMES } from './colormap';

const canvas = document.getElementById('canvas') as HTMLCanvasElement;
const infoEl = document.getElementById('info')!;
const coordEl = document.getElementById('coord')!;
const iterSlider = document.getElementById('iter-slider') as HTMLInputElement;
const iterVal = document.getElementById('iter-val')!;
const cmSelect = document.getElementById('cm-select') as HTMLSelectElement;
const resetBtn = document.getElementById('reset-btn') as HTMLButtonElement;

COLORMAP_NAMES.forEach((name) => {
  const opt = document.createElement('option');
  opt.value = name;
  opt.textContent = name.charAt(0).toUpperCase() + name.slice(1);
  cmSelect.appendChild(opt);
});

const renderer = new Renderer(canvas);

let viewport: Viewport = {
  centerX: -0.5,
  centerY: 0,
  zoom: Math.min(renderer.width, renderer.height) / 3.5,
};
let maxIter = 128;
let colorMapName = COLORMAP_NAMES[0];
let isDragging = false;
let dragStart = { x: 0, y: 0 };
let dragViewport: Viewport = { ...viewport };

function render() {
  renderer.render(viewport, maxIter, COLORMAPS[colorMapName]);
  const scale = 3.5 / viewport.zoom;
  infoEl.textContent = `Center: ${viewport.centerX.toFixed(8)} + ${viewport.centerY.toFixed(8)}i  |  Scale: ${scale.toExponential(2)}`;
}

canvas.addEventListener('wheel', (e) => {
  e.preventDefault();
  const factor = e.deltaY < 0 ? 1.25 : 0.8;
  const rect = canvas.getBoundingClientRect();
  const mx = e.clientX - rect.left;
  const my = e.clientY - rect.top;
  const [cx, cy] = renderer.getComplex(mx, my, viewport);
  viewport = {
    zoom: viewport.zoom * factor,
    centerX: cx + (viewport.centerX - cx) / factor,
    centerY: cy + (viewport.centerY - cy) / factor,
  };
  render();
}, { passive: false });

canvas.addEventListener('click', (e) => {
  if (Math.abs(e.clientX - dragStart.x) > 4 || Math.abs(e.clientY - dragStart.y) > 4) return;
  const rect = canvas.getBoundingClientRect();
  const [cx, cy] = renderer.getComplex(e.clientX - rect.left, e.clientY - rect.top, viewport);
  viewport = { ...viewport, centerX: cx, centerY: cy, zoom: viewport.zoom * 2 };
  render();
});

canvas.addEventListener('mousedown', (e) => {
  isDragging = true;
  dragStart = { x: e.clientX, y: e.clientY };
  dragViewport = { ...viewport };
  canvas.style.cursor = 'grabbing';
});

window.addEventListener('mousemove', (e) => {
  const rect = canvas.getBoundingClientRect();
  const [cx, cy] = renderer.getComplex(e.clientX - rect.left, e.clientY - rect.top, viewport);
  coordEl.textContent = `${cx.toFixed(8)} + ${cy.toFixed(8)}i`;

  if (!isDragging) return;
  const dpr = window.devicePixelRatio || 1;
  const dx = (e.clientX - dragStart.x) * dpr;
  const dy = (e.clientY - dragStart.y) * dpr;
  viewport = {
    ...dragViewport,
    centerX: dragViewport.centerX - dx / dragViewport.zoom,
    centerY: dragViewport.centerY - dy / dragViewport.zoom,
  };
  render();
});

window.addEventListener('mouseup', () => {
  isDragging = false;
  canvas.style.cursor = 'crosshair';
});

let lastTouchDist = 0;
canvas.addEventListener('touchstart', (e) => {
  e.preventDefault();
  if (e.touches.length === 1) {
    isDragging = true;
    dragStart = { x: e.touches[0].clientX, y: e.touches[0].clientY };
    dragViewport = { ...viewport };
  } else if (e.touches.length === 2) {
    isDragging = false;
    lastTouchDist = Math.hypot(
      e.touches[0].clientX - e.touches[1].clientX,
      e.touches[0].clientY - e.touches[1].clientY,
    );
  }
}, { passive: false });

canvas.addEventListener('touchmove', (e) => {
  e.preventDefault();
  if (e.touches.length === 1 && isDragging) {
    const dpr = window.devicePixelRatio || 1;
    const dx = (e.touches[0].clientX - dragStart.x) * dpr;
    const dy = (e.touches[0].clientY - dragStart.y) * dpr;
    viewport = {
      ...dragViewport,
      centerX: dragViewport.centerX - dx / dragViewport.zoom,
      centerY: dragViewport.centerY - dy / dragViewport.zoom,
    };
    render();
  } else if (e.touches.length === 2) {
    const dist = Math.hypot(
      e.touches[0].clientX - e.touches[1].clientX,
      e.touches[0].clientY - e.touches[1].clientY,
    );
    const factor = dist / lastTouchDist;
    lastTouchDist = dist;
    viewport = { ...viewport, zoom: viewport.zoom * factor };
    render();
  }
}, { passive: false });

canvas.addEventListener('touchend', () => { isDragging = false; });

iterSlider.value = String(maxIter);
iterVal.textContent = String(maxIter);
iterSlider.addEventListener('input', () => {
  maxIter = Number(iterSlider.value);
  iterVal.textContent = String(maxIter);
  render();
});

cmSelect.addEventListener('change', () => {
  colorMapName = cmSelect.value;
  render();
});

resetBtn.addEventListener('click', () => {
  viewport = {
    centerX: -0.5,
    centerY: 0,
    zoom: Math.min(renderer.width, renderer.height) / 3.5,
  };
  render();
});

window.addEventListener('keydown', (e) => {
  const panStep = 50 / viewport.zoom;
  switch (e.key) {
    case '+': case '=': viewport = { ...viewport, zoom: viewport.zoom * 1.5 }; break;
    case '-': viewport = { ...viewport, zoom: viewport.zoom / 1.5 }; break;
    case 'ArrowLeft': viewport = { ...viewport, centerX: viewport.centerX - panStep }; break;
    case 'ArrowRight': viewport = { ...viewport, centerX: viewport.centerX + panStep }; break;
    case 'ArrowUp': viewport = { ...viewport, centerY: viewport.centerY - panStep }; break;
    case 'ArrowDown': viewport = { ...viewport, centerY: viewport.centerY + panStep }; break;
    case 'r': case 'R': resetBtn.click(); return;
    default: return;
  }
  e.preventDefault();
  render();
});

window.addEventListener('resize', () => {
  const prevZoom = viewport.zoom;
  const prevMin = Math.min(renderer.width, renderer.height);
  renderer.resize();
  const newMin = Math.min(renderer.width, renderer.height);
  viewport = { ...viewport, zoom: prevZoom * (newMin / prevMin) };
  render();
});

render();
