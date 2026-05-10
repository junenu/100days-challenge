export type ColorMap = (t: number, maxIter: number) => [number, number, number];

// t: iteration count (0 = inside set), maxIter: max iterations
export const COLORMAPS: Record<string, ColorMap> = {
  classic: (t, maxIter) => {
    if (t === maxIter) return [0, 0, 0];
    const n = t / maxIter;
    const r = Math.floor(9 * (1 - n) * n * n * n * 255);
    const g = Math.floor(15 * (1 - n) * (1 - n) * n * n * 255);
    const b = Math.floor(8.5 * (1 - n) * (1 - n) * (1 - n) * n * 255);
    return [r, g, b];
  },

  fire: (t, maxIter) => {
    if (t === maxIter) return [0, 0, 0];
    const n = t / maxIter;
    const r = Math.min(255, Math.floor(n * 3 * 255));
    const g = Math.min(255, Math.floor((n * 3 - 1) * 255));
    const b = Math.min(255, Math.floor((n * 3 - 2) * 255));
    return [r, g, b];
  },

  electric: (t, maxIter) => {
    if (t === maxIter) return [0, 0, 0];
    const angle = (t / maxIter) * Math.PI * 2;
    const r = Math.floor((Math.sin(angle) * 0.5 + 0.5) * 255);
    const g = Math.floor((Math.sin(angle + 2) * 0.5 + 0.5) * 255);
    const b = Math.floor((Math.sin(angle + 4) * 0.5 + 0.5) * 255);
    return [r, g, b];
  },

  grayscale: (t, maxIter) => {
    if (t === maxIter) return [0, 0, 0];
    const v = Math.floor((t / maxIter) * 255);
    return [v, v, v];
  },

  ultraviolet: (t, maxIter) => {
    if (t === maxIter) return [0, 0, 0];
    const n = t / maxIter;
    // smooth banding with log
    const smooth = n + 1 - Math.log(Math.log(2)) / Math.log(2);
    const angle = smooth * Math.PI * 6;
    const r = Math.floor((Math.cos(angle) * 0.5 + 0.5) * 200);
    const g = Math.floor((Math.cos(angle + 1) * 0.5 + 0.5) * 100);
    const b = Math.floor((Math.cos(angle + 2) * 0.5 + 0.5) * 255);
    return [r, g, b];
  },
};

export const COLORMAP_NAMES = Object.keys(COLORMAPS);
