export const GRID_W = 256;
export const GRID_H = 256;

export interface SimParams {
  da: number;
  db: number;
  f: number;
  k: number;
}

export interface SimState {
  a: Float32Array;
  b: Float32Array;
  tmpA: Float32Array;
  tmpB: Float32Array;
  readonly width: number;
  readonly height: number;
  generation: number;
}

export interface Preset {
  label: string;
  f: number;
  k: number;
}

export const PRESETS: Record<string, Preset> = {
  coral:       { label: 'Coral',       f: 0.0545, k: 0.062  },
  maze:        { label: 'Maze',        f: 0.029,  k: 0.057  },
  spots:       { label: 'Spots',       f: 0.035,  k: 0.065  },
  worms:       { label: 'Worms',       f: 0.058,  k: 0.065  },
  mitosis:     { label: 'Mitosis',     f: 0.0367, k: 0.0649 },
  fingerprint: { label: 'Fingerprint', f: 0.037,  k: 0.060  },
};

export function createState(): SimState {
  const n = GRID_W * GRID_H;
  const a = new Float32Array(n).fill(1.0);
  const b = new Float32Array(n);
  const tmpA = new Float32Array(n);
  const tmpB = new Float32Array(n);
  return { a, b, tmpA, tmpB, width: GRID_W, height: GRID_H, generation: 0 };
}

export function resetState(state: SimState): void {
  state.a.fill(1.0);
  state.b.fill(0.0);
  state.generation = 0;
  seedCenter(state);
}

export function seedCenter(state: SimState): void {
  const { a, b, width, height } = state;
  const cx = Math.floor(width / 2);
  const cy = Math.floor(height / 2);
  const r = 12;
  for (let dy = -r; dy <= r; dy++) {
    for (let dx = -r; dx <= r; dx++) {
      const nx = (cx + dx + width) % width;
      const ny = (cy + dy + height) % height;
      const ni = ny * width + nx;
      a[ni] = 0.5 + (Math.random() - 0.5) * 0.1;
      b[ni] = 0.25 + (Math.random() - 0.5) * 0.1;
    }
  }
}

export function seedRandom(state: SimState, patchCount = 40): void {
  const { a, b, width, height } = state;
  a.fill(1.0);
  b.fill(0.0);
  state.generation = 0;
  const r = 5;
  for (let p = 0; p < patchCount; p++) {
    const cx = Math.floor(Math.random() * width);
    const cy = Math.floor(Math.random() * height);
    for (let dy = -r; dy <= r; dy++) {
      for (let dx = -r; dx <= r; dx++) {
        if (dx * dx + dy * dy > r * r) continue;
        const nx = (cx + dx + width) % width;
        const ny = (cy + dy + height) % height;
        const ni = ny * width + nx;
        a[ni] = 0.5 + (Math.random() - 0.5) * 0.1;
        b[ni] = 0.25 + (Math.random() - 0.5) * 0.1;
      }
    }
  }
}

export function addDrop(state: SimState, px: number, py: number, radius = 8): void {
  const { a, b, width, height } = state;
  const r2 = radius * radius;
  for (let dy = -radius; dy <= radius; dy++) {
    for (let dx = -radius; dx <= radius; dx++) {
      if (dx * dx + dy * dy > r2) continue;
      const nx = (px + dx + width) % width;
      const ny = (py + dy + height) % height;
      const ni = ny * width + nx;
      a[ni] = 0.5;
      b[ni] = 0.25;
    }
  }
}

export function stepN(state: SimState, params: SimParams, steps: number): void {
  for (let s = 0; s < steps; s++) {
    stepOnce(state, params);
  }
  state.generation += steps;
}

function stepOnce(state: SimState, params: SimParams): void {
  const { a, b, tmpA, tmpB, width, height } = state;
  const { da, db, f, k } = params;

  for (let y = 0; y < height; y++) {
    const ym = ((y - 1 + height) % height) * width;
    const yc = y * width;
    const yp = ((y + 1) % height) * width;

    for (let x = 0; x < width; x++) {
      const xm = (x - 1 + width) % width;
      const xp = (x + 1) % width;
      const idx = yc + x;

      // 9-point stencil Laplacian (stable, weights sum to 0)
      // Orthogonal: 0.20, Diagonal: 0.05, Center: -1.0
      const lapA =
        0.05 * (a[ym + xm] + a[ym + xp] + a[yp + xm] + a[yp + xp]) +
        0.20 * (a[ym + x]  + a[yp + x]  + a[yc + xm] + a[yc + xp]) -
        1.00 * a[idx];
      const lapB =
        0.05 * (b[ym + xm] + b[ym + xp] + b[yp + xm] + b[yp + xp]) +
        0.20 * (b[ym + x]  + b[yp + x]  + b[yc + xm] + b[yc + xp]) -
        1.00 * b[idx];

      const av = a[idx];
      const bv = b[idx];
      const react = av * bv * bv;

      let na = av + da * lapA - react + f * (1 - av);
      let nb = bv + db * lapB + react - (f + k) * bv;

      if (na < 0) na = 0;
      else if (na > 1) na = 1;
      if (nb < 0) nb = 0;
      else if (nb > 1) nb = 1;

      tmpA[idx] = na;
      tmpB[idx] = nb;
    }
  }

  // Swap buffers
  state.a.set(tmpA);
  state.b.set(tmpB);
}
