"""Generate a PNG screenshot of the roguelike game for the README."""
import random
import sys
import os

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
from dungeon import Dungeon, WALL, FLOOR, STAIRS
from entities import Player, spawn_monsters, spawn_items, Potion, Gold

# ── fixed seed for reproducible screenshot ─────────────────────────────────
random.seed(42)

# ── game state ─────────────────────────────────────────────────────────────
MAP_W, MAP_H = 70, 24
dungeon = Dungeon(MAP_W, MAP_H)
sx, sy = dungeon.rooms[0].center
player = Player(sx, sy)
player.floor = 2
player.level = 3
player.hp = 22
player.max_hp = 30
player.attack = 9
player.defense = 4
player.potions = 2
player.gold = 47
player.kills = 8
monsters = spawn_monsters(dungeon.rooms, 2)
items    = spawn_items(dungeon.rooms, 2)
dungeon.compute_fov(sx, sy, 9)

messages = [
    "Orc hits you for 4 dmg!  [22/30 HP]",
    "You hit Orc for 7 dmg!  [5/14 HP]",
    "=== Floor 2 / 5 ===  Find the stairs [>] and descend!",
]

# ── rendering constants ─────────────────────────────────────────────────────
CELL_W, CELL_H = 10, 18
IMG_W = MAP_W * CELL_W
IMG_H = (MAP_H + 9) * CELL_H   # +9 rows for UI

BG       = (18, 18, 28)
C_WALL   = (90, 90, 110)
C_WALL_D = (45, 45, 55)
C_FLOOR  = (50, 80, 100)
C_FLOOR_D= (28, 42, 52)
C_STAIR  = (200, 100, 220)
C_PLAYER = (255, 220, 50)
C_MON    = (220, 60, 60)
C_POTION = (70, 210, 100)
C_GOLD   = (255, 200, 50)
C_TEXT   = (200, 200, 210)
C_DIM    = (120, 120, 140)
C_SEP    = (60, 60, 80)
C_HP_OK  = (70, 200, 100)
C_HP_LOW = (220, 60, 60)

# Try to load a monospace font
def _load_font(size):
    candidates = [
        "/System/Library/Fonts/Supplemental/Courier New.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()

font      = _load_font(13)
font_bold = _load_font(13)

img  = Image.new("RGB", (IMG_W, IMG_H), BG)
draw = ImageDraw.Draw(img)


def draw_char(x, y, ch, color):
    px = x * CELL_W
    py = y * CELL_H
    draw.text((px + 1, py + 1), ch, font=font, fill=color)


# ── map ────────────────────────────────────────────────────────────────────
for my in range(MAP_H):
    for mx in range(MAP_W):
        vis = dungeon.visible[my][mx]
        exp = dungeon.explored[my][mx]
        tile = dungeon.tiles[my][mx]
        if vis:
            if tile == WALL:
                draw_char(mx, my, '#', C_WALL)
            elif tile == STAIRS:
                draw_char(mx, my, '>', C_STAIR)
            else:
                draw_char(mx, my, '·', C_FLOOR)
        elif exp:
            if tile == WALL:
                draw_char(mx, my, '#', C_WALL_D)
            elif tile == STAIRS:
                draw_char(mx, my, '>', (120, 60, 130))
            else:
                draw_char(mx, my, '·', C_FLOOR_D)

# items
for item in items:
    if not dungeon.visible[item.y][item.x]:
        continue
    color = C_GOLD if isinstance(item, Gold) else C_POTION
    draw_char(item.x, item.y, item.char, color)

# monsters
for m in monsters:
    if m.alive and dungeon.visible[m.y][m.x]:
        draw_char(m.x, m.y, m.char, C_MON)

# player
draw_char(player.x, player.y, '@', C_PLAYER)

# ── UI ─────────────────────────────────────────────────────────────────────
ui_y = MAP_H

# separator
draw.rectangle([(0, ui_y * CELL_H), (IMG_W, ui_y * CELL_H + 2)], fill=C_SEP)
ui_y += 1

# status bar
hp_ratio = player.hp / player.max_hp
bar_len = 12
filled = round(hp_ratio * bar_len)
hp_bar = '█' * filled + '░' * (bar_len - filled)
hp_color = C_HP_OK if hp_ratio >= 0.3 else C_HP_LOW
status = (f" HP [{hp_bar}] {player.hp}/{player.max_hp}"
          f"  Lv:{player.level}  XP:{player.xp}/{player.xp_next}"
          f"  ATK:{player.attack}  DEF:{player.defense}"
          f"  Potions:{player.potions}  Gold:{player.gold}"
          f"  Kills:{player.kills}  Floor:{player.floor}/5")
draw.text((2, ui_y * CELL_H + 2), status, font=font_bold, fill=hp_color)
ui_y += 1

draw.rectangle([(0, ui_y * CELL_H), (IMG_W, ui_y * CELL_H + 2)], fill=C_SEP)
ui_y += 1

controls = " [wasd/arrows/hjkl] Move  [p] Potion  [.] Wait  [q] Quit  [>] walk stairs"
draw.text((2, ui_y * CELL_H + 2), controls, font=font, fill=C_DIM)
ui_y += 1

draw.rectangle([(0, ui_y * CELL_H), (IMG_W, ui_y * CELL_H + 2)], fill=C_SEP)
ui_y += 1

for msg in messages[-3:]:
    draw.text((6, ui_y * CELL_H + 2), msg, font=font, fill=C_TEXT)
    ui_y += 1

# ── save ───────────────────────────────────────────────────────────────────
out = os.path.join(os.path.dirname(__file__), "screenshot.png")
img.save(out)
print(f"Saved: {out}")
