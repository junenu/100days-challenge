export type TetrominoType = 'I' | 'O' | 'T' | 'S' | 'Z' | 'J' | 'L';
export type Cell = TetrominoType | null;
export type Board = Cell[][];

export interface Position {
  x: number;
  y: number;
}

export interface Tetromino {
  type: TetrominoType;
  shape: number[][];
  pos: Position;
}

export interface GameState {
  board: Board;
  current: Tetromino;
  next: Tetromino;
  score: number;
  level: number;
  lines: number;
  gameOver: boolean;
  paused: boolean;
}

export const BOARD_COLS = 10;
export const BOARD_ROWS = 20;
export const CELL_SIZE = 32;

export const COLORS: Record<TetrominoType, string> = {
  I: '#00cfcf',
  O: '#f0c040',
  T: '#a020f0',
  S: '#40c040',
  Z: '#e03030',
  J: '#2060e0',
  L: '#f08020',
};

export const GHOST_ALPHA = 0.25;
