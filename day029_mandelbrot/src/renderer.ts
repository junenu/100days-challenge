import type { Viewport } from './mandelbrot';
import { computeMandelbrot, screenToComplex } from './mandelbrot';
import type { ColorMap } from './colormap';

export class Renderer {
  private canvas: HTMLCanvasElement;
  private ctx: CanvasRenderingContext2D;
  private offscreen: HTMLCanvasElement;
  private offCtx: CanvasRenderingContext2D;
  private animId: number | null = null;

  constructor(canvas: HTMLCanvasElement) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d')!;
    this.offscreen = document.createElement('canvas');
    this.offCtx = this.offscreen.getContext('2d')!;
    this.resize();
  }

  resize(): void {
    const dpr = window.devicePixelRatio || 1;
    const w = this.canvas.clientWidth;
    const h = this.canvas.clientHeight;
    this.canvas.width = w * dpr;
    this.canvas.height = h * dpr;
    this.offscreen.width = w * dpr;
    this.offscreen.height = h * dpr;
  }

  get width(): number { return this.canvas.width; }
  get height(): number { return this.canvas.height; }

  render(viewport: Viewport, maxIter: number, colorMap: ColorMap): void {
    if (this.animId !== null) cancelAnimationFrame(this.animId);
    this.animId = requestAnimationFrame(() => {
      const imageData = this.offCtx.createImageData(this.width, this.height);
      computeMandelbrot(imageData, viewport, maxIter, colorMap);
      this.offCtx.putImageData(imageData, 0, 0);
      this.ctx.drawImage(this.offscreen, 0, 0);
      this.animId = null;
    });
  }

  getComplex(px: number, py: number, viewport: Viewport): [number, number] {
    const dpr = window.devicePixelRatio || 1;
    return screenToComplex(px * dpr, py * dpr, this.width, this.height, viewport);
  }
}
