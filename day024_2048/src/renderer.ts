import type { Grid, TileAnimation } from "./types";

const TILE_COLORS: Record<number, { bg: string; text: string }> = {
  0:    { bg: "#cdc1b4", text: "#776e65" },
  2:    { bg: "#eee4da", text: "#776e65" },
  4:    { bg: "#ede0c8", text: "#776e65" },
  8:    { bg: "#f2b179", text: "#f9f6f2" },
  16:   { bg: "#f59563", text: "#f9f6f2" },
  32:   { bg: "#f67c5f", text: "#f9f6f2" },
  64:   { bg: "#f65e3b", text: "#f9f6f2" },
  128:  { bg: "#edcf72", text: "#f9f6f2" },
  256:  { bg: "#edcc61", text: "#f9f6f2" },
  512:  { bg: "#edc850", text: "#f9f6f2" },
  1024: { bg: "#edc53f", text: "#f9f6f2" },
  2048: { bg: "#edc22e", text: "#f9f6f2" },
};

const BG_COLOR = "#bbada0";
const PADDING = 10;
const CELL_SIZE = 100;
const BORDER_RADIUS = 6;
const GRID_SIZE = 4;

function getTileColor(value: number): { bg: string; text: string } {
  return TILE_COLORS[value] ?? { bg: "#3d3a33", text: "#f9f6f2" };
}

function getFontSize(value: number): number {
  if (value < 100) return 40;
  if (value < 1000) return 32;
  return 24;
}

function roundRect(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  w: number,
  h: number,
  r: number
) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.lineTo(x + w - r, y);
  ctx.quadraticCurveTo(x + w, y, x + w, y + r);
  ctx.lineTo(x + w, y + h - r);
  ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
  ctx.lineTo(x + r, y + h);
  ctx.quadraticCurveTo(x, y + h, x, y + h - r);
  ctx.lineTo(x, y + r);
  ctx.quadraticCurveTo(x, y, x + r, y);
  ctx.closePath();
}

export function canvasSize(): number {
  return CELL_SIZE * GRID_SIZE + PADDING * (GRID_SIZE + 1);
}

export function drawGrid(
  ctx: CanvasRenderingContext2D,
  grid: Grid,
  animations: TileAnimation[]
) {
  const size = canvasSize();
  ctx.clearRect(0, 0, size, size);

  // Background
  ctx.fillStyle = BG_COLOR;
  roundRect(ctx, 0, 0, size, size, BORDER_RADIUS * 2);
  ctx.fill();

  // Empty cells
  for (let r = 0; r < GRID_SIZE; r++) {
    for (let c = 0; c < GRID_SIZE; c++) {
      const x = PADDING + c * (CELL_SIZE + PADDING);
      const y = PADDING + r * (CELL_SIZE + PADDING);
      ctx.fillStyle = TILE_COLORS[0].bg;
      roundRect(ctx, x, y, CELL_SIZE, CELL_SIZE, BORDER_RADIUS);
      ctx.fill();
    }
  }

  // Tiles
  for (let r = 0; r < GRID_SIZE; r++) {
    for (let c = 0; c < GRID_SIZE; c++) {
      const value = grid[r][c];
      if (value === 0) continue;

      const anim = animations.find((a) => a.row === r && a.col === c);
      const scale = anim ? anim.scale : 1.0;

      const baseX = PADDING + c * (CELL_SIZE + PADDING);
      const baseY = PADDING + r * (CELL_SIZE + PADDING);
      const cx = baseX + CELL_SIZE / 2;
      const cy = baseY + CELL_SIZE / 2;

      const { bg, text } = getTileColor(value);

      ctx.save();
      ctx.translate(cx, cy);
      ctx.scale(scale, scale);
      ctx.translate(-CELL_SIZE / 2, -CELL_SIZE / 2);

      ctx.fillStyle = bg;
      roundRect(ctx, 0, 0, CELL_SIZE, CELL_SIZE, BORDER_RADIUS);
      ctx.fill();

      ctx.fillStyle = text;
      ctx.font = `bold ${getFontSize(value)}px "Clear Sans", "Helvetica Neue", Arial, sans-serif`;
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(String(value), CELL_SIZE / 2, CELL_SIZE / 2);

      ctx.restore();
    }
  }
}
