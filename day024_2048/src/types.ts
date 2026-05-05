export type Grid = number[][];
export type Direction = "up" | "down" | "left" | "right";

export interface SlideResult {
  grid: Grid;
  score: number;
  moved: boolean;
}

export interface GameState {
  grid: Grid;
  score: number;
  bestScore: number;
  gameOver: boolean;
  won: boolean;
  keepPlaying: boolean;
}

export interface TileAnimation {
  row: number;
  col: number;
  scale: number; // 1.0 = normal, >1.0 = pop-in
  type: "spawn" | "merge";
}
