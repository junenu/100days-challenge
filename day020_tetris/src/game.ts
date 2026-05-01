import type { Board, Cell, GameState, Tetromino } from './types.ts';
import { BOARD_COLS, BOARD_ROWS } from './types.ts';
import { randomTetromino, rotate, spawnPos } from './tetrominoes.ts';

function emptyBoard(): Board {
  return Array.from({ length: BOARD_ROWS }, () => Array(BOARD_COLS).fill(null));
}

function collides(board: Board, piece: Tetromino, dx = 0, dy = 0, shape = piece.shape): boolean {
  for (let r = 0; r < shape.length; r++) {
    for (let c = 0; c < shape[r].length; c++) {
      if (!shape[r][c]) continue;
      const nx = piece.pos.x + c + dx;
      const ny = piece.pos.y + r + dy;
      if (nx < 0 || nx >= BOARD_COLS || ny >= BOARD_ROWS) return true;
      if (ny >= 0 && board[ny][nx] !== null) return true;
    }
  }
  return false;
}

function lockPiece(board: Board, piece: Tetromino): Board {
  const next = board.map((row) => [...row] as Cell[]);
  for (let r = 0; r < piece.shape.length; r++) {
    for (let c = 0; c < piece.shape[r].length; c++) {
      if (!piece.shape[r][c]) continue;
      const y = piece.pos.y + r;
      const x = piece.pos.x + c;
      if (y >= 0) next[y][x] = piece.type;
    }
  }
  return next;
}

function clearLines(board: Board): { board: Board; cleared: number } {
  const remaining = board.filter((row) => row.some((cell) => cell === null));
  const cleared = BOARD_ROWS - remaining.length;
  const newRows = Array.from({ length: cleared }, () => Array(BOARD_COLS).fill(null) as Cell[]);
  return { board: [...newRows, ...remaining], cleared };
}

const SCORE_TABLE = [0, 100, 300, 500, 800];

function calcScore(cleared: number, level: number): number {
  return (SCORE_TABLE[cleared] ?? 0) * level;
}

export function initGame(): GameState {
  const current = randomTetromino();
  current.pos.x = spawnPos(current.shape, BOARD_COLS);
  const next = randomTetromino();
  next.pos.x = spawnPos(next.shape, BOARD_COLS);

  return {
    board: emptyBoard(),
    current,
    next,
    score: 0,
    level: 1,
    lines: 0,
    gameOver: false,
    paused: false,
  };
}

export function moveLeft(state: GameState): GameState {
  if (collides(state.board, state.current, -1, 0)) return state;
  return {
    ...state,
    current: { ...state.current, pos: { ...state.current.pos, x: state.current.pos.x - 1 } },
  };
}

export function moveRight(state: GameState): GameState {
  if (collides(state.board, state.current, 1, 0)) return state;
  return {
    ...state,
    current: { ...state.current, pos: { ...state.current.pos, x: state.current.pos.x + 1 } },
  };
}

export function rotatePiece(state: GameState): GameState {
  const rotated = rotate(state.current.shape);
  // Wall kick: try offsets 0, -1, +1, -2, +2
  for (const dx of [0, -1, 1, -2, 2]) {
    if (!collides(state.board, state.current, dx, 0, rotated)) {
      return {
        ...state,
        current: {
          ...state.current,
          shape: rotated,
          pos: { ...state.current.pos, x: state.current.pos.x + dx },
        },
      };
    }
  }
  return state;
}

export function softDrop(state: GameState): GameState {
  if (collides(state.board, state.current, 0, 1)) return lockAndSpawn(state);
  return {
    ...state,
    current: { ...state.current, pos: { ...state.current.pos, y: state.current.pos.y + 1 } },
    score: state.score + 1,
  };
}

export function hardDrop(state: GameState): GameState {
  let dy = 0;
  while (!collides(state.board, state.current, 0, dy + 1)) dy++;
  const dropped: GameState = {
    ...state,
    current: { ...state.current, pos: { ...state.current.pos, y: state.current.pos.y + dy } },
    score: state.score + dy * 2,
  };
  return lockAndSpawn(dropped);
}

export function tick(state: GameState): GameState {
  if (state.gameOver || state.paused) return state;
  if (collides(state.board, state.current, 0, 1)) return lockAndSpawn(state);
  return {
    ...state,
    current: { ...state.current, pos: { ...state.current.pos, y: state.current.pos.y + 1 } },
  };
}

function lockAndSpawn(state: GameState): GameState {
  const locked = lockPiece(state.board, state.current);
  const { board, cleared } = clearLines(locked);
  const newLines = state.lines + cleared;
  const level = Math.floor(newLines / 10) + 1;
  const score = state.score + calcScore(cleared, level);

  const current = { ...state.next, pos: { x: spawnPos(state.next.shape, BOARD_COLS), y: 0 } };
  const next = randomTetromino();
  next.pos.x = spawnPos(next.shape, BOARD_COLS);

  const gameOver = collides(board, current);

  return { board, current, next, score, level, lines: newLines, gameOver, paused: false };
}

export function ghostY(state: GameState): number {
  let dy = 0;
  while (!collides(state.board, state.current, 0, dy + 1)) dy++;
  return state.current.pos.y + dy;
}

export function dropInterval(level: number): number {
  return Math.max(100, 1000 - (level - 1) * 90);
}
