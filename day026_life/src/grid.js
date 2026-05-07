export function createGrid(rows, cols) {
  return Array.from({ length: rows }, () => new Uint8Array(cols));
}

export function cloneGrid(grid) {
  return grid.map(row => new Uint8Array(row));
}

export function clearGrid(grid) {
  for (const row of grid) row.fill(0);
}

export function randomize(grid, density = 0.3) {
  const rows = grid.length;
  const cols = grid[0].length;
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      grid[r][c] = Math.random() < density ? 1 : 0;
    }
  }
}

export function step(grid) {
  const rows = grid.length;
  const cols = grid[0].length;
  const next = createGrid(rows, cols);

  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      const neighbors = countNeighbors(grid, r, c, rows, cols);
      const alive = grid[r][c] === 1;
      // Conway's rules
      if (alive && (neighbors === 2 || neighbors === 3)) {
        next[r][c] = 1;
      } else if (!alive && neighbors === 3) {
        next[r][c] = 1;
      }
    }
  }
  return next;
}

function countNeighbors(grid, r, c, rows, cols) {
  let count = 0;
  for (let dr = -1; dr <= 1; dr++) {
    for (let dc = -1; dc <= 1; dc++) {
      if (dr === 0 && dc === 0) continue;
      const nr = (r + dr + rows) % rows;
      const nc = (c + dc + cols) % cols;
      count += grid[nr][nc];
    }
  }
  return count;
}

export function countAlive(grid) {
  return grid.reduce((sum, row) => sum + row.reduce((s, v) => s + v, 0), 0);
}

export function placePattern(grid, pattern, originRow, originCol) {
  const rows = grid.length;
  const cols = grid[0].length;
  for (const [dr, dc] of pattern) {
    const r = originRow + dr;
    const c = originCol + dc;
    if (r >= 0 && r < rows && c >= 0 && c < cols) {
      grid[r][c] = 1;
    }
  }
}
