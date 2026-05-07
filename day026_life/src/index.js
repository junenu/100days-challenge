import { createGrid, cloneGrid, clearGrid, randomize, step, countAlive, placePattern } from './grid.js';
import { PATTERNS, PATTERN_KEYS } from './patterns.js';
import { render, hideCursor, showCursor, clearScreen } from './renderer.js';

const MIN_INTERVAL = 50;
const MAX_INTERVAL = 1000;
const SPEED_STEP = 50;

function getTermSize() {
  const cols = Math.floor((process.stdout.columns || 80) / 2);
  const rows = (process.stdout.rows || 24) - 5;
  return { rows: Math.max(10, rows), cols: Math.max(20, cols) };
}

function loadPattern(grid, key) {
  const { rows, cols } = { rows: grid.length, cols: grid[0].length };
  clearGrid(grid);
  const pattern = PATTERNS[key];
  const patRows = Math.max(...pattern.cells.map(([r]) => r)) + 1;
  const patCols = Math.max(...pattern.cells.map(([, c]) => c)) + 1;
  const originRow = Math.floor((rows - patRows) / 2);
  const originCol = Math.floor((cols - patCols) / 2);
  placePattern(grid, pattern.cells, originRow, originCol);
  return pattern.name;
}

function main() {
  let { rows, cols } = getTermSize();
  let grid = createGrid(rows, cols);
  let prevGrid = createGrid(rows, cols);
  let timerId = null;

  const state = {
    paused: false,
    generation: 0,
    alive: 0,
    interval: 100,
    patternName: 'Random',
    running: true,
  };

  randomize(grid);
  state.alive = countAlive(grid);

  if (!process.stdin.isTTY) {
    process.stderr.write('Error: must be run in an interactive terminal.\n');
    process.exit(1);
  }

  hideCursor();
  process.stdin.setRawMode(true);
  process.stdin.resume();
  process.stdin.setEncoding('utf8');

  function cleanup() {
    state.running = false;
    if (timerId) clearTimeout(timerId);
    showCursor();
    clearScreen();
    process.stdout.write('Bye!\n');
    process.exit(0);
  }

  process.stdin.on('data', (key) => {
    switch (key) {
      case 'q':
      case '\x03':
        cleanup();
        break;
      case ' ':
        state.paused = !state.paused;
        break;
      case 'r':
        clearGrid(grid);
        randomize(grid);
        state.generation = 0;
        state.alive = countAlive(grid);
        state.patternName = 'Random';
        break;
      case 'c':
        clearGrid(grid);
        state.generation = 0;
        state.alive = 0;
        state.patternName = 'Clear';
        break;
      case 's':
        prevGrid = cloneGrid(grid);
        grid = step(grid);
        state.generation++;
        state.alive = countAlive(grid);
        break;
      case '+':
      case '=':
        state.interval = Math.max(MIN_INTERVAL, state.interval - SPEED_STEP);
        break;
      case '-':
        state.interval = Math.min(MAX_INTERVAL, state.interval + SPEED_STEP);
        break;
      default: {
        const idx = parseInt(key, 10) - 1;
        if (!isNaN(idx) && idx >= 0 && idx < PATTERN_KEYS.length) {
          state.patternName = loadPattern(grid, PATTERN_KEYS[idx]);
          state.generation = 0;
          state.alive = countAlive(grid);
        }
        break;
      }
    }
    // Force re-render on input
    render(grid, prevGrid, state);
  });

  process.stdout.on('resize', () => {
    const size = getTermSize();
    const newGrid = createGrid(size.rows, size.cols);
    const minRows = Math.min(grid.length, size.rows);
    const minCols = Math.min(grid[0].length, size.cols);
    for (let r = 0; r < minRows; r++) {
      for (let c = 0; c < minCols; c++) {
        newGrid[r][c] = grid[r][c];
      }
    }
    grid = newGrid;
    prevGrid = createGrid(size.rows, size.cols);
    rows = size.rows;
    cols = size.cols;
  });

  process.on('SIGTERM', cleanup);
  process.on('SIGINT', cleanup);

  function tick() {
    if (!state.running) return;
    if (!state.paused) {
      prevGrid = cloneGrid(grid);
      grid = step(grid);
      state.generation++;
      state.alive = countAlive(grid);
    }
    render(grid, prevGrid, state);
    timerId = setTimeout(tick, state.interval);
  }

  tick();
}

main();
