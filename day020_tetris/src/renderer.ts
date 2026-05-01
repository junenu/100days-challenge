import type { Board, Tetromino, TetrominoType } from './types.ts';
import { CELL_SIZE, COLORS, GHOST_ALPHA } from './types.ts';

const BORDER_RADIUS = 3;

function drawCell(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  type: TetrominoType,
  alpha = 1,
  size = CELL_SIZE,
): void {
  const px = x * size;
  const py = y * size;
  const color = COLORS[type];

  ctx.globalAlpha = alpha;
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.roundRect(px + 1, py + 1, size - 2, size - 2, BORDER_RADIUS);
  ctx.fill();

  // Highlight
  ctx.fillStyle = 'rgba(255,255,255,0.25)';
  ctx.beginPath();
  ctx.roundRect(px + 2, py + 2, size - 4, 6, 2);
  ctx.fill();

  ctx.globalAlpha = 1;
}

export function renderBoard(
  ctx: CanvasRenderingContext2D,
  board: Board,
  current: Tetromino,
  ghostY: number,
): void {
  const { canvas } = ctx;
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Background grid
  ctx.fillStyle = '#0d0d14';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  for (let r = 0; r < board.length; r++) {
    for (let c = 0; c < board[r].length; c++) {
      ctx.strokeStyle = '#1a1a28';
      ctx.lineWidth = 0.5;
      ctx.strokeRect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE);

      if (board[r][c]) {
        drawCell(ctx, c, r, board[r][c]!);
      }
    }
  }

  // Ghost piece
  for (let r = 0; r < current.shape.length; r++) {
    for (let c = 0; c < current.shape[r].length; c++) {
      if (!current.shape[r][c]) continue;
      const gx = current.pos.x + c;
      const gy = ghostY + r;
      if (gy >= 0) drawCell(ctx, gx, gy, current.type, GHOST_ALPHA);
    }
  }

  // Current piece
  for (let r = 0; r < current.shape.length; r++) {
    for (let c = 0; c < current.shape[r].length; c++) {
      if (!current.shape[r][c]) continue;
      const px = current.pos.x + c;
      const py = current.pos.y + r;
      if (py >= 0) drawCell(ctx, px, py, current.type);
    }
  }
}

export function renderNextPiece(ctx: CanvasRenderingContext2D, piece: Tetromino): void {
  const SIZE = 20;
  const { canvas } = ctx;
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = '#0d0d14';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  const offX = Math.floor((canvas.width / SIZE - piece.shape[0].length) / 2);
  const offY = Math.floor((canvas.height / SIZE - piece.shape.length) / 2);

  for (let r = 0; r < piece.shape.length; r++) {
    for (let c = 0; c < piece.shape[r].length; c++) {
      if (!piece.shape[r][c]) continue;
      const px = (offX + c) * SIZE;
      const py = (offY + r) * SIZE;
      ctx.fillStyle = COLORS[piece.type];
      ctx.beginPath();
      ctx.roundRect(px + 1, py + 1, SIZE - 2, SIZE - 2, 2);
      ctx.fill();
    }
  }
}
