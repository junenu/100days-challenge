import type { ColorMap } from './colormap';

export interface Viewport {
  centerX: number;
  centerY: number;
  zoom: number; // pixels per unit in complex plane
}

export function computeMandelbrot(
  imageData: ImageData,
  viewport: Viewport,
  maxIter: number,
  colorMap: ColorMap,
): void {
  const { width, height } = imageData;
  const data = imageData.data;
  const { centerX, centerY, zoom } = viewport;

  for (let py = 0; py < height; py++) {
    for (let px = 0; px < width; px++) {
      const cx = centerX + (px - width / 2) / zoom;
      const cy = centerY + (py - height / 2) / zoom;

      let x = 0;
      let y = 0;
      let iter = 0;

      while (x * x + y * y <= 4 && iter < maxIter) {
        const xNew = x * x - y * y + cx;
        y = 2 * x * y + cy;
        x = xNew;
        iter++;
      }

      const idx = (py * width + px) * 4;
      let r: number, g: number, b: number;

      if (iter === maxIter) {
        [r, g, b] = [0, 0, 0];
      } else {
        // smooth coloring: fractional escape count
        const log2 = Math.log(x * x + y * y) / 2;
        const nu = Math.log(log2 / Math.log(2)) / Math.log(2);
        const smooth = iter + 1 - nu;
        [r, g, b] = colorMap(smooth, maxIter);
      }

      data[idx] = r;
      data[idx + 1] = g;
      data[idx + 2] = b;
      data[idx + 3] = 255;
    }
  }
}

export function screenToComplex(
  px: number,
  py: number,
  width: number,
  height: number,
  viewport: Viewport,
): [number, number] {
  return [
    viewport.centerX + (px - width / 2) / viewport.zoom,
    viewport.centerY + (py - height / 2) / viewport.zoom,
  ];
}
