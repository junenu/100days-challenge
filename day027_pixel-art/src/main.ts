import { createState, cloneState, setPixel, floodFill, render, exportPng } from './canvas';
import { DEFAULT_PALETTE } from './palette';
import type { CanvasState, Color, Tool } from './types';
import './style.css';

const CELL_SIZES = [4, 8, 16, 24, 32];
const GRID_SIZES = [8, 16, 32, 64];
const MAX_HISTORY = 50;

let state: CanvasState = createState(16, 16);
let history: CanvasState[] = [cloneState(state)];
let historyIndex = 0;

let activeTool: Tool = 'pencil';
let activeColor: Color = '#000000';
let cellSize = 16;
let showGrid = true;
let isDrawing = false;
let lastCell: [number, number] | null = null;

const canvas = document.getElementById('art-canvas') as HTMLCanvasElement;
const ctx = canvas.getContext('2d')!;

function resizeCanvas(): void {
  canvas.width = state.width * cellSize;
  canvas.height = state.height * cellSize;
}

function repaint(): void {
  render(ctx, state, cellSize, showGrid);
}

function pushHistory(newState: CanvasState): void {
  history = history.slice(0, historyIndex + 1);
  history.push(cloneState(newState));
  if (history.length > MAX_HISTORY) history.shift();
  historyIndex = history.length - 1;
  updateUndoRedo();
}

function undo(): void {
  if (historyIndex > 0) {
    historyIndex--;
    state = cloneState(history[historyIndex]);
    repaint();
    updateUndoRedo();
  }
}

function redo(): void {
  if (historyIndex < history.length - 1) {
    historyIndex++;
    state = cloneState(history[historyIndex]);
    repaint();
    updateUndoRedo();
  }
}

function updateUndoRedo(): void {
  (document.getElementById('btn-undo') as HTMLButtonElement).disabled = historyIndex <= 0;
  (document.getElementById('btn-redo') as HTMLButtonElement).disabled = historyIndex >= history.length - 1;
}

function getCellCoords(e: MouseEvent | TouchEvent): [number, number] | null {
  const rect = canvas.getBoundingClientRect();
  const scaleX = canvas.width / rect.width;
  const scaleY = canvas.height / rect.height;

  let clientX: number, clientY: number;
  if (e instanceof TouchEvent) {
    const touch = e.touches[0] ?? e.changedTouches[0];
    clientX = touch.clientX;
    clientY = touch.clientY;
  } else {
    clientX = e.clientX;
    clientY = e.clientY;
  }

  const x = Math.floor(((clientX - rect.left) * scaleX) / cellSize);
  const y = Math.floor(((clientY - rect.top) * scaleY) / cellSize);
  if (x < 0 || y < 0 || x >= state.width || y >= state.height) return null;
  return [x, y];
}

function applyTool(x: number, y: number): void {
  if (activeTool === 'eyedropper') {
    const picked = state.pixels[y][x].color;
    if (picked) {
      activeColor = picked;
      updateColorDisplay();
    }
    activeTool = 'pencil';
    updateToolUI();
    return;
  }

  if (activeTool === 'fill') {
    const filled = floodFill(state, x, y, activeColor);
    if (filled !== state) {
      state = filled;
      pushHistory(state);
      repaint();
    }
    return;
  }

  const color = activeTool === 'eraser' ? null : activeColor;
  const next = setPixel(state, x, y, color);
  if (next.pixels[y][x].color !== state.pixels[y][x].color) {
    state = next;
    repaint();
  }
}

function onPointerDown(e: MouseEvent | TouchEvent): void {
  e.preventDefault();
  isDrawing = true;
  lastCell = null;
  const cell = getCellCoords(e);
  if (!cell) return;
  lastCell = cell;
  applyTool(cell[0], cell[1]);
}

function onPointerMove(e: MouseEvent | TouchEvent): void {
  if (!isDrawing) return;
  e.preventDefault();
  const cell = getCellCoords(e);
  if (!cell) return;
  if (lastCell && lastCell[0] === cell[0] && lastCell[1] === cell[1]) return;
  lastCell = cell;
  if (activeTool === 'fill' || activeTool === 'eyedropper') return;
  applyTool(cell[0], cell[1]);
}

function onPointerUp(): void {
  if (isDrawing && activeTool !== 'fill' && activeTool !== 'eyedropper') {
    pushHistory(state);
  }
  isDrawing = false;
  lastCell = null;
}

canvas.addEventListener('mousedown', onPointerDown);
canvas.addEventListener('mousemove', onPointerMove);
canvas.addEventListener('mouseup', onPointerUp);
canvas.addEventListener('mouseleave', onPointerUp);
canvas.addEventListener('touchstart', onPointerDown, { passive: false });
canvas.addEventListener('touchmove', onPointerMove, { passive: false });
canvas.addEventListener('touchend', onPointerUp);

document.querySelectorAll<HTMLButtonElement>('.tool-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    activeTool = btn.dataset.tool as Tool;
    updateToolUI();
  });
});

function updateToolUI(): void {
  document.querySelectorAll<HTMLButtonElement>('.tool-btn').forEach(b =>
    b.classList.toggle('active', b.dataset.tool === activeTool)
  );
}

function buildPalette(): void {
  const container = document.getElementById('palette')!;
  container.innerHTML = '';
  DEFAULT_PALETTE.forEach(hex => {
    const swatch = document.createElement('div');
    swatch.className = 'swatch';
    swatch.style.background = hex;
    swatch.title = hex;
    swatch.addEventListener('click', () => {
      activeColor = hex;
      updateColorDisplay();
    });
    container.appendChild(swatch);
  });
}

function updateColorDisplay(): void {
  const el = document.getElementById('active-color') as HTMLInputElement;
  el.value = activeColor;
  document.getElementById('active-color-preview')!.style.background = activeColor;
}

const colorInput = document.getElementById('active-color') as HTMLInputElement;
colorInput.addEventListener('input', () => {
  activeColor = colorInput.value;
  document.getElementById('active-color-preview')!.style.background = activeColor;
});

document.getElementById('btn-grid')!.addEventListener('click', () => {
  showGrid = !showGrid;
  document.getElementById('btn-grid')!.classList.toggle('active', showGrid);
  repaint();
});

document.getElementById('btn-zoom-in')!.addEventListener('click', () => {
  const idx = CELL_SIZES.indexOf(cellSize);
  if (idx < CELL_SIZES.length - 1) {
    cellSize = CELL_SIZES[idx + 1];
    resizeCanvas();
    repaint();
  }
});
document.getElementById('btn-zoom-out')!.addEventListener('click', () => {
  const idx = CELL_SIZES.indexOf(cellSize);
  if (idx > 0) {
    cellSize = CELL_SIZES[idx - 1];
    resizeCanvas();
    repaint();
  }
});

const sizeSelect = document.getElementById('canvas-size') as HTMLSelectElement;
GRID_SIZES.forEach(s => {
  const opt = document.createElement('option');
  opt.value = String(s);
  opt.textContent = `${s}×${s}`;
  if (s === 16) opt.selected = true;
  sizeSelect.appendChild(opt);
});
sizeSelect.addEventListener('change', () => {
  const size = parseInt(sizeSelect.value);
  state = createState(size, size);
  history = [cloneState(state)];
  historyIndex = 0;
  updateUndoRedo();
  resizeCanvas();
  repaint();
});

document.getElementById('btn-clear')!.addEventListener('click', () => {
  state = createState(state.width, state.height);
  pushHistory(state);
  repaint();
});

document.getElementById('btn-export')!.addEventListener('click', () => {
  exportPng(state);
});

document.getElementById('btn-undo')!.addEventListener('click', undo);
document.getElementById('btn-redo')!.addEventListener('click', redo);

document.addEventListener('keydown', e => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'z' && !e.shiftKey) { e.preventDefault(); undo(); }
  if ((e.ctrlKey || e.metaKey) && (e.key === 'y' || (e.key === 'z' && e.shiftKey))) { e.preventDefault(); redo(); }
  if (!e.ctrlKey && !e.metaKey) {
    if (e.key === 'p') { activeTool = 'pencil'; updateToolUI(); }
    if (e.key === 'e') { activeTool = 'eraser'; updateToolUI(); }
    if (e.key === 'f') { activeTool = 'fill'; updateToolUI(); }
    if (e.key === 'i') { activeTool = 'eyedropper'; updateToolUI(); }
    if (e.key === 'g') {
      showGrid = !showGrid;
      document.getElementById('btn-grid')!.classList.toggle('active', showGrid);
      repaint();
    }
  }
});

buildPalette();
updateColorDisplay();
resizeCanvas();
pushHistory(state);
updateUndoRedo();
document.getElementById('btn-grid')!.classList.add('active');
document.querySelector<HTMLButtonElement>('[data-tool="pencil"]')!.classList.add('active');
repaint();
