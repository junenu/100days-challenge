import random
import math
from dataclasses import dataclass

WALL = '#'
FLOOR = '.'
STAIRS = '>'


@dataclass
class Room:
    x: int
    y: int
    w: int
    h: int

    @property
    def center(self) -> tuple[int, int]:
        return self.x + self.w // 2, self.y + self.h // 2

    def random_point(self) -> tuple[int, int]:
        return (random.randint(self.x + 1, self.x + self.w - 2),
                random.randint(self.y + 1, self.y + self.h - 2))

    def intersects(self, other: 'Room', margin: int = 1) -> bool:
        return (self.x - margin < other.x + other.w and
                self.x + self.w + margin > other.x and
                self.y - margin < other.y + other.h and
                self.y + self.h + margin > other.y)


class Dungeon:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.tiles: list[list[str]] = [[WALL] * width for _ in range(height)]
        self.rooms: list[Room] = []
        self.visible: list[list[bool]] = [[False] * width for _ in range(height)]
        self.explored: list[list[bool]] = [[False] * width for _ in range(height)]
        self._generate()

    def _generate(self):
        for _ in range(300):
            w = random.randint(5, 12)
            h = random.randint(4, 9)
            x = random.randint(1, self.width - w - 2)
            y = random.randint(1, self.height - h - 2)
            room = Room(x, y, w, h)

            if any(room.intersects(r) for r in self.rooms):
                continue

            self._carve_room(room)
            if self.rooms:
                self._connect(self.rooms[-1], room)
            self.rooms.append(room)

            if len(self.rooms) >= 14:
                break

        if self.rooms:
            sx, sy = self.rooms[-1].center
            self.tiles[sy][sx] = STAIRS

    def _carve_room(self, room: Room):
        for y in range(room.y, room.y + room.h):
            for x in range(room.x, room.x + room.w):
                self.tiles[y][x] = FLOOR

    def _connect(self, a: Room, b: Room):
        ax, ay = a.center
        bx, by = b.center
        if random.random() < 0.5:
            self._h_tunnel(ax, bx, ay)
            self._v_tunnel(ay, by, bx)
        else:
            self._v_tunnel(ay, by, ax)
            self._h_tunnel(ax, bx, by)

    def _h_tunnel(self, x1: int, x2: int, y: int):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            if 0 <= y < self.height and 0 <= x < self.width:
                self.tiles[y][x] = FLOOR

    def _v_tunnel(self, y1: int, y2: int, x: int):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            if 0 <= y < self.height and 0 <= x < self.width:
                self.tiles[y][x] = FLOOR

    def walkable(self, x: int, y: int) -> bool:
        return (0 <= x < self.width and
                0 <= y < self.height and
                self.tiles[y][x] != WALL)

    def compute_fov(self, px: int, py: int, radius: int = 9):
        for row in self.visible:
            row[:] = [False] * self.width

        self.visible[py][px] = True
        self.explored[py][px] = True

        for i in range(360):
            angle = math.radians(i)
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            for r in range(1, radius + 1):
                rx = int(px + r * cos_a + 0.5)
                ry = int(py + r * sin_a + 0.5)
                if not (0 <= rx < self.width and 0 <= ry < self.height):
                    break
                self.visible[ry][rx] = True
                self.explored[ry][rx] = True
                if self.tiles[ry][rx] == WALL:
                    break
