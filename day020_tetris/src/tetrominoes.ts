import type { TetrominoType, Tetromino } from './types.ts';

const SHAPES: Record<TetrominoType, number[][]> = {
  I: [
    [0, 0, 0, 0],
    [1, 1, 1, 1],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
  ],
  O: [
    [1, 1],
    [1, 1],
  ],
  T: [
    [0, 1, 0],
    [1, 1, 1],
    [0, 0, 0],
  ],
  S: [
    [0, 1, 1],
    [1, 1, 0],
    [0, 0, 0],
  ],
  Z: [
    [1, 1, 0],
    [0, 1, 1],
    [0, 0, 0],
  ],
  J: [
    [1, 0, 0],
    [1, 1, 1],
    [0, 0, 0],
  ],
  L: [
    [0, 0, 1],
    [1, 1, 1],
    [0, 0, 0],
  ],
};

const TYPES: TetrominoType[] = ['I', 'O', 'T', 'S', 'Z', 'J', 'L'];

export function randomTetromino(): Tetromino {
  const type = TYPES[Math.floor(Math.random() * TYPES.length)];
  const shape = SHAPES[type].map((row) => [...row]);
  return { type, shape, pos: { x: 3, y: 0 } };
}

export function rotate(shape: number[][]): number[][] {
  const n = shape.length;
  return shape[0].map((_, col) =>
    shape.map((row) => row[col]).reverse()
  ).map((row) => row.slice(0, n));
}

export function spawnPos(shape: number[][], cols: number): number {
  return Math.floor((cols - shape[0].length) / 2);
}
