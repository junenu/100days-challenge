from math import pi

WIDTH = 960
HEIGHT = 640
FPS = 60
TILE = 40
MAP_W = 24
MAP_H = 16
MAP_PX_W = MAP_W * TILE
MAP_PX_H = MAP_H * TILE

TITLE = "Crystal Shards"

WALL = 0
FLOOR = 1
GRASS = 2
WATER = 3
PORTAL = 4
STONE = 5

TILE_COLORS = {
    WALL: (60, 40, 30),
    FLOOR: (110, 90, 70),
    GRASS: (60, 100, 50),
    WATER: (40, 80, 160),
    PORTAL: (180, 100, 220),
    STONE: (100, 100, 110),
}
WALKABLE = {FLOOR, GRASS, PORTAL, STONE}

BG = (18, 20, 28)
WHITE = (245, 245, 245)
BLACK = (10, 10, 12)
RED = (220, 60, 60)
BLUE = (70, 130, 230)
CYAN = (150, 220, 255)
YELLOW = (245, 220, 80)
GRAY = (80, 80, 90)
DARK_GRAY = (45, 45, 52)
GREEN = (80, 200, 80)
PURPLE = (120, 50, 180)
ORANGE = (200, 100, 50)
GOLD = (255, 215, 0)

PLAYER_RADIUS = 16
PLAYER_START = (TILE * 4.5, TILE * 8.5)
NPC_POS = (TILE * 12.5, TILE * 8.5)
ATTACK_RANGE = 55
ATTACK_ARC = pi * 2 / 3
ATTACK_COOLDOWN = 0.32
ATTACK_FLASH = 0.2
KNOCKBACK = 20
INVULN_TIME = 0.35

PLAYER_BASE = {
    "hp": 80,
    "max_hp": 80,
    "mp": 30,
    "max_mp": 30,
    "atk": 12,
    "def": 4,
    "spd": 180,
    "level": 1,
    "xp": 0,
    "xp_next": 30,
    "gold": 0,
    "potions": 2,
}

ENEMY_STATS = {
    "slime": {"hp": 18, "atk": 6, "def": 0, "spd": 80, "xp": 6, "gold": 3, "aggro": 160, "range": 40, "cd": 1.2, "color": GREEN, "radius": 14},
    "goblin": {"hp": 28, "atk": 9, "def": 1, "spd": 110, "xp": 10, "gold": 6, "aggro": 200, "range": 45, "cd": 1.0, "color": ORANGE, "radius": 14},
    "skeleton": {"hp": 40, "atk": 13, "def": 2, "spd": 90, "xp": 16, "gold": 10, "aggro": 220, "range": 48, "cd": 0.9, "color": (220, 220, 200), "radius": 14},
    "dark_orb": {"hp": 30, "atk": 11, "def": 0, "spd": 120, "xp": 14, "gold": 8, "aggro": 250, "range": 200, "cd": 1.5, "color": (100, 30, 180), "radius": 12},
    "giant_slime": {"hp": 120, "atk": 14, "def": 2, "spd": 70, "xp": 60, "gold": 40, "aggro": 240, "range": 52, "cd": 1.0, "color": (30, 180, 30), "radius": 26},
    "bone_knight": {"hp": 200, "atk": 20, "def": 6, "spd": 85, "xp": 100, "gold": 70, "aggro": 260, "range": 56, "cd": 0.95, "color": (240, 240, 210), "radius": 22},
    "dark_wizard": {"hp": 280, "atk": 18, "def": 4, "spd": 75, "xp": 160, "gold": 120, "aggro": 280, "range": 180, "cd": 1.2, "color": (80, 20, 140), "radius": 20},
}

PROJECTILE_SPEED = 220
PROJECTILE_RADIUS = 6

DROP_GOLD_RATE = 0.6
DROP_POTION_RATE = 0.3
POTION_HEAL = 30
MAX_POTIONS = 5

HUD_H = 56
FONT_NAME = None
PORTAL_LABELS = ["Forest", "Cave", "Tower"]
PORTAL_TARGETS = ["DUNGEON_1", "DUNGEON_2", "DUNGEON_3"]

NPC_TEXT = [
    "The Crystal of Light has been shattered!",
    "Three shards lie in the Forest, the Cave,",
    "and the Dark Tower. You are our only hope.",
]

STATE_LABELS = {
    "TITLE": "Crystal Shards",
    "VILLAGE": "Village",
    "DUNGEON_1": "Forest Shrine",
    "DUNGEON_2": "Echo Cave",
    "DUNGEON_3": "Dark Tower",
    "GAME_OVER": "Game Over",
    "VICTORY": "Victory",
}
