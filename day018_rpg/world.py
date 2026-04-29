from dataclasses import dataclass

import pygame

import config as C


def blank(tile):
    grid = [[tile for _ in range(C.MAP_W)] for _ in range(C.MAP_H)]
    for y in range(C.MAP_H):
        for x in range(C.MAP_W):
            if x in (0, C.MAP_W - 1) or y in (0, C.MAP_H - 1):
                grid[y][x] = C.WALL
    return grid


def carve_rect(grid, x, y, w, h, tile):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            if 0 <= xx < C.MAP_W and 0 <= yy < C.MAP_H:
                grid[yy][xx] = tile


def wall_rect(grid, x, y, w, h):
    for xx in range(x, x + w):
        grid[y][xx] = C.WALL
        grid[y + h - 1][xx] = C.WALL
    for yy in range(y, y + h):
        grid[yy][x] = C.WALL
        grid[yy][x + w - 1] = C.WALL


@dataclass
class Area:
    name: str
    tiles: list
    spawns: list
    boss: dict | None
    portals: list
    npc_pos: tuple | None = None
    spawn_point: tuple = C.PLAYER_START


class TileMap:
    def __init__(self, tiles):
        self.tiles = tiles
        self.width = C.MAP_PX_W
        self.height = C.MAP_PX_H

    def get_tile(self, px, py):
        tx = int(px // C.TILE)
        ty = int(py // C.TILE)
        if 0 <= tx < C.MAP_W and 0 <= ty < C.MAP_H:
            return self.tiles[ty][tx]
        return C.WALL

    def walkable(self, px, py, radius):
        for ox in (-radius, radius):
            for oy in (-radius, radius):
                if self.get_tile(px + ox, py + oy) not in C.WALKABLE:
                    return False
        return True

    def render(self, surf, camera, tick):
        pulse = 80 + int(35 * (1 + pygame.math.Vector2(1, 0).rotate(tick * 180).x))
        for y, row in enumerate(self.tiles):
            for x, tile in enumerate(row):
                rect = pygame.Rect(x * C.TILE, y * C.TILE, C.TILE, C.TILE)
                pygame.draw.rect(surf, C.TILE_COLORS[tile], camera.apply(rect))
                if tile == C.WALL:
                    pygame.draw.rect(surf, (90, 70, 50), camera.apply(rect), 2)
                elif tile == C.WATER:
                    pygame.draw.line(surf, (120, 170, 230), camera.apply(rect).topleft, camera.apply(rect).bottomright, 2)
                elif tile == C.PORTAL:
                    r = camera.apply(rect)
                    col = (pulse, 100, 220)
                    pygame.draw.circle(surf, col, r.center, 14, 3)
                    pygame.draw.circle(surf, (210, 180, 240), r.center, 7, 2)


def village(shards):
    grid = blank(C.GRASS)
    carve_rect(grid, 0, 6, C.MAP_W, 4, C.FLOOR)
    carve_rect(grid, 3, 3, 5, 3, C.FLOOR)
    carve_rect(grid, 16, 3, 5, 3, C.FLOOR)
    wall_rect(grid, 4, 3, 3, 3)
    wall_rect(grid, 17, 3, 3, 3)
    for x in (6, 12, 18):
        grid[13][x] = C.PORTAL if shards >= (x - 6) // 6 else C.STONE
        grid[14][x] = C.PORTAL if shards >= (x - 6) // 6 else C.STONE
    portals = [
        {"target": "DUNGEON_1", "rect": pygame.Rect(6 * C.TILE, 13 * C.TILE, C.TILE, C.TILE * 2), "active": True, "label": "Forest"},
        {"target": "DUNGEON_2", "rect": pygame.Rect(12 * C.TILE, 13 * C.TILE, C.TILE, C.TILE * 2), "active": shards >= 1, "label": "Cave"},
        {"target": "DUNGEON_3", "rect": pygame.Rect(18 * C.TILE, 13 * C.TILE, C.TILE, C.TILE * 2), "active": shards >= 2, "label": "Tower"},
    ]
    return Area("VILLAGE", grid, [], None, portals, C.NPC_POS, C.PLAYER_START)


def dungeon1():
    grid = blank(C.STONE)
    for x in range(4, 20, 3):
        carve_rect(grid, x, 4 + (x % 2), 1, 6, C.WALL)
    spawns = [(2 + i % 4 * 5, 2 + i // 4 * 4, "slime") for i in range(8)]
    spawns += [(6, 12, "goblin"), (18, 12, "goblin")]
    boss = {"kind": "giant_slime", "pos": (12.5 * C.TILE, 8 * C.TILE), "shard": 1}
    return Area("DUNGEON_1", grid, spawns, boss, [], None, (2.5 * C.TILE, 8 * C.TILE))


def dungeon2():
    grid = blank(C.STONE)
    for x in range(3, 21):
        if x not in (7, 15):
            grid[5][x] = C.WALL
            grid[10][x] = C.WALL
    for y in range(2, 14):
        if y not in (4, 12):
            grid[y][8] = C.WALL
        if y not in (3, 11):
            grid[y][16] = C.WALL
    spawns = [(3, 3, "goblin"), (6, 12, "goblin"), (11, 3, "goblin"), (13, 12, "goblin"), (19, 4, "goblin"), (20, 11, "goblin")]
    spawns += [(5, 8, "skeleton"), (10, 8, "skeleton"), (15, 8, "skeleton"), (19, 8, "skeleton")]
    boss = {"kind": "bone_knight", "pos": (12.5 * C.TILE, 8 * C.TILE), "shard": 2}
    return Area("DUNGEON_2", grid, spawns, boss, [], None, (2.5 * C.TILE, 2.5 * C.TILE))


def dungeon3():
    grid = blank(C.STONE)
    for x in range(4, 20):
        if x not in (7, 12, 17):
            grid[4][x] = C.WALL
            grid[11][x] = C.WALL
    for y in range(3, 13):
        if y not in (6, 9):
            grid[y][5] = C.WALL
            grid[y][18] = C.WALL
    carve_rect(grid, 10, 6, 4, 4, C.FLOOR)
    spawns = [(3, 3, "skeleton"), (8, 2, "skeleton"), (14, 2, "skeleton"), (20, 3, "skeleton")]
    spawns += [(3, 12, "skeleton"), (8, 13, "skeleton"), (14, 13, "skeleton"), (20, 12, "skeleton")]
    spawns += [(6, 7, "dark_orb"), (9, 8, "dark_orb"), (16, 7, "dark_orb"), (19, 8, "dark_orb")]
    boss = {"kind": "dark_wizard", "pos": (12.5 * C.TILE, 8 * C.TILE), "shard": 3}
    return Area("DUNGEON_3", grid, spawns, boss, [], None, (12.5 * C.TILE, 13 * C.TILE))


def make_area(name, shards):
    return {
        "VILLAGE": village(shards),
        "DUNGEON_1": dungeon1(),
        "DUNGEON_2": dungeon2(),
        "DUNGEON_3": dungeon3(),
    }[name]
