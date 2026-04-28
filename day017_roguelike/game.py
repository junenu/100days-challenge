import curses
import math
import random
import sys

from dungeon import Dungeon, WALL, STAIRS
from entities import (
    Player, Monster, Item, Potion, Gold,
    spawn_monsters, spawn_items,
)

MAX_FLOOR = 5
FOV_RADIUS = 9
MSG_LINES = 3
UI_LINES = 6  # separator + status + separator + controls + separator + msgs


# ── colour pair indices ────────────────────────────────────────────────────
C_DEFAULT  = 1
C_PLAYER   = 2
C_MONSTER  = 3
C_POTION   = 4
C_FLOOR    = 5
C_GOLD     = 6
C_STAIRS   = 7
C_WALL_DIM = 8
C_HP_LOW   = 9


class Game:
    def __init__(self, stdscr: curses.window):
        self.scr = stdscr
        self.sh, self.sw = stdscr.getmaxyx()
        self.map_h = max(16, self.sh - UI_LINES - 1)
        self.map_w = max(40, self.sw - 1)
        self.messages: list[str] = []
        self.player: Player | None = None
        self._init_colors()
        self._new_floor(1)

    # ── setup ──────────────────────────────────────────────────────────────

    def _init_colors(self):
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(C_DEFAULT,  curses.COLOR_WHITE,   -1)
        curses.init_pair(C_PLAYER,   curses.COLOR_YELLOW,  -1)
        curses.init_pair(C_MONSTER,  curses.COLOR_RED,     -1)
        curses.init_pair(C_POTION,   curses.COLOR_GREEN,   -1)
        curses.init_pair(C_FLOOR,    curses.COLOR_CYAN,    -1)
        curses.init_pair(C_GOLD,     curses.COLOR_YELLOW,  -1)
        curses.init_pair(C_STAIRS,   curses.COLOR_MAGENTA, -1)
        curses.init_pair(C_WALL_DIM, curses.COLOR_WHITE,   -1)
        curses.init_pair(C_HP_LOW,   curses.COLOR_RED,     -1)

    def _new_floor(self, floor_num: int):
        self.dungeon = Dungeon(self.map_w, self.map_h)
        sx, sy = self.dungeon.rooms[0].center

        if self.player is None:
            self.player = Player(sx, sy)
        else:
            self.player.x, self.player.y = sx, sy
            self.player.floor = floor_num

        self.monsters = spawn_monsters(self.dungeon.rooms, floor_num)
        self.items = spawn_items(self.dungeon.rooms, floor_num)
        self.dungeon.compute_fov(sx, sy, FOV_RADIUS)
        self._msg(f"=== Floor {floor_num} / {MAX_FLOOR} ===  Find the stairs [>] and descend!")

    # ── messages ───────────────────────────────────────────────────────────

    def _msg(self, text: str):
        self.messages.append(text)
        while len(self.messages) > 30:
            self.messages.pop(0)

    # ── main loop ──────────────────────────────────────────────────────────

    def run(self):
        while True:
            self._draw()
            key = self.scr.getch()
            result = self._handle_key(key)
            if result in ('win', 'dead', 'quit'):
                self._show_end(result)
                return

    def _handle_key(self, key: int) -> str | None:
        dx, dy = 0, 0
        if key in (curses.KEY_UP,    ord('k'), ord('w')): dy = -1
        elif key in (curses.KEY_DOWN, ord('j'), ord('s')): dy = 1
        elif key in (curses.KEY_LEFT, ord('h'), ord('a')): dx = -1
        elif key in (curses.KEY_RIGHT,ord('l'), ord('d')): dx = 1
        elif key in (ord('p'), ord('i')): return self._use_potion()
        elif key == ord('.'): pass          # wait a turn
        elif key == ord('q'): return 'quit'
        else: return None

        if dx or dy or key == ord('.'):
            result = self._move_player(dx, dy)
            if result:
                return result
            self._move_monsters()
            if not self.player.alive:
                return 'dead'
            self.dungeon.compute_fov(self.player.x, self.player.y, FOV_RADIUS)
        return None

    # ── player actions ─────────────────────────────────────────────────────

    def _move_player(self, dx: int, dy: int) -> str | None:
        p = self.player
        nx, ny = p.x + dx, p.y + dy

        # Attack if monster is at target cell
        for m in self.monsters:
            if m.alive and m.x == nx and m.y == ny:
                dmg = p.attack + random.randint(-1, 3)
                actual = m.take_damage(dmg)
                self._msg(f"You hit {m.name} for {actual} dmg!  [{m.hp}/{m.max_hp} HP]")
                if not m.alive:
                    self._msg(f"  {m.name} is slain!  +{m.xp_value} XP")
                    p.kills += 1
                    if p.gain_xp(m.xp_value):
                        self._msg(f"*** LEVEL UP!  Now Lv {p.level}  "
                                  f"(HP +8, ATK +2, DEF +1) ***")
                return None

        if not self.dungeon.walkable(nx, ny):
            return None

        p.x, p.y = nx, ny

        # Pick up items
        for item in self.items[:]:
            if item.x == nx and item.y == ny:
                self._msg(item.pick_up(p))
                self.items.remove(item)

        # Check stairs
        if self.dungeon.tiles[ny][nx] == STAIRS:
            next_fl = p.floor + 1
            if next_fl > MAX_FLOOR:
                return 'win'
            self._msg("You descend deeper into the dungeon...")
            self._new_floor(next_fl)

        return None

    def _use_potion(self) -> None:
        p = self.player
        if p.potions <= 0:
            self._msg("You have no potions!")
            return None
        p.potions -= 1
        healed = p.heal(random.randint(15, 28))
        self._msg(f"You drink a potion.  +{healed} HP  [{p.hp}/{p.max_hp}]")
        return None

    # ── monster AI ─────────────────────────────────────────────────────────

    def _move_monsters(self):
        p = self.player
        for m in self.monsters:
            if not m.alive:
                continue

            if not self.dungeon.visible[m.y][m.x]:
                # Wander aimlessly
                if random.random() < 0.25:
                    rdx = random.choice([-1, 0, 1])
                    rdy = random.choice([-1, 0, 1])
                    nx, ny = m.x + rdx, m.y + rdy
                    if (self.dungeon.walkable(nx, ny) and
                            not any(o.x == nx and o.y == ny and o.alive
                                    for o in self.monsters if o is not m)):
                        m.x, m.y = nx, ny
                continue

            dx = p.x - m.x
            dy = p.y - m.y
            dist = math.hypot(dx, dy)

            if dist < 1.5:
                dmg = m.attack + random.randint(-1, 2)
                actual = p.take_damage(dmg)
                self._msg(f"{m.name} hits you for {actual} dmg!  "
                          f"[{p.hp}/{p.max_hp} HP]")
            else:
                # Step toward player (prefer axis with larger delta)
                step_x = (1 if dx > 0 else -1) if abs(dx) >= abs(dy) else 0
                step_y = (1 if dy > 0 else -1) if abs(dy) > abs(dx) else 0
                nx, ny = m.x + step_x, m.y + step_y
                blocked = any(o.x == nx and o.y == ny and o.alive
                              for o in self.monsters if o is not m)
                at_player = (nx == p.x and ny == p.y)
                if self.dungeon.walkable(nx, ny) and not blocked and not at_player:
                    m.x, m.y = nx, ny

    # ── rendering ──────────────────────────────────────────────────────────

    def _draw(self):
        self.scr.erase()
        self._draw_map()
        self._draw_ui()
        self.scr.refresh()

    def _draw_map(self):
        dng = self.dungeon
        p = self.player

        for y in range(dng.height):
            if y >= self.sh - 1:
                break
            for x in range(dng.width):
                if x >= self.sw - 1:
                    break
                vis = dng.visible[y][x]
                exp = dng.explored[y][x]
                tile = dng.tiles[y][x]

                if vis:
                    if tile == WALL:
                        ch, attr = '#', curses.color_pair(C_DEFAULT)
                    elif tile == STAIRS:
                        ch, attr = '>', curses.color_pair(C_STAIRS) | curses.A_BOLD
                    else:
                        ch, attr = '·', curses.color_pair(C_FLOOR)
                elif exp:
                    if tile == WALL:
                        ch, attr = '#', curses.color_pair(C_WALL_DIM) | curses.A_DIM
                    elif tile == STAIRS:
                        ch, attr = '>', curses.color_pair(C_STAIRS) | curses.A_DIM
                    else:
                        ch, attr = '·', curses.color_pair(C_FLOOR) | curses.A_DIM
                else:
                    continue

                try:
                    self.scr.addch(y, x, ch, attr)
                except curses.error:
                    pass

        # Items
        for item in self.items:
            if not dng.visible[item.y][item.x]:
                continue
            color = C_GOLD if isinstance(item, Gold) else C_POTION
            try:
                self.scr.addch(item.y, item.x, item.char,
                               curses.color_pair(color) | curses.A_BOLD)
            except curses.error:
                pass

        # Monsters
        for m in self.monsters:
            if not m.alive or not dng.visible[m.y][m.x]:
                continue
            try:
                self.scr.addch(m.y, m.x, m.char,
                               curses.color_pair(C_MONSTER) | curses.A_BOLD)
            except curses.error:
                pass

        # Player
        try:
            self.scr.addch(p.y, p.x, '@',
                           curses.color_pair(C_PLAYER) | curses.A_BOLD)
        except curses.error:
            pass

    def _draw_ui(self):
        p = self.player
        ui_y = self.map_h
        sep = '─' * (self.sw - 1)

        # HP bar
        bar_len = 12
        filled = round(p.hp / p.max_hp * bar_len)
        hp_bar = '█' * filled + '░' * (bar_len - filled)
        hp_attr = (curses.color_pair(C_HP_LOW) | curses.A_BOLD
                   if p.hp / p.max_hp < 0.3
                   else curses.color_pair(C_POTION) | curses.A_BOLD)

        status = (f" HP [{hp_bar}] {p.hp:>3}/{p.max_hp:<3}"
                  f"  Lv:{p.level}  XP:{p.xp}/{p.xp_next}"
                  f"  ATK:{p.attack}  DEF:{p.defense}"
                  f"  Potions:{p.potions}  Gold:{p.gold}"
                  f"  Kills:{p.kills}  Floor:{p.floor}/{MAX_FLOOR}")
        controls = (" [wasd / arrows / hjkl] Move  "
                    "[p] Potion  [.] Wait  [q] Quit  "
                    "[>] walk onto stairs to descend")

        try:
            self.scr.addstr(ui_y,     0, sep, curses.color_pair(C_DEFAULT))
            self.scr.addstr(ui_y + 1, 0, status[:self.sw - 1], hp_attr)
            self.scr.addstr(ui_y + 2, 0, sep, curses.color_pair(C_DEFAULT))
            self.scr.addstr(ui_y + 3, 0, controls[:self.sw - 1],
                            curses.color_pair(C_DEFAULT) | curses.A_DIM)
            self.scr.addstr(ui_y + 4, 0, sep, curses.color_pair(C_DEFAULT))
            for i, msg in enumerate(self.messages[-MSG_LINES:]):
                self.scr.addstr(ui_y + 5 + i, 1, msg[:self.sw - 2],
                                curses.color_pair(C_DEFAULT))
        except curses.error:
            pass

    # ── end screen ─────────────────────────────────────────────────────────

    def _show_end(self, result: str):
        self.scr.erase()
        p = self.player
        if result == 'win':
            title = '*** VICTORY!  You conquered the dungeon! ***'
        elif result == 'dead':
            title = '*** GAME OVER — You have been slain! ***'
        else:
            title = '*** Farewell, adventurer! ***'

        lines = [
            '',
            title,
            '',
            f'  Floor reached : {p.floor} / {MAX_FLOOR}',
            f'  Level         : {p.level}',
            f'  Gold collected: {p.gold}',
            f'  Monsters slain: {p.kills}',
            '',
            '  Press any key to exit...',
            '',
        ]
        cy = self.sh // 2 - len(lines) // 2
        for i, line in enumerate(lines):
            cx = max(0, self.sw // 2 - 25)
            try:
                self.scr.addstr(cy + i, cx, line, curses.A_BOLD)
            except curses.error:
                pass

        self.scr.refresh()
        self.scr.getch()


# ── entry point ────────────────────────────────────────────────────────────

def main():
    def _run(stdscr: curses.window):
        curses.curs_set(0)
        stdscr.keypad(True)
        game = Game(stdscr)
        game.run()

    curses.wrapper(_run)


if __name__ == '__main__':
    main()
