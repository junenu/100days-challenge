import { BOARD_COLS, BOARD_ROWS, CELL_SIZE } from './types.ts';
import {
  initGame,
  moveLeft,
  moveRight,
  rotatePiece,
  softDrop,
  hardDrop,
  tick,
  ghostY,
  dropInterval,
} from './game.ts';
import { renderBoard, renderNextPiece } from './renderer.ts';
import type { GameState } from './types.ts';

const boardCanvas = document.getElementById('board') as HTMLCanvasElement;
const nextCanvas = document.getElementById('next-canvas') as HTMLCanvasElement;
const scoreEl = document.getElementById('score')!;
const levelEl = document.getElementById('level')!;
const linesEl = document.getElementById('lines')!;
const overlay = document.getElementById('overlay')!;
const startBtn = document.getElementById('start-btn')!;

boardCanvas.width = BOARD_COLS * CELL_SIZE;
boardCanvas.height = BOARD_ROWS * CELL_SIZE;
nextCanvas.width = 100;
nextCanvas.height = 80;

const boardCtx = boardCanvas.getContext('2d')!;
const nextCtx = nextCanvas.getContext('2d')!;

let state: GameState = initGame();
let lastTick = 0;
let rafId = 0;
let running = false;

function updateHUD(): void {
  scoreEl.textContent = state.score.toString();
  levelEl.textContent = state.level.toString();
  linesEl.textContent = state.lines.toString();
}

function render(): void {
  renderBoard(boardCtx, state.board, state.current, ghostY(state));
  renderNextPiece(nextCtx, state.next);
}

function gameLoop(ts: number): void {
  if (!running) return;

  if (state.gameOver) {
    showGameOver();
    return;
  }

  if (!state.paused && ts - lastTick >= dropInterval(state.level)) {
    state = tick(state);
    lastTick = ts;
  }

  render();
  updateHUD();
  rafId = requestAnimationFrame(gameLoop);
}

function showGameOver(): void {
  overlay.innerHTML = `
    <h1>GAME OVER</h1>
    <div class="final-score">Score: ${state.score}</div>
    <p>Level ${state.level} — ${state.lines} lines</p>
    <button id="start-btn">RETRY</button>
  `;
  overlay.style.display = 'flex';
  document.getElementById('start-btn')!.addEventListener('click', startGame);
  running = false;
}

function startGame(): void {
  state = initGame();
  overlay.style.display = 'none';
  running = true;
  lastTick = performance.now();
  cancelAnimationFrame(rafId);
  rafId = requestAnimationFrame(gameLoop);
}

const KEY_HANDLERS: Record<string, () => void> = {
  ArrowLeft: () => { state = moveLeft(state); },
  ArrowRight: () => { state = moveRight(state); },
  ArrowUp: () => { state = rotatePiece(state); },
  ArrowDown: () => { state = softDrop(state); },
  ' ': () => { state = hardDrop(state); },
  p: () => { state = { ...state, paused: !state.paused }; },
  P: () => { state = { ...state, paused: !state.paused }; },
};

document.addEventListener('keydown', (e) => {
  if (!running || state.gameOver) return;
  const handler = KEY_HANDLERS[e.key];
  if (handler) {
    e.preventDefault();
    handler();
    render();
    updateHUD();
  }
});

startBtn.addEventListener('click', startGame);
