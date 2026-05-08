export type Tool = 'pencil' | 'eraser' | 'fill' | 'eyedropper';

export type Color = string; // hex like '#ff0000'

export interface Pixel {
  color: Color | null; // null = transparent
}

export interface CanvasState {
  width: number;
  height: number;
  pixels: Pixel[][];
}

export type History = CanvasState[];
