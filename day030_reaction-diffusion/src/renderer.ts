import type { SimState } from './simulation.ts';

export type ColorTheme = 'ocean' | 'fire' | 'plasma' | 'gray';

interface ColorStop {
  t: number;
  r: number;
  g: number;
  b: number;
}

const THEMES: Record<ColorTheme, ColorStop[]> = {
  ocean: [
    { t: 0.0, r: 0,   g: 10,  b: 60  },
    { t: 0.4, r: 0,   g: 80,  b: 140 },
    { t: 0.7, r: 20,  g: 160, b: 200 },
    { t: 1.0, r: 200, g: 235, b: 255 },
  ],
  fire: [
    { t: 0.0, r: 0,   g: 0,   b: 0   },
    { t: 0.3, r: 160, g: 0,   b: 0   },
    { t: 0.6, r: 255, g: 100, b: 0   },
    { t: 0.85,r: 255, g: 220, b: 0   },
    { t: 1.0, r: 255, g: 255, b: 220 },
  ],
  plasma: [
    { t: 0.0, r: 10,  g: 0,   b: 40  },
    { t: 0.25,r: 100, g: 0,   b: 140 },
    { t: 0.5, r: 200, g: 40,  b: 200 },
    { t: 0.75,r: 255, g: 160, b: 60  },
    { t: 1.0, r: 255, g: 255, b: 100 },
  ],
  gray: [
    { t: 0.0, r: 0,   g: 0,   b: 0   },
    { t: 1.0, r: 255, g: 255, b: 255 },
  ],
};

function sampleColor(stops: ColorStop[], t: number): [number, number, number] {
  const clamped = Math.max(0, Math.min(1, t));
  let lo = stops[0];
  let hi = stops[stops.length - 1];
  for (let i = 0; i < stops.length - 1; i++) {
    if (clamped >= stops[i].t && clamped <= stops[i + 1].t) {
      lo = stops[i];
      hi = stops[i + 1];
      break;
    }
  }
  const span = hi.t - lo.t;
  const u = span > 0 ? (clamped - lo.t) / span : 0;
  return [
    Math.round(lo.r + (hi.r - lo.r) * u),
    Math.round(lo.g + (hi.g - lo.g) * u),
    Math.round(lo.b + (hi.b - lo.b) * u),
  ];
}

const B_SCALE = 3.5;

export function render(
  ctx: CanvasRenderingContext2D,
  state: SimState,
  theme: ColorTheme,
  imageData: ImageData,
): void {
  const stops = THEMES[theme];
  const { b, width, height } = state;
  const data = imageData.data;
  const n = width * height;

  for (let i = 0; i < n; i++) {
    const t = Math.min(1, b[i] * B_SCALE);
    const [r, g, bl] = sampleColor(stops, t);
    const p = i * 4;
    data[p]     = r;
    data[p + 1] = g;
    data[p + 2] = bl;
    data[p + 3] = 255;
  }

  ctx.putImageData(imageData, 0, 0);
}
