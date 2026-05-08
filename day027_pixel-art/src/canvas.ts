import type { CanvasState, Color } from './types';

export function createState(width: number, height: number): CanvasState {
  return {
    width,
    height,
    pixels: Array.from({ length: height }, () =>
      Array.from({ length: width }, () => ({ color: null }))
    ),
  };
}

export function cloneState(state: CanvasState): CanvasState {
  return {
    width: state.width,
    height: state.height,
    pixels: state.pixels.map(row => row.map(p => ({ ...p }))),
  };
}

export function setPixel(state: CanvasState, x: number, y: number, color: Color | null): CanvasState {
  const next = cloneState(state);
  next.pixels[y][x] = { color };
  return next;
}

export function floodFill(state: CanvasState, x: number, y: number, fillColor: Color): CanvasState {
  const target = state.pixels[y][x].color;
  if (target === fillColor) return state;

  const next = cloneState(state);
  const queue: [number, number][] = [[x, y]];
  const visited = new Set<string>();

  while (queue.length > 0) {
    const [cx, cy] = queue.shift()!;
    const key = `${cx},${cy}`;
    if (visited.has(key)) continue;
    if (cx < 0 || cy < 0 || cx >= state.width || cy >= state.height) continue;
    if (next.pixels[cy][cx].color !== target) continue;

    visited.add(key);
    next.pixels[cy][cx] = { color: fillColor };
    queue.push([cx + 1, cy], [cx - 1, cy], [cx, cy + 1], [cx, cy - 1]);
  }

  return next;
}

export function render(
  ctx: CanvasRenderingContext2D,
  state: CanvasState,
  cellSize: number,
  showGrid: boolean
): void {
  const { width, height, pixels } = state;
  const canvasW = width * cellSize;
  const canvasH = height * cellSize;

  // Background (transparent pattern)
  ctx.clearRect(0, 0, canvasW, canvasH);
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const isDark = (x + y) % 2 === 0;
      ctx.fillStyle = isDark ? '#c8c8c8' : '#f0f0f0';
      ctx.fillRect(x * cellSize, y * cellSize, cellSize, cellSize);
    }
  }

  // Pixels
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const { color } = pixels[y][x];
      if (color) {
        ctx.fillStyle = color;
        ctx.fillRect(x * cellSize, y * cellSize, cellSize, cellSize);
      }
    }
  }

  // Grid overlay
  if (showGrid && cellSize >= 4) {
    ctx.strokeStyle = 'rgba(0,0,0,0.12)';
    ctx.lineWidth = 0.5;
    for (let x = 0; x <= width; x++) {
      ctx.beginPath();
      ctx.moveTo(x * cellSize, 0);
      ctx.lineTo(x * cellSize, canvasH);
      ctx.stroke();
    }
    for (let y = 0; y <= height; y++) {
      ctx.beginPath();
      ctx.moveTo(0, y * cellSize);
      ctx.lineTo(canvasW, y * cellSize);
      ctx.stroke();
    }
  }
}

export function exportPng(state: CanvasState): void {
  const offscreen = document.createElement('canvas');
  offscreen.width = state.width;
  offscreen.height = state.height;
  const ctx = offscreen.getContext('2d')!;

  for (let y = 0; y < state.height; y++) {
    for (let x = 0; x < state.width; x++) {
      const { color } = state.pixels[y][x];
      if (color) {
        ctx.fillStyle = color;
        ctx.fillRect(x, y, 1, 1);
      }
    }
  }

  const link = document.createElement('a');
  link.download = 'pixel-art.png';
  link.href = offscreen.toDataURL('image/png');
  link.click();
}
