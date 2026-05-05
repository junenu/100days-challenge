import type { Grid, Direction, SlideResult, GameState } from "./types";

const GRID_SIZE = 4;
const WIN_TILE = 2048;

export function createEmptyGrid(): Grid {
  return Array.from({ length: GRID_SIZE }, () => Array(GRID_SIZE).fill(0));
}

export function addRandomTile(grid: Grid): Grid {
  const empty: [number, number][] = [];
  for (let r = 0; r < GRID_SIZE; r++) {
    for (let c = 0; c < GRID_SIZE; c++) {
      if (grid[r][c] === 0) empty.push([r, c]);
    }
  }
  if (empty.length === 0) return grid;

  const [r, c] = empty[Math.floor(Math.random() * empty.length)];
  const value = Math.random() < 0.9 ? 2 : 4;
  return grid.map((row, ri) =>
    row.map((cell, ci) => (ri === r && ci === c ? value : cell))
  );
}

function slideRowLeft(row: number[]): { row: number[]; score: number; moved: boolean } {
  const filtered = row.filter((v) => v !== 0);
  const result: number[] = [];
  let score = 0;
  let moved = false;
  let i = 0;

  while (i < filtered.length) {
    if (i + 1 < filtered.length && filtered[i] === filtered[i + 1]) {
      const merged = filtered[i] * 2;
      result.push(merged);
      score += merged;
      i += 2;
    } else {
      result.push(filtered[i]);
      i++;
    }
  }

  while (result.length < GRID_SIZE) result.push(0);

  if (result.some((v, idx) => v !== row[idx])) moved = true;

  return { row: result, score, moved };
}

function transpose(grid: Grid): Grid {
  return grid[0].map((_, c) => grid.map((row) => row[c]));
}

function reverseRows(grid: Grid): Grid {
  return grid.map((row) => [...row].reverse());
}

export function slide(grid: Grid, direction: Direction): SlideResult {
  let working = grid.map((row) => [...row]);
  let totalScore = 0;
  let anyMoved = false;

  // Normalize: always slide left on the transformed grid
  if (direction === "right") {
    working = reverseRows(working);
  } else if (direction === "up") {
    working = transpose(working);
  } else if (direction === "down") {
    working = transpose(reverseRows(working));
  }

  working = working.map((row) => {
    const res = slideRowLeft(row);
    totalScore += res.score;
    if (res.moved) anyMoved = true;
    return res.row;
  });

  // Undo transform
  if (direction === "right") {
    working = reverseRows(working);
  } else if (direction === "up") {
    working = transpose(working);
  } else if (direction === "down") {
    working = reverseRows(transpose(working));
  }

  return { grid: working, score: totalScore, moved: anyMoved };
}

export function hasWon(grid: Grid): boolean {
  return grid.some((row) => row.some((v) => v >= WIN_TILE));
}

export function isGameOver(grid: Grid): boolean {
  for (let r = 0; r < GRID_SIZE; r++) {
    for (let c = 0; c < GRID_SIZE; c++) {
      if (grid[r][c] === 0) return false;
      if (c + 1 < GRID_SIZE && grid[r][c] === grid[r][c + 1]) return false;
      if (r + 1 < GRID_SIZE && grid[r][c] === grid[r + 1][c]) return false;
    }
  }
  return true;
}

export function initGame(bestScore: number): GameState {
  let grid = createEmptyGrid();
  grid = addRandomTile(grid);
  grid = addRandomTile(grid);
  return { grid, score: 0, bestScore, gameOver: false, won: false, keepPlaying: false };
}
