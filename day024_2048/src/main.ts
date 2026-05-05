import { initGame, slide, addRandomTile, hasWon, isGameOver } from "./game";
import { drawGrid, canvasSize } from "./renderer";
import type { GameState, TileAnimation, Direction } from "./types";

const STORAGE_KEY = "2048-best-score";
const ANIM_DURATION = 150; // ms

let state: GameState;
let animations: TileAnimation[] = [];
let animStart = 0;
let animating = false;
let pendingDirection: Direction | null = null;

const canvas = document.getElementById("game-canvas") as HTMLCanvasElement;
const ctx = canvas.getContext("2d")!;
const scoreEl = document.getElementById("score")!;
const bestEl = document.getElementById("best")!;
const messageEl = document.getElementById("message")!;
const newGameBtn = document.getElementById("new-game")!;
const keepPlayingBtn = document.getElementById("keep-playing")!;

function loadBest(): number {
  return parseInt(localStorage.getItem(STORAGE_KEY) ?? "0", 10);
}

function saveBest(score: number) {
  localStorage.setItem(STORAGE_KEY, String(score));
}

function updateUI() {
  scoreEl.textContent = String(state.score);
  bestEl.textContent = String(state.bestScore);

  if (state.gameOver) {
    messageEl.textContent = "Game Over!";
    messageEl.className = "message show game-over";
    keepPlayingBtn.style.display = "none";
  } else if (state.won && !state.keepPlaying) {
    messageEl.textContent = "You Win!";
    messageEl.className = "message show won";
    keepPlayingBtn.style.display = "inline-block";
  } else {
    messageEl.className = "message";
    keepPlayingBtn.style.display = "none";
  }
}

function startAnimations(anims: TileAnimation[]) {
  animations = anims;
  animStart = performance.now();
  animating = true;
  requestAnimationFrame(animLoop);
}

function animLoop(now: number) {
  const t = Math.min((now - animStart) / ANIM_DURATION, 1);
  const eased = t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t; // ease in-out

  // Scale: start at 0.6, peak at 1.15 halfway, settle at 1.0
  const scale = t < 1 ? 0.6 + eased * 0.55 + Math.sin(eased * Math.PI) * 0.15 : 1.0;

  const currentAnims = animations.map((a) => ({ ...a, scale }));
  drawGrid(ctx, state.grid, currentAnims);

  if (t < 1) {
    requestAnimationFrame(animLoop);
  } else {
    animating = false;
    animations = [];
    drawGrid(ctx, state.grid, []);
    if (pendingDirection) {
      const dir = pendingDirection;
      pendingDirection = null;
      processMove(dir);
    }
  }
}

function processMove(dir: Direction) {
  if (state.gameOver) return;
  if (state.won && !state.keepPlaying) return;
  if (animating) {
    pendingDirection = dir;
    return;
  }

  const result = slide(state.grid, dir);
  if (!result.moved) return;

  const newScore = state.score + result.score;
  const newBest = Math.max(state.bestScore, newScore);
  if (newBest > state.bestScore) saveBest(newBest);

  const newGrid = addRandomTile(result.grid);

  // Find newly added tile for spawn animation
  const spawnAnims: TileAnimation[] = [];
  for (let r = 0; r < 4; r++) {
    for (let c = 0; c < 4; c++) {
      if (result.grid[r][c] === 0 && newGrid[r][c] !== 0) {
        spawnAnims.push({ row: r, col: c, scale: 0.6, type: "spawn" });
      }
    }
  }

  // Find merged tiles (score > 0 and tile value changed)
  if (result.score > 0) {
    for (let r = 0; r < 4; r++) {
      for (let c = 0; c < 4; c++) {
        if (result.grid[r][c] > state.grid[r][c] && result.grid[r][c] === state.grid[r][c] * 2) {
          spawnAnims.push({ row: r, col: c, scale: 0.6, type: "merge" });
        }
      }
    }
  }

  state = {
    ...state,
    grid: newGrid,
    score: newScore,
    bestScore: newBest,
    won: !state.keepPlaying && hasWon(newGrid),
    gameOver: isGameOver(newGrid),
  };

  updateUI();
  startAnimations(spawnAnims);
}

function newGame() {
  state = initGame(loadBest());
  messageEl.className = "message";
  keepPlayingBtn.style.display = "none";

  const spawnAnims: TileAnimation[] = [];
  for (let r = 0; r < 4; r++) {
    for (let c = 0; c < 4; c++) {
      if (state.grid[r][c] !== 0) {
        spawnAnims.push({ row: r, col: c, scale: 0.6, type: "spawn" });
      }
    }
  }
  updateUI();
  startAnimations(spawnAnims);
}

// Keyboard input
window.addEventListener("keydown", (e) => {
  const map: Record<string, Direction> = {
    ArrowUp: "up",
    ArrowDown: "down",
    ArrowLeft: "left",
    ArrowRight: "right",
  };
  const dir = map[e.key];
  if (dir) {
    e.preventDefault();
    processMove(dir);
  }
});

// Touch/swipe input
let touchStartX = 0;
let touchStartY = 0;

canvas.addEventListener("touchstart", (e) => {
  touchStartX = e.touches[0].clientX;
  touchStartY = e.touches[0].clientY;
  e.preventDefault();
}, { passive: false });

canvas.addEventListener("touchend", (e) => {
  const dx = e.changedTouches[0].clientX - touchStartX;
  const dy = e.changedTouches[0].clientY - touchStartY;
  const absX = Math.abs(dx);
  const absY = Math.abs(dy);
  if (Math.max(absX, absY) < 20) return;

  if (absX > absY) {
    processMove(dx > 0 ? "right" : "left");
  } else {
    processMove(dy > 0 ? "down" : "up");
  }
  e.preventDefault();
}, { passive: false });

// Buttons
newGameBtn.addEventListener("click", newGame);
keepPlayingBtn.addEventListener("click", () => {
  state = { ...state, keepPlaying: true };
  messageEl.className = "message";
  keepPlayingBtn.style.display = "none";
});

// Init
const size = canvasSize();
canvas.width = size;
canvas.height = size;
newGame();
