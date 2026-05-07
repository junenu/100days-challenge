const ESC = '\x1b';
const RESET = `${ESC}[0m`;
const HIDE_CURSOR = `${ESC}[?25l`;
const SHOW_CURSOR = `${ESC}[?25h`;
const CLEAR_SCREEN = `${ESC}[2J`;
const HOME = `${ESC}[H`;

// Colors
const CELL_ALIVE = `${ESC}[38;5;141m`; // purple
const CELL_NEW   = `${ESC}[38;5;51m`;  // cyan  (born this gen)
const CELL_OLD   = `${ESC}[38;5;99m`;  // dark purple (> 1 gen)
const DIM        = `${ESC}[2m`;
const BOLD       = `${ESC}[1m`;
const CYAN       = `${ESC}[36m`;
const YELLOW     = `${ESC}[33m`;
const GREEN      = `${ESC}[32m`;

const ALIVE_CHAR = '██';
const DEAD_CHAR  = '  ';

export function hideCursor() {
  process.stdout.write(HIDE_CURSOR);
}

export function showCursor() {
  process.stdout.write(SHOW_CURSOR);
}

export function render(grid, prevGrid, state) {
  const rows = grid.length;
  const cols = grid[0].length;
  const lines = [];

  lines.push(HOME);

  // Header
  const status = state.paused
    ? `${YELLOW}${BOLD}[PAUSED]${RESET}`
    : `${GREEN}${BOLD}[RUNNING]${RESET}`;
  const speed = `${CYAN}speed:${RESET} ${state.interval}ms`;
  const gen   = `${CYAN}gen:${RESET}   ${String(state.generation).padStart(6)}`;
  const alive = `${CYAN}alive:${RESET} ${String(state.alive).padStart(6)}`;
  const pat   = `${CYAN}pattern:${RESET} ${state.patternName}`;
  lines.push(`${BOLD}Conway's Game of Life${RESET}  ${status}  ${gen}  ${alive}  ${speed}  ${pat}`);
  lines.push('');

  // Grid
  for (let r = 0; r < rows; r++) {
    let line = '';
    for (let c = 0; c < cols; c++) {
      if (grid[r][c] === 1) {
        const wasAlive = prevGrid && prevGrid[r][c] === 1;
        line += (wasAlive ? CELL_OLD : CELL_NEW) + ALIVE_CHAR + RESET;
      } else {
        line += DIM + DEAD_CHAR + RESET;
      }
    }
    lines.push(line);
  }

  // Footer
  lines.push('');
  lines.push(
    `${DIM}space${RESET}:pause  ` +
    `${DIM}r${RESET}:random  ` +
    `${DIM}c${RESET}:clear  ` +
    `${DIM}s${RESET}:step  ` +
    `${DIM}+/-${RESET}:speed  ` +
    `${DIM}1-7${RESET}:pattern  ` +
    `${DIM}q${RESET}:quit`
  );

  process.stdout.write(CLEAR_SCREEN + lines.join('\n'));
}

export function clearScreen() {
  process.stdout.write(CLEAR_SCREEN + HOME);
}
