"""Render one frame of Crystal Shards and save as PNG (no display needed)."""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
pygame.init()

import config as C
from camera import Camera
from world import TileMap, make_area
from entities import Player, Enemy, Item
from ui import HUD

# ── headless surface ──────────────────────────────────────────────────────
screen = pygame.Surface((C.WIDTH, C.HEIGHT))

# ── game state setup ──────────────────────────────────────────────────────
player = Player()
area = make_area("DUNGEON_1", 0)
tilemap = TileMap(area.tiles)
player.reset_pos((6 * C.TILE, 8 * C.TILE))
player.hp = 55
player.gold = 38
player.potions = 2
player.level = 2
player.xp = 14
player.xp_next = 32
player.facing = pygame.Vector2(1, 0)

enemies = []
for tx, ty, kind in area.spawns[:6]:
    e = Enemy(kind, (tx + 0.5) * C.TILE, (ty + 0.5) * C.TILE)
    enemies.append(e)
boss = Enemy(area.boss["kind"], *area.boss["pos"], boss=True)
boss.shard_id = area.boss["shard"]
all_enemies = pygame.sprite.Group(*enemies, boss)

# ── drop a few items on the floor ─────────────────────────────────────────
items_group = pygame.sprite.Group(
    Item(9 * C.TILE, 7 * C.TILE, "gold",   8),
    Item(5 * C.TILE, 10 * C.TILE, "potion", 0),
)

camera = Camera()
camera.update(player)

hud = HUD()

# ── render ────────────────────────────────────────────────────────────────
tick = 1.2
screen.fill(C.BG)
tilemap.render(screen, camera, tick)

for item in items_group:
    item.draw(screen, camera)

for enemy in all_enemies:
    enemy.draw(screen, camera, tick)

player.draw(screen, camera)
hud.draw(screen, player, "DUNGEON_1", "Goblin dies! +10 XP")

# ── save ──────────────────────────────────────────────────────────────────
out = os.path.join(os.path.dirname(__file__), "screenshot.png")
pygame.image.save(screen, out)
pygame.quit()
print(f"Saved: {out}  ({C.WIDTH}x{C.HEIGHT})")
